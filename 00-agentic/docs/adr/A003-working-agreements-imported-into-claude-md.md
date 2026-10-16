# A003 Working agreements live in `00-agentic/agreements/` and are imported into `CLAUDE.md`

- Status: accepted
- Date: 2026-10-16
- Tickets: T015
- Basis: investigated (`@path` imports in `CLAUDE.md` are documented in the Claude Code changelog; a fresh `claude -p` session on 2026-10-16 quoted the imported rules without reading any file)
- Amended: 2026-10-16: Context corrected, subdirectory `CLAUDE.md` files load on demand (found in T027); the decision is unchanged

## Context

`CLAUDE.md` mixed project facts (stack, commands, end-to-end check) with the agent's working rules (tickets, decisions, honesty, memory). The rules belong to the agentic layer, which will leave the repo; Claude Code loads the root `CLAUDE.md` at every session; a subdirectory's `CLAUDE.md` only when it works on a file in that subdirectory (checked on 2.1.281, 2026-10-16). Rules needed in every session must be reachable from the root one.

## Decision

`CLAUDE.md` keeps the project facts and imports the working agreements with `@00-agentic/agreements/<file>.md` lines. The reference material (ticket and ADR processes) stays out of the imports, in `00-agentic/processes/`, read when a rule points to it.

## Alternatives ruled out

- Everything in `CLAUDE.md`: the layer can't be extracted without rewriting it, and the boundary with the project stays blurry.
- A plugin or shared user config now: the rules still change often; that's the target for when the layer leaves the repo, not a first step.
- Claude Code's native `.claude/rules/` (loaded without imports, can be scoped to paths): splits the layer between `.claude/` and `00-agentic/`, and ties it to Claude Code. Worth it later for agreements scoped to some files. The folder is named `agreements/` partly to avoid confusion with it.
- Importing the processes too: templates and lifecycles in context at every session, for rules that point to them when needed.

## Consequences

- One place to edit each rule; `CLAUDE.md` is short and about the project.
- The rules depend on Claude Code's import syntax; another agent tool would need its own way to load them.

## Revisit when

The layer moves out of the repo (imports replaced by a plugin or shared config), or another agent tool has to read the same rules.
