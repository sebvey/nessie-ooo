# ADR009 An analysis ticket delivers a report on its issue and proposed tickets, never a change to the repository

- Status: accepted
- Date: 2026-10-19
- Tickets: #44
- Basis: quick look (the path #20 took on 2026-10-19: report first written in `docs/concepts/` through a pull request, then moved to an issue comment, pull request closed unmerged; the other places weighed in discussion, not tried)

## Context

The ticket loop assumed every ticket changes the repository: a branch, a draft pull request that sets In Progress, a merge that sets Done. On 2026-10-19 #20, an investigation (why PyIceberg ignored DuckDB's delete files), went through that path: its report became a page in `docs/concepts/`, which the developer judged counterproductive, since a finding about two tool versions is not how the project is now. The report moved to an issue comment, the pull request was closed unmerged and the issue closed by hand. The analysis also led to two tickets (#42, #44), proposed in conversation.

## Decision

- A ticket whose result is a finding is an analysis ticket, marked `Type: analysis` (label `type:analysis` on GitHub).
- It has no branch, no pull request, no commit. Its deliverable is an analysis report kept with the ticket (an issue comment on GitHub) and an Outcome with the finding and a "Proposed tickets" section.
- At the validation, the developer decides each proposed ticket (filed in Backlog, merged into a ticket, dropped); the analysis closes once every decision is noted. On GitHub the agent sets In Progress by hand, since no pull request does it.

## Alternatives ruled out

- The report in `docs/`: a doc says how things are now, a finding is dated evidence; and a pull request for it ties a finding to a code review.
- GitHub Discussions: one more place to follow, with no status in the GitHub Project.
- The repository's wiki: a second documentation space next to `docs/`.
- A gist: tied to a personal account, not to the project.
- Filing proposed tickets as soon as the analysis finds them: the analysis may still be discussed; filing at the validation keeps the Backlog to what the developer agreed.

## Consequences

- An analysis leaves no trace in git: its analysis report lives in the ticket backend, outside the code. A finding that changes how the project is goes into the docs or an ADR through the ticket it proposes.
- GitHub's In Progress for an analysis depends on the agent setting it.
- The layer's local backend keeps the report in the ticket file (a `## Analysis report` section), with no history.

## Revisit when

A report needs a review in the repository (a finding that others must approve), or the ticket backend changes.
