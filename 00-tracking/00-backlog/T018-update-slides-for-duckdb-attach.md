# T018 Update the slides for DuckDB attached to the Nessie branch

Since T001, dbt reads and writes the Iceberg tables through DuckDB attached to the branch (ADR004); the PyIceberg dbt plugins are gone. `docs/presentation/presentation.html` still tells the PyIceberg detour.

## Notes

- Slide 05 "Le détour par PyIceberg": becomes "what we did before DuckDB 2.0", or goes.
- The "Maturité" slide: DuckDB moves to "Mature (≥ 2.0)".
- The PyIceberg card (role, demo lines, alternatives) and the "Plugin dbt custom" card (`iceberg_write`, `dbt_plugins/`), the diagram labelled `plugin iceberg_write`, the read/write paragraph naming both plugins.
- New material for the talk: [dbt on Iceberg](../../docs/project/dbt-on-iceberg.md) (why `table` fails, the `replace` strategy, one commit per run).
- Slides stay in French.
