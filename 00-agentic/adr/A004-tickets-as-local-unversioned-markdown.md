# A004 Tickets are local Markdown files, not versioned, until they move to a ticket tool

- Status: accepted
- Date: 2026-10-16
- Tickets: none (small work on branch `X666-local-tracking`)
- Basis: arbitrary (the developer's choice, to keep ticket bookkeeping out of git; no other local option compared)
- Supersedes: A001
- Amended: 2026-10-16: link to the local backend file, where the local process moved (T026)

## Context

Since A001, tickets were Markdown files in `00-tracking/`, versioned with the code: filing a ticket or moving it to ready was a commit on `main`, and a ticket's status change went into the work's squashed commit. Those bookkeeping commits mixed ticket management with the project's history, and the rules for them took room in the workflow. Tickets are meant to move to a ticket tool (GitHub Issues is the candidate, 2026-10-16); a versioned local tool with a UI (Backlog.md, used by the developer on another project) is the option for a richer local setup.

## Decision

`00-tracking/` stays as it is (one file per ticket, foldered by status, same template), but is listed in `.gitignore` and removed from the index: tickets are local files, edited and moved without commits. Only the work is committed. How the local backend works is in [`ticket-backends/local.md`](../ticket-backends/local.md); the format, in [`processes/tickets.md`](../processes/tickets.md).

## Alternatives ruled out

- Keep tickets versioned (A001): the bookkeeping commits are the problem this solves.
- Move to Backlog.md now: richer, but a separate topic; not needed for one developer and one agent.

## Consequences

- No commit on `main` for ticket bookkeeping; the squashed commit holds only the work.
- No history and no backup of tickets beyond the developer's own; the history up to 2026-10-16 stays in git.
- Tickets are absent from clones and from git worktrees: an agent in a worktree reads and writes them in the main checkout, by absolute path.
- Ticket IDs in docs, ADRs and commits point to files a reader of the repo doesn't have; evidence an ADR rests on must already be outside tickets (ADR process).

## Revisit when

Tickets move to a ticket tool, or the work needs ticket history or sharing (someone else joins, several machines).
