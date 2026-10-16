# Ticket backend: local Markdown files

How the operations of the ticket workflow ([`agreements/tickets.md`](../agreements/tickets.md)) are done when tickets are local Markdown files. A project uses this backend by importing this file in its `CLAUDE.md`.

## Where tickets live

- `00-tracking/`, one Markdown file per ticket, in one subfolder per status (created when first needed). The folder is local: the line `00-tracking/` in `.gitignore`, never committed, with no history and no backup but the developer's own. A ticket's changes are file edits and moves, never commits.
- From a git worktree, where ignored files are absent, read and write tickets in the main checkout's `00-tracking/`, by absolute path.

| Status | Folder |
|---|---|
| Backlog | `00-tracking/00-backlog/` |
| Ready | `00-tracking/01-ready/` |
| In progress | `00-tracking/02-in-progress/` |
| Done (finished or abandoned) | `00-tracking/03-done/` |

## Reference

- ID: `T<nnn>`, the highest existing one across all folders plus one. Tickets are never deleted, so an ID is never reused.
- File name: `T<nnn>-<short-kebab-case-title>.md`, e.g. `T004-refactor-dbt-project.md`. The file starts with `# T<nnn> <Title>`, then the template's sections.
- Branch: the file name without `.md` (`T004-refactor-dbt-project`).
- Commit subject: `T<nnn> <title>` (`T004 Refactor the dbt project`).

## Operations

| Operation | How |
|---|---|
| File a ticket | Create the file in `00-backlog/`, with the next ID. |
| Read, list by status | Read the file; list the status folder. |
| Change status | Move the file to the status folder (`mv`); it keeps its name. |
| Tick or untick a criterion | Edit the checkbox in the file. |
| Add a note, a follow-up to propose | Edit the `Notes` section. |
| Close as done or abandoned | Fill the `Outcome` section, then move the file to `03-done/`. |
