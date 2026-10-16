# History under Nessie: commits, not snapshots

With Nessie as the Iceberg catalog, history lives in Nessie commits. A table's `metadata.json` only holds its current snapshot. This is a design choice, not snapshot expiration.

## Two versioning layers

| | Iceberg (table) | Nessie (catalog) |
|---|---|---|
| Unit | snapshot | commit |
| Scope | one table | every table of the catalog |
| Stored in | `metadata.json` (snapshot list, snapshot log, metadata log) | the version store |
| Time travel | `VERSION AS OF <snapshot-id>` | read a tag, a commit hash or a timestamp |

## What a classic catalog does

With Hive, Glue, JDBC or Polaris, each commit writes a new `metadata.json` that carries the previous snapshots: `snapshots: [s1, s2, s3]`. Snapshot time travel works directly, and `expire_snapshots` trims the list. (Details in [Iceberg metadata](iceberg-metadata.md).)

## What Nessie does

Each Nessie commit points to a `metadata.json` that describes the table as of that commit, with one snapshot. Observed on a table after several appends:

```text
snapshots: 1   snapshot-log: 1   metadata-log: 0
s3://iceberg-warehouse/raw/orders_<uuid>/metadata/00000-<uuid>.metadata.json
```

Consequences:
- Listing a table's snapshots or reading `VERSION AS OF <snapshot-id>` only sees the current one. PyIceberg's `snapshot-loading-mode=all` changes nothing: the server has nothing more to send.
- Time travel goes through Nessie: read a tag, `<branch> AT COMMIT <hash>`, or reassign a branch to roll back.
- Maintenance must go through Nessie too (see [operations](nessie-operations.md#cleanup)).

## Who creates the commits

An engine writing through Iceberg REST (PyIceberg, Spark, DuckDB…):
1. loads the table from the catalog (the branch is in the URI);
2. writes new Parquet files and manifests to the warehouse;
3. sends a REST commit: "apply these metadata updates, provided the table is still at the state I read" (requirements).

Nessie checks the requirements, writes the new `metadata.json`, and records one commit on the branch with a generated message:

```text
Update ICEBERG_TABLE raw.orders
Create ICEBERG_TABLE marts.daily_orders
update namespace raw
```

The Iceberg REST spec has no field for commit messages or authors, so engines can't set them. A merge produces a single commit on the target (`Merged <branch> at <hash>`), whatever the number of tables.

## Where meaning comes from

Engines write data and Nessie turns each write into a technical commit. The operations that carry meaning go through the Nessie API or CLI:
- the **branch name** (one branch per pipeline run, per feature…);
- the **merge**, which is the promotion;
- the **tag**, which marks a validated state.

Think in Nessie commits and refs, not in Iceberg snapshot lists.
