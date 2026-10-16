# Nessie deployment options

## Runtime

- **Single container**: `ghcr.io/projectnessie/nessie`, fine for local work.
- **docker compose**: Nessie plus its version store and object storage (this repo).
- **Kubernetes**: Nessie publishes a Helm chart. Nessie is stateless when the version store is
  external, so it scales horizontally.

## Version store (`nessie.version.store.type`)

| Type | Use |
|---|---|
| `IN_MEMORY` | Tests only (default value): everything is lost on restart |
| `ROCKSDB` | Single node, embedded on a volume; no HA |
| `JDBC2` | PostgreSQL, MySQL/MariaDB, H2…; the usual choice for teams |
| `MONGODB2`, `CASSANDRA2`, `BIGTABLE`, `DYNAMODB2` | Managed or distributed backends |

`JDBC`, `MONGODB` and `CASSANDRA` (without the `2`) are deprecated for removal; the Nessie Server Admin
Tool migrates their data. This repo still uses `JDBC` on Postgres (to switch before any reuse).

## Storage

- Nessie stores catalog history only, in the version store.
- Iceberg files live in the warehouse declared to Nessie (`nessie.catalog.warehouses.*`): S3, GCS,
  ADLS, or an S3-compatible store (Silo here). With Iceberg REST, Nessie needs credentials for that
  store, because it writes `metadata.json` files and can hand storage settings to clients.

## Choices in this repo

| Concern | Choice | Why |
|---|---|---|
| Runtime | docker compose, Nessie `0.106.0` | One command, everything local |
| Version store | Postgres (`JDBC`) | Durable across restarts, close to a production setup |
| Warehouse | Silo (`s3://iceberg-warehouse`) | S3 API locally; official MinIO images are gone |
| Engines | PyIceberg, dbt-duckdb | Light, no JVM; DuckDB can't address a Nessie branch yet |
| Nessie operations | `src/nessie_demo/nessie.py` (API v2), Nessie CLI | `pynessie` is API v1 and unmaintained |

## Before production

Authentication and authorization (disabled here), `JDBC2`, Nessie GC for cleanup, and a durable
object store. See the "À creuser" slide in `docs/presentation/presentation.html`.
