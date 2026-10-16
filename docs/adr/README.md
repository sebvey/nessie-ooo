# Architecture decision records

Why the Nessie demo is the way it is: stack, dependencies, data plane. What deserves an ADR, the lifecycle and the template are in the ADR process: [`00-agentic/processes/adr.md`](../../00-agentic/processes/adr.md).

The "Choices" table in [`architecture.md`](../project/architecture.md#choices) stays as the one-line summary of the setup; a row links to an ADR when one exists.

## Records

| ADR | Decision | Status |
|---|---|---|
| [ADR001](ADR001-lock-is-the-source-of-truth.md) | `uv.lock` is the source of truth; `pyproject.toml` has `>=` floors equal to the locked versions and no preventive upper bound | accepted |
| [ADR002](ADR002-no-dependency-cooldown.md) | No dependency cooldown | accepted |
| [ADR003](ADR003-pyiceberg-as-the-data-plane.md) | PyIceberg is the data plane until DuckDB can read and write Iceberg on a Nessie branch | accepted |
