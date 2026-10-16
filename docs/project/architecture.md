# Architecture

What runs, how it's wired, and why. For the concepts behind it, see [Nessie overview](../concepts/nessie-overview.md).

## Components

| Plane | Component | Role |
|---|---|---|
| Orchestration | `src/nessie_demo/pipeline.py` | Runs the steps, merges if the tests pass, alerts otherwise |
| Control plane | `src/nessie_demo/nessie.py` | Python class over the Nessie API v2: create, merge, tag, delete branches |
| Control plane | `src/nessie_demo/alert.py` | Console alert, optional Slack webhook |
| Data plane | PyIceberg (`catalog.py`, `ingest.py`) | Reads and writes Iceberg tables on a branch |
| Data plane | dbt on DuckDB | Transforms and tests; DuckDB only computes |
| Data plane | `dbt_plugins/iceberg_write.py` | dbt-duckdb plugin that writes a model as an Iceberg table on the branch |
| Infra | Nessie, PostgreSQL, Silo | Catalog, version store, S3 storage (docker compose) |

## Services (docker compose)

| Service | Image | Role | Host ports |
|---|---|---|---|
| `nessie` | `ghcr.io/projectnessie/nessie:0.106.0` | Nessie API (`/api/v2`) and Iceberg REST (`/iceberg/<branch>`) | `19120` (API), `19000` (management: health, metrics) |
| `postgres` | `postgres:15` | Nessie version store | `35432` |
| `minio` | `pgsty/minio` | Silo, the community fork of MinIO: S3 storage for Iceberg files | `29000` (S3 API), `29090` (console) |
| `minio-setup` | `pgsty/mc` | One-shot job: creates the `iceberg-warehouse` bucket | none |
| `nessie-cli` | `ghcr.io/projectnessie/nessie-cli:0.106.0` | Nessie REPL, started by `mise run cli` (profile `tools`) | none |

The official MinIO images are no longer published (Docker Hub and quay.io answer 401), hence Silo. The Docker service is still called `minio`.

Start order: `postgres` and `minio` become healthy, `minio-setup` creates the bucket, then `nessie` starts. `mise run stack-up` then creates the `raw` and `marts` namespaces on `main`, so that `main` has commits and can receive merges.

## Nessie configuration

- **Version store**: `nessie.version.store.type=JDBC2` on Postgres, through the Quarkus datasource named `postgresql` (`nessie.version.store.persist.jdbc.datasource`, `quarkus.datasource.postgresql.*`). Nessie creates its two tables at startup: `refs2` (branches and tags, like `.git/refs`) and `objs2` (commits, content values and internal objects, each serialized in `obj_value`, like `.git/objects`). Nessie itself is stateless: restarting it loses nothing.
- **Warehouse**: `s3://iceberg-warehouse/`, declared as the default warehouse. Nessie announces it in `/v1/config` and writes the `metadata.json` files there.
- **S3 endpoints**: Nessie reaches Silo at `http://minio:9000` (compose network); its `external-endpoint` (`http://127.0.0.1:29000`) is the address meant for clients. The demo's clients set their S3 endpoint themselves anyway (`settings.py`, `dbt/profiles.yml`).
- **Security**: authentication and authorization are disabled. Anyone who can reach port 19120 can write to any branch, including `main`.

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

## Why PyIceberg, and not DuckDB directly

Decision and alternatives: [ADR003](../adr/ADR003-pyiceberg-as-the-data-plane.md).

DuckDB's Iceberg extension can attach an Iceberg REST catalog, but up to DuckDB 1.5 it ignores the `overrides.uri` Nessie returns and calls `/iceberg/<branch>/v1/<branch>/…`: it only works on `main` (duckdb-iceberg#1145, fixed on the extension's main branch, not in a stable release yet). So:

- PyIceberg talks to the catalog, with the branch in its URI.
- dbt-duckdb reads sources through its bundled `iceberg` plugin (PyIceberg scan to Arrow) and writes models through `iceberg_write`; DuckDB only runs the SQL.
- The notebook asks PyIceberg for each table's `metadata.json` and lets DuckDB read it with `iceberg_scan`, which doesn't go through the REST catalog.

Plan to drop the detour once DuckDB 2.0 ships: [DuckDB 2.0](duckdb-2.0.md).

## Choices

| Concern | Choice | Why |
|---|---|---|
| Runtime | docker compose, Nessie `0.106.0` | One command, everything local |
| Version store | Postgres (`JDBC2`) | Durable across restarts, same model as production: stateless Nessie, external database |
| Warehouse | Silo (`s3://iceberg-warehouse`) | S3 API locally; official MinIO images are gone |
| Engines | PyIceberg, dbt-duckdb | Light, no JVM ([ADR003](../adr/ADR003-pyiceberg-as-the-data-plane.md)) |
| Nessie operations | `nessie.py` (API v2), Nessie CLI | `pynessie` is API v1 and unmaintained |
| Tasks and env | mise (`mise.toml`, `tasks.toml`) | Tools, env vars and tasks in one place |

## Credentials

- Postgres (version store): `NESSIE_PG_USER` / `NESSIE_PG_PASSWORD` in `mise.local.toml` (ignored by git, template in `mise.local.toml.example`). `docker-compose.yml` reads them for both the `postgres` and `nessie` services and refuses to start without them, so run compose through mise. Changing the password needs `mise run stack-reset`: Postgres only reads it on first start.
- Silo: `minioadmin` / `8qqR90Az` (console at http://localhost:29090), still hardcoded in several files and exported by `mise.toml` (`AWS_*`) for S3 clients.

## Checks

```bash
curl -s http://localhost:19000/q/health                  # Nessie health
curl -s http://localhost:19120/api/v2/trees              # branches and tags
curl -s http://localhost:19120/iceberg/main/v1/config    # Iceberg REST config for main
mise run branches                                        # branches and tags, formatted
```
