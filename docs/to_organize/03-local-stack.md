# Local stack (docker-compose): Nessie + MinIO

Use one docker-compose to run both Nessie (catalog) and MinIO (S3-compatible storage for Iceberg files) with non-conflicting ports.

## Prerequisites
- Docker + Docker Compose
- Free ports: 19120 (Nessie API), 19000 (Nessie health), 9000/9001 (MinIO API/console)
- `curl` for checks

## docker-compose.yml
Save this at the repo root as `docker-compose.yml`:

```yaml
services:
  nessie:
    image: ghcr.io/projectnessie/nessie:latest
    container_name: nessie
    environment:
      NESSIE_VERSION_STORE_TYPE: ROCKSDB
      QUARKUS_SWAGGER_UI_ALWAYS_INCLUDE: "true"  # enable Swagger UI in prod mode
    ports:
      - "19120:19120"  # Nessie API
      - "19000:9000"   # Quarkus health (container 9000 -> host 19000)
    volumes:
      - nessie_data:/nessie/data

  minio:
    image: quay.io/minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"  # MinIO S3 API
      - "9001:9001"  # MinIO console
    volumes:
      - minio_data:/data

volumes:
  nessie_data:
  minio_data:
```

## Start both services
```bash
docker compose up -d
```

## Health checks
- Nessie health (Quarkus): `curl -s http://localhost:19000/q/health/ready || echo "Nessie not reachable"`
- Nessie API sanity: `curl -s http://localhost:19120/api/v2/trees`
- MinIO console: open `http://localhost:9001` (login `minioadmin/minioadmin`)
- Swagger/OpenAPI UI (enabled via env above): try `http://localhost:19120/q/swagger-ui` or `http://localhost:19000/q/swagger-ui` (management port). Some builds omit the UI even when `QUARKUS_SWAGGER_UI_ALWAYS_INCLUDE` is set; if 404 persists, use the OpenAPI JSON (`curl http://localhost:19120/q/openapi`) or `pynessie`.

## Create the Iceberg bucket (one-time)
```bash
docker run --rm --network host quay.io/minio/mc:latest \
  mc alias set local http://localhost:9000 minioadmin minioadmin && \
  mc mb -p local/iceberg-warehouse
```

- What it does:
  - Runs the MinIO client (`mc`) in a disposable container (`--rm`), using host networking so `localhost:9000` reaches your MinIO.
  - `mc alias set local …` registers an alias `local` pointing to the MinIO S3 API with the default creds.
  - `mc mb -p local/iceberg-warehouse` creates the `iceberg-warehouse` bucket (parents if missing).

Use `s3a://iceberg-warehouse` as your Iceberg warehouse URI when configuring Spark.

Alternative: create the bucket via the MinIO console
- Open `http://localhost:9001`
- Login: access key `minioadmin`, secret `minioadmin`
- Create a bucket named `iceberg-warehouse`

## Optional: `pynessie` CLI walkthrough
Inspect Nessie refs/history without Spark. Install and point it at your local server:

```bash
uv tool install pynessie
nessie remote add local http://localhost:19120/api/v2
nessie remote show
```

Useful commands (append `--help` to explore):
- List branches/tags: `nessie branch list`, `nessie tag list`
- Create a feature branch from main: `nessie branch create feature/test -r main`
- Show commit log (current ref or specify): `nessie log` or `nessie log main`
- Show current default branch: `nessie config show`
- Show table/content entries on a ref: `nessie content list --ref main`
- Diff two refs: `nessie diff --from main --to feature/test`
- Merge a branch into main: `nessie merge feature/test -b main`

Tip: align Spark with the same branch by setting `spark.sql.catalog.nessie.ref=<branch>` before reads/writes.

## Stop / cleanup
- Stop services: `docker compose down`
- Remove persisted state (destructive reset): `docker volume rm nessie_data minio_data`

## Troubleshooting
- Check containers: `docker compose ps`
- Logs: `docker compose logs -f nessie` (or `minio`)
- Health still 404: ensure you are using port 19000 for Nessie health (mapped from container 9000). The API remains on 19120.
- Swagger UI 404: try both `19120` and `19000` ports; if still absent, the image may omit the UI in prod builds—use OpenAPI JSON (`/q/openapi`) or `pynessie` instead.
