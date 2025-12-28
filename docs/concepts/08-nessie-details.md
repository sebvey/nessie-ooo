# Nessie details: concepts and behavior

Nessie is a Git-like catalog layer for tables. It tracks versioned pointers to table metadata (e.g., Iceberg `metadata.json`) per branch/tag, but does not store data or manifests. Use this to understand what Nessie is, what it isn’t, and how its concepts map to catalog operations.

## What Nessie is
- A catalog/version-control service: stores references from table identifiers (content keys) to current table metadata, plus a commit graph with branches/tags.
- API/clients: REST API (`/api/v2`), SDKs, Spark/Trino/Flint connectors, CLI (`pynessie`).
- Backends: pluggable version stores (RocksDB, JDBC DBs, DynamoDB, etc.); Nessie itself is stateless when using external storage.

## What Nessie is not
- Not a data lake: it never stores data files or manifests.
- Not a storage system: your warehouse (S3/MinIO/local FS/HDFS) holds data/metadata files.
- Not a compute engine: Spark/Trino/etc. perform reads/writes; Nessie only tracks pointers and history.

## Key concepts
- **Catalog**: logical namespace mapping content keys (e.g., `nessie.demo_weather`) to table metadata pointers.
- **Content key**: the identifier for an entry (table, view, etc.). For Iceberg, the value is a pointer to `metadata.json`.
- **Commit**: a change to one or more content keys; updates pointers to new table metadata paths and adds to the commit graph.
- **Branch**: mutable ref that advances with commits and can be merged or deleted; default is typically `main`.
- **Tag**: immutable ref pointing to a specific commit; good for releases/audits.
- **Ref**: generic term for branches and tags.
- **Merge**: apply changes from one branch to another, resolving conflicts if needed.
- **Cherry-pick/transplant**: apply specific commit(s) from one ref to another without merging the entire branch history.
- **Version store backend**: storage for the commit graph and content pointers (RocksDB/JDBC/DynamoDB). Nessie server uses this; data files stay in your warehouse.
- **Endpoint**: Nessie REST base, e.g., `http://localhost:19120/api/v2`.

## How Nessie works with Iceberg (pointers, not data)
1) Engine (e.g., Spark) is configured with the Nessie Iceberg catalog: `spark.sql.catalog.nessie.*`.
2) Write: Iceberg creates data files, manifests, manifest list, and a new `metadata.json` in the warehouse. The catalog commit updates the Nessie content key to point to that new `metadata.json` on the active ref.
3) Read: Engine asks Nessie for the content key on a ref; Nessie returns the current `metadata.json` path. Engine reads manifests/data from the warehouse.
4) Branching: change `spark.sql.catalog.nessie.ref` (or CLI) to switch refs; each ref has its own pointer to the table metadata.
5) Rollback/time travel (catalog-level): move the ref to an older commit to restore the pointer to an older `metadata.json`. Within that metadata, Iceberg time travel still applies while snapshots/files exist.

## Operations and behavior
- **Commits**: catalog-level; can update one or many content keys atomically. Most engines commit per table, but multi-table commits are allowed.
- **Branches/Tags**: lightweight; stored in the version store. Tags are immutable; branches are mutable.
- **Conflict handling**: Nessie enforces optimistic concurrency. If the base commit you assumed differs from the current head when committing/merging, you must resolve/retry.
- **Merges/Cherry-picks/Transplants**: apply commits across refs; underlying data files are not moved—only pointers change.
- **Deletion**: removing a table entry removes the pointer; files may remain in the warehouse unless separately cleaned by the engine/maintenance.

## Lifecycle and cleanup considerations
- Catalog history lives in the version store; data/metadata files live in the warehouse. Deleting a ref does not delete files.
- Safe cleanup requires coordination: do not delete Iceberg snapshots/metadata files that are still referenced by any Nessie ref. Drop/merge refs, then run Iceberg snapshot expiration and orphan cleanup.

## Mental model
- Nessie = commit graph + refs + pointers to table metadata.
- Warehouse = data/metadata files (e.g., `metadata.json`, manifest lists, manifests, data/delete files).
- Engine = reads/writes files, asks Nessie for the current pointer on a ref, and commits pointer updates.
