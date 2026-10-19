# Architecture decision records

Why the Nessie demo is the way it is: stack, dependencies, data plane, repository layout. What deserves an ADR, the lifecycle and the template are in the ADR process of the agentic layer: [`00-agentic/processes/adr.md`](../../00-agentic/processes/adr.md).

The "Choices" table in [`architecture.md`](../project/architecture.md#choices) stays as the one-line summary of the setup; a row links to an ADR when one exists.

## Records

| ADR | Decision | Status |
|---|---|---|
| [ADR001](ADR001-lock-is-the-source-of-truth.md) | `uv.lock` is the source of truth; `pyproject.toml` has `>=` floors equal to the locked versions and no preventive upper bound | accepted |
| [ADR002](ADR002-no-dependency-cooldown.md) | No dependency cooldown | accepted |
| [ADR003](ADR003-pyiceberg-as-the-data-plane.md) | PyIceberg is the data plane until DuckDB can read and write Iceberg on a Nessie branch | superseded by ADR004 |
| [ADR004](ADR004-duckdb-attached-to-the-nessie-branch.md) | DuckDB reads and writes the dbt models directly on the Nessie branch; PyIceberg only ingests | accepted |
| [ADR005](ADR005-vierbein-imported-from-a-sibling-folder.md) | The agentic layer, vierbein, is imported from a sibling folder | superseded by ADR006 |
| [ADR006](ADR006-vierbein-copied-into-the-repository.md) | The agentic layer, vierbein, is copied into the repository (`00-agentic/`) | accepted |
| [ADR007](ADR007-tickets-move-to-github-issues.md) | Nessie's tickets move to GitHub Issues, all of them, with issue `#n` for ticket `Tn` | accepted |
| [ADR008](ADR008-work-delivered-by-pull-requests.md) | Work is delivered by pull requests, squash-merged into a `main` protected with no bypass (public repository) | accepted |
| [ADR009](ADR009-analysis-tickets-deliver-a-report-on-the-issue.md) | An analysis ticket delivers a report on its issue and proposed tickets, never a change to the repository | accepted |
| [ADR010](ADR010-components-as-uv-workspace-members.md) | The repository is split into components, each a uv workspace member with its own dependencies, under one lock | proposed |
