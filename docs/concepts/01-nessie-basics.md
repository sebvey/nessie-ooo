# Nessie + Iceberg 101

## What is Project Nessie?
- A Git-inspired catalog for data tables. It stores table metadata (not the data files) and tracks commits, branches, and tags.
- Compatible catalogs: Apache Iceberg (covered here), Delta Lake, Hive tables via Hive 3, SQL (Trino/Presto/Flint), and Spark.
- Access patterns: REST API (`/api/v2`), SDKs, Spark extensions, Trino/Presto connectors, and the `pynessie` CLI.

## How Nessie works with Iceberg
- Iceberg stores data files + manifest/metadata files in a warehouse location (filesystem or object storage).
- Nessie stores Iceberg table pointers (the metadata locations) in its version store. When you commit changes in Spark, Nessie records a new pointer on the active branch.
- Result: you can branch for experiments, tag releases, and merge/rollback table versions without moving data files.

## Key concepts
- **Catalog**: logical namespace that maps table identifiers to Iceberg metadata locations.
- **Branch**: mutable line of history (default is `main`). You can set your Spark session to a branch via `spark.sql.catalog.nessie.ref`.
- **Tag**: immutable pointer to a commit (think releases).
- **Commit**: unit of change; holds references to new Iceberg metadata snapshots.
- **Version store backend**: where Nessie keeps its commit graph (RocksDB, JDBC DBs, or DynamoDB).

## Backends & storage separation
- Nessie’s own metadata lives in its version store (e.g., RocksDB or Postgres).
- Iceberg data and metadata files live in the warehouse you configure (local folder, HDFS, S3/MinIO). MinIO is only for Iceberg files, not for Nessie itself in this guide.
- Nessie is built on **Quarkus** (a lightweight Java framework), so its operational endpoints follow Quarkus conventions (for example, health checks under `/q/health` on the management port, default 9000 — map it to an open host port, e.g., `-p 19000:9000` if port 9000 is used by MinIO).

## Typical flows
1) Point your engine (Spark) at Nessie + Iceberg catalog.
2) Create/write a table. Iceberg writes data files to the warehouse; Nessie commits the new metadata pointer.
3) Switch branches for isolated work, then merge when validated. Tag snapshots you want to keep.

## Why use Nessie
- Safer experimentation (branch per feature).
- Auditable history and easy rollback of table states.
- Reproducible reads by pinning to tags/commits.
- Works across multiple engines that support Iceberg and Nessie.

## SVE

nessie exposes the Iceberg REST API at http://<nessie_host_port>/iceberg/<branch>/

To see config :
curl -s http://127.0.0.1:19120/iceberg/main/v1/config | jq .

It provides endpoint list:
- GET /v1/{prefix}/namespaces
- GET /v1/{prefix}/namespaces/{namespace}
- HEAD /v1/{prefix}/namespaces/{namespace}
- ...


That {prefix} is simply a free-form path segment that a server can use to route requests to some internal catalog context. So: {prefix} is a routing/context handle, server-defined.

Examples of what {prefix} could mean in different servers:
* a tenant name
*	a “warehouse ID”

! BUT NOT USED BY NESSIE'S ICEBERG REST API ! 

=> To pick a branch/tag, append it to the URI: http://.../iceberg/my_branch 
