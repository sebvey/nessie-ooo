# T024 Consistent naming of the data layers

The names of the layers don't line up: the Iceberg namespaces are `raw` and `marts`, while the dbt project has a `staging` folder (`models/staging/`, holding `sources.yml` for `raw.orders` and the `stg_orders` view) and a `marts` folder. Reading the repo or the demo, it's unclear whether "staging" and "raw" are the same layer. Make the naming consistent across namespaces, dbt folders and model names, docs and pipeline output.

## Notes

- Not necessarily a mistake: in dbt's usual layering, `raw` is the loaded data (the source), `staging` is a light cleaning layer over it (`stg_` models, one per source), then `marts`. Here staging is a view in dbt's local DuckDB file, not in the catalog (the Iceberg extension can't create views there, T001). The ticket may end with renaming, or with keeping the dbt convention and explaining it where it shows (docs, slides, pipeline output).
- Where the names show (2026-10-16): `dbt/dbt_project.yml`, `dbt/models/staging/` (`sources.yml`, `stg_orders.sql`, `stg_orders.yml`), `dbt/tests/assert_amount_non_negative.sql`, `src/nessie_demo/pipeline.py` (model and test labels), `src/nessie_demo/bootstrap.py` (namespaces), `docs/project/pipeline.md`, `docs/project/dbt-on-iceberg.md` and `dbt/profiles.yml` (comment) once T001 lands, and the slides.
- Renaming tests changes their names in `run_results.json`: the labels in `pipeline.py` follow.
