# Nessie deployment options

## Runtime

- **Single container**: `ghcr.io/projectnessie/nessie`, fine for local work.
- **docker compose**: Nessie plus its version store and object storage.
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
Tool migrates their data. The `2` variants are new implementations of the same backend with less
storage overhead: with `JDBC2`, each object is one serialized value (`objs2.obj_value`) instead of a
wide table with one column per field.

## Storage

- Nessie stores catalog history only, in the version store.
- Iceberg files live in the warehouse declared to Nessie (`nessie.catalog.warehouses.*`): S3, GCS,
  ADLS, or an S3-compatible store. With Iceberg REST, Nessie needs credentials for that
  store, because it writes `metadata.json` files and can hand storage settings to clients.

## Before production

Authentication and authorization, `JDBC2` (or another non-deprecated store), Nessie GC for cleanup
(see [operations](nessie-operations.md)), and a durable object store.
