# Adopting the layer

How to use the layer in a project: what to put where, what the project's `CLAUDE.md` must provide, and what the layer takes for granted.

## Steps

1. Put the layer at `00-agentic/` in the project (the agreements and processes cite that path). The repo needs a first commit on `main`: the workflow branches from it.
2. Keep what a project uses: `agreements/`, `processes/`, `ticket-backends/`. The rest (`CLAUDE.md`, `README.md`, `docs/`) serves evolving the layer and can be left out.
3. Write the project's `CLAUDE.md` with the contract below.
4. Set up the chosen ticket backend, as its file says (the local backend needs only the line `00-tracking/` in `.gitignore`).
5. Check: a fresh session, asked how it would file a ticket and write an ADR, answers with the project's names and paths.

## The contract with the project's `CLAUDE.md`

The layer is written so that the project's `CLAUDE.md` fills these slots. Anything missing leaves the agent guessing.

| Slot | Why | Example |
|---|---|---|
| The agreements, by `@` imports | The rules the agent applies without being asked | `@00-agentic/agreements/tickets.md`, and the other files of `agreements/` |
| One ticket backend, by an `@` import | Where tickets live and how to handle them; the workflow names operations only | `@00-agentic/ticket-backends/local.md` |
| The project's ADR series: folder and ID prefix | `agreements/decisions.md` and `processes/adr.md` refer to it | `docs/adr/`, `ADR001`, `ADR002`… |
| Exceptions to "English everywhere", if any | `agreements/writing.md` sets English as the default and points here for exceptions | slides in French |
| Setup the agent must not do itself: files and commands | `agreements/boundaries.md` says the developer owns the setup and the project names it | trusting a config, a local secrets file, starting Docker; how to set a value for one command |
| Ticket areas, if any | `processes/tickets.md` allows an `Area: <name>` line, named in the project's `CLAUDE.md` | `Area: frontend` |

Template:

```markdown
# CLAUDE.md

<What the project is, in two lines.>

## Where to read

<The project's docs, including its ADR folder and ID prefix.>

## Working agreements

@00-agentic/agreements/tickets.md
@00-agentic/agreements/decisions.md
@00-agentic/agreements/honesty.md
@00-agentic/agreements/memory.md
@00-agentic/agreements/writing.md
@00-agentic/agreements/boundaries.md

Ticket backend:

@00-agentic/ticket-backends/local.md

## Language

<Exceptions to English, if any.>

## Running things

<How to run the project; the setup files and commands the developer owns.>
```

## Assumptions

- **Claude Code**, with `@` imports and on-demand loading of subdirectory `CLAUDE.md` files ([dependencies](dependencies.md)).
- **Git**, with a `main` branch, a branch per ticket, a squashed commit per ticket, fast-forward merges; the developer pushes.
- **One developer validating**: the agent proposes, the developer decides (tickets filed, Ready, validation, merges). Several developers would need the validation steps revisited.
- **English by default** for everything in the repo.

## What comes from the project, not the layer

The project's own agent setup (pre-approved permissions, MCP servers, tool managers such as mise or asdf, user-level instructions) is outside the layer. Document it in the project's docs; the layer works without any of it.
