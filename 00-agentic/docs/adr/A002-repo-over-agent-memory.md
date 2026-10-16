# A002 The repo, not the agent's memory, is the source of truth

- Status: accepted
- Date: 2026-10-16
- Tickets: T015
- Basis: investigated (the rule predates the ADR; its reasons, reconstructed in T015, are known properties of the memory: per developer and per machine, outside git, unreviewed)

## Context

Claude Code keeps a memory across sessions, in files on the developer's machine. It's convenient to remember things there, but nobody else sees it, it isn't versioned, and it isn't reviewed.

## Decision

Anything about the project or the agentic layer (architecture, decisions, conventions, status) goes in the repo: docs, ADRs, `CLAUDE.md`, `00-agentic/`, tickets. The memory only holds the developer's personal working preferences. When memory and repo disagree, the repo wins and the memory is fixed or deleted. Rule: [`agreements/memory.md`](../../agreements/memory.md).

## Alternatives ruled out

- Let the agent remember project facts in its memory: invisible to others, unreviewed, goes stale silently.
- No memory at all: loses the personal preferences that make sessions smoother and don't belong in the repo.

## Consequences

- Every session starts from what the repo says; a new developer or agent gets the same context.
- Writing things down in the repo costs a commit, sometimes a ticket.

## Revisit when

The memory becomes shared and reviewable (a team memory under version control), or the layer moves out of the repo and needs another home for its facts.
