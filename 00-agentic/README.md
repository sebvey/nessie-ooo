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
