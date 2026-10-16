# Dependencies

What the layer relies on, whatever the project. Facts checked on 2026-10-16 with Claude Code 2.1.281. A project's own agent setup (permissions, MCP servers, tool managers) belongs in the project's docs, not here.

## Claude Code

- **`@` imports in `CLAUDE.md`**, loaded at the start of every session: the agreements and the ticket backend reach the agent this way ([A003](adr/A003-working-agreements-imported-into-claude-md.md)). A fresh `claude -p` session quoted imported rules without reading any file.
- **Subdirectory `CLAUDE.md` loaded on demand**, when the agent works on a file in that subdirectory: `00-agentic/CLAUDE.md`, the instructions for evolving the layer, reaches the agent this way ([A006](adr/A006-evolving-the-layer-in-its-own-claude-md.md)). A project that only uses the layer doesn't need it.

Another agent tool would need its own way to load the agreements; nothing in them is specific to Claude Code beyond these two mechanisms.

## Git

The workflow assumes a git repository with a `main` branch, one branch per ticket, a squashed commit per ticket, and fast-forward merges into `main`. Pushing is the developer's.

## Nothing else is required

No MCP server, tool manager or network access is required by the layer. A ticket backend may need a tool (a CLI, a token): its backend file says so.

## Instructions from outside the repo

User-level and organization-level instructions apply on top of the project's `CLAUDE.md`; the layer doesn't replace them and doesn't copy them.
