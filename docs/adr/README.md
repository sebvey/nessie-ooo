# Architecture decision records

One file per important decision: what was decided, why, what was ruled out, and how solid the basis is. The docs in `docs/project/` say how things are now; an ADR says why they are that way.

Few ADRs, each worth reading: a choice that doesn't pass the three tests below goes elsewhere.

## What deserves an ADR

A decision that passes all three tests:

1. **Real alternatives**: at least one other option was weighed, or deliberately not examined (then the ADR says so).
2. **Costly to reverse, or bound to be re-opened**: without the ADR, someone would ask "why not X?" or redo the analysis.
3. **Outlives its ticket**: it constrains future work, not just the change at hand.

What goes elsewhere:

| Content | Where |
|---|---|
| Work to do | a ticket in `00-tracking/` |
| How things are now | a doc in `docs/project/` |
| Working rules for the repo | `CLAUDE.md` |
| A local implementation choice | a code comment |

The "Choices" table in [`architecture.md`](../project/architecture.md#choices) stays as the one-line summary of the setup; a row links to an ADR when one exists.

**One decision per ADR.** A ticket that takes several choices produces an ADR only for those that pass the tests.

## Lifecycle

- **Naming**: `ADR<nnn>-<short-kebab-case-title>.md`, referred to by ID (`ADR001`). The ID is the highest existing one plus one, never reused.
- **Written in the ticket that takes the decision**, with status `proposed`. It becomes `accepted` when the developer validates the ticket, in the same squashed commit.
- **An accepted ADR is never edited**, except its status line. Changing a decision means a new ADR that supersedes it; the old one gets `superseded by ADR<nnn>` and stays. Never deleted.
- **Dated facts** (versions, issue status) are true on the ADR's date. Re-check them before relying on them; if they changed the decision, write a new ADR.

## Template

One screen at most.

```markdown
# ADR<nnn> <The decision, as a sentence>

- Status: proposed | accepted | superseded by ADR<nnn>
- Date: <YYYY-MM-DD>
- Tickets: T<nnn>
- Basis: investigated | arbitrary (<what wasn't examined>)

## Context

<The problem and the constraints, with dated facts.>

## Decision

<What we do.>

## Alternatives ruled out

- <Option>: <why not>.

## Consequences

<What it costs, what it makes easier, what it forbids.>

## Revisit when

<The event or fact that would re-open the decision.>
```

## Records

| ADR | Decision | Status |
|---|---|---|
| [ADR001](ADR001-lock-is-the-source-of-truth.md) | `uv.lock` is the source of truth; `pyproject.toml` has `>=` floors equal to the locked versions and no preventive upper bound | accepted |
| [ADR002](ADR002-no-dependency-cooldown.md) | No dependency cooldown | accepted |
| [ADR003](ADR003-pyiceberg-as-the-data-plane.md) | PyIceberg is the data plane until DuckDB can read and write Iceberg on a Nessie branch | accepted |
