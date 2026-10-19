# ADR004 DuckDB reads and writes the dbt models directly on the Nessie branch; PyIceberg only ingests

- Status: accepted
- Date: 2026-10-16
- Tickets: T001
- Basis: investigated (pipeline runs and probes on 2026-10-16 with DuckDB `2.0.0.dev2610151406`, dbt-duckdb 1.10.1, PyIceberg 0.10.0; [dbt on Iceberg](../project/dbt-on-iceberg.md))
- Supersedes: ADR003
- Amended: 2026-10-19: PyIceberg 0.12 applies the delete files DuckDB writes (#42); Consequences and Revisit when updated, the decision is unchanged.

## Context

ADR003 routed every Iceberg read and write through PyIceberg because DuckDB's Iceberg extension ignored the URI Nessie returns and only saw `main`. The fix (duckdb-iceberg#1230) is in DuckDB 2.0. On 2026-10-16 DuckDB 2.0.0 is announced for 2026-10-21; the repo is a POC, so a pre-release is acceptable. With the pre-release, `ATTACH` on `http://…/iceberg/<branch>` reads and writes on the branch. Three limits of the extension shape how dbt can use it: no `CREATE OR REPLACE TABLE` (duckdb-iceberg#784), no views in the catalog, and a transaction can't mix table updates with renames, which breaks dbt-duckdb's `table` materialization.

## Decision

- dbt attaches the Nessie catalog of the branch as `lake` (`transformation/profiles.yml`); no dbt plugin.
- Sources read `lake.raw`; staging models are views in the local DuckDB database; mart models are Iceberg tables in `lake.marts`, materialized `incremental` with a `replace` strategy of ours (delete all rows, insert the model's result, one transaction, one Iceberg commit).
- Tables DuckDB writes are read with DuckDB (`lake.py`: pipeline output, notebook).
- PyIceberg stays for ingestion, namespace creation and the raw row count from snapshot metadata.

## Alternatives ruled out

- dbt-duckdb's `table` materialization: fails, the REST catalog refuses its create-then-rename transaction.
- A custom materialization doing `DROP` then `CREATE TABLE AS`: two commits, and the table is missing between them; not needed since the incremental strategy works.
- Built-in `delete+insert` strategy: needs a `unique_key` and only replaces the matching rows; not tried.
- Keeping the PyIceberg plugins (ADR003): no longer needed, and they carried dbt-duckdb internals.
- Waiting for DuckDB 2.0 stable: the POC doesn't need it; the move to stable is a follow-up ticket.

## Consequences

- One dependency on a DuckDB pre-release until 2.0 ships.
- The marts are read by the engine that writes them. PyIceberg reads them right from 0.12 on (locked since 2026-10-19); older versions mishandle the manifest entries DuckDB writes (apache/iceberg-python#3256), and 0.10 counts the deleted rows too.
- Each run adds data and delete files to `daily_orders` (merge-on-read), never compacted: fine at demo scale.
- `SET iceberg_use_metadata_log = false` is required for writes.
- The slides still describe the PyIceberg detour.

## Revisit when

DuckDB 2.0 ships as stable, or duckdb-iceberg#784 is fixed (the `table` materialization or a `CREATE OR REPLACE` may become possible).
