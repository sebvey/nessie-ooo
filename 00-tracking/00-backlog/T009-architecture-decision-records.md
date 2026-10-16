# T009 Architecture decision records

Important decisions are scattered: in ticket Notes and Outcomes (T003, T007, T008), in docs ("Why PyIceberg" in `docs/project/architecture.md`), or only in conversations. Nothing says what was decided, why, what was ruled out, and how sure we were. Add a `00-adr/` folder that records them, linked from `CLAUDE.md` so the agent reads and follows them, and writes one when a decision is taken.

**To refine before moving to `01-ready/`**: work out what goes in, so the folder doesn't turn into a dump of every choice.

## Questions to settle when refining

- **What deserves an ADR**: criteria that tell an ADR from a ticket (work to do), a doc (how things are) and a code comment. Lead: a decision that is costly to reverse, or that someone would otherwise re-open, with alternatives actually weighed.
- **Format**: a short template (context, decision, alternatives ruled out, consequences). Plus a field saying how solid the decision is (investigated or arbitrary) and what would make us revisit it.
- **Lifecycle**: statuses (proposed, accepted, superseded by ADR-xxx), numbering, never deleted (like tickets), how an ADR and a ticket refer to each other.
- **Place and language**: `00-adr/` at the root next to `00-tracking/`, English like the rest of the repo. Relation to `docs/project/`: the doc says the current state, the ADR says why.
- **Agent rules in `CLAUDE.md`**: when to read the ADRs, when to propose a new one, never change an accepted one without the developer.
- **Backfill**: which past decisions to record, from the candidates below.

## Candidate decisions (to sort, not all will qualify)

- From T008 (dependency policy, 2026-10-16): `uv.lock` is the source of truth; `>=` floors only, no `~=`; upper bounds only for an observed incompatibility; application floors follow the lock; the application itself isn't versioned (git tags); library rules (justified floors tested with `lowest-direct`, SemVer 0.x); review before each talk and on vulnerability alerts; stay on PyPI rather than Red Hat Trusted Libraries.
- **No dependency cooldown** (`exclude-newer`): an arbitrary choice, not investigated (2026-10-16). The ADR must say so and that it is to be challenged.
- From T003: Nessie version store on JDBC2 over Postgres.
- PyIceberg as the data plane while DuckDB can't write Iceberg on a branch (`docs/project/architecture.md`, T001).
- Repo conventions: English everywhere except `docs/presentation/`, tickets workflow (maybe `CLAUDE.md` is enough for those).

## Acceptance criteria

To write when refining.

## Notes

## Outcome
