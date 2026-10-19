# How to write the documentation

Where a piece of documentation goes, and what each page holds. The reader is the developer who maintains the repository. The writing rules themselves (English, no hard wrapping, docs describe how things are now) are in [`00-agentic/agreements/writing.md`](../../00-agentic/agreements/writing.md).

## Where it goes

| Content | Where |
|---|---|
| What the repository is, the quick start, the map of the components and of the docs | The root [`README.md`](../../README.md), the one entry point |
| What concerns one component only: its role, how to run it, its files, its dependencies, what is specific to it | `<component>/README.md`, and longer pages in `<component>/docs/` |
| How the whole works: the flow, how the components connect, who reads and writes what | [Architecture overview](architecture.md) |
| What concerns several components or the way of working (dependencies, documentation, agent setup) | `docs/project/` |
| Iceberg and Nessie knowledge, valid outside this repository | `docs/concepts/`, with its reading order in [`docs/concepts/README.md`](../concepts/README.md) |
| Why things are the way they are | An ADR in `docs/adr/` ([process](../../00-agentic/processes/adr.md)) |
| Instructions for the coding agent | `CLAUDE.md` and the agentic layer, `00-agentic/`; they point to the docs for facts instead of repeating them |
| The talk | `docs/presentation/`, in French |

## Rules

- **One entry point.** Every page can be reached by links from the root README, directly or through a component's README, `docs/concepts/README.md` or `docs/adr/README.md`. A new page gets its link where it belongs in that tree. The agentic layer, `00-agentic/`, is the exception: its own README describes it, and `CLAUDE.md` imports its files.
- **Every component has a `README.md`**, even a short one, with these sections: what it does (the first paragraph), `Run`, `Files`, `Depends on`, then what is specific to it. A page too long for the README goes in the component's `docs/` folder (`transformation/docs/dbt-on-iceberg.md`), and the README links to it.
- **One place per piece of information.** A fact (a list of components, a file tree, a credential, a command's options) is written once; other pages link to it. A one-line summary that links to the details is not a duplicate. The list of mise tasks is `tasks.toml` itself (`mise tasks` prints it); each component's README says how to run that component.
- **One kind per page**, said by its title:
  - an **overview** explains how something works ("Architecture overview", "dbt on Iceberg: how the models are materialized");
  - a **how-to** gives the steps to reach a goal ("How to work on your own branch");
  - a **reference** lists facts to look up ("Nessie CLI reference").

  A component's README is a reference card with the fixed sections above. Everything in `docs/concepts/` is an overview. A how-to may end with a short "Background" section when the context is needed to apply it.
- **Commands are written for the developer's shell**, where mise is activated: `uv run dbt build`, not `mise exec -- uv run dbt build`. The agent adds the prefix itself (`CLAUDE.md`, "Running things").
- **Links are relative** (`../adr/ADR004-….md`), so they work on GitHub and in an editor. After moving or renaming a page, grep for its old path.

## Vocabulary

Project terms, one per concept ([`writing.md`](../../00-agentic/agreements/writing.md), "Names don't collide").

- **Silo**: pgsty's community fork of MinIO (`pgsty/silo`), the S3 storage the stack runs. It is MinIO-compatible: same `MINIO_*` variables, same data format. Docs, code comments, docstrings and console output call it Silo, and say it is a fork of MinIO only where its origin matters (why this image, why `MINIO_*` variables).
- **MinIO**: the upstream project, the S3-compatible object storage server of MinIO, Inc. (`minio/minio`), whose community edition is no longer distributed. The name is used only for that project.
- **`minio`**, in any case, appears otherwise only in technical identifiers that keep it on purpose (`MINIO_*` variables, the `/minio/health/…` routes), always in backticks in the docs.
