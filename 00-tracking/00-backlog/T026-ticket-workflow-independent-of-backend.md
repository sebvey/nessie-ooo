# T026 Ticket workflow independent of where tickets are stored

The ticket workflow (`00-agentic/agreements/tickets.md`) is written for Markdown files in `00-tracking/`: folders, `git mv`, bookkeeping commits on `main`. T025 moves tickets to GitHub, and the developer wants the mechanism reusable in other projects, with the storage as an option among others. Separate the workflow (statuses, who decides what, branch per ticket, criteria, validation, squash) from the backend (how each operation is done), document the current Markdown backend that way, with no change in behaviour. Prerequisite to T025, which then adds a GitHub backend.

Area: agentic

## Notes

Analysis, 2026-10-16. Basis: quick look (current agreements and processes read; nothing drafted).

### Proposed split

| Layer | Holds | Where (proposal) |
|---|---|---|
| Workflow | Statuses and their meaning (backlog, ready, in progress, done or abandoned), who moves a ticket where, branch per ticket, ticking criteria, report, validation, squash, references kept out of code | `00-agentic/agreements/tickets.md` (rules) and `00-agentic/processes/tickets.md` (template, statuses), both backend-free |
| Backend | How to do each operation: file, read, list by status, change status, tick a criterion, close with an Outcome, abandon; the ticket reference format (`T004`, `#25`) and how it shows in branches and commits; setup | one doc per backend, e.g. `00-agentic/processes/ticket-backends/markdown.md`, later `github.md` (a reusable setup guide) |
| Project binding | Which backend this project uses, and its values (later: Project number, field and option IDs) | the project part of `CLAUDE.md` (it stays in the repo when `00-agentic/` leaves) |

The workflow names operations ("set the ticket to in progress", "the ticket reference"); the backend doc says how. The ticket template (Why, Area, Acceptance criteria, Notes, Outcome, Not verified) stays in the workflow: it is the same content in a file or an issue body.

### Where the workflow leaks the backend today

The steps and who decides don't change; some rules only make sense for Markdown files and move to the backend doc:

- "Move the ticket to `02-in-progress/` on that branch": with files, the status is only visible on `main` after the merge; with GitHub, at once.
- Bookkeeping commits allowed on `main` (filing a ticket, moving it to ready): Markdown only.
- The status change versioned in the squashed commit: Markdown only. With GitHub, closing comes from `Closes #n` at the push.
- Ticking criteria: a file edit on the branch, versus an issue body rewrite visible immediately.
- ID rule (highest plus one) and the parallel collision of T016: Markdown only; GitHub assigns numbers.
- Commit subject `T004 <title>` and branch `T004-<slug>`: depends on the reference format.

### Choices to discuss

- Doc layout: one doc per backend under `processes/`, or a section each in `processes/tickets.md`. Leaning: one doc each, so a project keeps only the one it uses.
- A Claude Code skill per backend (operations as a procedure the agent loads) instead of, or on top of, a doc: fits the layer leaving the repo as a plugin (`00-agentic/layer.md`). Leaning: doc first, skill if the GitHub procedures prove fiddly.
- An `A` ADR "the ticket workflow doesn't depend on the backend": likely passes the three tests (real alternative: write the workflow for GitHub directly; costly to undo; constrains future work). To confirm.
- No-ticket work (`X666-<object>`): its naming depends on the reference format, so it belongs with the backend, or gets a format that works with both.
