# T019 Move from the DuckDB 2.0 pre-release to the stable release

T001 pinned `duckdb>=2.0.0.dev2610151406`, a pre-release, because DuckDB 2.0 wasn't out on 2026-10-16 (announced for 2026-10-21 on the DuckDB release calendar, tentative). Move to the stable release once it ships.

## Notes

- Upgrade per `docs/project/dependency-policy.md`: `uv lock --upgrade-package duckdb`, floor = locked version, `mise run audit-python`, end-to-end check.
- Re-check against the stable release what T001 observed on the pre-release ([dbt on Iceberg](../../docs/project/dbt-on-iceberg.md)): `SET iceberg_use_metadata_log = false` still needed, `table` materialization still refused, views in the catalog, duckdb-iceberg#784.
- Check dbt-duckdb's support for DuckDB 2.0 (1.10.1 is locked; 1.11.0 out on 2026-08-07).
