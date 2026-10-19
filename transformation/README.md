# transformation

The dbt project: it turns `raw.orders` into `marts.daily_orders` and tests the data on the way, on a Nessie branch. dbt-duckdb runs it: DuckDB attaches the branch's Iceberg catalog as `lake` and writes the mart there, so a red test never reaches `main`.

## Run

The pipeline runs `dbt build` at its step 3 ([orchestration](../orchestration/README.md#steps)). By hand:

```bash
mise run dbt-inspect <branch>                                  # replay dbt build on a branch, e.g. a kept pipeline-ko branch
mise exec -- env NESSIE_BRANCH=<branch> uv run dbt build       # the same, without swallowing the exit code
```

`mise.toml` exports `DBT_PROJECT_DIR` and `DBT_PROFILES_DIR`, so dbt runs from anywhere in the repository. The branch comes from `NESSIE_BRANCH`; without it, `profiles.yml` falls back to `main` and dbt writes straight to `main`. To work on a branch of your own: [How to work on your own branch](docs/working-on-a-branch.md).

## Files

```text
dbt_project.yml              materializations: staging as views, marts as Iceberg tables in `lake`
profiles.yml                 dbt-duckdb, Nessie catalog attached as `lake`; branch = env NESSIE_BRANCH
macros/                      schema naming, incremental strategy `replace`
models/staging/              sources.yml (raw.orders), stg_orders (+ tests)
models/marts/                daily_orders (Iceberg table) (+ tests)
tests/                       singular test: amount ≥ 0
docs/dbt-on-iceberg.md       how the models are materialized on the attached catalog
docs/working-on-a-branch.md  how to run dbt on a branch of your own
```

## Depends on

No other component: dbt reads and writes through the attached catalog, not through `lakehouse-client`. Packages: `dbt-duckdb` and `duckdb`, a 2.0 pre-release: DuckDB reaches a Nessie branch from 2.0 on ([ADR004](../docs/adr/ADR004-duckdb-attached-to-the-nessie-branch.md)). Not a Python package: its `pyproject.toml` only carries dependencies.

## Models and tests

| Node | Tests |
|---|---|
| source `raw.orders` | |
| `stg_orders` (view) | `order_id` not null and unique, `customer_id` not null, amount ≥ 0 (singular test) |
| `daily_orders` (Iceberg table) | `order_date` not null and unique |

dbt skips `daily_orders` when a staging test fails. The results are in `target/run_results.json`, which the pipeline reads for its summary. Where each node lives, why `incremental` with a `replace` strategy rather than `table`, and what each run leaves in the branch's history: [dbt on Iceberg](docs/dbt-on-iceberg.md).
