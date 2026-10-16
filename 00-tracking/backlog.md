# Backlog

Every item is a **draft**: to be refined (scope, acceptance criteria) before it's ready.

## Features and checks

### Drop PyIceberg with DuckDB 2.0

DuckDB would read and write directly on a Nessie branch (`ATTACH` with the branch in the URI),
without the PyIceberg dbt plugins. The fix (duckdb-iceberg#1230) won't be in a stable release before
DuckDB 2.0.

- Tests of 2026-10-15: DuckDB 1.5.6 fails; pre-release `2.0.0.dev2610011535` reads and writes (with
  `SET iceberg_use_metadata_log = false`), `CREATE OR REPLACE` still refused (#784).
- Integration plan (dbt, notebook, cleanup, slides):
  [`docs/project/duckdb-2.0.md`](../docs/project/duckdb-2.0.md).

### Test Snowflake on a Nessie branch

Documentation research only, nothing tested. Approach: one `ICEBERG_REST` catalog integration with
`PREFIX = '<branch>'` and one catalog-linked database per branch.

Prerequisites: Nessie reachable from the internet and authenticated (Snowflake only accepts OAuth,
bearer or SigV4), files on a real S3 (external volume).

To check: is `PREFIX` honored? Does Snowflake cope with a `metadata.json` that only holds the current
snapshot?

### Nessie version store: `JDBC` to `JDBC2`

`docker-compose.yml` uses `nessie.version.store.type=JDBC`, deprecated for removal in favor of
`JDBC2`. Switching needs a fresh store (`mise run stack-reset`) or a migration with the Nessie Server
Admin Tool.

## Refactoring

The project was built quickly for a live demo. These items turn it into something maintainable.

### dbt project

Observed:
- **Hardcoded credentials and endpoints** in `dbt/profiles.yml`: Silo access key and secret, Nessie
  and S3 URLs, duplicated in both plugin blocks.
- **Silent fallback to `main`**: without `NESSIE_BRANCH`, `env_var('NESSIE_BRANCH', 'main')` makes
  dbt write straight to `main`.
- **`config(location = …)` in `daily_orders.sql`**: an artifact of the `external` materialization,
  which writes a local Parquet file before the `iceberg_write` plugin pushes it to Iceberg. Model
  code shouldn't carry it.
- **`iceberg_write` plugin**: hardcodes the `marts` namespace (ignores the model's schema), always
  overwrites the whole table, goes through pandas (`target_to_df`) then Arrow, only handles added
  columns.
- Staging model described as "typed" but casts nothing; source columns undocumented; `order by` in a
  mart; `tests:` key (dbt ≥ 1.8 prefers `data_tests:`, to check).

Leads: credentials and URLs through `env_var()` set by mise; fail when no branch is given; move
materialization details out of the models (`dbt_project.yml` or a custom materialization); decide
the plugin's future against the DuckDB 2.0 item, which could remove it.

### Python package

Observed:
- **Nessie client** (`nessie.py`): no timeouts, no session or retries, no authentication, raw dicts
  in and out, hash-then-act races (`delete_branch`, `merge`). Could become its own project
  (typed Nessie API v2 client, with tests): to discuss, `pynessie` being dead.
- **No tests** at all, no lint, format or type checking, no CI.
- **Settings**: secrets as code defaults (`settings.py`), `env_prefix=""` so generic variable names
  (`WAREHOUSE`, `S3_ENDPOINT`…).
- **`pipeline.py` mixes orchestration and narrated display** (`display.py`, French strings): the
  demo output should be a layer on top of a reusable pipeline.
- Packaging: dependencies to review (`pandas` is only there for the dbt plugin path, `numpy` only for
  synthetic data), `uv_build<0.10` constraint warning with the current uv, `ingest` script entry
  point still exposed.

Leads: decide the client's scope first (in repo or separate package); add pytest with the stack as a
fixture for integration tests; ruff and a type checker; split core and presentation.

### Configuration and secrets (cross-cutting)

The same values are repeated in `docker-compose.yml`, `mise.toml`, `settings.py`, `dbt/profiles.yml`
and `bootstrap.py` (Silo `minioadmin` / `8qqR90Az`, Nessie and S3 URLs). One source of truth, with
secrets kept out of tracked files (e.g. `mise.local.toml` or a generated `.env`).
