# A007 The layer is a project that adopts its own layer

- Status: accepted
- Date: 2026-10-17
- Tickets: none (small work on branches `X666-layer-relative-paths` and `X666-agentic-as-a-project`)
- Basis: investigated (Claude Code 2.1.281: `@` imports in a subdirectory `CLAUDE.md` resolve relative to that file, and a file imported by both the root and the subdirectory appears once in context, per the session's own report; fresh `claude -p` sessions checked in the host, in the layer, and in a standalone copy of the layer)

## Context

The layer is developed inside a host project (`nessie-ooo`, 2026-10-17) and will move to its own repository, where it will be worked on as a project. Until then, its tickets were the host's (`Area: agentic`), its rules referred to it by the host path `00-agentic/`, and its `CLAUDE.md` held only the rules for evolving it. The layer has a contract for projects that use it (`docs/adopting.md`) that no project but the host had followed.

## Decision

The layer's `CLAUDE.md` is the `CLAUDE.md` of a project that adopts the layer, written from `docs/adopting.md`: it imports the agreements and the local ticket backend relative to itself, with its own ticket prefix (`t`) and store (the layer's `00-tracking/`), names its ADR series, and says how a change is checked. The layer refers to its own files relative to itself, and the local backend works from the folder of the importing `CLAUDE.md`. While the layer sits in the host, a "Coexistence" section says which project a piece of work belongs to; it goes when the layer moves out.

## Alternatives ruled out

- Keep the layer's tickets in the host until the move: the layer can't be worked on as a project, and the move becomes a migration.
- Move the layer to its own repository now: the host still uses and shapes it daily; the coexistence period lets the move be rehearsed first.
- Renumber the tickets moved from the host: their `T` IDs are in commits and ADRs, which aren't rewritten.

## Consequences

- The layer checks its own contract: if it can't adopt itself from `docs/adopting.md`, the guide is wrong.
- Moving out is moving a folder that already works as a repository root.
- While the two projects share a repository, two ticket prefixes and two stores coexist; the agent picks by the files a change touches. On a case-insensitive file system, branch names that differ only by the prefix's case (`t001-x`, `T001-x`) would collide.

## Revisit when

The layer moves to its own repository (drop the Coexistence section), or the way projects consume the layer (plugin, template) changes how it imports its own files.
