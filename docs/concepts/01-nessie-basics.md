# Nessie + Iceberg 101

## What is Project Nessie?

A Git-inspired catalog for Iceberg tables. It stores pointers to table metadata (never the data
files) and versions them with commits, branches and tags. One commit can touch several tables, and
a branch covers the whole catalog, not a single table.

Ways in:
- **Iceberg REST catalog** at `/iceberg/<branch>`: what PyIceberg, Spark, DuckDB or Snowflake use.
- **Nessie API v2** at `/api/v2`: branches, tags, merges, history (`src/nessie_demo/nessie.py`).
- **Nessie CLI** (SQL-like REPL): `mise run cli`.

The `pynessie` Python client and CLI only speak API v1 and are no longer maintained (last release
in February 2024): don't use them.

## Key concepts

- **Catalog**: maps table identifiers (`raw.orders`) to the location of their current
  `metadata.json`.
- **Namespace**: groups tables, like a SQL schema (`raw`, `marts`). Plain Iceberg concept; in Nessie
  a namespace is a versioned entry, so creating one is a commit.
- **Commit**: a change to one or more catalog entries, with a hash and a parent.
- **Branch**: mutable pointer to a commit (`main`, `pipeline-HHMMSS`).
- **Tag**: pointer meant to stay put (`release-HHMMSS`).
- **Merge**: replays a branch's changes onto another. Nessie refuses it if the same table changed on
  both sides since the common ancestor.
- **Version store**: where Nessie keeps commits and refs (Postgres here).

## Where things live

- Nessie's own state (commit graph, refs, pointers) lives in its version store.
- Iceberg files (`metadata.json`, manifest lists, manifests, Parquet data files) live in the
  warehouse: `s3://iceberg-warehouse` on Silo here.
- Nessie runs on Quarkus: health and metrics are on the management port (container `9000`, mapped
  to `19000` here).

## Selecting a branch through Iceberg REST

The branch is part of the catalog URI: `http://localhost:19120/iceberg/<branch>`. The client first
calls `GET <uri>/v1/config`; Nessie answers with:

- `defaults.prefix = <branch>`: the `{prefix}` segment of every Iceberg REST route
  (`/v1/{prefix}/namespaces`, …). Nessie's prefix pattern is `{ref}|{warehouse}`.
- `overrides.uri = http://localhost:19120/iceberg/`: the base URI to use from then on.

So the client ends up calling `/iceberg/v1/<branch>/namespaces/...`.

```bash
curl -s http://localhost:19120/iceberg/main/v1/config | jq .
curl -s http://localhost:19120/iceberg/v1/main/namespaces | jq .
```

A client that ignores `overrides.uri` calls `/iceberg/<branch>/v1/<branch>/...` and finds nothing.
That is DuckDB issue duckdb-iceberg#1145, fixed on the extension's main branch but not in a stable
DuckDB release yet: see [`DUCKDB-2.0.md`](../../DUCKDB-2.0.md).

## Why use Nessie

- Isolation: write and test on a branch, merge only what passed.
- Atomic multi-table promotion: one merge publishes every table of the branch at once.
- Audit and rollback: every change is a commit, `main` can be reassigned to a tag.
- Reproducible reads: read a tag or a commit hash.
