# Agent setup reference

What the coding agent runs on and with in this project. Facts dated 2026-10-16, the agentic layer and tickets sections 2026-10-17. The agentic layer itself (working agreements, processes, ticket backends) comes from vierbein, a separate repository; this page is this project's side of it.

## Agentic layer (`00-agentic/`)

`CLAUDE.md` imports the agreements and the ticket backend from [`00-agentic/`](../../00-agentic/README.md), this project's copy of vierbein (decision: [ADR006](../adr/ADR006-vierbein-copied-into-the-repository.md), which superseded the sibling import of [ADR005](../adr/ADR005-vierbein-imported-from-a-sibling-folder.md)).

- **No setup**: the imports are inside the project's folder, so Claude Code loads them in every session, `claude -p` and the Claude desktop app included, with no checkout of vierbein and no external-import approval.
- **The copy is this project's**: it changes with commits here. A change in vierbein reaches this project only when copied here. `00-agentic/README.md` gives the vierbein commit it comes from and lists what was adapted since.
- **Git worktrees and clones** get the working agreements like the main checkout.

## Tickets (GitHub)

Tickets are issues of `sebvey/nessie-ooo`, with their status in GitHub Project 3 (`nessie-ooo`, private), as the [GitHub backend](../../00-agentic/ticket-backends/github.md) says; its one-time setup is in [`github-setup.md`](../../00-agentic/ticket-backends/github-setup.md) (decision: [ADR007](../adr/ADR007-tickets-move-to-github-issues.md)). Ticket `T<nnn>` from before the move (2026-10-17) is issue `#<nnn>`; the seven IDs that left with the layer (T015, T016, T021, T025 to T028) are placeholder issues, closed as not planned and out of the Project.

- **`gh`** (2.102.0 on 2026-10-17), run through `mise exec` for the workspace's credentials, with the `project` scope on top of `repo` (`gh auth refresh -s project`, the developer's setup).
- Every `gh` command works from any checkout, worktrees included: tickets are no longer local files.

## Delivery (pull requests)

Every change reaches `main` through a pull request, squash-merged by GitHub, as the [ticket loop](../../00-agentic/agreements/tickets.md) and the [GitHub backend](../../00-agentic/ticket-backends/github.md) say (decision: [ADR008](../adr/ADR008-work-delivered-by-pull-requests.md)). Facts dated 2026-10-18.

- **A ticket opens its draft pull request when it starts**, linked by `Closes #<n>`: the GitHub Project moves the issue to `In Progress`, and to `Done` at the merge. An analysis ticket (label `type:analysis`) has no pull request: its analysis report is a comment on the issue ([ADR009](../adr/ADR009-analysis-tickets-deliver-a-report-on-the-issue.md)).
- **The developer merges** in the web UI by default; the agent never offers to, and merges only when asked.
- **`main` is protected** by a ruleset with no bypass, admins included: neither the developer nor the agent, which uses the developer's `gh` token and SSH key, can push to it, force-push or delete it. The repository is public, which GitHub Free requires for a ruleset. Setup: [`github-setup.md`](../../00-agentic/ticket-backends/github-setup.md), steps 5 and 6.
- **Commit subjects on `main`**: the pull request's title and number (`… (#34)`) from #30 on; earlier subjects carry the ticket's number (`… (#29)`) or `X666`.

## Claude Code

The agent is Claude Code (CLI 2.1.281 on the developer's machine, also used from the Claude desktop app). It reads `CLAUDE.md` and its `@` imports at the start of each session.

## Permissions (`.claude/settings.json`)

Committed in the repo, where Claude Code reads it. It pre-approves read-only commands, so the agent doesn't ask for them; everything else still asks, unless the session runs in a mode that skips prompts.

| Family | Examples | Why pre-approved |
|---|---|---|
| Git, read-only, through mise | `mise exec -- git status`, `log`, `diff`, `show`, `grep`, `ls-files` | Inspecting the repo; `mise exec` gives git the workspace identity |
| Environment | `printenv`, `mise env` | Checking which variables are set. They may print secret values: the developer's global rule is to list names only (`mise env \| cut -d= -f1`) |
| Stack, read-only | `docker compose ps`, `config`, `logs`, `aws s3 ls`, `mise run branches` | Checking the local stack without changing it |
| Tickets and pull requests, read-only, through mise | `mise exec -- gh issue view`, `gh issue list`, `gh pr view`, `gh pr list`, `gh pr checks`, `gh project item-list`, `gh project field-list` | Reading tickets, their status and their pull requests; creating or editing an issue or a pull request still asks |
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
