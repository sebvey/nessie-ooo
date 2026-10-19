# Architecture overview

How the demo works as a whole: the flow of a pipeline run, how the components connect, and how each of them reaches a Nessie branch. The Iceberg and Nessie concepts behind it: [Concepts](../concepts/README.md).

## The flow

A run of the pipeline works on a branch of its own, and `main` changes only through a merge:

1. **orchestration** opens a branch `pipeline-ok|ko-HHMMSS` from `main` (Nessie API).
2. **ingestion** appends new orders to `raw.orders` on that branch (PyIceberg).
3. **transformation** runs `dbt build` on the branch: DuckDB reads `raw.orders`, writes `marts.daily_orders`, and dbt tests the data.
4. **orchestration** merges the branch into `main` and tags it if every test passed; otherwise it alerts and keeps the branch, and `main` never sees the bad data.

Step by step, with what the console shows: [orchestration](../../orchestration/README.md#steps). The **stack** runs the services every step talks to; **exploration** reads any branch afterwards.

## Components

The repository is split into **components**: a top-level folder with one responsibility and its own `README.md`. The list, with a line each, is in the [root README](../../README.md#components). Each component is a uv workspace member with its own `pyproject.toml`, which declares the dependencies the component uses, other components included. The workspace has one `uv.lock` and one `.venv`. The root `pyproject.toml` is the whole demo: it depends on every component, so `uv run <command>` works from anywhere in the repository. Why: [ADR010](../adr/ADR010-components-as-uv-workspace-members.md). How a component declares a dependency, and how to check it: [dependency policy](dependency-policy.md#components).

How they connect:

- **lakehouse-client** is the only library: every Python component that reaches Nessie or the Iceberg tables goes through it (Nessie API, PyIceberg catalog, DuckDB with the branch attached, settings).
- **orchestration** drives a run: it calls **ingestion** as a library (step 2) and runs **transformation**'s `dbt build` as a subprocess (step 3).
- **transformation** doesn't use lakehouse-client: dbt attaches the branch's catalog itself, from its profile.
- **stack** runs Nessie, PostgreSQL and Silo; its bootstrap uses lakehouse-client to prepare `main`.
- **exploration** only reads, through lakehouse-client.

Every component talks to the stack over HTTP: the Nessie API (`/api/v2`), Nessie's Iceberg REST catalog (`/iceberg/<branch>`), and Silo's S3 API for the data files.

## Read and write paths

Read:
1. The client opens `http://localhost:19120/iceberg/<branch>` and calls `/v1/config`; Nessie returns the prefix (the branch) and the base URI.
2. It loads `raw.orders`: Nessie returns the metadata that the branch's pointer names.
3. It reads the manifest list, the manifests, then only the Parquet files it needs, from Silo.

Write:
1. The client writes new Parquet files and manifests to Silo.
2. It sends a commit for that table and branch, with its requirements.
3. Nessie checks them, writes the new `metadata.json`, and records a commit on the branch.

Other branches, `main` included, are untouched until a merge. Creating a branch copies no file; a merge only moves pointers.

## Who reads and writes what

Decision and alternatives: [ADR004](../adr/ADR004-duckdb-attached-to-the-nessie-branch.md), which supersedes [ADR003](../adr/ADR003-pyiceberg-as-the-data-plane.md) (the former PyIceberg detour).

Every client puts the branch in the catalog URI (`http://localhost:19120/iceberg/<branch>`):

- **Ingestion**: PyIceberg appends to `raw.orders` (`ingestion`); `stack`'s bootstrap creates the namespaces through PyIceberg too.
- **dbt**: DuckDB attaches the branch's catalog as `lake` (`transformation/profiles.yml`), reads `lake.raw.orders` and writes `lake.marts.daily_orders`. How the models are materialized: [dbt on Iceberg](../../transformation/dbt-on-iceberg.md).
- **Pipeline output and notebook**: DuckDB, through `lakehouse-client`'s `lake.py` (the same `ATTACH`, read-only): the marts are read by the engine that writes them. The raw row count still comes from PyIceberg's snapshot summary (metadata only).

DuckDB reaches a branch from DuckDB 2.0 on (duckdb-iceberg#1230); before, it ignored the `overrides.uri` Nessie returns and only saw `main` (duckdb-iceberg#1145). The repo runs a 2.0 pre-release.
