# A001 Tickets are Markdown files in the repo, until they move to a ticket tool

- Status: accepted
- Date: 2026-10-16
- Tickets: T014, T015
- Basis: arbitrary (the choice predates the ADRs and its reasons weren't written down; GitHub issues were not compared)

## Context

Tickets live in `00-tracking/`, one Markdown file each, foldered by status, since 2026-10-16 (before that, a single `backlog.md`). The developer has said they are kept there temporarily and will move to GitHub or similar (T014).

## Decision

Tickets stay Markdown files in `00-tracking/` for now, with the process in [`processes/tickets.md`](../processes/tickets.md). Everything is written so the move stays cheap: no ticket ID in code or config, an `Area` line that maps to a label.

## Alternatives ruled out

- GitHub issues now: not examined.

## Consequences

- The agent reads and writes tickets with its file tools, with no extra access; a ticket's status change is versioned with the code it concerns (same squashed commit).
- No board, no notifications, no assignees: fine for one developer and one agent.
- References to tickets in docs and ADRs will need a mapping when tickets move.

## Revisit when

Someone else joins the work, a board becomes useful, or the agent gets reliable access to a ticket tool.
