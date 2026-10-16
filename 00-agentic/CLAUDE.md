# CLAUDE.md

The agentic layer: working agreements, processes and ticket backends for working on a repository with a coding agent. This folder is a project of its own, which adopts its own layer; for now it sits inside a host project (see "Coexistence").

## Where to read

- `README.md`: entry point.
- `docs/adopting.md`: what a project must provide to use the layer. This file follows it.
- `docs/layer.md`: how the parts fit. `docs/dependencies.md`: what the layer relies on.
- `docs/adr/`: decisions on the layer. The project's ADR series: `A001`, `A002`… (index in `docs/adr/README.md`).

## Working agreements

@agreements/tickets.md
@agreements/decisions.md
@agreements/honesty.md
@agreements/memory.md
@agreements/writing.md
@agreements/boundaries.md

Ticket backend, ticket prefix `t`:

@ticket-backends/local.md

## Language

English everywhere, no exception.

## Running things

No build and no setup. A change is checked by:

- reading it as an outside adopter would;
- `python3 scripts/check-links.py`: relative links in the project's Markdown (prints the broken ones, exits non-zero if any);
- a fresh `claude -p` session asked how it would apply the changed rule, from a folder where the change is in context.

## Evolving the layer

- **Boundary test**: would this still hold for another repo worked on the same way? Then it belongs in the layer; otherwise in the project that uses it.
- **What a project uses stays self-contained**: `agreements/`, `processes/` and `ticket-backends/` never point to `README.md`, `docs/`, `scripts/` or this file, so a project can take them alone.
- **Keep the docs in sync**: a change to an agreement, process or backend updates `docs/layer.md`, `docs/adopting.md`, `docs/dependencies.md` and `README.md` when it touches them.
- **Rules that change themselves**: a ticket that changes the workflow is carried out under the rules in force when it started; the new rules apply from the next ticket.

## Coexistence

While the layer sits inside a host project (today `nessie-ooo`), two projects share one git repository. Remove this section when the layer moves to its own repository.

- The host's root `CLAUDE.md` is another project, with its own tickets (prefix `T`, in the host's `00-tracking/`) and its own ADR series. When both are in context, this file decides for work on files under this folder.
- A ticket belongs to the project whose files it changes. A change that touches both projects is two tickets, one in each.
- Branches and commits carry the ticket's prefix (`t001-…` here, `T029-…` in the host), on the shared `main`.
- Tickets moved here from the host on 2026-10-17 keep their `T` IDs; their `Area: agentic` line is history. They don't count for the next `t` ID.
