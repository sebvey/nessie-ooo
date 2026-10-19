# Architecture

What runs, how it's wired, and why. For the concepts behind it, see [Nessie overview](../concepts/nessie-overview.md).

## Components

The repository is split into **components**: a top-level folder with one responsibility. Each is a uv workspace member with its own `pyproject.toml`, which declares the dependencies the component uses, other components included. The workspace has one `uv.lock` and one `.venv`. The root `pyproject.toml` is the whole demo: it depends on every component, so `uv run <command>` works from anywhere in the repository. Why: [ADR010](../adr/ADR010-components-as-uv-workspace-members.md).

| Component | Plane | Holds | Depends on |
|---|---|---|---|
| `stack/` | Infra | `docker-compose.yml` (Nessie, PostgreSQL, Silo); `bootstrap` (`mise run stack-up`): starts the stack, creates the namespaces on `main` | `lakehouse-client` |
| `lakehouse-client/` | Control and data plane | `nessie.py`: Python class over the Nessie API v2 (create, merge, tag, delete branches); `catalog.py`: PyIceberg catalog scoped to a branch; `lake.py`: DuckDB with the branch's catalog attached as `lake`; `settings.py`: config read from the mise environment | |
| `ingestion/` | Data plane | `ingest.py`: synthetic orders appended to `raw.orders` with PyIceberg (`--ko` for the failing case) | `lakehouse-client` |
| `transformation/` | Data plane | The dbt project: dbt-duckdb transforms and tests, reading and writing the branch's Iceberg tables through an `ATTACH` | |
| `orchestration/` | Orchestration | `pipeline.py`: runs the steps, merges if the tests pass, alerts otherwise; `display.py`: narrated console output; `alert.py`: console alert, optional Slack webhook | `lakehouse-client`, `ingestion`, `transformation` |
| `exploration/` | | `explore.mo.py`: marimo notebook to query a branch | `lakehouse-client` |

`transformation` and `exploration` are not Python packages (a dbt project, a notebook): their `pyproject.toml` only carries dependencies. The commands keep the names of their entry points: `bootstrap` (stack), `ingest` (ingestion), `pipeline` (orchestration).

### Checking a component's dependencies

The shared `.venv` holds every component's dependencies, so an import a component doesn't declare still works in it. `--exact` removes from the `.venv` what the component doesn't declare, then runs the command:

```bash
mise exec -- uv run --exact --package orchestration pipeline --help
mise exec -- uv run --exact --package transformation dbt parse
mise exec -- uv run --exact --package exploration python -P -c "import lakehouse_client.lake"
mise exec -- uv sync    # put every component back
```

`python -P`: Python run from the repository root also sees the component folders (`orchestration/`, `stack/`…) as namespace packages, which would hide a missing dependency on another component. Entry points (`pipeline`, `dbt`…) don't have that problem.

## Services (docker compose)

In `stack/docker-compose.yml`. `mise.toml` exports `COMPOSE_FILE`, so `docker compose` finds it from anywhere in the repository; the file fixes the compose project name (`nessie-ooo`), which names the containers' volumes.

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
- **S3 endpoints**: Nessie reaches Silo at `http://minio:9000` (compose network); its `external-endpoint` (`http://127.0.0.1:29000`) is the address meant for clients. The demo's clients set their S3 endpoint themselves anyway (`AWS_ENDPOINT_URL`, read by `settings.py` and `transformation/profiles.yml`).
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

## Who reads and writes what

Decision and alternatives: [ADR004](../adr/ADR004-duckdb-attached-to-the-nessie-branch.md), which supersedes [ADR003](../adr/ADR003-pyiceberg-as-the-data-plane.md) (the former PyIceberg detour).

Every client puts the branch in the catalog URI (`http://localhost:19120/iceberg/<branch>`):

- **Ingestion**: PyIceberg appends to `raw.orders` (`ingest.py`); `bootstrap.py` creates the namespaces through PyIceberg too.
- **dbt**: DuckDB attaches the branch's catalog as `lake` (`transformation/profiles.yml`), reads `lake.raw.orders` and writes `lake.marts.daily_orders`. How the models are materialized: [dbt on Iceberg](dbt-on-iceberg.md).
- **Pipeline output and notebook**: DuckDB, through `lake.py` (the same `ATTACH`, read-only): the marts are read by the engine that writes them. The raw row count still comes from PyIceberg's snapshot summary (metadata only).

DuckDB reaches a branch from DuckDB 2.0 on (duckdb-iceberg#1230); before, it ignored the `overrides.uri` Nessie returns and only saw `main` (duckdb-iceberg#1145). The repo runs a 2.0 pre-release.

## Choices

| Concern | Choice | Why |
|---|---|---|
| Runtime | docker compose, Nessie `0.106.0` | One command, everything local |
| Version store | Postgres (`JDBC2`) | Durable across restarts, same model as production: stateless Nessie, external database |
| Warehouse | Silo (`s3://iceberg-warehouse`) | S3 API locally; official MinIO images are gone |
| Engines | DuckDB 2.0 (pre-release) with dbt-duckdb, PyIceberg for ingestion | Light, no JVM ([ADR004](../adr/ADR004-duckdb-attached-to-the-nessie-branch.md)) |
| Nessie operations | `nessie.py` (API v2), Nessie CLI | `pynessie` is API v1 and unmaintained |
| Tasks and env | mise (`mise.toml`, `tasks.toml`) | Tools, env vars and tasks in one place |
| Repository layout | Components as uv workspace members, one lock | Each component declares what it needs ([ADR010](../adr/ADR010-components-as-uv-workspace-members.md)) |

## Credentials

- Postgres (version store): `NESSIE_PG_USER` / `NESSIE_PG_PASSWORD` in `mise.local.toml` (ignored by git, template in `mise.local.toml.example`). `stack/docker-compose.yml` reads them for both the `postgres` and `nessie` services and refuses to start without them, so run compose through mise. Changing the password needs `mise run stack-reset`: Postgres only reads it on first start.
- Silo: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `mise.local.toml`, the root user of Silo (console at http://localhost:29090). The standard AWS names, so `stack/docker-compose.yml` (Silo, its bucket setup, Nessie), `settings.py`, `transformation/profiles.yml` and the AWS CLI all read the same pair. Compose refuses to start without them; `settings.py` and dbt stop with the name of the missing variable.

The other values the clients need are not secrets and live in `mise.toml`: `NESSIE_URI` (Nessie from the host) and `AWS_ENDPOINT_URL`, `AWS_REGION` (Silo from the host), `SILO_CONSOLE_URL` (Silo console). `settings.py` has no default for them: outside mise, it stops instead of guessing.

## Checks

```bash
curl -s http://localhost:19000/q/health                  # Nessie health
curl -s http://localhost:19120/api/v2/trees              # branches and tags
curl -s http://localhost:19120/iceberg/main/v1/config    # Iceberg REST config for main
mise run branches                                        # branches and tags, formatted
```
