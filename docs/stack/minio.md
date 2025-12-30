# MinIO stack notes

MinIO is the S3-compatible object store used here to hold Iceberg data/metadata files. The compose stack runs a single MinIO node with a local volume.

## Deployment (docker-compose)
- Image: `quay.io/minio/minio:latest`
- Command: `server /data --console-address ":9001"`
- Ports:
  - `9000` — S3 API endpoint
  - `9001` — Web console
- Credentials (from compose env):
  - Access key: `minioadmin`
  - Secret key: `minioadmin`
- Volume: `minio_data` mounted at `/data`

Start/stop:
```bash
docker compose up -d
docker compose down
```

## Health and console
- Console: http://localhost:9001 (login with the access/secret above).
- API reachability: `curl -I http://localhost:9000`

## Buckets (e.g., `iceberg-warehouse`)
Create/list via AWS CLI:
```bash
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin
export AWS_EC2_METADATA_DISABLED=true
export AWS_ENDPOINT_URL=http://localhost:9000

aws s3 ls
aws s3 mb s3://iceberg-warehouse
aws s3 ls s3://iceberg-warehouse
```

## Troubleshooting
- `AccessDenied`: ensure credentials match the running MinIO; if a persisted volume exists, credentials are taken from the first startup. Recreate the `minio_data` volume if needed (`docker compose down && docker volume rm minio_data && docker compose up -d`).
- `NoSuchBucket`: verify `WAREHOUSE` matches an existing bucket name exactly and the endpoint is `http://localhost:9000`.
- SSL: the stack uses plain HTTP; set `fs.s3a.connection.ssl.enabled=false` (as in `scripts/first_table.py`) for Spark clients.

## References
- MinIO Quickstart: https://min.io/docs/minio/container/index.html
- AWS CLI with custom endpoints: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-s3.html#cli-configure-s3-endpoints
