# vierbein

An agentic layer: a set of working agreements, processes and ticket backends for working on a repository with a coding agent (Claude Code). A project imports it from its `CLAUDE.md`; the agent then follows the same workflow in every project that uses it.

## The name

In general relativity, a vierbein (German for "four legs", also called a tetrad) is a local frame attached to each point of spacetime: it lets physics be written in the simple local terms of that point, while staying tied to the laws that hold everywhere. The layer does the same for projects. Each project has its local frame, set in its own `CLAUDE.md` (ticket backend, ticket prefix, ADR series, setup), and through it the agent applies the same agreements and the same workflow as everywhere else.

## Principles

- **The agent proposes, the developer decides**: tickets are filed, made ready and closed with the developer's agreement; nothing reaches `main` without the developer's validation.
- **Tickets with checkable criteria**: each criterion is ticked when verified, with how, and reported one by one with what wasn't verified.
- **Decisions are recorded**: the ones that pass three tests get an ADR, with its basis stated.
- **Say how solid it is**: every finding states its basis (investigated, quick look, arbitrary); "not checked" is a finding.
- **The repo is the source of truth**, not the agent's memory.
- **The developer's setup is theirs**, and nothing created by someone else is destroyed without asking.

## What's in it

| Folder | For | Content |
|---|---|---|
| `agreements/` | projects | The rules, imported by the project's `CLAUDE.md` |
| `processes/` | projects | Ticket statuses and template, ADR process and template |
| `ticket-backends/` | projects | One file per way of storing tickets; a project imports one |
| `docs/` | adopters, maintainers | Adopting the layer, how it is built, its dependencies, its decisions |
| `CLAUDE.md` | maintainers | The layer as a project: its own bindings (ticket prefix `t`, ADR series `A`), checks, rules for evolving it |
| `scripts/` | maintainers | `check-links.py`: relative links in the layer's Markdown |

## Two paths

- **Adopting it in a project**: [docs/adopting.md](docs/adopting.md) (steps, the contract with the project's `CLAUDE.md`, assumptions), then [docs/dependencies.md](docs/dependencies.md).
- **Evolving it**: [docs/layer.md](docs/layer.md) (how the parts fit, the two missions), [docs/adr/](docs/adr/README.md) (decisions on the layer, `A001`…), and [CLAUDE.md](CLAUDE.md) (the rules an agent follows when changing the layer).

## Status

Developed inside a host project for now, as a project of its own (its `CLAUDE.md`, its local tickets, its ADRs), and meant to be extracted to its own repository; the form projects will use it in (plugin, template, shared config) isn't chosen. Until then, a project imports its files from the folder it sits in.
