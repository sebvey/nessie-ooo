# T004 Refactor the dbt project

The dbt project was built quickly for a live demo; make it maintainable.

## Notes

Observed:
- **Hardcoded credentials and endpoints** in `dbt/profiles.yml`: Silo access key and secret, Nessie and S3 URLs (since T001: in the `secrets` and `attach` blocks).
- **Silent fallback to `main`**: without `NESSIE_BRANCH`, `env_var('NESSIE_BRANCH', 'main')` makes dbt write straight to `main`.
- ~~`config(location = …)` in `daily_orders.sql` and the `iceberg_write` plugin~~: gone with T001 (DuckDB attached to the branch, incremental `replace` strategy).
- Staging model described as "typed" but casts nothing; source columns undocumented; `order by` in a mart; `tests:` key (dbt ≥ 1.8 prefers `data_tests:`, to check).

Leads: credentials and URLs through `env_var()` set by mise (see [T006](T006-configuration-and-secrets.md)); fail when no branch is given.
