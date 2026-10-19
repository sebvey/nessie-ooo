# Ticket backend: local Markdown files

How the operations of the ticket loop ([`agreements/tickets.md`](../agreements/tickets.md)) are done when tickets are local Markdown files. A project uses this backend by importing this file in its `CLAUDE.md`. The project's root is the folder of that `CLAUDE.md`; paths below are relative to it.

## Where tickets live

- `00-tracking/` at the project's root, one Markdown file per ticket, in one subfolder per status (created when first needed). The folder is local: the line `00-tracking/` in the project's `.gitignore`, never committed, with no history and no backup but the developer's own. A ticket's changes are file edits and moves, never commits. With no history, a rewrite moves superseded content to a dated section of the ticket, never deletes it.
- From a git worktree, where ignored files are absent, read and write tickets in the project's `00-tracking/` in the main checkout, by absolute path.

| Status | Folder |
|---|---|
| Backlog | `00-tracking/00-backlog/` |
| Ready | `00-tracking/01-ready/` |
| In Progress | `00-tracking/02-in-progress/` |
| Done (finished or abandoned) | `00-tracking/03-done/` |

## Reference

- Prefix: set in the project's `CLAUDE.md` (`T` if it says nothing). It tells the project's tickets apart in branch names and commits, e.g. when two projects share a repo. Case matters: `t` and `T` are different prefixes.
- ID: `<prefix><nnn>`, the highest existing ID with that prefix, across all folders, plus one. Tickets with another prefix (kept from another project) keep their ID and don't count. Tickets are never deleted, so an ID is never reused.
- File name: `<ID>-<short-kebab-case-title>.md`, e.g. `T004-refactor-dbt-project.md`. The file starts with `# <ID> <Title>`, then the template's sections.
- Branch: the file name without `.md` (`T004-refactor-dbt-project`).
- Commit subject: `<ID> <title>` (`T004 Refactor the dbt project`).

## Operations

| Operation | How |
|---|---|
| File a ticket | Create the file in `00-tracking/00-backlog/`, with the next ID. |
| Read, list by status | Read the file; list the status folder. |
| Change status | Move the file to the status folder (`mv`); it keeps its name. |
| Tick or untick a criterion | Edit the checkbox in the file. |
| Add a note, a follow-up to propose | Edit the `Notes` section. |
| Close as done or abandoned | Fill the `Outcome` section, then move the file to `03-done/`. |

An analysis ticket keeps its `Type: analysis` line and has no branch and no commit; its analysis report is a `## Analysis report` section of the ticket file, before `## Outcome`.
