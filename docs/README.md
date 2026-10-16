# Documentation

## Concepts

General knowledge about Iceberg and Nessie, valid outside this repo. Read in this order:

1. [Iceberg metadata](concepts/iceberg-metadata.md): `metadata.json`, snapshots, manifests, data files.
2. [Nessie overview](concepts/nessie-overview.md): what Nessie is, refs and commits, how a branch is selected through Iceberg REST.
3. [History under Nessie](concepts/nessie-history.md): Nessie commits versus Iceberg snapshots, who creates which commit.
4. [Nessie operations](concepts/nessie-operations.md): merge and conflicts, rollback, cleanup with Nessie GC, access control.
5. [Nessie deployment](concepts/nessie-deployment.md): runtimes and version stores.

## This project

What we built and how to use it:

- [Architecture](project/architecture.md): components, docker compose services, Nessie configuration, read and write paths, why PyIceberg.
- [The pipeline](project/pipeline.md): branch, ingest, dbt build, merge or alert, step by step.
- [Working on your own branch](project/working-on-a-branch.md): run dbt on a personal Nessie branch through `mise.local.toml`.
- [Nessie CLI](project/nessie-cli.md): REPL commands (refs, history, merge, rollback).
- [DuckDB 2.0](project/duckdb-2.0.md): test results and plan to drop the PyIceberg detour.

## Presentation (French)

- [`iceberg.html`](presentation/iceberg.html): Iceberg refresher deck.
- [`presentation.html`](presentation/presentation.html): Nessie demo deck.
- [`demo-cli.md`](presentation/demo-cli.md): guided REPL walkthrough, rollback included.
