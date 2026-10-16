# Evolving the agentic layer

Instructions for working on `00-agentic/` itself. Claude Code loads this file when it works on files in this folder; the root `CLAUDE.md` holds what any project using the layer needs.

## What the layer is

How we work with a coding agent: the working agreements (`agreements/`, imported by a project's `CLAUDE.md`), the processes they point to (`processes/`), the ticket backends (`ticket-backends/`, a project imports one), and its docs (`README.md` as entry point, `docs/`: adopting it, how it is built, its dependencies, its decisions in `docs/adr/`). It is developed in this repo for now and will leave it: what a project uses must not depend on what only serves developing the layer.

Boundary test: would this still hold for another repo worked on the same way? Then it belongs in the layer; otherwise in the project.

## Rules when changing the layer

- **Keep the docs in sync**: a change to an agreement, process or backend updates `docs/layer.md` (how the parts fit), `docs/adopting.md` (what a project must provide, assumptions), `docs/dependencies.md` (what the layer relies on) and `README.md` when it touches them.
- **Its own ADR series**: decisions on the layer go in `docs/adr/` (`A001`, `A002`…, index in `docs/adr/README.md`), with the same process as the project's ADRs ([`processes/adr.md`](processes/adr.md)). A project using the layer has only its own series.
- **Tickets on the layer** share the project's backend and carry an `Area: agentic` line under their first paragraph (a label in a backend that has labels).
- **What a project uses stays self-contained**: `agreements/`, `processes/` and `ticket-backends/` never point to `README.md`, `docs/` or this file, so the evolving part can be removed without breaking them.
