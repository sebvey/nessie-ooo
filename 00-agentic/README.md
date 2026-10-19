# Agentic layer (copy of vierbein)

How we work with the coding agent on this repository: working agreements, processes, ticket backends. `CLAUDE.md` imports the agreements and the ticket backend from here (decision: [ADR006](../docs/adr/ADR006-vierbein-copied-into-the-repository.md)). This project's side of the setup: [Agent setup](../docs/project/agent-setup.md).

This folder is a copy of vierbein, the agentic layer, a separate repository. The copy is this project's: change it here, with a commit here, like any other file of the repository, and list each change under "Adapted" below, so a later update of the layer can be carried over.

## Provenance

- Source: vierbein, commit `c88e379` (`main`, 2026-10-17).
- Copied on 2026-10-17, verbatim (`git archive c88e379 agreements processes ticket-backends`).
- Files copied:
  - `agreements/`: `boundaries.md`, `decisions.md`, `honesty.md`, `memory.md`, `tickets.md`, `writing.md`
  - `processes/`: `adr.md`, `tickets.md`
  - `ticket-backends/`: `local.md`, `github.md`, `github-setup.md`
- Not copied: vierbein's `CLAUDE.md`, `README.md`, `docs/`, `scripts/`.

## Adapted

Changes made here since the copy, one line each (date, file, what and why).

- Nothing at the copy.
- 2026-10-18, `agreements/writing.md`: carried over from vierbein at `959f77d` (file now identical to it): "Docs say how things are now", and the conversation with the developer in the developer's language.
- 2026-10-18, `agreements/tickets.md`, `processes/adr.md`, `ticket-backends/github-setup.md`: carried over from vierbein at `959f77d` (files now identical to it): tickets live outside the code, instead of a forecast that they will leave the repo; the Project workflows marked "pull request" described as unused by the backend. `ticket-backends/github.md` not carried over: its "at the push" leaves who pushes to the project, and here the developer pushes.
- 2026-10-18, `agreements/tickets.md`, `ticket-backends/github.md`, `ticket-backends/github-setup.md`, `processes/adr.md`: work delivered by pull requests instead of a local squash and fast-forward (decision: [ADR008](../docs/adr/ADR008-work-delivered-by-pull-requests.md)). A draft pull request linked by `Closes #<n>` at the start, which sets `In Progress`; GitHub's squash merge, by the developer by default; the PR title without a number, GitHub appending the PR's; `proposed` ADRs `accepted` when the pull request is ready for review; abandoning a ticket that has an open pull request; setup steps for a public repository, the merge settings and a ruleset on `main` with no bypass; the Project workflows on pull requests now used. vierbein's versions of these files still describe the local squash and fast-forward.
- 2026-10-19, `agreements/tickets.md`, `processes/tickets.md`, `ticket-backends/github.md`, `ticket-backends/github-setup.md`, `ticket-backends/local.md`: analysis tickets (decision: [ADR009](../docs/adr/ADR009-analysis-tickets-deliver-a-report-on-the-issue.md)). Marked `Type: analysis` (label `type:analysis` on GitHub), no branch or pull request, a report kept with the ticket and an Outcome with proposed tickets decided at the validation; on GitHub, `In Progress` set by hand at the start. Not in vierbein.
