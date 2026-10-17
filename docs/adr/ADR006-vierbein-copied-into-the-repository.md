# ADR006 The agentic layer, vierbein, is copied into the repository

- Status: accepted
- Date: 2026-10-17
- Tickets: T031
- Basis: investigated (Claude Code 2.1.281: `@` imports outside the project's folder dropped silently by `claude -p` and the desktop app until approved interactively, see ADR005; Claude Code 2.1.302, 2026-10-17: imports inside the project loaded without approval by a fresh `claude -p` session in a clone of the T031 branch, in a folder never approved)
- Supersedes: ADR005

## Context

ADR005 imported vierbein from a sibling checkout, outside the project's folder. On 2026-10-17 that had three costs: a one-time interactive approval per folder, which `claude -p` and the Claude desktop app skip silently when it's missing (the desktop app doesn't offer it); git worktrees and cloud sessions running without the working agreements; and a change in vierbein changing how the agent works here without a commit here. Imports inside the project's folder need no approval. vierbein has no packaged form (plugin, template), and no mechanism to carry its updates into a project yet.

## Decision

The parts of vierbein this project needs (`agreements/`, `processes/`, `ticket-backends/`) are copied into `00-agentic/`, and `CLAUDE.md` imports them from there (`@00-agentic/…`). The copy is this project's: it changes with commits here. [`00-agentic/README.md`](../../00-agentic/README.md) gives its provenance (vierbein commit, date, files) and lists what was adapted since, so later updates of the layer can be carried over.

## Alternatives ruled out

- The sibling import (ADR005): no copy to sync, but the approval, no worktrees or cloud sessions, and an unpinned layer.
- `git subtree` or a submodule: a pinned version with history, but a ceremony at each update; a submodule also needs a recursive clone and doesn't come with a worktree by default.
- A Claude Code plugin: not examined; unclear whether a plugin can carry rules that are always in context like a `CLAUDE.md`.

## Consequences

- Every checkout of this repository (clone, worktree, cloud session) has the working agreements, with no setup and no approval.
- The layer is pinned by this repository's history: a change in vierbein reaches this project only when copied here, with a commit here.
- Updates of the layer are carried by hand until vierbein offers a mechanism; the provenance and the "Adapted" list are what make that diff possible.

## Revisit when

vierbein gets a mechanism to carry its updates into a project, or a packaged form (plugin, template).
