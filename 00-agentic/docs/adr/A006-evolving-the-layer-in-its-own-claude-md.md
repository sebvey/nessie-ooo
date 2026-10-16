# A006 Instructions for evolving the layer live in `00-agentic/CLAUDE.md`, loaded on demand

- Status: accepted
- Date: 2026-10-16
- Tickets: T027
- Basis: investigated (Claude Code 2.1.281: a canary in `00-agentic/CLAUDE.md` was absent from a fresh `claude -p` session's context, and present right after the session read a file in `00-agentic/`; unplug test run on a copy of the repo, see T027)

## Context

The agent has two missions in this repo: implementing the Nessie demo, and evolving the agentic layer, which will leave the repo. Until 2026-10-16 both missions' instructions were mixed: the root `CLAUDE.md` explained the layer, the decisions agreement and ADR process described the layer's own ADR series next to the project's, and the generic ticket template required an `Area: agentic` line. Claude Code loads a subdirectory's `CLAUDE.md` when it works on a file in that subdirectory (checked on 2.1.281, 2026-10-16).

## Decision

The instructions for evolving the layer (boundary test, the `A` series, `Area: agentic`, docs to keep in sync) live in `00-agentic/CLAUDE.md`. The root `CLAUDE.md` is about the project and plugs the layer by imports only. What a project uses (`agreements/`, `processes/`, `ticket-backends/`) never points to what only serves evolving the layer (`00-agentic/CLAUDE.md`, `README.md`, `docs/`), so that part can be removed without breaking the rest.

## Alternatives ruled out

- One root `CLAUDE.md` with a section per mission: the layer's rules in context in every session, and unplugging means editing the project's file.
- Claude Code's `.claude/rules/` scoped to `00-agentic/**`: same on-demand effect, but splits the layer between `.claude/` and `00-agentic/` (as A003 noted for the agreements).
- A separate repo for the layer now: the layer still changes with this project every day.

## Consequences

- The layer's rules are absent until a file in `00-agentic/` is read: filing a ticket on the layer from a discussion, without touching the layer's files, can miss the `Area: agentic` line.
- Unplugging is a removal plus replacing the `@00-agentic/…` imports, without rewriting the project part of the root `CLAUDE.md`.
- The rule "what a project uses never points to the evolving part" has to hold at each change of the layer.

## Revisit when

The layer leaves the repo, or Claude Code changes how it loads subdirectory `CLAUDE.md` files.
