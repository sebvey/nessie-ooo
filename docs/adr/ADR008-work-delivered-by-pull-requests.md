# ADR008 Work is delivered by pull requests, squash-merged into a `main` protected with no bypass

- Status: accepted
- Date: 2026-10-18
- Tickets: #30, #33
- Basis: investigated (`gh` 2.102.0 on vierbein-sandbox, 2026-10-18: draft pull requests linked by `Closes #<n>`, squash merges with each message setting, a pull request closed unmerged, and this ruleset applied with pushes from an admin account; results in #30's Notes. `gh api` on `sebvey/nessie-ooo`, 2026-10-18: rulesets and branch protection refused on the private repository)

## Context

Until 2026-10-18 the agent squashed a ticket's branch locally, rebased it on `main` and fast-forwarded `main`, and the developer pushed. Nothing on GitHub stopped a direct push to `main`, and the agent pushes with the developer's token, which is an admin of the repository. One developer works on the repository, with the agent, sometimes from git worktrees or several sessions at once. On GitHub Free, rulesets and branch protection are refused on a private repository. On 2026-10-18 a secret scan of the whole history and a read of every issue found nothing that needed to stay private, and the developer made the repository public (#33). The repository has no CI yet (#32).

## Decision

Every change reaches `main` through a pull request: a ticket's draft pull request is opened when the ticket starts, linked by `Closes #<n>`, and GitHub squash-merges it, the PR title and body becoming the commit. The developer merges by default; the agent merges only when asked. The repository is public, and a ruleset on `main` with no bypass, admins included, refuses direct pushes, force pushes and deletion, and requires a pull request (no approval) and squash as the only merge method. The Project workflows move the issue to `In Progress` when the pull request is linked and to `Done` when it is merged. The procedure is in [`github-setup.md`](../../00-agentic/ticket-backends/github-setup.md) (steps 4 to 6) and the loop in [`agreements/tickets.md`](../../00-agentic/agreements/tickets.md).

## Alternatives ruled out

- Keep the local squash and fast-forward: no protection of `main`, no visible work in progress, and a merge done by whoever pushes.
- A ruleset with a bypass for admins: the agent, with the developer's token, could still push to `main`.
- Stay private and protect `main` by convention only: nothing enforces it.
- GitHub Pro to protect a private repository: a cost for no need, since nothing in the repository is confidential.
- Required approvals: a developer working alone can't approve their own pull request.
- Merge commits or rebase merges: one commit per change on `main` keeps its history readable, and the PR body carries `Closes #<n>` and the description.

## Consequences

- Nobody, the agent included, can push to `main` outside a pull request; a one-line fix goes through one too.
- The repository, its history and its issues are public.
- The number in a commit subject on `main` is the pull request's from now on; older subjects carry the ticket's.
- Each ticket opens a pull request early, with an empty first commit, since GitHub refuses a pull request with no commit ahead of `main`.
- Required status checks can be added to the ruleset once a CI exists (#32).

## Revisit when

A second developer joins (approvals become possible), the repository must become private again, the CI lands (#32), or GitHub changes what Free allows on private repositories.
