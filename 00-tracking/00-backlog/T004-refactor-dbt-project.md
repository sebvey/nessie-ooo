# T004 Refactor the dbt project

The dbt project was built quickly for a live demo; make it maintainable.

## Notes

Observed:
- **Hardcoded credentials and endpoints** in `dbt/profiles.yml`: Silo access key and secret, Nessie and S3 URLs, duplicated in both plugin blocks.
- **Silent fallback to `main`**: without `NESSIE_BRANCH`, `env_var('NESSIE_BRANCH', 'main')` makes dbt write straight to `main`.
- **`config(location = …)` in `daily_orders.sql`**: an artifact of the `external` materialization, which writes a local Parquet file before the `iceberg_write` plugin pushes it to Iceberg. Model code shouldn't carry it.
- **`iceberg_write` plugin**: hardcodes the `marts` namespace (ignores the model's schema), always overwrites the whole table, goes through pandas (`target_to_df`) then Arrow, only handles added columns.
- Staging model described as "typed" but casts nothing; source columns undocumented; `order by` in a mart; `tests:` key (dbt ≥ 1.8 prefers `data_tests:`, to check).

Leads: credentials and URLs through `env_var()` set by mise (see [T006](T006-configuration-and-secrets.md)); fail when no branch is given; move materialization details out of the models (`dbt_project.yml` or a custom materialization); the `iceberg_write` plugin goes with [T001](../01-ready/T001-duckdb-direct-on-nessie-branch.md).
