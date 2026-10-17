# ADR007 Nessie's tickets move to GitHub Issues, all of them, with issue `#n` for ticket `Tn`

- Status: accepted
- Date: 2026-10-17
- Tickets: T029
- Basis: investigated (`gh` 2.102.0 on `sebvey/nessie-ooo`, 2026-10-17: private, 0 issues and 0 pull requests before the migration; each issue number checked right after its creation, and every issue compared with its ticket file by a check script, procedure in T029)

## Context

Nessie's tickets were local Markdown files in `00-tracking/`, ignored by git: no history, no backup but the developer's own, and absent from git worktrees and cloud sessions. vierbein, the agentic layer copied into `00-agentic/` (ADR006), has a GitHub ticket backend: issues, with their status in a GitHub Project. On 2026-10-17 the tickets used IDs T001 to T031, seven of which (T015, T016, T021, T025 to T028) had left with the layer when it became its own repository. Ticket IDs are cited in ADR001 to ADR004, in `docs/project/dependency-policy.md` and in commit subjects, which can't be rewritten. Nothing in the tickets is confidential.

## Decision

Every ticket moves to an issue of `sebvey/nessie-ooo`, in ID order, so that ticket `Tn` is issue `#n`. The seven IDs that left with the layer become placeholder issues, closed as not planned and kept out of the GitHub Project. Done tickets are migrated too, closed. `CLAUDE.md` imports the GitHub backend from the copy (`00-agentic/ticket-backends/github.md`) and says that `T<nnn>` from before the move is issue `#<nnn>`. The local folder is purged once the migration is checked.

## Alternatives ruled out

- Stay local: no history, no backup, no tickets in worktrees or cloud sessions.
- Migrate only open tickets: ADRs and docs cite done tickets, whose content would be lost.
- A new numbering with a mapping table: a permanent table to keep, a rewrite of every reference, and commit subjects that would keep pointing to the old IDs.

## Consequences

- References `Tn` in docs, ADRs and commit subjects stay valid: they read as `#n`, with no rewrite.
- Seven placeholder issues stay in the repository forever.
- Ticket history is the issue's from now on, and each ticket change is a network call that others see.
- The numbering only held because nothing created an issue or a pull request in the repository before the migration; after it, numbers are GitHub's.

## Revisit when

The repository moves to another host or to a GitHub organization (which offers issue types and fields), or an issue or pull request is created before the migration ends.
