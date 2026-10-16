# The layer

The components of the agentic layer and how they fit. The working agreements themselves are in [`agreements/`](agreements/); this page explains them.

## Instruction files

- **`CLAUDE.md`** at the root, loaded by Claude Code at every session. It holds the project facts (what the repo is, where to read, language, running things) and imports the agent rules from `00-agentic/agreements/` with `@` lines. Moving the layer out of the repo means replacing those imports (by a plugin or a shared config), not rewriting the project part.
- **`agreements/`**: the working agreements, short, imperative, always in context. Only what the agent must apply without being asked. Named "agreements", not "rules", for two reasons: they come out of a discussion and the developer validates them, and some bind the developer too (who owns the setup, who validates). The name also avoids confusion with Claude Code's own `.claude/rules/` mechanism.
- **`processes/`**: reference material (templates, statuses, lifecycle), read when a rule points to it. Kept out of the imports to keep the context small.
- **Outside the repo**: the developer's global `CLAUDE.md` and the organization's instructions also apply ([`infra.md`](infra.md)).

## The ticket loop

Tickets are local files, ignored by git: the loop moves and edits them, and only the work itself is committed.

1. An idea or a problem becomes a ticket in `00-tracking/00-backlog/`, never a widening of the ticket in progress.
2. Refining (goal, acceptance criteria) is a discussion with the developer, who decides when it moves to `01-ready/`.
3. The agent starts a ready ticket on a branch named after it and moves it to `02-in-progress/`.
4. It ticks each criterion in the ticket as soon as it's verified, then reports them one by one (state, how verified, what wasn't) and waits for the developer's validation.
5. On validation: ticket to `03-done/` with its Outcome; the work goes in one squashed commit `T<nnn> <title>` on `main`, fast-forward. Pushing is the developer's.

Small work without a ticket follows the same discipline, lighter: an `X666-<object>` branch, merged into `main` only after the developer's explicit validation.

Rules: [`agreements/tickets.md`](agreements/tickets.md). Format: [`processes/tickets.md`](processes/tickets.md).

## Decisions

Decisions that pass three tests (real alternatives, costly to reverse or bound to be re-opened, outlives its ticket) get an ADR. Two series, one process: project decisions in `docs/adr/`, decisions on this layer in [`adr/`](adr/README.md). An ADR is proposed in the ticket that takes the decision and accepted when the developer validates it; a change of substance supersedes it, a change of form amends it.

Rules: [`agreements/decisions.md`](agreements/decisions.md). Process: [`processes/adr.md`](processes/adr.md).

## Honesty

Every recommendation, decision or finding states its basis (investigated, quick look, arbitrary), every report lists what wasn't verified, and every ticket's Outcome has a `Not verified` line. The ADR `Basis` field is the same idea. The point is a slot that must be filled: leaving it out shows at review.

Rules: [`agreements/honesty.md`](agreements/honesty.md).

## Memory

The agent has a memory across sessions. It holds only the developer's personal working preferences; anything about the project or this layer goes in the repo, which wins when they disagree.

Rule: [`agreements/memory.md`](agreements/memory.md).
