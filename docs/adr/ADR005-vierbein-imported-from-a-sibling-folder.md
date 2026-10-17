# ADR005 The agentic layer, vierbein, is imported from a sibling folder

- Status: superseded by ADR006
- Date: 2026-10-17
- Tickets: none (small work on branch `X666-vierbein-moved-out`)
- Basis: investigated (Claude Code 2.1.281, on a side-by-side copy in a scratch folder: `@../vierbein/…` imports were dropped by `claude -p` until external imports were approved in an interactive session, then loaded, with tickets placed at this project's root and the layer's links resolved; behaviour documented in Claude Code's memory docs and [anthropics/claude-code#79046](https://github.com/anthropics/claude-code/issues/79046))

## Context

The agentic layer was developed in this repo, in `00-agentic/`, and was extracted to its own repository, vierbein, on 2026-10-17, to be worked on as a project. This project still needs the layer's working agreements and ticket backend in every session. One developer works on both, on one machine, and both are still changing often. An `@` import outside the project's folder is loaded only after a one-time interactive approval per folder, given with the `claude` CLI in a terminal; without it, `claude -p` and the Claude desktop app drop it silently, and the desktop app doesn't offer the approval (checked by the developer on 2026-10-17).

## Decision

`CLAUDE.md` imports the layer from a sibling checkout: `@../vierbein/agreements/…` and `@../vierbein/ticket-backends/local.md`. The setup (checkout next to this repository, the approval, no git worktrees) is in [`agent-setup.md`](../project/agent-setup.md).

## Alternatives ruled out

- A copy of the layer in this repo: complete on its own, but synced by hand while the layer changes daily.
- `git subtree` (or a submodule): a pinned version with history, but a ceremony at each update of the layer, for one developer.
- A Claude Code plugin: not examined; unclear whether a plugin can carry rules that are always in context like a `CLAUDE.md`.

## Consequences

- No copy: a change in vierbein applies here at the next session.
- A clone of this repo without vierbein next to it, a git worktree, or a folder where external imports weren't approved runs the agent without the working agreements, and `claude -p` gives no warning.
- The layer's version isn't pinned: a change there can change how the agent works here without a commit here.

## Revisit when

Someone else works on this repo, sessions run in worktrees or in the cloud, or vierbein gets a packaged form (plugin, template).
