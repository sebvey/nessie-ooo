# Evolving the agentic layer

Instructions for working on `00-agentic/` itself. Claude Code loads this file when it works on files in this folder; the root `CLAUDE.md` holds what any project using the layer needs.

## What the layer is

How we work with a coding agent: the working agreements (`agreements/`, imported by a project's `CLAUDE.md`), the processes they point to (`processes/`), the ticket backends (`ticket-backends/`, a project imports one), and, for developing the layer only, its docs (`README.md`, `layer.md`, `infra.md`) and its decisions (`adr/`). It is developed in this repo for now and will leave it: what a project uses must not depend on what only serves developing the layer.

Boundary test: would this still hold for another repo worked on the same way? Then it belongs in the layer; otherwise in the project.

## Rules when changing the layer

- **Keep the docs in sync**: a change to an agreement, process or backend updates `layer.md` (components and how they fit) and `README.md` (contents) when it touches them, and `infra.md` when it touches the agent's setup.
- **Its own ADR series**: decisions on the layer go in `adr/` (`A001`, `A002`…, index in `adr/README.md`), with the same process as the project's ADRs ([`processes/adr.md`](processes/adr.md)). A project using the layer has only its own series.
- **Tickets on the layer** share the project's backend and carry an `Area: agentic` line under their first paragraph (a label in a backend that has labels).
- **What a project uses stays self-contained**: `agreements/`, `processes/` and `ticket-backends/` never point to `README.md`, `layer.md`, `infra.md`, `adr/` or this file, so the evolving part can be removed without breaking them.
