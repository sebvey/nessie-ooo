# The layer

The components of the agentic layer and how they fit. The working agreements themselves are in [`agreements/`](../agreements/); this page explains them.

## The layer as its own project

The layer adopts itself: its [`CLAUDE.md`](../CLAUDE.md) follows [`adopting.md`](adopting.md) like any project's. It imports the layer's agreements and the local ticket backend (prefix `t`, tickets in the layer's own `00-tracking/`), names its ADR series (`A001`… in [`adr/`](adr/README.md)), says how a change is checked, and adds the rules for evolving the layer (boundary test, self-contained parts, docs in sync, rules that change themselves).

While the layer sits inside a host project, two projects share one git repository, and the agent has two missions:

| Mission | Instructions | Loaded |
|---|---|---|
| Implementing the host project | the host's root `CLAUDE.md` and its `@` imports (the layer's agreements, one ticket backend) | at every session |
| Evolving the layer | the layer's `CLAUDE.md` and its imports (the same agreements, loaded once) | when Claude Code works on a file in the layer's folder |

The layer's `CLAUDE.md` has a "Coexistence" section for this period: a ticket belongs to the project whose files it changes, each project has its own ticket prefix and store.

What a project uses (`agreements/`, `processes/`, `ticket-backends/`) never points to what only serves adopting or evolving the layer (`CLAUDE.md`, `README.md`, `docs/`, `scripts/`).

**Moving out**: move the layer's folder to its own repository (with its history, e.g. `git subtree split`), drop the "Coexistence" section, and in the host replace the `@00-agentic/…` imports by the layer's final form (plugin, shared config, a copy). The host's `CLAUDE.md` keeps its project part as it is.

## Instruction files

- **`CLAUDE.md`** at the root, loaded by Claude Code at every session. It holds the project facts (what the repo is, where to read, the project's ADR series, language, running things) and imports the agreements and the ticket backend with `@` lines, without explaining the layer.
- **The layer's `CLAUDE.md`**: the layer as a project (its bindings, its checks) and the rules for evolving it, loaded on demand while the layer sits in a host (see "The layer as its own project").
- **`agreements/`**: the working agreements, short, imperative, always in context. Only what the agent must apply without being asked. Named "agreements", not "rules", for two reasons: they come out of a discussion and the developer validates them, and some bind the developer too (who owns the setup, who validates). The name also avoids confusion with Claude Code's own `.claude/rules/` mechanism.
- **`processes/`**: reference material (templates, statuses, lifecycle), read when a rule points to it. Kept out of the imports to keep the context small.
- **`ticket-backends/`**: one file per way of storing tickets (today only [`local.md`](../ticket-backends/local.md): Markdown files in the project's `00-tracking/`). Each says where tickets live, how to do each operation the workflow names, and the ticket reference format. A project imports exactly one, from the project part of its `CLAUDE.md`: that line is the plug point, and switching backend means changing it.
- **Outside the repo**: user-level and organization-level instructions also apply ([`dependencies.md`](dependencies.md)); a project's own agent setup is documented in the project.

## The ticket loop

The loop names statuses and operations; the backend imported by `CLAUDE.md` says how each is done. With the local backend, tickets are files ignored by git: the loop moves and edits them, and only the work itself is committed.

1. An idea or a problem becomes a ticket in Backlog, never a widening of the ticket in progress. The agent proposes it, in the conversation or in its finishing report; it is filed once the developer agrees.
2. Refining (goal, acceptance criteria) is a discussion with the developer, who decides when it is set to Ready.
3. The agent starts a ready ticket on a branch named after it and sets it to In progress.
4. It ticks each criterion in the ticket as soon as it's verified, then reports them one by one (state, how verified, what wasn't) and waits for the developer's validation.
5. On validation: the ticket is closed as done with its Outcome; the work goes in one squashed commit on `main`, its subject carrying the ticket reference, fast-forward. Pushing is the developer's.

Small work without a ticket follows the same discipline, lighter: an `X666-<object>` branch, merged into `main` only after the developer's explicit validation.

Rules: [`agreements/tickets.md`](../agreements/tickets.md). Format: [`processes/tickets.md`](../processes/tickets.md). Backend: [`ticket-backends/local.md`](../ticket-backends/local.md).

## Decisions

Decisions that pass three tests (real alternatives, costly to reverse or bound to be re-opened, outlives its ticket) get an ADR. A project has one series, named in its `CLAUDE.md` (here `docs/adr/`); this layer has its own, in [`adr/`](adr/README.md), described in [`CLAUDE.md`](../CLAUDE.md). An ADR is proposed in the ticket that takes the decision and accepted when the developer validates it; a change of substance supersedes it, a change of form amends it.

Rules: [`agreements/decisions.md`](../agreements/decisions.md). Process: [`processes/adr.md`](../processes/adr.md).

## Honesty

Every recommendation, decision or finding states its basis (investigated, quick look, arbitrary), every report lists what wasn't verified, and every ticket's Outcome has a `Not verified` line. The ADR `Basis` field is the same idea. The point is a slot that must be filled: leaving it out shows at review.

Rules: [`agreements/honesty.md`](../agreements/honesty.md).

## Memory

The agent has a memory across sessions. It holds only the developer's personal working preferences; anything about the project or this layer goes in the repo, which wins when they disagree.

Rule: [`agreements/memory.md`](../agreements/memory.md).
