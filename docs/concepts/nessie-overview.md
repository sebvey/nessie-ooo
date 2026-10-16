# Nessie overview

## What Nessie is

Project Nessie is a Git-inspired catalog for Iceberg tables. It maps each table to its current metadata file and versions that mapping with commits, branches and tags. A branch covers the whole catalog: one commit or one merge can change several tables at once.

What it is not:
- **Not storage**: data and metadata files live in the warehouse (S3, GCS, ADLS, MinIO…).
- **Not a compute engine**: PyIceberg, Spark, Trino, DuckDB… read and write the files. Through Iceberg REST, Nessie does write the `metadata.json` files itself.

Ways in:
- **Iceberg REST catalog** at `/iceberg/<branch>`: what engines use.
- **Nessie API v2** at `/api/v2`: branches, tags, merges, history.
- **Nessie CLI**: a SQL-like REPL on top of the API.

The `pynessie` Python client and CLI only speak API v1 and are no longer maintained (last release in February 2024).

## Key concepts

- **Catalog**: maps table identifiers (`raw.orders`) to the location of their current `metadata.json`.
- **Namespace**: groups tables, like a SQL schema. A plain Iceberg concept; in Nessie a namespace is a versioned entry, so creating one is a commit.
- **Content key**: the identifier of a catalog entry (namespace, Iceberg table, Iceberg view).
- **Commit**: a change to one or more content keys, with a hash, a parent and a message.
- **Branch**: mutable pointer to a commit; it moves with commits and can be merged, reassigned or dropped.
- **Tag**: pointer meant to stay put. Reassigning one is possible but meant to be exceptional.
- **Merge**: replays a branch's changes onto another.
- **Version store**: where Nessie keeps commits and refs (a database: PostgreSQL, RocksDB…).

A brand-new branch sits on the "no ancestor" hash (`2e1cfa82…`), the equivalent of an empty Git repository. Nessie refuses to merge into a branch without history ("No common ancestor"), so a fresh `main` needs at least one commit first.

## Selecting a branch through Iceberg REST

The branch is part of the catalog URI: `http://<host>:19120/iceberg/<branch>`. The client first calls `GET <uri>/v1/config`, and Nessie answers with:

- `defaults.prefix = <branch>`: the `{prefix}` segment of every Iceberg REST route (`/v1/{prefix}/namespaces`, …). Nessie's prefix pattern is `{ref}|{warehouse}`.
- `overrides.uri = http://<host>:19120/iceberg/`: the base URI to use from then on.

So the client ends up calling `/iceberg/v1/<branch>/namespaces/...`.

```bash
curl -s http://localhost:19120/iceberg/main/v1/config | jq .
curl -s http://localhost:19120/iceberg/v1/main/namespaces | jq .
```

A client that ignores `overrides.uri` calls `/iceberg/<branch>/v1/<branch>/...` and finds nothing. That's what DuckDB 1.5 does (duckdb-iceberg#1145).

## Where things live

- Nessie's own state (commit graph, refs, pointers) lives in its version store.
- Iceberg files (`metadata.json`, manifest lists, manifests, Parquet files) live in the warehouse.
- Nessie runs on Quarkus: health and metrics are on the management port (`9000` in the container).

## Why use Nessie

- Isolation: write and test on a branch, merge only what passed.
- Atomic multi-table promotion: one merge publishes every table of the branch at once.
- Audit and rollback: every change is a commit, and a branch can be reassigned to an older state.
- Reproducible reads: read a tag or a commit hash.

Next: [history](nessie-history.md) (commits versus Iceberg snapshots), then [operations](nessie-operations.md).
