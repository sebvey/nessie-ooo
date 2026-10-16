# Agentic layer ADRs

Decisions on how we work with the agent: rules, processes, agent infra. Same process as the project ADRs ([`processes/adr.md`](../processes/adr.md)), own series: `A001`, `A002`…

## Records

| ADR | Decision | Status |
|---|---|---|
| [A001](A001-tickets-as-markdown-in-the-repo.md) | Tickets are Markdown files in the repo, until they move to a ticket tool | superseded by A004 |
| [A002](A002-repo-over-agent-memory.md) | The repo, not the agent's memory, is the source of truth | accepted |
| [A003](A003-working-agreements-imported-into-claude-md.md) | Working agreements live in `00-agentic/agreements/` and are imported into `CLAUDE.md` | accepted |
| [A004](A004-tickets-as-local-unversioned-markdown.md) | Tickets are local Markdown files, not versioned, until they move to a ticket tool (supersedes A001) | accepted |
