# Setting up the GitHub ticket backend

What the developer sets up once, before a project imports [`github.md`](github.md). Read when setting up, not imported. Checked on 2026-10-17 with `gh` 2.102.0, on a personal account with GitHub Free.

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

Menu `…`, Workflows. The backend relies on three of the Project workflows enabled on a new Project: "Item added to project" (sets `Backlog`), "Item closed" (sets `Done`) and "Auto-close issue" (closes the issue when its Status is set to `Done`). Leave them on. Leave "Auto-add to project" off: the backend adds each issue itself.

All the Project workflows of a new Project, as shown in the web UI on 2026-10-17 (after step 3). A ticket loop based on pull requests will depend on the ones marked "pull request".

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

## 5. Labels for areas (if any)

For each area the project names: `gh label create area:<name>`.

## 6. The project's `CLAUDE.md`

It imports `github.md` as its ticket backend and names the GitHub Project:

```markdown
Ticket backend: GitHub, GitHub Project <number> of <owner>:

@<path-to-the-layer>/ticket-backends/github.md
```
