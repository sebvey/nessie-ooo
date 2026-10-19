# The pipeline: branch, test, merge

`mise run pipeline-ok` and `mise run pipeline-ko` run `orchestration/src/orchestration/pipeline.py`. It processes new orders on an isolated branch, tests them with dbt, and merges into `main` only if every test passes. Otherwise the bad data stays on its branch and an alert is raised: `main` never sees it.

```text
open branch  ->  ingest  ->  dbt build (transform + test)  ->  green? -> MERGE + TAG on main
pipeline-ok|ko-  raw.orders  marts.daily_orders                 red?   -> no merge + ALERT
HHMMSS                                                                    (branch pipeline-ko-HHMMSS kept)
```

The console output is meant to be narrated: one block per step, with a pause (Enter) that names the next step.

## Before the first run: `mise run stack-up`

`stack/src/stack/bootstrap.py` starts the stack, shows that `main` sits on the "no ancestor" commit, then creates the `raw` (raw data, as ingested) and `marts` (transformed and tested data) namespaces on `main`. A `main` without commits can't receive a merge ("No common ancestor"); the pipeline refuses to start until this is done. Running it again is harmless ("already there").

## Steps

0. **Starting point**: hash of `main`, and the content of `raw.orders` and `marts.daily_orders` on `main` ("doesn't exist yet" on the first run). Read from the Nessie API, PyIceberg (raw row count from the metadata) and DuckDB (`daily_orders`); nothing is written.
1. **Open a branch**: `Nessie.create_branch("pipeline-ok-HHMMSS", from_ref="main")` (`pipeline-ko-HHMMSS` with `--ko`). Same commit as `main`, no data copied.
2. **Ingest**: `ingest.py` generates 5 synthetic orders and appends them to `raw.orders` on the branch through PyIceberg. With `--ko`, one order has a negative amount and one a `null` customer (shown in red). The branch now has 5 more rows; `main` hasn't moved.
3. **Transform and test**: `NESSIE_BRANCH=<branch> dbt build`:
   - DuckDB attaches the branch's catalog as `lake` and reads `lake.raw.orders`;
   - builds `stg_orders` (view in dbt's local DuckDB file) then `lake.marts.daily_orders`, an Iceberg table on the branch, replaced at every run in one commit ([dbt on Iceberg](dbt-on-iceberg.md));
   - runs the tests: `order_id` not null and unique, `customer_id` not null, amount ≥ 0 (singular test `transformation/tests/assert_amount_non_negative.sql`), `order_date` not null and unique. The summary is read from `transformation/target/run_results.json`. dbt skips `daily_orders` when the staging tests fail.
4. **Decision**:
   - all green: `Nessie.merge(branch -> main)` (one atomic commit on `main`, both tables at once), tag `release-HHMMSS`, branch deleted;
   - red: no merge, `main`'s hash unchanged, `alert()` (console, plus Slack if `SLACK_WEBHOOK_URL` is set), branch kept for investigation.

## Options

```bash
uv run pipeline --ko         # inject bad rows (what pipeline-ko does)
uv run pipeline --keep       # keep the branch even after a merge
uv run pipeline --no-pause   # no Enter between steps
uv run pipeline --verbose    # raw dbt output
```

## After a red run

```bash
mise run branches                         # the pipeline-ko branch is still there
mise run dbt-inspect pipeline-ko-HHMMSS   # replay dbt build on it
mise run ui-exploration                    # pick the branch, query raw_orders
```

## Files

```text
stack/
├─ docker-compose.yml           Nessie, PostgreSQL, Silo
└─ src/stack/bootstrap.py       stack-up: stack + namespaces on main
lakehouse-client/src/lakehouse_client/
├─ settings.py                  config (Nessie URIs, S3), read from the mise environment
├─ nessie.py                    Nessie API v2 client: branch, merge, tag, delete, list, log
├─ catalog.py                   PyIceberg catalog scoped to a branch
└─ lake.py                      DuckDB with the branch's catalog attached as `lake` (reads the marts)
ingestion/src/ingestion/
└─ ingest.py                    synthetic orders -> raw.orders (--ko for the failing case)
transformation/
├─ profiles.yml                 dbt-duckdb, Nessie catalog attached as `lake`; branch = env NESSIE_BRANCH
├─ macros/                      schema naming, incremental strategy `replace`
├─ models/staging/              sources.yml, stg_orders (+ tests)
├─ models/marts/                daily_orders (Iceberg table) (+ tests)
└─ tests/                       singular test: amount ≥ 0
orchestration/src/orchestration/
├─ pipeline.py                  orchestrator: steps 0 to 4
├─ display.py                   narrated console output (steps, pauses, tables)
└─ alert.py                     alert (console + optional Slack webhook)
```
