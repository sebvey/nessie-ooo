# How the pieces work together

Who knows what, and what happens on a read and a write, with Nessie used as an Iceberg REST catalog.

## Roles

- **Engine** (PyIceberg, dbt-duckdb through its plugins): plans reads and writes, writes Parquet data
  files and manifests.
- **Iceberg** (table format): the layout of `metadata.json`, manifest lists, manifests and data
  files.
- **Nessie** (catalog and version control): maps each table to its current `metadata.json`, per
  branch; writes the `metadata.json` files when a commit arrives through Iceberg REST; keeps the
  commit graph in Postgres.
- **Silo** (S3 storage): holds every Iceberg file. Nessie and the engines both talk to it.

## Who knows the warehouse?

Nessie does: the warehouse location and its S3 settings are server configuration
(`nessie.catalog.warehouses.warehouse.location=s3://iceberg-warehouse/`). Clients only need the
catalog URI and S3 access. Nessie announces the default warehouse in `/v1/config`, and its
`external-endpoint` setting (`http://127.0.0.1:29000`) is the S3 address meant for clients. The demo's
clients set their S3 endpoint themselves anyway (`settings.py`, `profiles.yml`).

## Read path

1. The engine opens the catalog `http://localhost:19120/iceberg/<branch>` and calls `/v1/config`:
   Nessie returns the prefix (`<branch>`) and the base URI to use.
2. The engine loads `raw.orders`: Nessie returns the table's current metadata, read from the
   `metadata.json` its pointer names on that branch.
3. The engine reads the manifest list, the manifests, then only the Parquet files it needs, from Silo.

## Write path

1. The engine writes new Parquet files and manifests to Silo.
2. It sends a commit to Nessie for that table and branch, with its requirements ("the table is still
   at the state I read").
3. Nessie checks them, writes the new `metadata.json` to Silo, and records a commit on the branch
   that points the table to it.

`main` and every other branch are untouched until a merge.

## Branches

A branch is only a pointer in Nessie. Creating one copies no file: both branches point to the same
`metadata.json` until one of them writes. Merging moves pointers on the target; no file is copied
either.

## If files disappear

Nessie keeps pointing to whatever `metadata.json` was committed. If those files, or the manifests and
data files they reference, are deleted from Silo, reads fail. That's why cleanup has to go through
Nessie GC (see [Nessie details](../concepts/080-nessie-details.md#cleanup-maintenance)).

## Mental model

- Nessie: versioned pointers and the commit graph, plus `metadata.json` writing.
- Iceberg: the file layout.
- Engines: read and write data files.
- Silo: stores the files.
