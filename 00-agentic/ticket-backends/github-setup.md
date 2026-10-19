# Setting up the GitHub ticket backend

What the developer sets up once, before a project imports [`github.md`](github.md). Read when setting up, not imported. Checked on 2026-10-17 with `gh` 2.102.0, on a personal account with GitHub Free; the pull request steps (4 and 6) on 2026-10-18, on vierbein-sandbox.

## 1. `gh` with the `project` scope

The agent uses the `gh` CLI, authenticated for the repository. GitHub Projects need the `project` scope on top of `repo`:

```bash
gh auth refresh -s project
```

`gh auth status` lists `project` under the token scopes.

## 2. A GitHub Project linked to the repository

```bash
gh project create --owner <owner> --title "<title>"
gh project link <number> --owner <owner> --repo <owner>/<repo>
```

- `gh project create` prints the GitHub Project's number, which the project's `CLAUDE.md` names. A new GitHub Project is private.
- `gh project link` with `--owner "@me"` fails ("has different owner from '@me'"): pass the login.

## 3. The Status options (web UI)

`gh` can't edit the options of an existing field, so this step is in the web UI: the Project, menu `…`, Settings, field `Status`. A new Project has `Todo`, `In Progress`, `Done`. Rename `Todo` to `Backlog` and add `Ready`, in this order: `Backlog`, `Ready`, `In Progress`, `Done`. The names must match exactly: the backend passes them to `gh`.

Renaming `Todo` keeps it as the option the Project workflows point to: "Item added to project" then sets `Backlog`.

## 4. The Project workflows (web UI)

Menu `…`, Workflows. The backend relies on five of the Project workflows enabled on a new Project: "Item added to project" (sets `Backlog`), "Pull request linked to issue" (sets `In Progress` when a pull request's body links it with `Closes #<n>`, drafts included), "Pull request merged" (sets `Done`), "Item closed" (sets `Done`) and "Auto-close issue" (closes the issue when its Status is set to `Done`). Leave them on. Leave "Auto-add to project" off: the backend adds each issue itself.

All the Project workflows of a new Project, as shown in the web UI on 2026-10-17 (after step 3).

| Project workflow | Default | Trigger and action |
|---|---|---|
| Auto-add sub-issues to project | on | When an item in the project has sub-issues: add them to the project. No settings. |
| Auto-close issue | on | When Status is set to `Done`: close the issue. No close reason offered. |
| Item added to project | on | Set Status to `Todo`, which step 3 renames `Backlog`. |
| Item closed | on | Set Status to `Done`. |
| Pull request linked to issue | on | Set Status to `In Progress`. |
| Pull request merged | on | Set Status to `Done`. |
| Auto-add to project | off | When an item of a chosen repository matches a filter: add it to the project. The repository is preselected (not necessarily the linked one); filter empty. Limited to one such Project workflow on Free, five on Pro. |
| Auto-archive items | off | Archive items matching a filter (greyed example: `is:issue is:closed updated:<@today-2w`); with `updated:`, runs every 12 hours. |
| Code changes requested | off | When a pull request gets a review requesting changes: set Status (shown: `Ready`). |
| Code review approved | off | When a pull request is approved: set Status (shown: `Ready`). |
| Item reopened | off | When an issue or pull request is reopened: set Status (shown: `Ready`). |

The GitHub docs read on 2026-10-17 say only two Project workflows are enabled by default and don't name most of these: the web UI is the source. The values shown for disabled Project workflows may be placeholders.

## 5. Public repository

On GitHub Free, rulesets and branch protection are refused on a private repository (`gh api repos/<owner>/<repo>/rulesets`: 403, "Upgrade to GitHub Pro or make this repository public", 2026-10-18). Step 6 needs a public repository, or a paid plan. Before making a repository public, check what becomes visible: the whole git history (a secret scan of all refs, not only the current tree) and the issues.

```bash
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

## 6. Merge settings and the protection of `main`

Pull requests are squash-merged, with the PR title and body as the commit, and the branch deleted after the merge:

```bash
gh api -X PATCH repos/<owner>/<repo> -F allow_merge_commit=false -F allow_rebase_merge=false -F allow_squash_merge=true -F delete_branch_on_merge=true -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY
```

A ruleset on the default branch, with no bypass, admins included: the agent works with the developer's token, so a bypass for admins would let it push to `main`. It refuses deleting the branch, force pushes and direct pushes, and requires a linear history and a pull request, with no approval (a developer working alone can't approve their own pull request) and squash as the only merge method. Save this body to a file outside the repository:

```json
{
  "name": "main",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "required_linear_history"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": false,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": false,
      "allowed_merge_methods": ["squash"]
    }}
  ]
}
```

```bash
gh api -X POST repos/<owner>/<repo>/rulesets --input <file>
```

GitHub adds `require_extra_approval_for_unattributed_changes: true` to the `pull_request` rule on its own (meaning not examined; it blocked nothing in the test). The check: a direct push to `main` is refused (`GH013`, "Changes must be made through a pull request"), a force push too, and a pull request merges only by squash, once out of draft.

## 7. Labels

- Analysis tickets: `gh label create type:analysis --description "Analysis ticket: the deliverable is a report on the issue, no change to the repository"`.
- Areas, if any: for each area the project names, `gh label create area:<name>`.

## 8. The project's `CLAUDE.md`

It imports `github.md` as its ticket backend and names the GitHub Project:

```markdown
Ticket backend: GitHub, GitHub Project <number> of <owner>:

@<path-to-the-layer>/ticket-backends/github.md
```
