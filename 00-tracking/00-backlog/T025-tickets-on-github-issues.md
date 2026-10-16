# T025 Move tickets to GitHub Issues

Tickets are Markdown files in `00-tracking/`, kept there temporarily until they move to GitHub or similar (A001, T014). The repo is on GitHub (`sebvey/nessie-ooo`, private, personal account), so GitHub Issues is the natural target. Decide how the ticket workflow maps onto GitHub, migrate the existing tickets, and update the agentic layer accordingly.

Area: agentic

## Notes

Analysis, 2026-10-16. Basis: quick look (repo state and `gh` checked, GitHub docs read for the plan limits; nothing tested: no issue created, no Project, no auto-close). It builds on an earlier exploration done for another project (GitHub docs read on 2026-09-29), whose main objections (code on GitLab, client data outside the EU) don't apply here.

### Facts checked (2026-10-16)

- Repo `sebvey/nessie-ooo`: private, personal account (not an organization), issues and projects enabled, **0 issues and 0 PRs** so far, default labels only.
- `gh` 2.102.0, authenticated as `sebvey` with scopes `repo`, `read:org`, `gist`, `admin:public_key`: enough for issues; **not for Projects** (`gh project list` asks for `read:project`; writing needs `project`, via `gh auth refresh -s project`, the developer's setup).
- No GitHub MCP server configured (no `.mcp.json`).
- Ticket IDs T001 to T024 are all taken, none missing.
- 10 files in `docs/` and `00-agentic/` cite ticket IDs (T007 most, 7 times).
- GitHub offer (docs, 2026-10-16): issue dependencies ("blocked by", "blocking") and sub-issues are available on Free, `gh issue view --json blockedBy,blocking` reads them. Issue types and issue fields are organization-level only: not available on a personal account. Earlier exploration (2026-09-29): custom autolink references are Pro-only for private repos; Projects and issues have no Free restriction on private repos. Edit history of an issue body is capped at 100 entries (changelog 2026-07-02).

### Mapping

| Today | On GitHub | Comment |
|---|---|---|
| `T<nnn>` ID, highest plus one | issue number `#<n>`, assigned by GitHub | Solves the ticket half of T016 (parallel-safe numbering); ADR IDs keep the problem. Numbers are shared with PRs. |
| Folder = status | open/closed plus labels, or a Projects Status field | See "Status" below. |
| `03-done/` with Outcome | closed as "completed"; abandoned = closed as "not planned" | GitHub's close reason covers "finished or abandoned" natively. |
| `Area: agentic` line | label `area:agentic` | Issue types would fit better but need an organization. |
| Acceptance criteria checkboxes | task list in the issue body | Rendered and checkable in the UI; the agent ticks them by rewriting the body (`gh issue edit --body-file`). |
| Outcome section | section in the body, filled at closing | Keeps the ticket readable in one place; a closing comment can link the commit. |
| Notes | body section, or comments for findings along the way | |
| Ticket ID in branch, commit | branch `T025-…` or `25-…`, commit `T025 <title>` or `#25 <title>` | `#25` autolinks in commits and closes the issue on push to `main` with `Closes #25`; `T025` doesn't autolink (custom autolinks are Pro). |

### Keep the numbers: T<n> = #<n>

The repo has no issue and no PR yet. Creating the 24 tickets as issues in ID order (done ones closed right after creation) would give issue `#n` for ticket `Tn`. Existing references in docs, ADRs and commits stay valid with one line of mapping ("ticket T<nnn> is issue #<nnn>"), with no rewriting. This only holds if nothing else creates an issue or a PR before the migration, and if creation is sequential (a failed creation shifts every number after it).

### Status

Three open states to tell apart (backlog, ready, in progress). Two options:

- **Labels** (`ready`, `in-progress`; backlog = open with neither): works with today's token and `gh issue`, no setup. Labels aren't exclusive: the agent keeps them consistent by discipline, which is how folders work today anyway.
- **Projects** (a board with a single-select Status): a real status and a board, built-in workflows (auto-add from the repo, closed -> Done). Costs: the `project` scope, the project lives at account level and not in the repo, and `gh project item-edit` needs project, field and option IDs (more steps for each status change).

Leaning (arbitrary, to discuss): labels now, a Project only when a board is wanted; A001 already lists "a board becomes useful" as a trigger.

### Agent access

- `gh` CLI: already authenticated through mise, writes bodies from files (`--body-file`), no new infra. Read-only commands (`gh issue view`, `gh issue list`) could be pre-approved in `.claude/settings.json`; writes would keep asking.
- GitHub MCP server (`github/github-mcp-server`, official): typed tools, but one more server to configure, and its tools take context. Not needed to start.

Leaning: `gh`.

### What we lose or what changes

- Tickets leave git: a status change is no longer in the same squashed commit as the code; offline work on tickets stops; the history of a ticket is GitHub's (body edits capped at 100).
- Every ticket action becomes a network call with side effects: filing, ticking a criterion, closing. The agent asks for each one unless pre-approved.
- Whole-body rewrites: if the developer edits an issue in the UI while the agent rewrites the body, one of the edits is lost. Re-read before writing.
- Bookkeeping commits on `main` (filing a ticket, moving it to ready) disappear: a simplification.
- The developer's untracked notes in `00-tracking/` (if any) have to be looked at before the folder is removed.

### Work this ticket implies

- Choose status model, ID convention in branches and commits, where the Outcome goes; write an `A` ADR superseding A001.
- Create labels; migrate T001 to T024 in order (script with `gh issue create --body-file`, then `gh issue close --reason completed|not planned`), check `#n = Tn`.
- Update `00-agentic/agreements/tickets.md`, `00-agentic/processes/tickets.md`, `00-agentic/layer.md`, `00-agentic/infra.md`, `CLAUDE.md`, `00-tracking/README.md`; remove `00-tracking/` once migrated (git history keeps the files); add the T-to-# mapping line where tickets are cited.
- Narrow T016 to ADR IDs.

### Open questions

- Are the tickets meant to stay private? (The repo is private; issues follow its visibility.)
- Keep the `T` prefix in branch names and commits, or switch to `#n`?
- Labels or a Project for the status?
