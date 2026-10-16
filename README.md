# Nessie demo: a *branch, test, merge* pipeline on an Iceberg lakehouse

A demo of **Project Nessie**, a Git-like versioned catalog for Iceberg tables. A data pipeline processes new data **on an isolated branch**, **tests it with dbt**, and **merges into `main`** only if the tests pass. Otherwise the bad data stays on its branch and an **alert** is raised: `main` never sees it.

```text
open branch  ->  ingest  ->  dbt build (transform + test)  ->  green? -> MERGE + TAG on main
pipeline-HHMMSS  raw.orders  marts.daily_orders                 red?   -> no merge + ALERT
                                                                          (branch pipeline-HHMMSS-bad kept)
```

Everything runs locally: Nessie, PostgreSQL (version store) and Silo (S3 storage, community fork of MinIO) in docker compose; PyIceberg, dbt and DuckDB in Python. Details in [`docs/project/architecture.md`](docs/project/architecture.md).

## Prerequisites

- Docker with compose, running (e.g. Colima)
- [mise](https://mise.jdx.dev): env vars in `mise.toml`, tasks in `tasks.toml`; it installs [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
mise trust                                   # once per clone: let mise load mise.toml
cp mise.local.toml.example mise.local.toml   # once per clone: then set NESSIE_PG_PASSWORD
mise run stack-up      # start Nessie + Postgres + Silo, create the bucket and the raw / marts namespaces
mise run pipeline-ok   # nominal run: branch -> ingest -> dbt build (green) -> merge into main
mise run pipeline-ko   # failing run: bad data -> red tests -> no merge + alert
```

Other tasks:

```bash
mise run branches              # list Nessie branches and tags
mise run cli                   # Nessie REPL connected to main
mise run notebook              # marimo notebook to explore a branch
mise run dbt-inspect <branch>  # replay dbt build on a branch (e.g. the kept -bad branch)
mise run stack-down            # stop the stack, keep the data
mise run stack-reset           # stop and delete everything
```

- Nessie API: http://localhost:19120
- Silo console: http://localhost:29090 (`minioadmin` / `8qqR90Az`)

## Explore the data

`mise run notebook` opens `notebooks/explore.mo.py` in marimo:
- pick a Nessie branch (branches only, not tags);
- every table of every namespace becomes a DuckDB view named `<namespace>_<table>` (`raw.orders` -> `raw_orders`). PyIceberg asks Nessie for each table's current `metadata.json` and DuckDB reads it with `iceberg_scan`: nothing is loaded in advance;
- query them in the SQL cell (`SELECT * FROM raw_orders WHERE amount < 0`).

## Slack alert (optional)

```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…
mise run pipeline-ko   # the alert is also posted to Slack
```

## Documentation

[`docs/README.md`](docs/README.md): Iceberg and Nessie concepts, the project's architecture and pipeline, the Nessie CLI, and the talk's slides and notes (in French).
