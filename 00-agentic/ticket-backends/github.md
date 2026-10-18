# Ticket backend: GitHub Issues, a GitHub Project and pull requests

How the operations of the ticket loop ([`agreements/tickets.md`](../agreements/tickets.md)) are done when tickets are GitHub issues, with their status in a GitHub Project ("the Project" below; "the project" is the repository that adopts the layer), and work is delivered by pull requests squash-merged into a protected `main`. A project uses this backend by importing this file in its `CLAUDE.md`, which names the GitHub Project's owner (a login or an organization) and number. The setup is done once, by the developer: [`github-setup.md`](github-setup.md).

## Where tickets live

- One issue per ticket in the project's GitHub repository: the title is the ticket's title, the body holds the template's sections (from the "why" paragraph to `## Outcome`). The ticket's history is the issue's.
- The status is the `Status` field of the issue's item in the Project. The issue's open or closed state follows it: open while Backlog, Ready or In Progress; closed when Done.
- An area, if the project has any, is a label `area:<name>` (`--label` on `gh issue create` or `gh issue edit`), instead of the `Area:` line.
- One project per repository: issue numbers are the repository's, so there is no ticket prefix.
- All commands use `gh`, from any checkout of the repository, worktrees included. Each one is a network call that changes what others see: re-read an issue before rewriting it, since the developer may have edited it in the web UI.

| Status | In the Project | Issue |
|---|---|---|
| Backlog | `Backlog` | open |
| Ready | `Ready` | open |
| In Progress | `In Progress` | open |
| Done (finished) | `Done` | closed as completed |
| Done (abandoned) | `Done` | closed as not planned |

The Project workflows move some statuses on their own (setup: "Item added to project", "Pull request linked to issue", "Pull request merged", "Item closed", "Auto-close issue"): adding an issue to the Project sets it to `Backlog`, linking a pull request to it sets `In Progress`, merging that pull request or closing the issue sets `Done`, and setting `Done` closes it. So **nobody sets `In Progress` or `Done` by hand**: the draft pull request does the first, and setting `Done` would close the issue before the work is on `main`. Done follows from the merge, or from closing the issue.

## Reference

- ID: the issue number, `#<n>`, given by GitHub at creation. Issues are never deleted, so a number is never reused.
- Branch: `<n>-<short-kebab-case-title>` (`42-refactor-dbt-project`).
- Pull request: titled with the ticket's title, with no number (`Refactor the dbt project`); its body says what the change does and has `Closes #<n>` alone on a line, which links it to the issue and closes the issue at the merge. Small work without a ticket: branch `X666-<object>`, no `Closes` line.
- Commit on `main`: the squash merge makes one commit per pull request, its subject the PR title followed by GitHub's ` (#<PR number>)`, its message the PR body, with a `Co-authored-by` line that GitHub adds from the branch's commits. Issues and pull requests share one numbering, so the number in a subject is the pull request's; the issue is the one its `Closes` line names.
- Commits on the branch: any subject; the squash replaces them.

## Operations

`<owner>` and `<number>` are the GitHub Project's owner and number named in the project's `CLAUDE.md`; `<repo>` is the repository (`<owner>/<name>`), `<pr>` a pull request's number. Write bodies to a temporary file outside the repository, never in the working tree.

| Operation | How |
|---|---|
| File a ticket | `gh issue create --title "<Title>" --body-file <file>`, then `gh project item-add <number> --owner <owner> --url <issue-url>`. The Project sets it to `Backlog`. |
| Read | `gh issue view <n>`; its status: `gh issue view <n> --json projectItems`. |
| List by status | `gh project item-list <number> --owner <owner> -L 500 --format json --jq '.items[] \| select(.status == "Ready") \| {number: .content.number, title}'`. Filter with `--jq`, not `--query`: the search behind `--query` lags a few seconds behind a status change. The default limit is 30 items. |
| Change status (Backlog, Ready) | `gh project item-edit <number> --owner <owner> --url <issue-url> --field Status --value "<status>"`. Ready: the agent sets it once the developer agreed in the conversation, or the developer moves the card. Never `In Progress` (the draft pull request sets it) nor `Done`. |
| Start: open the draft pull request | On the ticket's branch: `git commit --allow-empty -m "Start <title>"` (GitHub refuses a pull request with no commit ahead of `main`), `git push -u origin <branch>`, then `gh pr create --draft --title "<Title>" --body-file <file>`, the body with `Closes #<n>`. The Project sets the issue to `In Progress` a few seconds later. |
| Mark ready for review | `gh pr ready <pr>`, once the Outcome is filled and the branch pushed. |
| Merge | The developer merges in the web UI, by default. The agent merges only when the developer asks: `gh api -X PUT repos/<repo>/pulls/<pr>/merge -f merge_method=squash`, which takes the repository's squash message (PR title and body). The branch is deleted after the merge (repository setting). |
| Tick or untick a criterion | Read the body (`gh issue view <n> --json body --jq .body > <file>`), edit the checkbox, write it back (`gh issue edit <n> --body-file <file>`). |
| Add a note, a follow-up to propose | Same as ticking, in the `Notes` section. |
| Close as done | Fill the `Outcome` section in the body before marking the pull request ready. At the merge, the PR body's `Closes #<n>` closes the issue as completed and the Project sets `Done`. Until then the ticket stays In Progress. |
| Close as abandoned | Only after the developer's validation: fill the `Outcome` section (why, with a link to the pull request if there is one). If a pull request is open, close it first, so none is left to merge by mistake: `gh pr close <pr> --comment "Abandoned, see #<n>" --delete-branch` (a closed pull request keeps its commits, and GitHub offers to restore the branch). Then `gh issue close <n> --reason "not planned"`. The Project sets `Done`. Closing a pull request unmerged leaves the issue's status as it is. |

Never delete an issue (`gh issue delete`): an abandoned ticket is closed as not planned.
