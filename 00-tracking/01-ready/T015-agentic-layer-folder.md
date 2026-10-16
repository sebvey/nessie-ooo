# T015 Agentic layer folder

The repo has an agentic layer, scattered and mixed with the project: agent rules in `CLAUDE.md` next to project facts (stack, end-to-end check), permissions in `.claude/settings.json`, the ticket process in `00-tracking/README.md`, the ADR process in `docs/adr/README.md`, and external dependencies documented nowhere (the developer's global `CLAUDE.md` with the `mise exec` rule, the organization's instructions). Gather it in `00-agentic/`, to document and track what we set up, with a clear boundary from the Nessie project: this layer will live outside the repo at some point.

Area: agentic

## Acceptance criteria

- [ ] `00-agentic/README.md` says what the layer is, where its boundary with the project lies, and indexes the folder.
- [ ] `00-agentic/layer.md` describes the components and how they fit: instruction files, the ticket loop (ticket, branch, validation, squash), the decision process, the memory and "say how solid it is" rules.
- [ ] `00-agentic/infra.md` describes the Claude Code setup: the permission families in `.claude/settings.json` and why, the MCP servers the sessions use, `mise exec`, and what the repo depends on outside it (global `CLAUDE.md`, organization instructions), without copying their content.
- [ ] `CLAUDE.md` keeps only the project facts and imports the agent rules from `00-agentic/rules/` with `@` imports. A new session loads the same rules as before (checked by asking a fresh session to list its rules on tickets, ADRs and honesty).
- [ ] The process rules move to `00-agentic/`: the ticket process (from `00-tracking/README.md`) and the ADR process (criteria, lifecycle, template, from `docs/adr/README.md`). `00-tracking/` keeps the tickets and `docs/adr/` the project ADRs, each with a pointer to the rules. One ADR process serves both ADR sets.
- [ ] `00-agentic/adr/` holds the ADRs on the agentic layer, numbered `A001`, `A002`… apart from the project's `ADR001` series. The candidates below are sorted with the three tests; only those that pass are written.
- [ ] Tickets on the agentic layer stay in `00-tracking/` and carry an `Area: agentic` line (a label once tickets move to GitHub); the ticket template mentions it.
- [ ] No broken link in the Markdown files.

## Design (agreed on 2026-10-16)

- **Scope**: the whole way of working with the agent, processes included, since the agent runs them.
- **`00-agentic/`**, not `00-agentification/`: the folder describes a layer. `00-` marks folders outside the product, like `00-tracking/`.
- **`@` imports** keep `CLAUDE.md` at the root (Claude Code loads it from there) while the rules live in `00-agentic/rules/`. Moving the layer out later means swapping the imports for a plugin or a shared config. Claude Code supports `@path/to/file.md` imports in `CLAUDE.md` (changelog, checked 2026-10-16); behaviour with relative paths to be checked while implementing.
- **One `00-tracking/`**, with `Area: agentic`, rather than a second ticket system.

## Notes

- ADR candidates for `00-agentic/adr/` (to sort, not all will pass): tickets as Markdown in the repo rather than GitHub issues now; the repo as source of truth rather than the agent's memory; agent rules imported into `CLAUDE.md`; one squashed commit per ticket; the developer validates before any ticket is closed.
- `.claude/settings.json` stays where Claude Code reads it; `infra.md` documents it.

## Outcome
