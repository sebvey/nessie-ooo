# Tickets

Tickets live in `00-tracking/`, one file per ticket, foldered by status. How to write and file them (statuses, naming, IDs, template): `00-agentic/processes/tickets.md`. The workflow:

- **Entry point**: a new idea, follow-up or problem found along the way becomes a ticket in `00-backlog/`. Don't widen the ticket in progress.
- **Refining** a backlog ticket (scope, acceptance criteria) is a discussion: propose, and only move it to `01-ready/` once the user agrees.
- **What to work on**: only a ticket from `01-ready/`, unless the user asks otherwise.
- **Starting**: check the working tree is clean, switch to an up-to-date `main` if needed, create a branch named like the ticket file without `.md` (`T004-refactor-dbt-project`), and move the ticket to `02-in-progress/` on that branch.
- **Finishing**: check every acceptance criterion, report, and **wait for the user's validation**. Then move the ticket to `03-done/` (criteria ticked, Outcome filled), set the ticket's `proposed` ADRs to `accepted`, squash the branch into one commit `T004 <title>` rebased on `main`, and fast-forward `main`.
- **Small work without a ticket** (a fix, an ADR amendment, a few lines asked for directly): on a branch `X666-<object>` (`X666-amend-a001`: the ticket-like ID says there is no ticket), committed there, reported, and merged into `main` (fast-forward) only after the developer's explicit validation. Nothing is committed directly on `main`, except ticket bookkeeping: filing a backlog ticket, or moving one to `01-ready/` once the developer agreed.
- **Commit only your own files**: stage the paths you created or changed, never a whole folder that may hold the developer's untracked files.
- **References**: name tickets by ID (`T004`) in tickets, commits, branches, docs and ADRs. **Never in code or config** (comments, task descriptions, console output): tickets are a separate concern and will leave the repo. Write the reason itself instead ("dbt-core 1.11.12 rejects sqlparse 0.6", not "see T007"); a link to an upstream issue is fine.
