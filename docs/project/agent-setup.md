# Agent setup

What the coding agent runs on and with in this project. Facts dated 2026-10-16, the vierbein section 2026-10-17. The agentic layer itself (working agreements, processes, ticket backends) is vierbein, a separate repository; this page is this project's side of it.

## vierbein

`CLAUDE.md` imports the layer's agreements and ticket backend from a sibling folder: `@../vierbein/…` (decision: [ADR005](../adr/ADR005-vierbein-imported-from-a-sibling-folder.md)).

- **Checkout**: vierbein must be cloned next to this repository, as `../vierbein/`. Without it, the agent works without the working agreements.
- **One-time approval**: these imports are outside the project's folder, so Claude Code loads them only after the developer approved external imports for this folder, once, in an interactive `claude` session in a terminal (a dialog at start). Before that, `claude -p` drops them silently, and so does the Claude desktop app, which doesn't offer the approval (checked on 2026-10-17); after it, both load them. The approval is stored per folder in the user's Claude Code config.
- **Git worktrees** of this repository don't see `../vierbein/` at the right place, and are new folders for the approval: a session in a worktree has no working agreements. Work in the main checkout.

## Claude Code

The agent is Claude Code (CLI 2.1.281 on the developer's machine, also used from the Claude desktop app). It reads `CLAUDE.md` and its `@` imports at the start of each session.

## Permissions (`.claude/settings.json`)

Committed in the repo, where Claude Code reads it. It pre-approves read-only commands, so the agent doesn't ask for them; everything else still asks, unless the session runs in a mode that skips prompts.

| Family | Examples | Why pre-approved |
|---|---|---|
| Git, read-only, through mise | `mise exec -- git status`, `log`, `diff`, `show`, `grep`, `ls-files` | Inspecting the repo; `mise exec` gives git the workspace identity |
| Environment | `printenv`, `mise env` | Checking which variables are set. They may print secret values: the developer's global rule is to list names only (`mise env \| cut -d= -f1`) |
| Stack, read-only | `docker compose ps`, `config`, `logs`, `aws s3 ls`, `mise run branches` | Checking the local stack without changing it |
| MCP, read-only | `tavily_search`, `tavily_extract`, Context7 docs, browser `find` and `get_page_text`, `read_terminal` | Looking things up and reading pages or the developer's terminal |

Writes (commits, file edits, stack resets, network calls with side effects) are not pre-approved.

## MCP servers

None is configured in the repo (no `.mcp.json`): they come from the developer's Claude Code and desktop app setup. The permissions above refer to:

- **Context7**: current library documentation.
- **Tavily**: web search and page extraction.
- **Claude Browser** (desktop app): a browser pane.
- **Terminal** (desktop app): reading the developer's terminal.

A session without them still works; the permissions above simply go unused.

## mise

Every tool runs through mise (`mise run <task>`, `mise exec -- <command>`): it provides the pinned tools, the env vars from `mise.toml` and `mise.local.toml`, and the workspace's git identity and credentials. The agent's shell doesn't have them otherwise. Setup (trusting the config, writing `mise.local.toml`, starting Docker) is the developer's job; the rule is in `CLAUDE.md`.

## Outside the repo

The agent also follows instructions that are not in the repo and are not copied here:

- **The developer's global `CLAUDE.md`** (`~/.claude/CLAUDE.md`): personal working environment, notably running git and dev tools through `mise exec`.
- **The organization's instructions** (Ippon Technologies), set by the administrator in Claude: posture, writing style, language. They take precedence over user preferences.

Someone else working on the repo with an agent gets the repo's rules, but not these two: the `mise exec` habit, at least, has to come from their own setup.
