# How Nessie + Iceberg + MinIO work together

This explains the control plane (Nessie) versus the data plane (Iceberg files on disk or MinIO) and how Spark interacts with both.

## Roles
- **Spark (compute engine):** Reads/writes data files and Iceberg metadata files (manifests, metadata.json). Knows the warehouse location (e.g., `s3a://iceberg-warehouse` for MinIO).
- **Iceberg (table format):** Defines how table metadata and data files are organized. Metadata files live in the warehouse you set.
- **Nessie (catalog + version control):** Stores *pointers* to Iceberg table metadata files per branch/tag. It never stores data files; it stores references to the table’s current metadata.json per ref, and the commit graph (branches/tags).
- **MinIO (object storage):** Holds Iceberg data/metadata files when you set the warehouse to `s3a://...`. If you use local FS, MinIO is not involved.

## Who knows the warehouse?
- Spark knows the warehouse via `spark.sql.catalog.nessie.warehouse` (e.g., `s3a://iceberg-warehouse`).
- Nessie does **not** store the warehouse path for you; it stores the *resulting Iceberg metadata location* after a write (e.g., `s3a://iceberg-warehouse/nessie/demo_weather/metadata/<uuid>.metadata.json`), per branch/tag.

## Typical read path
1) Spark is configured with the Nessie catalog: `spark.sql.catalog.nessie = org.apache.iceberg.nessie.NessieCatalog`, `uri = http://localhost:19120/api/v2`, `ref = main`, `warehouse = s3a://iceberg-warehouse`.
2) Spark asks Nessie for table `nessie.demo_weather` on ref `main`.
3) Nessie returns the current metadata pointer for that table/ref (a path to the Iceberg metadata file in the warehouse).
4) Spark reads the Iceberg metadata and then the data files from MinIO (or local FS).

## Typical write path
1) Spark writes new data files and a new Iceberg metadata.json into the warehouse (MinIO/local).
2) Spark sends a commit to Nessie on the active ref (`spark.sql.catalog.nessie.ref`), updating the pointer to the new metadata.json.
3) Nessie records that commit on the branch, preserving history (old metadata pointers remain reachable via history/refs).

## Branches and tags
- Branches/tags live only in Nessie’s version store. They select which metadata pointer is considered “current.”
- Switching branches in Spark = change `spark.sql.catalog.nessie.ref` (config at session start or `spark.conf.set(...)`).
- Tags are immutable pointers to a specific commit/metadata pointer; you can set ref to a tag for reproducible reads.

## What happens if the warehouse changes?
- Nessie will still point to whatever metadata path was committed. If you move or delete data/metadata files from MinIO/local disk, reads will fail because Iceberg files are missing. Nessie does not relocate data.

## MinIO versus local filesystem
- MinIO is only involved because Spark writes to `s3a://...`. Nessie doesn’t talk to MinIO directly; it just stores the metadata paths Spark produced.
- If `warehouse` is `file:/tmp/iceberg-warehouse`, paths in Nessie commits point to local files instead.

## Summary mental model
- Nessie = versioned pointers (control plane) + commit graph.
- Iceberg = table format and metadata layout.
- Spark = reads/writes data/metadata and tells Nessie which metadata pointer is current on a branch/tag.
- MinIO/local FS = where Iceberg stores files; Nessie never stores data files.
