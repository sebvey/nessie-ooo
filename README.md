# Nessie demo: a *branch, test, merge* pipeline on an Iceberg lakehouse

A demo of **Project Nessie**, a Git-like versioned catalog for Iceberg tables. A data pipeline processes new data **on an isolated branch**, **tests it with dbt**, and **merges into `main`** only if the tests pass. Otherwise the bad data stays on its branch and an **alert** is raised: `main` never sees it.

```text
open branch  ->  ingest  ->  dbt build (transform + test)  ->  green? -> MERGE + TAG on main
pipeline-ok|ko-  raw.orders  marts.daily_orders                 red?   -> no merge + ALERT
HHMMSS                                                                    (branch pipeline-ko-HHMMSS kept)
```

Everything runs locally: Nessie, PostgreSQL (version store) and Silo (S3 storage, community fork of MinIO) in docker compose; PyIceberg, dbt and DuckDB in Python. Details in [`docs/project/architecture.md`](docs/project/architecture.md).

## Prerequisites

- Docker with compose, running (e.g. Colima)
- [mise](https://mise.jdx.dev): env vars in `mise.toml`, tasks in `tasks.toml`; it installs [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
mise trust                                   # once per clone: let mise load mise.toml
cp mise.local.toml.example mise.local.toml   # once per clone: then set the passwords (Postgres, Silo)
mise run stack-up      # start Nessie + Postgres + Silo, create the bucket and the raw / marts namespaces
mise run pipeline-ok   # nominal run: branch -> ingest -> dbt build (green) -> merge into main
mise run pipeline-ko   # failing run: bad data -> red tests -> no merge + alert
```

Other tasks:

```bash
mise run branches              # list Nessie branches and tags
mise run cli                   # Nessie REPL connected to main
mise run ui-nessie             # open Nessie's web UI in the browser
mise run ui-silo               # open the Silo console in the browser
mise run ui-exploration        # marimo notebook to explore a branch
mise run dbt-inspect <branch>  # replay dbt build on a branch (e.g. the kept pipeline-ko branch)
mise run stack-down            # stop the stack, keep the data
mise run stack-reset           # stop and delete everything
mise run audit-python          # known vulnerabilities in the locked Python dependencies (not the images)
```

- Nessie API: http://localhost:19120
- Silo console: http://localhost:29090 (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` from `mise.local.toml`)

## Explore the data

`mise run ui-exploration` opens `exploration/explore.mo.py` in marimo:
- pick a Nessie branch (branches only, not tags);
- DuckDB attaches the branch's catalog as `lake` and lists its tables with their row counts; nothing is loaded in advance;
- query them in the SQL cell as `lake.<namespace>.<table>` (`SELECT * FROM lake.raw.orders WHERE amount < 0`).

## Slack alert (optional)

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…
mise run pipeline-ko   # the alert is also posted to Slack
```

## Repository layout

One folder per component, each a uv workspace member with its own dependencies ([architecture](docs/project/architecture.md#components)):

```text
stack/              docker compose (Nessie, PostgreSQL, Silo) and the stack-up bootstrap
lakehouse-client/   Nessie API client, PyIceberg catalog and DuckDB access to a branch, settings
ingestion/          synthetic orders appended to raw.orders
transformation/     the dbt project: models and tests
orchestration/      the pipeline: branch, ingest, dbt build, merge or alert
exploration/        marimo notebook to query a branch
```

## Documentation

[`docs/README.md`](docs/README.md): Iceberg and Nessie concepts, the project's architecture and pipeline, the Nessie CLI, and the talk's slides and notes (in French).
