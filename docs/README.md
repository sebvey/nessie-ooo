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

- [Architecture](project/architecture.md): components, docker compose services, Nessie configuration, read and write paths, who reads and writes what.
- [The pipeline](project/pipeline.md): branch, ingest, dbt build, merge or alert, step by step.
- [Working on your own branch](project/working-on-a-branch.md): run dbt on a personal Nessie branch through `mise.local.toml`.
- [Nessie CLI](project/nessie-cli.md): REPL commands (refs, history, merge, rollback).
- [dbt on Iceberg](project/dbt-on-iceberg.md): how dbt-duckdb materializes the models on the attached Nessie catalog, the SQL sent, the commits left on the branch.
- [Dependency policy](project/dependency-policy.md): version specifiers for an application and for a library, upgrade procedure, vulnerability check and the OSV database.
- [Agent setup](project/agent-setup.md): the coding agent's permissions, MCP servers, mise, and the instructions it follows from outside the repo.

## Decisions

[Architecture decision records](adr/README.md): what was decided about the demo, why, what was ruled out. The ADR process (selection tests, lifecycle, template) is part of the agentic layer, vierbein: `processes/adr.md` in `../vierbein/`.

How we work with the agent on this repo is the agentic layer, vierbein, a separate repository checked out next to this one (`../vierbein/`): working agreements imported by `CLAUDE.md`, processes, ticket backends. This project's side of it: [Agent setup](project/agent-setup.md).

## Presentation (French)

- [`iceberg.html`](presentation/iceberg.html): Iceberg refresher deck.
- [`presentation.html`](presentation/presentation.html): Nessie demo deck.
- [`demo-cli.md`](presentation/demo-cli.md): guided REPL walkthrough, rollback included.
