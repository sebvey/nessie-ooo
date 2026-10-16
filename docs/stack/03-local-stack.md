# Local stack (docker compose)

`docker-compose.yml` runs everything the demo needs on one machine. Start it with `mise run stack-up`,
which also creates the `raw` and `marts` namespaces on `main`.

## Services

| Service | Image | Role | Host ports |
|---|---|---|---|
| `nessie` | `ghcr.io/projectnessie/nessie:0.106.0` | Versioned catalog: Nessie API (`/api/v2`) and Iceberg REST (`/iceberg/<branch>`) | `19120` (API), `19000` (management: health, metrics) |
| `postgres` | `postgres:15` | Nessie version store (commit graph, refs, table pointers) | `35432` |
| `minio` | `pgsty/minio` | Silo, the community fork of MinIO: S3 storage for Iceberg files | `29000` (S3 API), `29090` (console) |
| `minio-setup` | `pgsty/mc` | One-shot job: creates the `iceberg-warehouse` bucket, then exits | none |
| `nessie-cli` | `ghcr.io/projectnessie/nessie-cli:0.106.0` | Nessie REPL, only started by `mise run cli` (profile `tools`) | none |

The official MinIO images are no longer published (Docker Hub and quay.io answer 401), hence Silo.
The Docker service is still called `minio`.

Start order: `postgres` and `minio` become healthy, `minio-setup` creates the bucket, then `nessie`
starts.

## How Nessie is configured

- **Version store**: `nessie.version.store.type=JDBC` on Postgres. `JDBC` is deprecated for removal
  in favor of `JDBC2`; switching requires a fresh store or a migration with the Nessie Server Admin
  Tool.
- **Warehouse**: `s3://iceberg-warehouse/`, declared as the default warehouse `warehouse`. Nessie
  itself writes the Iceberg `metadata.json` files there when clients commit through Iceberg REST.
- **S3 endpoints**: Nessie reaches Silo at `http://minio:9000` (compose network) and hands clients
  `http://127.0.0.1:29000` (`external-endpoint`).
- **Security**: authentication and authorization are disabled. Anyone who can reach port 19120 can
  write to any branch, including `main`.

## Credentials

Local demo values, also exported by `mise.toml` (`AWS_*`) for S3 clients:

- Silo: `minioadmin` / `8qqR90Az` (console at http://localhost:29090)
- Postgres: `nessie` / `nessie`

## Checks

```bash
curl -s http://localhost:19000/q/health          # Nessie health
curl -s http://localhost:19120/api/v2/trees      # branches and tags
curl -s http://localhost:19120/iceberg/main/v1/config   # Iceberg REST config for branch main
mise run branches                                # same as /trees, formatted
```

## Lifecycle

```bash
mise run stack-up      # start and prepare main (idempotent)
mise run stack-down    # stop, keep volumes
mise run stack-reset   # stop and delete volumes: Nessie history and all Iceberg files
```
