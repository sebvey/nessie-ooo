# Agentic layer

How we work with a coding agent (Claude Code) on this repo: the rules it follows, the processes it runs, the infra it runs on, and the decisions behind them. This layer is documented and tracked here, apart from the Nessie demo, because it will live outside the repo at some point.

## Boundary with the project

| Agentic layer (here) | Project (elsewhere) |
|---|---|
| Working agreements: tickets workflow, decisions, honesty, memory, writing, boundaries | What the repo is, the stack, how to run it: `CLAUDE.md`, `README.md` |
| Processes: tickets, ADRs | The tickets themselves: `00-tracking/`, local, ignored by git |
| Agent infra: Claude Code permissions, MCP servers, external instructions | Project ADRs: `docs/adr/` |
| Decisions on the layer: `adr/` | Project docs: `docs/` |

Test: would this still hold for another repo worked on the same way? Then it belongs here.

## Contents

- [`layer.md`](layer.md): the components and how they fit.
- [`infra.md`](infra.md): Claude Code setup and what the layer depends on outside the repo.
- [`agreements/`](agreements/): the working agreements between the developer and the agent, imported by `CLAUDE.md` (`@00-agentic/agreements/…`).
  - [`tickets.md`](agreements/tickets.md): the ticket workflow and references.
  - [`decisions.md`](agreements/decisions.md): reading and proposing ADRs.
  - [`honesty.md`](agreements/honesty.md): say how solid it is, facts that age.
  - [`memory.md`](agreements/memory.md): the repo, not the agent's memory, is the source of truth.
  - [`writing.md`](agreements/writing.md): English, unwrapped Markdown.
  - [`boundaries.md`](agreements/boundaries.md): the developer's setup, destructive actions.
- [`processes/`](processes/): reference for humans and the agent, read when needed.
  - [`tickets.md`](processes/tickets.md): statuses, naming, IDs, template, `Area` line.
  - [`adr.md`](processes/adr.md): what deserves an ADR, lifecycle, template, for both series.
- [`adr/`](adr/README.md): decisions on the agentic layer (`A001`…).

## Tracking

Work on this layer is tracked like the rest, in the local `00-tracking/`, with an `Area: agentic` line in the ticket.
