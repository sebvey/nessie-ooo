# Agentic layer

A set of working agreements, processes and ticket backends for working on a repository with a coding agent (Claude Code). A project imports it from its `CLAUDE.md`; the agent then follows the same workflow in every project that uses it.

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
| `CLAUDE.md` | maintainers | Instructions for an agent evolving the layer |

## Two paths

- **Adopting it in a project**: [docs/adopting.md](docs/adopting.md) (steps, the contract with the project's `CLAUDE.md`, assumptions), then [docs/dependencies.md](docs/dependencies.md).
- **Evolving it**: [docs/layer.md](docs/layer.md) (how the parts fit, the two missions), [docs/adr/](docs/adr/README.md) (decisions on the layer, `A001`…), and [CLAUDE.md](CLAUDE.md) (the rules an agent follows when changing the layer).

## Status

Developed inside a host project for now, and meant to be extracted; the form it will take (plugin, template, shared config) isn't chosen. Until then, it is used by importing its files from `00-agentic/`.
