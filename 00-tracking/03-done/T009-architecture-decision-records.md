# T009 Architecture decision records

Important decisions are scattered: in ticket Notes and Outcomes (T003, T007, T008), in docs ("Why PyIceberg" and the "Choices" table in `docs/project/architecture.md`), or only in conversations. Nothing says what was decided, why, what was ruled out, and how sure we were. Add a `docs/adr/` folder that records them, linked from `CLAUDE.md` so the agent reads and follows them, and proposes one when a decision is taken.

The risk is a dump of every choice. The selection criteria below are the core of the ticket: few ADRs, each one worth reading.

## Acceptance criteria

- [x] `docs/adr/README.md` gives the selection criteria, the template, the lifecycle and the naming below, and says what goes elsewhere (ticket, doc, `CLAUDE.md`, code comment).
- [x] Three ADRs are backfilled with status `accepted`: ADR001, ADR002, ADR003 below. Each fits on one screen and names its ticket(s) and the doc it explains.
- [x] ADR002 (cooldown) says its basis is arbitrary, what wasn't examined, and what should make us revisit it.
- [x] The docs link to the ADRs instead of repeating the reasoning: `docs/project/dependency-policy.md` (ADR001, ADR002) and the "Why PyIceberg" section of `docs/project/architecture.md` (ADR003).
- [x] `docs/README.md` indexes `docs/adr/`.
- [x] `CLAUDE.md` lists `docs/adr/` under "Where to read" and gives the agent rules below; the ticket workflow mentions the ADR step when finishing a ticket.
- [x] `CLAUDE.md` has a "Say how solid it is" section using the ADR basis words, and the ticket template's Outcome has a mandatory "Not verified" line (added during the ticket, 2026-10-16).

## Design

**What deserves an ADR**: a decision that meets all three tests.

1. **Real alternatives**: at least one other option was weighed, or deliberately not examined (then say so).
2. **Costly to reverse, or bound to be re-opened**: someone would otherwise ask "why not X?" or redo the analysis.
3. **Outlives its ticket**: it constrains future work, not just the change at hand.

Goes elsewhere: work to do -> ticket; how things are now -> doc (`docs/project/`); working rules for the repo -> `CLAUDE.md`; a local implementation choice -> code comment. The "Choices" table in `architecture.md` stays as the one-line summary of the current setup; a row links to an ADR when one exists.

**One decision per ADR.** T008 took several choices; only the ones passing the tests become ADRs.

**Template** (short sections, one screen):

```markdown
# ADR<nnn> <The decision, as a sentence>

- Status: proposed | accepted | superseded by ADR<nnn>
- Date: <YYYY-MM-DD>
- Tickets: T<nnn>
- Basis: investigated | arbitrary (<what wasn't examined>)

## Context
## Decision
## Alternatives ruled out
## Consequences
## Revisit when
```

**Lifecycle**

- Naming: `docs/adr/ADR<nnn>-<short-kebab-case-title>.md`, referred to as `ADR001`; IDs never reused. No status folders: the status is in the file.
- An ADR is written in the ticket that takes the decision, as `proposed`, and becomes `accepted` when the developer validates the ticket (same squashed commit).
- An accepted ADR is never edited except its status line. Changing a decision means a new ADR that supersedes it; the old one gets `superseded by ADR<nnn>` and stays.

**Agent rules for `CLAUDE.md`**

- Before changing something an ADR covers, read it. If the work would contradict an accepted ADR, stop and ask.
- When a ticket takes a decision that passes the three tests, draft the ADR on the ticket branch and say so in the report.
- Never edit an accepted ADR beyond its status line.

**Backfill**

| ADR | Decision | Source | Basis |
|---|---|---|---|
| ADR001 | `uv.lock` is the source of truth; `pyproject.toml` has `>=` floors equal to the locked versions and no preventive upper bound | T007, T008 | investigated |
| ADR002 | No dependency cooldown (`exclude-newer`) | T008 | arbitrary, to challenge |
| ADR003 | PyIceberg as the data plane until DuckDB can read and write Iceberg on a Nessie branch | architecture, T001 | investigated (duckdb-iceberg#1145, #1230) |

Ruled out of the backfill: JDBC2 on Postgres (T003: JDBC was deprecated, the local stack is disposable, so cheap to reverse); Silo, mise, docker compose (one line in "Choices" is enough); language and ticket conventions (`CLAUDE.md` rules); library rules, review cadence, unversioned application, PyPI over Red Hat Trusted Libraries (doc content, or no real alternative weighed).

## Notes

- Candidate for later, in its own ticket: `nessie.py` as our own client rather than `pynessie` (API v1, unmaintained), when T005 decides whether it becomes a separate package.
- ADR003 will likely be superseded by T001 when DuckDB 2.0 ships: a good first test of the lifecycle.

## Outcome

Done on 2026-10-16.

- `docs/adr/README.md`: the three selection tests, what goes elsewhere, lifecycle (naming, `proposed` then `accepted` at validation, never edited, superseded), template with a `Basis` field, list of records.
- Backfilled, status `accepted`: ADR001 (lock as the source of truth, floors), ADR002 (no dependency cooldown, basis arbitrary, with what wasn't examined and when to revisit), ADR003 (PyIceberg as the data plane until DuckDB 2.0).
- Links: `docs/project/dependency-policy.md` and the "Why PyIceberg" section and "Choices" table of `docs/project/architecture.md` point to the ADRs; `docs/README.md` indexes `docs/adr/`.
- `CLAUDE.md`: `docs/adr/` under "Where to read", a "Decisions" section with the agent rules, the ADR step in "Finishing", and a "Say how solid it is" section. Added during the ticket at the developer's request: that section and the mandatory "Not verified" line in the ticket template (`00-tracking/README.md`).
- Location changed when refining: `docs/adr/` instead of `00-adr/`.
- Not verified: ADR003's dated facts were not re-checked beyond DuckDB's latest stable release on PyPI (still 1.5.6 on 2026-10-16); duckdb-iceberg#1230 and #784 are as recorded on 2026-10-15. Whether the new `CLAUDE.md` rules change the agent's behaviour can only be seen over the next tickets.
