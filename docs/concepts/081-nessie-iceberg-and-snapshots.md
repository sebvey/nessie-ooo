# Iceberg snapshots under Nessie

With Nessie as the Iceberg catalog, a table's `metadata.json` only holds its **current snapshot**.
History lives in Nessie commits, not in the table metadata. This is a design choice, not snapshot
expiration.

## Two versioning layers

| | Iceberg (table) | Nessie (catalog) |
|---|---|---|
| Unit | snapshot | commit |
| Scope | one table | every table of the catalog |
| Stored in | `metadata.json` (snapshot list, snapshot log, metadata log) | the version store |
| Time travel | `VERSION AS OF <snapshot-id>` | read a tag, a commit hash or a timestamp |

## What a classic catalog does

With Hive, Glue, JDBC or Polaris, each commit writes a new `metadata.json` that carries the previous
snapshots: `snapshots: [s1, s2, s3]`. Snapshot time travel works directly, and `expire_snapshots`
trims the list.

## What Nessie does

Each Nessie commit points to a `metadata.json` that describes the table **as of that commit**, with
one snapshot. Checked on this repo after several pipeline runs:

```text
snapshots: 1   snapshot-log: 1   metadata-log: 0
s3://iceberg-warehouse/raw/orders_<uuid>/metadata/00000-<uuid>.metadata.json
```

Consequences:
- Listing a table's snapshots or reading `VERSION AS OF <snapshot-id>` only sees the current one.
  PyIceberg's `snapshot-loading-mode=all` changes nothing: the server has nothing more to send.
- Time travel goes through Nessie: read `release-…`, `main AT COMMIT <hash>`, or reassign `main` to
  roll back.
- Maintenance must go through Nessie too: Iceberg's `expire_snapshots` / `remove_orphan_files` only
  see one snapshot per file and would delete files other commits still use. Use Nessie GC (see
  [Nessie details](080-nessie-details.md#cleanup-maintenance)).

## Mental model

- Nessie versions the catalog: commits, branches, tags, across tables.
- Under Nessie, an Iceberg table is "one snapshot per commit".
- Think in Nessie commits, not in Iceberg snapshot lists.
