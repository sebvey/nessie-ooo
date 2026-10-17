# Ticket backend: GitHub Issues and a GitHub Project

How the operations of the ticket loop ([`agreements/tickets.md`](../agreements/tickets.md)) are done when tickets are GitHub issues, with their status in a GitHub Project ("the Project" below; "the project" is the repository that adopts the layer). A project uses this backend by importing this file in its `CLAUDE.md`, which names the GitHub Project's owner (a login or an organization) and number. The setup is done once, by the developer: [`github-setup.md`](github-setup.md).

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

The Project workflows move some statuses on their own (setup: "Item added to project", "Item closed", "Auto-close issue"): adding an issue to the Project sets it to `Backlog`, closing it sets `Done`, and setting `Done` closes it. So **nobody sets `Done` by hand**: it would close the issue before the work is on `main`. Done follows from closing the issue.

## Reference

- ID: the issue number, `#<n>`, given by GitHub at creation. Issues are never deleted, so a number is never reused.
- Branch: `<n>-<short-kebab-case-title>` (`42-refactor-dbt-project`).
- Commit subject: `<Title> (#<n>)` (`Refactor the dbt project (#42)`), with `Closes #<n>` alone on a line of the body. `(#<n>)` goes at the end: git drops lines starting with `#` from a message written in an editor.

## Operations

`<owner>` and `<number>` are the GitHub Project's owner and number named in the project's `CLAUDE.md`. Write bodies to a temporary file outside the repository, never in the working tree.

| Operation | How |
|---|---|
| File a ticket | `gh issue create --title "<Title>" --body-file <file>`, then `gh project item-add <number> --owner <owner> --url <issue-url>`. The Project sets it to `Backlog`. |
| Read | `gh issue view <n>`; its status: `gh issue view <n> --json projectItems`. |
| List by status | `gh project item-list <number> --owner <owner> -L 500 --format json --jq '.items[] \| select(.status == "Ready") \| {number: .content.number, title}'`. Filter with `--jq`, not `--query`: the search behind `--query` lags a few seconds behind a status change. The default limit is 30 items. |
| Change status (Backlog, Ready, In Progress) | `gh project item-edit <number> --owner <owner> --url <issue-url> --field Status --value "<status>"`. Ready: the agent sets it once the developer agreed in the conversation, or the developer moves the card. Never `Done`. |
| Tick or untick a criterion | Read the body (`gh issue view <n> --json body --jq .body > <file>`), edit the checkbox, write it back (`gh issue edit <n> --body-file <file>`). |
| Add a note, a follow-up to propose | Same as ticking, in the `Notes` section. |
| Close as done | Fill the `Outcome` section in the body before the squash. The squashed commit carries `Closes #<n>`; the issue closes, and the Project sets `Done`, when that commit reaches the default branch on GitHub, at the developer's push. Until then the ticket stays In Progress. |
| Close as abandoned | Only after the developer's validation: fill the `Outcome` section, then `gh issue close <n> --reason "not planned"`. The Project sets `Done`. |

Never delete an issue (`gh issue delete`): an abandoned ticket is closed as not planned.
