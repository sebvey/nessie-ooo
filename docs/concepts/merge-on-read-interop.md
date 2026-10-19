# Merge-on-read across engines

A table one engine writes with row-level deletes is only read right by another engine that applies those deletes the same way. This page explains how a reader matches delete files to data files, and the two interoperability bugs found between DuckDB (writer) and PyIceberg (reader). Background on manifests and files: [Iceberg metadata](iceberg-metadata.md).

## How a reader applies position deletes

In merge-on-read, a `DELETE` doesn't rewrite data files: the writer adds a **position delete file**, whose rows are `(file_path, pos)` pairs, each marking one row of one data file as removed. To read the table, the scan planner attaches to each data file the delete files that may apply to it, then drops the marked rows.

A delete file applies to a data file when both hold:

- **Sequence numbers**: the delete file's data sequence number is greater than or equal to the data file's (a delete only removes rows that existed when it was committed).
- **Path**: the delete file may target that data file. The planner prunes with the bounds of the delete file's `file_path` column (field ID `2147483546`) stored in the manifest, or with `referenced_data_file` when the delete file targets a single data file. Without bounds, it can't prune: the delete file is a candidate for every data file, and the `file_path` values inside it filter the rows.

### Inherited fields

In a v2 manifest, an entry may leave `snapshot_id`, `sequence_number` and `file_sequence_number` null: the reader inherits them from the manifest list (the manifest's `added_snapshot_id` and `sequence_number`), the sequence numbers only for entries with status `ADDED`. Writers differ: PyIceberg and Java write `snapshot_id` explicitly, DuckDB leaves all three null. Both are valid, so a reader must handle both.

## DuckDB to PyIceberg

Investigated on 2026-10-19 on a scratch Nessie branch: DuckDB `2.0.0.dev2610151406` (iceberg extension `5b9ff899a1`) creates a v2 table, inserts 3 rows, deletes 1; DuckDB then reads 2 rows. The manifests were decoded with fastavro as an independent reader, and PyIceberg's code read.

| PyIceberg | Rows read | Delete file attached |
|---|---|---|
| 0.10.0 | 3 (wrong) | none |
| 0.11.1 | 2 | yes |
| 0.12.0 | 2 | yes |

### Bug 1, PyIceberg: the inherited `snapshot_id` overwrites `status`

In PyIceberg up to 0.11.1, the `ManifestEntry.snapshot_id` setter writes into the `status` slot ([apache/iceberg-python#3256](https://github.com/apache/iceberg-python/issues/3256), fixed by [#3257](https://github.com/apache/iceberg-python/pull/3257), first released in 0.12.0). It only fires when an entry's `snapshot_id` is null, which is DuckDB's case and not PyIceberg's own. Then:

- `status` holds a snapshot ID instead of `ADDED`, so the sequence numbers aren't inherited and stay null;
- in 0.10, the planner keeps a delete file only if its sequence number is strictly greater than the data file's after a null falls back to 0, so `0 > 0` drops every delete file;
- 0.11 rewrote the matching (`DeleteFileIndex`) with "greater than or equal": `0 >= 0` keeps them, so the scan comes out right although the entries are still corrupted. Right by accident: any check that reads `status` or the sequence numbers of these entries is still wrong in 0.11.

### Bug 2, DuckDB: the delete file's path bounds under the wrong field ID

DuckDB's iceberg extension writes a delete file's `file_path` bounds in the manifest under field ID `2147483646` instead of `2147483546` (the Parquet file itself uses the right IDs) ([duckdb/duckdb-iceberg#1566](https://github.com/duckdb/duckdb-iceberg/issues/1566), fixed on 2026-10-13 by [#1568](https://github.com/duckdb/duckdb-iceberg/pull/1568), after the extension build above). Readers find no path bounds and can't prune delete files: slower planning on large tables, still correct results. `referenced_data_file` is written right.
