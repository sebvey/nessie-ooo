# A005 The ticket workflow doesn't depend on the storage; a backend file is plugged by an import

- Status: accepted
- Date: 2026-10-16
- Tickets: T026
- Basis: investigated for the local backend (rules rewritten, a fresh `claude -p` session described the same workflow before and after); quick look for GitHub and Backlog.md (operations mapped on paper from docs and CLI help, nothing run)

## Context

`00-agentic/` is meant to become a reusable layer for other projects, where tickets may be stored as local Markdown files, in Backlog.md, in GitHub or GitLab issues. Until 2026-10-16 the workflow rules named folders, file moves, the ID rule and the `T<nnn>` format. The backends differ on points beyond mechanics: where the status lives, who allocates IDs, what closes a ticket (a file move, `Closes #n` at a push), whether the tool commits by itself (Backlog.md's `auto_commit`), whether files may be edited directly.

## Decision

The workflow (`agreements/tickets.md`) and the ticket format (`processes/tickets.md`) name statuses (Backlog, Ready, In progress, Done) and operations (file, change status, tick, note, close) only. One file per backend in `ticket-backends/` says where tickets live, how each operation is done, and the reference format in branch names and commit subjects. A project imports exactly one backend file in the project part of its `CLAUDE.md`, so its rules are always in context; switching backend means changing that import.

## Alternatives ruled out

- Write the workflow for one backend (the local files, or GitHub directly): every other backend would mean rewriting the workflow.
- A section per backend inside the workflow file: every project would carry all backends in context.
- A skill per backend: not ruled out for good, but a doc is enough while procedures are short; reconsider if a backend's procedures prove fiddly.

## Consequences

- Adding a backend is a new file plus its setup; the workflow stays.
- The workflow's wording must stay operation-level ("close the ticket as done"), which hides the order of steps a backend may impose (GitHub closes at the push); the backend file states it.
- With a single real backend so far, the operation list is a guess checked on paper; the second backend may change it.

## Revisit when

A second backend is implemented (GitHub is next) and the operation list or the import mechanism doesn't fit, or the layer leaves the repo in a form (plugin, shared config) where an `@` import isn't available.
