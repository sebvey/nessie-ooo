# CLAUDE.md

Demo of Project Nessie (Git-like catalog for Iceberg tables): a pipeline works on a Nessie branch, tests it with dbt, and merges into `main` only if the tests pass.

## Where to read

- `README.md`: what the repo does, quick start, mise tasks.
- `docs/README.md`: documentation index.
  - `docs/concepts/`: Iceberg and Nessie knowledge, valid outside this repo.
  - `docs/project/`: what we built (architecture, pipeline, CLI, DuckDB 2.0 plan).
  - `docs/presentation/`: the talk's slides and notes.
- `00-tracking/`: tickets, one file each, foldered by status (rules in `00-tracking/README.md`).

## Language

Everything in the repo is in **English**: code, comments, docstrings, console output, docs, backlog, and commit messages (older commits are in French; leave them). The only exception is `docs/presentation/`, which stays in French.

Markdown: no hard wrapping. One line per paragraph or list item; let the editor wrap.

## Memory

The repo is the source of truth: anything about the project (architecture, decisions, conventions, status) goes in the docs, `CLAUDE.md` or a ticket, never in the agent's memory. Memory is only for the developer's personal working preferences that don't belong in the repo. When memory and the repo disagree, the repo wins: fix or delete the memory.

## Facts that age

Versions, release status and issue status written in docs and tickets are dated. Re-verify them against a primary source (release notes, the issue itself) before relying on them, and update the doc or ticket when they changed.

## Running things

- Run tools through mise: `mise run <task>` (see `tasks.toml`) or `mise exec -- <command>`. Env vars come from `mise.toml` and `mise.local.toml`.
- `mise.local.toml` is ignored by git and holds local values and secrets (template: `mise.local.toml.example`). `docker-compose.yml` refuses to start without them.
- Setup is the developer's job, not the agent's: if mise reports an untrusted config, `mise.local.toml` is missing, or Docker isn't running, stop and ask the developer to run `mise trust`, create `mise.local.toml` from the example, or start Docker (Colima). Never create or edit `mise.local.toml` yourself; to target another branch, set the variable on the command line (`NESSIE_BRANCH=<branch> mise exec -- ...`).
- Stack: `mise run stack-up`, `stack-down`, `stack-reset` (deletes all data: Nessie history and Iceberg files).
- The local stack is disposable, except refs the developer created. Before `stack-reset`, or before dropping a branch or tag, list the refs (`curl -s http://localhost:19120/api/v2/trees`): if any wasn't created during your session (by you or by a pipeline run you launched), ask first. Say in your report when you reset the stack.
- End-to-end check after a change: `mise run stack-reset`, `stack-up`, then `uv run pipeline --no-pause` and `uv run pipeline --bad --no-pause` (through `mise exec --`). The `-bad` run must end with no merge and `main` unchanged.
- Dependencies: adding, upgrading or bounding one follows `docs/project/dependency-policy.md` (floors equal to the locked versions, `uv lock --upgrade-package` one package at a time).
- The Nessie CLI (`mise run cli`) is for humans (it needs a TTY). Programmatic actions and checks go through the Nessie API: `src/nessie_demo/nessie.py` or `curl http://localhost:19120/api/v2/...`.

## Tickets

Tickets live in `00-tracking/`, one file per ticket, foldered by status. How to write and file them (statuses, naming, IDs, template): `00-tracking/README.md`. The workflow:

- **Entry point**: a new idea, follow-up or problem found along the way becomes a ticket in `00-backlog/`. Don't widen the ticket in progress.
- **Refining** a backlog ticket (scope, acceptance criteria) is a discussion: propose, and only move it to `01-ready/` once the user agrees.
- **What to work on**: only a ticket from `01-ready/`, unless the user asks otherwise.
- **Starting**: check the working tree is clean, switch to an up-to-date `main` if needed, create a branch named like the ticket file without `.md` (`T004-refactor-dbt-project`), and move the ticket to `02-in-progress/` on that branch.
- **Finishing**: check every acceptance criterion, report, and **wait for the user's validation**. Then move the ticket to `03-done/` (criteria ticked, Outcome filled), squash the branch into one commit `T004 <title>` rebased on `main`, and fast-forward `main`.
- **References**: name tickets by ID (`T004`) in commits, branches and docs.
