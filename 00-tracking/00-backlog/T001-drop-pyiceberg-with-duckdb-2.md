# T001 Drop PyIceberg with DuckDB 2.0

DuckDB would read and write directly on a Nessie branch (`ATTACH` with the branch in the URI),
without the PyIceberg dbt plugins. The fix (duckdb-iceberg#1230) won't be in a stable release before
DuckDB 2.0.

## Notes

- Tests of 2026-10-15: DuckDB 1.5.6 fails; pre-release `2.0.0.dev2610011535` reads and writes (with
  `SET iceberg_use_metadata_log = false`), `CREATE OR REPLACE` still refused (#784).
- Integration plan (dbt, notebook, cleanup, slides):
  [`docs/project/duckdb-2.0.md`](../../docs/project/duckdb-2.0.md).
- Overlaps with [T004](T004-refactor-dbt-project.md): the `iceberg_write` plugin may go.
