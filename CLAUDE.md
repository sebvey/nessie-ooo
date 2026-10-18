# CLAUDE.md

Demo of Project Nessie (Git-like catalog for Iceberg tables): a pipeline works on a Nessie branch, tests it with dbt, and merges into `main` only if the tests pass.

## Where to read

- `README.md`: what the repo does, quick start, mise tasks.
- `docs/README.md`: documentation index.
  - `docs/concepts/`: Iceberg and Nessie knowledge, valid outside this repo.
  - `docs/project/`: what we built (architecture, pipeline, CLI, dependency policy).
  - `docs/presentation/`: the talk's slides and notes.
  - `docs/adr/`: architecture decision records, why things are the way they are. The project's ADR series: `ADR001`, `ADR002`…
- `00-agentic/`: the agentic layer (working agreements, processes, ticket backends), this project's copy of vierbein.

## Working agreements

From the agentic layer, a copy of vierbein in `00-agentic/` that this project owns (provenance in `00-agentic/README.md`, [agent setup](docs/project/agent-setup.md)):

@00-agentic/agreements/tickets.md
@00-agentic/agreements/decisions.md
@00-agentic/agreements/honesty.md
@00-agentic/agreements/memory.md
@00-agentic/agreements/writing.md
@00-agentic/agreements/boundaries.md

Ticket backend: GitHub, GitHub Project 3 of sebvey:

@00-agentic/ticket-backends/github.md

Ticket `T<nnn>` from before the move is issue `#<nnn>`.

## Language

English everywhere in the repo (rule in `00-agentic/agreements/writing.md`), with two exceptions: `docs/presentation/` stays in French, and older commits are in French (leave them).

## Running things

- Run tools through mise: `mise run <task>` (see `tasks.toml`) or `mise exec -- <command>`. Env vars come from `mise.toml` and `mise.local.toml`.
- `mise.local.toml` is ignored by git and holds local values and secrets (template: `mise.local.toml.example`). `docker-compose.yml` refuses to start without them.
- Setup (rule in `00-agentic/agreements/boundaries.md`): if mise reports an untrusted config, `mise.local.toml` is missing, or Docker isn't running, ask the developer to run `mise trust`, create `mise.local.toml` from the example, or start Docker (Colima). Never edit `mise.local.toml`; to target another branch for one command, `mise exec -- env NESSIE_BRANCH=<branch> <command>` (a `NESSIE_BRANCH=… mise exec` prefix is overridden by `mise.local.toml`).
- Stack: `mise run stack-up`, `stack-down`, `stack-reset` (deletes all data: Nessie history and Iceberg files).
- The local stack is disposable, except refs the developer created (rule in `00-agentic/agreements/boundaries.md`). Before `stack-reset`, or before dropping a branch or tag, list the refs: `curl -s http://localhost:19120/api/v2/trees`.
- End-to-end check after a change: `mise run stack-reset`, `stack-up`, then `uv run pipeline --no-pause` and `uv run pipeline --ko --no-pause` (through `mise exec --`). The `--ko` run must end with no merge and `main` unchanged.
- Dependencies: adding, upgrading or bounding one follows `docs/project/dependency-policy.md` (floors equal to the locked versions, `uv lock --upgrade-package` one package at a time). After any change to `uv.lock`, run `mise run audit-python` (Python dependencies only; container images aren't audited).
- The Nessie CLI (`mise run cli`) is for humans (it needs a TTY). Programmatic actions and checks go through the Nessie API: `src/nessie_demo/nessie.py` or `curl http://localhost:19120/api/v2/...`.
