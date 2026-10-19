# orchestration

The demo pipeline: it opens a Nessie branch, ingests new orders on it, runs `dbt build`, and merges into `main` only if every test passes. Otherwise the bad data stays on its branch and an alert is raised: `main` never sees it. The console output is meant to be narrated: one block per step, with a pause (Enter) that names the next step.

## Run

The stack must be up and bootstrapped ([`mise run stack-up`](../stack/README.md#bootstrap-mise-run-stack-up)): the pipeline refuses to start on a `main` without commits.

```bash
mise run pipeline-ok   # nominal run: branch -> ingest -> dbt build (green) -> merge into main
mise run pipeline-ko   # failing run: bad data -> red tests -> no merge + alert
```

The command behind them, `pipeline`, with its options:

```bash
uv run pipeline --ko         # inject bad rows (what pipeline-ko does)
uv run pipeline --keep       # keep the branch even after a merge
uv run pipeline --no-pause   # no Enter between steps
uv run pipeline --verbose    # raw dbt output
```

To post the alert to Slack as well, set `SLACK_WEBHOOK_URL` (`export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…`) before a run.

## Files

```text
src/orchestration/
├─ pipeline.py    the steps 0 to 4 (command `pipeline`)
├─ display.py     narrated console output: steps, pauses, tables
└─ alert.py       alert: console panel, optional Slack webhook
```

## Depends on

[`lakehouse-client`](../lakehouse-client/README.md) (Nessie API, catalog, DuckDB reads), [`ingestion`](../ingestion/README.md) (step 2, called as a library), [`transformation`](../transformation/README.md) (step 3, `dbt build` run as a subprocess on `transformation/`). Packages: `rich` (console), `requests` (Slack), `duckdb`, `pyarrow`.

## Steps

0. **Starting point**: hash of `main`, and the content of `raw.orders` and `marts.daily_orders` on `main` ("doesn't exist yet" on the first run). Read from the Nessie API, PyIceberg (raw row count from the metadata) and DuckDB (`daily_orders`); nothing is written.
1. **Open a branch**: `pipeline-ok-HHMMSS` from `main` (`pipeline-ko-HHMMSS` with `--ko`). Same commit as `main`, no data copied.
2. **Ingest**: 5 synthetic orders appended to `raw.orders` on the branch ([ingestion](../ingestion/README.md)); with `--ko`, the dirty rows are shown in red. The branch now has 5 more rows; `main` hasn't moved.
3. **Transform and test**: `NESSIE_BRANCH=<branch> dbt build` ([transformation](../transformation/README.md#models-and-tests)). The summary of models and tests is read from dbt's `run_results.json`.
4. **Decision**:
   - all green: merge the branch into `main` (one atomic commit on `main`, both tables at once), tag `release-HHMMSS`, delete the branch;
   - red: no merge, `main`'s hash unchanged, alert, branch kept for investigation.

## After a red run

```bash
mise run branches                         # the pipeline-ko branch is still there
mise run dbt-inspect pipeline-ko-HHMMSS   # replay dbt build on it
mise run ui-exploration                   # pick the branch, query raw.orders
```
