# dbt on Iceberg: how the models are materialized

How dbt-duckdb builds models when the Nessie catalog is attached to DuckDB as an Iceberg database, which SQL it sends, and what each run leaves in the branch's Nessie history. Why this setup: [ADR004](../adr/ADR004-duckdb-attached-to-the-nessie-branch.md).

Observed on 2026-10-16 with DuckDB `2.0.0.dev2610151406`, dbt-core 1.11.16, dbt-duckdb 1.10.1, Nessie 0.106.0. The SQL comes from dbt's log (`dbt/logs/dbt.log`) and from dbt-duckdb's macros (`dbt/include/duckdb/macros/materializations/` in the installed package).

## The setup

`dbt/profiles.yml` opens a local DuckDB file (`dbt/target/nessie_demo.duckdb`), loads `httpfs` and `iceberg`, creates an S3 secret for Silo, and attaches the catalog:

```sql
ATTACH IF NOT EXISTS 'warehouse' AS lake (TYPE iceberg, ENDPOINT 'http://localhost:19120/iceberg/<branch>', AUTHORIZATION_TYPE 'none')
```

The branch comes from `NESSIE_BRANCH`. Every write through `lake` is a commit on that branch, never on `main`.

| Node | Lives in | Why |
|---|---|---|
| source `raw.orders` | `lake.raw.orders` | `database: lake` in `sources.yml` |
| `stg_orders` (view) | local DuckDB file, `main.stg_orders` | the Iceberg extension can't create views in the catalog (`Not implemented Error: Create View`) |
| `daily_orders` (incremental) | `lake.marts.daily_orders` | `+database: lake`, `+schema: marts` in `dbt_project.yml`; `macros/generate_schema_name.sql` keeps `marts` as is instead of dbt's default `main_marts` |

Writes need `SET iceberg_use_metadata_log = false` (profile `settings`): otherwise any write after a table creation fails with "table metadata does not contain a metadata-log".

## The `table` materialization: doesn't work

dbt-duckdb's `table` materialization (`table.sql`) never sends `CREATE OR REPLACE`. Inside one transaction it runs:

1. `create table <model>__dbt_tmp as <query>`
2. if the model exists: `alter table <model> rename to <model>__dbt_backup`
3. `alter table <model>__dbt_tmp rename to <model>`
4. `commit`, then `drop table <model>__dbt_backup`

The Iceberg REST catalog commits a transaction atomically, and DuckDB refuses to send one that mixes table updates with renames: `TransactionContext Error: Iceberg REST Catalog cannot commit this transaction atomically because it mixes table updates with rename/drop requests`. The model fails from the first run, since step 3 follows step 1 in the same transaction. A rename alone, outside a transaction, works (one Nessie commit "rename table …").

## The `incremental` materialization with the `replace` strategy: what we use

dbt-duckdb's `incremental` materialization (`incremental.sql`) has two paths:

**The table doesn't exist** (first run on a branch where `main` has no `daily_orders`): one statement in a transaction.

```sql
create table "lake"."marts"."daily_orders" as (<query>)
```

Nessie commit: `Create ICEBERG_TABLE marts.daily_orders`.

**The table exists** (every later run): dbt computes the model into a local temporary table, then calls the strategy macro.

```sql
create temporary table "daily_orders__dbt_tmp…" as (<query>)  -- local DuckDB, not in the catalog
-- strategy `replace` (dbt/macros/incremental_replace.sql):
delete from "lake"."marts"."daily_orders";
insert into "lake"."marts"."daily_orders" by name select * from "daily_orders__dbt_tmp…";
commit
```

Nessie commit: one `Update ICEBERG_TABLE marts.daily_orders` per run. The delete and the insert land in a single Iceberg commit, so the branch never shows an empty table.

Details:

- **`by name`**: dbt lists the columns of the target to build the insert, but on an attached Iceberg table it gets a placeholder column `__` of type `UNKNOWN` (the extension loads a table's schema lazily). Matching by name avoids that list.
- **`--full-refresh`** takes the `table` path above (create an intermediate table, then rename in the same transaction), so it should fail the same way. Read from the macro, not tried; the pipeline doesn't use it.
- **Built-in strategies** `append` and `delete+insert` should work the same way (temporary table, then statements on the target), but weren't tried. `delete+insert` needs a `unique_key` and only replaces the rows whose key comes back.

## What the files look like

DuckDB deletes rows with **position delete files** (merge-on-read): the old data files stay, and a delete file marks their rows as removed. Each run adds one data file and one delete file to `daily_orders`, never compacted. Fine at demo scale.

A reader must apply these delete files, or it returns the deleted rows too. The pipeline and the notebook read the marts with DuckDB, the engine that writes them (`src/nessie_demo/lake.py`). PyIceberg reads them right from 0.12 on; older versions attach no delete file to the data files when a manifest entry leaves its `snapshot_id` null, as DuckDB's do ([apache/iceberg-python#3256](https://github.com/apache/iceberg-python/issues/3256)). The raw row count still comes from PyIceberg's snapshot summary, valid because `raw.orders` only gets appends.

## One run in the branch's history

A pipeline run where `main` already has `daily_orders`:

```text
Update ICEBERG_TABLE marts.daily_orders   <- dbt, incremental `replace`
Update ICEBERG_TABLE raw.orders           <- ingestion, PyIceberg append
```

The merge into `main` then carries both tables in one commit, as before.
