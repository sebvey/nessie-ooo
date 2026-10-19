# ADR010 The repository is split into components, each a uv workspace member with its own dependencies, under one lock

- Status: accepted
- Date: 2026-10-19
- Tickets: #55
- Basis: investigated (uv 0.13.1, 2026-10-19: a scratch workspace, then this repository; `uv run --package <member>` leaves other members' dependencies in the shared `.venv`, `uv run --exact --package <member>` removes them and the undeclared import fails; a virtual member's dependencies reach the members that depend on it)

## Context

On 2026-10-19 one Python package, `src/nessie_demo/`, held a shared client (Nessie API, PyIceberg catalog, DuckDB, settings), the stack bootstrap, the synthetic source data, the pipeline and its narrated output; `dbt/` and `notebooks/` sat beside it, named after their tools. One dependency list served everything: nothing said or checked which part needed what, and the notebook imported the same package as the pipeline. The goal is maintainability: parts with one responsibility each, whose dependencies are written down and checkable.

## Decision

The top level holds one folder per **component**, a part of the repository with one responsibility: `stack`, `lakehouse-client`, `ingestion`, `transformation`, `orchestration`, `exploration`. Each component is a uv workspace member with its own `pyproject.toml`, declaring the dependencies it uses, other components included. The workspace has one `uv.lock` (ADR001 unchanged). A component that is not a Python package (the dbt project, the notebook) is a virtual member that only carries dependencies. The root `pyproject.toml` is a virtual member too; it depends on every component, so `uv run <command>` works from anywhere. A component's dependencies are checked with `uv run --exact --package <component>`. How: [architecture](../project/architecture.md#components).

## Alternatives ruled out

- Plain folders under one `pyproject.toml`: cheaper, but they neither say nor check which component needs what; an import going the wrong way (the notebook into the pipeline) would need an extra tool to catch.
- One lock per component (separate projects): the components run together in one demo and must agree on versions; several locks would multiply the upgrade procedure and the audit.
- Splitting the shared code finer (a standalone Nessie client taking its configuration as arguments): a code change, not a move; left to a later ticket (#5).

## Consequences

- Each component's `pyproject.toml` is the list of what it needs; a package used by several components is declared in each.
- One `.venv` holds everything: an undeclared dependency still imports during development. Only `--exact` catches it, and Python run from the repository root also sees the component folders as namespace packages (`python -P` avoids it).
- Commands run through `uv run`, with `--package` when only one component should be installed.
- Extracting a component into its own repository or package (the Nessie client) starts from a folder that already declares its dependencies.

## Revisit when

uv changes how workspaces share a `.venv` or sync members, or a component needs versions the others can't share (then one lock no longer fits).
