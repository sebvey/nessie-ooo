# The pipeline: branch, test, merge

`mise run pipeline-ok` and `mise run pipeline-ko` run `src/nessie_demo/pipeline.py`. It processes new orders on an isolated branch, tests them with dbt, and merges into `main` only if every test passes. Otherwise the bad data stays on its branch and an alert is raised: `main` never sees it.

```text
open branch  ->  ingest  ->  dbt build (transform + test)  ->  green? -> MERGE + TAG on main
pipeline-HHMMSS  raw.orders  marts.daily_orders                 red?   -> no merge + ALERT
                                                                          (branch pipeline-HHMMSS-bad kept)
```

The console output is meant to be narrated: one block per step, with a pause (Enter) that names the next step.

## Before the first run: `mise run stack-up`

`src/nessie_demo/bootstrap.py` starts the stack, shows that `main` sits on the "no ancestor" commit, then creates the `raw` (raw data, as ingested) and `marts` (transformed and tested data) namespaces on `main`. A `main` without commits can't receive a merge ("No common ancestor"); the pipeline refuses to start until this is done. Running it again is harmless ("already there").

## Steps

0. **Starting point**: hash of `main`, and the content of `raw.orders` and `marts.daily_orders` on `main` ("doesn't exist yet" on the first run). Read from the Nessie API and the Iceberg metadata; nothing is written.
1. **Open a branch**: `Nessie.create_branch("pipeline-HHMMSS", from_ref="main")` (suffix `-bad` with `--bad`). Same commit as `main`, no data copied.
2. **Ingest**: `ingest.py` generates 5 synthetic orders and appends them to `raw.orders` on the branch through PyIceberg. With `--bad`, one order has a negative amount and one a `null` customer (shown in red). The branch now has 5 more rows; `main` hasn't moved.
3. **Transform and test**: `NESSIE_BRANCH=<branch> dbt build`:
   - reads `raw.orders` on the branch (dbt-duckdb's bundled `iceberg` plugin);
   - builds `stg_orders` (DuckDB view) then `marts.daily_orders`, written as an Iceberg table on the branch by the `iceberg_write` plugin;
   - runs the tests: `order_id` not null and unique, `customer_id` not null, amount ≥ 0 (singular test `dbt/tests/assert_amount_non_negative.sql`), `order_date` not null and unique. The summary is read from `dbt/target/run_results.json`. dbt skips `daily_orders` when the staging tests fail.
4. **Decision**:
   - all green: `Nessie.merge(branch -> main)` (one atomic commit on `main`, both tables at once), tag `release-HHMMSS`, branch deleted;
   - red: no merge, `main`'s hash unchanged, `alert()` (console, plus Slack if `SLACK_WEBHOOK_URL` is set), branch kept for investigation.

## Options

```bash
uv run pipeline --bad        # inject bad rows (what pipeline-ko does)
uv run pipeline --keep       # keep the branch even after a merge
uv run pipeline --no-pause   # no Enter between steps
uv run pipeline --verbose    # raw dbt output
```

## After a red run

```bash
mise run branches                          # the -bad branch is still there
mise run dbt-inspect pipeline-HHMMSS-bad   # replay dbt build on it
mise run notebook                          # pick the branch, query raw_orders
```

## Files

```text
src/nessie_demo/
├─ settings.py        config (Nessie URIs, S3), local defaults
├─ nessie.py          Nessie API v2 client: branch, merge, tag, delete, list, log
├─ catalog.py         PyIceberg catalog scoped to a branch
├─ ingest.py          synthetic orders -> raw.orders (--bad for the failing case)
├─ bootstrap.py       stack-up: stack + namespaces on main
├─ pipeline.py        orchestrator: steps 0 to 4
├─ display.py         narrated console output (steps, pauses, tables)
├─ alert.py           alert (console + optional Slack webhook)
└─ dbt_plugins/iceberg_write.py   dbt-duckdb plugin: writes a model as an Iceberg table on the branch
dbt/
├─ profiles.yml       dbt-duckdb; branch = env NESSIE_BRANCH
├─ models/staging/    sources.yml, stg_orders (+ tests)
├─ models/marts/      daily_orders (Iceberg table) (+ tests)
└─ tests/             singular test: amount ≥ 0
```
