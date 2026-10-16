# T020 PyIceberg doesn't apply the delete files DuckDB writes

Found in T001. DuckDB replaces the rows of `marts.daily_orders` with a delete then an insert; it writes position delete files (merge-on-read). PyIceberg 0.10.0 doesn't apply them: `table.scan()` returns the deleted rows too (2 rows instead of 1 on `main` after two runs), and `plan_files()` attaches no delete file to any data file. DuckDB reads the same table correctly. The pipeline and the notebook now read the marts with DuckDB, so nothing in the demo is wrong today; but any PyIceberg reader of a DuckDB-written table would be.

Find out why (sequence numbers in DuckDB's delete manifests? a PyIceberg limitation? Nessie keeping one snapshot per `metadata.json`?), whether a newer PyIceberg fixes it, and whether it's worth an upstream issue.

## Notes

- Observed on 2026-10-16: DuckDB `2.0.0.dev2610151406`, PyIceberg 0.10.0, Nessie 0.106.0, table format v2.
- `snapshot.summary` shows `total-position-deletes` and `total-delete-files` greater than 0, so the delete files are in the metadata.
