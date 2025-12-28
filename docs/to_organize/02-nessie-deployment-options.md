# Deployment options and choices

## Deployment patterns
- **Single container (Docker)**: simplest for local dev; use built-in RocksDB store on a volume.
- **Docker Compose**: add dependencies like object storage (MinIO) or external DBs for the version store.
- **Kubernetes/Helm**: Nessie publishes Helm charts; common in shared dev/test clusters with Postgres/DynamoDB backends.
- **Managed DB backends**: use Postgres/MySQL/Aurora or DynamoDB for HA in production; Nessie is stateless when the backend is external.

## Version store backends
- **RocksDB**: embedded key-value store; best for local dev or single-node demos. Fast, no extra infra; not HA.
- **JDBC (Postgres, MySQL, MariaDB, Oracle, SQL Server)**: durable and scalable for teams; runs with Nessie statelessly.
- **DynamoDB**: cloud-friendly, serverless option; good for AWS-native stacks.

## Object storage vs catalog storage
- Nessie stores catalog history only (in the backend above).
- Iceberg table files and metadata live in your warehouse: local FS/HDFS/S3/MinIO. This guide uses **local FS by default** and **MinIO optionally** to mimic S3.

## What this tutorial chooses and why
- **Nessie runtime**: Docker + RocksDB, run via a single `docker-compose` that also brings up MinIO with non-conflicting ports.
- **Warehouse**: MinIO (`s3a://iceberg-warehouse`) by default in the compose stack; you can still point Spark at local FS if you prefer.
- **Compute**: PySpark because Iceberg + Nessie integration is mature there.
- **CLI**: `pynessie` for inspecting branches/commits without writing code.

## Ports and network
- Nessie REST: `19120` (exposed from the container).
- MinIO API/console (optional): `9000` / `9001`.
- Spark runs locally and connects to Nessie via HTTP and to storage via filesystem or S3A.
