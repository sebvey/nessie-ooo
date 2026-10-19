# stack

The local infrastructure: Nessie, its PostgreSQL version store and Silo (S3 storage) in docker compose, and `bootstrap`, which starts them and prepares `main`. Everything else in the repository talks to this stack.

## Run

```bash
mise run stack-up      # start the stack, create the raw / marts namespaces on main
mise run stack-down    # stop the stack, keep the data
mise run stack-reset   # stop and delete everything: Nessie history and Iceberg files
mise run branches      # list Nessie branches and tags
mise run cli           # Nessie REPL connected to main
mise run ui-nessie     # open Nessie's web UI in the browser
mise run ui-silo       # open the Silo console in the browser
```

- Nessie API: http://localhost:19120
- Silo console: http://localhost:29090 (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` from `mise.local.toml`)

`mise.toml` exports `COMPOSE_FILE`, so `docker compose` finds the compose file from anywhere in the repository. The file fixes the compose project name (`nessie-ooo`), which names the containers' volumes.

The Nessie REPL's commands: [Nessie CLI reference](docs/nessie-cli.md).

## Files

```text
docker-compose.yml           services, below
src/stack/bootstrap.py       stack-up: start the stack, create the namespaces on main
docs/nessie-cli.md           Nessie CLI reference
```

## Depends on

[`lakehouse-client`](../lakehouse-client/README.md) (Nessie API, PyIceberg catalog, settings), and `rich` for the console output.

## Bootstrap: `mise run stack-up`

`bootstrap` starts the stack, shows that `main` sits on the "no ancestor" commit, then creates the `raw` (raw data, as ingested) and `marts` (transformed and tested data) namespaces on `main`. A `main` without commits can't receive a merge ("No common ancestor"); the pipeline refuses to start until this is done. Running it again is harmless ("already there").

## Services

| Service | Image | Role | Host ports |
|---|---|---|---|
| `nessie` | `ghcr.io/projectnessie/nessie:0.106.0` | Nessie API (`/api/v2`) and Iceberg REST (`/iceberg/<branch>`) | `19120` (API), `19000` (management: health, metrics) |
| `postgres` | `postgres:15` | Nessie version store | `35432` |
| `minio` | `pgsty/minio` | Silo, the community fork of MinIO: S3 storage for Iceberg files | `29000` (S3 API), `29090` (console) |
| `minio-setup` | `pgsty/mc` | One-shot job: creates the `iceberg-warehouse` bucket | none |
| `nessie-cli` | `ghcr.io/projectnessie/nessie-cli:0.106.0` | Nessie REPL, started by `mise run cli` (profile `tools`) | none |

Start order: `postgres` and `minio` become healthy, `minio-setup` creates the bucket, then `nessie` starts.

Why these: docker compose runs everything locally with one command. Postgres keeps the history across restarts, the same model as production (a stateless Nessie, an external database). Silo gives an S3 API locally: the official MinIO images are no longer published (Docker Hub and quay.io answer 401). The Docker service is still called `minio`.

## Nessie configuration

- **Version store**: `nessie.version.store.type=JDBC2` on Postgres, through the Quarkus datasource named `postgresql` (`nessie.version.store.persist.jdbc.datasource`, `quarkus.datasource.postgresql.*`). Nessie creates its two tables at startup: `refs2` (branches and tags, like `.git/refs`) and `objs2` (commits, content values and internal objects, each serialized in `obj_value`, like `.git/objects`). Nessie itself is stateless: restarting it loses nothing.
- **Warehouse**: `s3://iceberg-warehouse/`, declared as the default warehouse. Nessie announces it in `/v1/config` and writes the `metadata.json` files there.
- **S3 endpoints**: Nessie reaches Silo at `http://minio:9000` (compose network); its `external-endpoint` (`http://127.0.0.1:29000`) is the address meant for clients. The demo's clients set their S3 endpoint themselves anyway (`AWS_ENDPOINT_URL`).
- **Security**: authentication and authorization are disabled. Anyone who can reach port 19120 can write to any branch, including `main`.

## Credentials and settings

- Postgres (version store): `NESSIE_PG_USER` / `NESSIE_PG_PASSWORD` in `mise.local.toml` (ignored by git, template in `mise.local.toml.example`). `docker-compose.yml` reads them for both the `postgres` and `nessie` services and refuses to start without them, so run compose through mise. Changing the password needs `mise run stack-reset`: Postgres only reads it on first start.
- Silo: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in `mise.local.toml`, the root user of Silo. The standard AWS names, so `docker-compose.yml` (Silo, its bucket setup, Nessie), the clients' settings (`lakehouse-client`), dbt's profile (`transformation`) and the AWS CLI all read the same pair. Compose refuses to start without them; the settings and dbt stop with the name of the missing variable.

The other values the clients need are not secrets and live in `mise.toml`: `NESSIE_URI` (Nessie from the host) and `AWS_ENDPOINT_URL`, `AWS_REGION` (Silo from the host), `SILO_CONSOLE_URL` (Silo console). The settings have no default for them: outside mise, they stop instead of guessing.

## Checks

```bash
curl -s http://localhost:19000/q/health                  # Nessie health
curl -s http://localhost:19120/api/v2/trees              # branches and tags
curl -s http://localhost:19120/iceberg/main/v1/config    # Iceberg REST config for main
mise run branches                                        # branches and tags, formatted
```
