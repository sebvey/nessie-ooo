# T014 Keep ticket references out of code

Tickets are referenced in code, e.g. `tasks.toml`: "Container images are not audited (T011)". Ticketing is temporarily kept as Markdown files in the repo, but it's a separate concern from the code, and it will later move to GitHub or similar. Tickets should not be mentioned in code.

## Acceptance criteria

- [ ] No ticket ID in code or config (`src/`, `dbt/`, `notebooks/`, `*.toml`, `*.yml`, `docker-compose.yml`): comments, task descriptions, console output. Checked with a search for `T0nn` outside `00-tracking/`, `docs/` and the Markdown files at the root.
- [ ] `CLAUDE.md` states the rule in the tickets workflow: where ticket IDs belong (tickets, commits, branches, docs, ADRs) and where they don't (code and config), and what to write instead.
- [ ] The rules that asked for a ticket in a code comment are rewritten: `docs/project/dependency-policy.md` (upper bound, `--ignore-vuln`).
- [ ] ADR001 says the same, and an accepted ADR can't be edited: ADR004 supersedes it with the corrected rule, ADR001 gets `superseded by ADR004`, and the links to ADR001 point to ADR004.

## Design (refined by the agent, the developer delegated it)

- **The line: code and config versus the rest.** Code and config must make sense on their own, whatever the ticket tool. Docs and ADRs may cite tickets: they record the project's history, and the IDs can be mapped when tickets move to GitHub. Commits and branches keep their ticket IDs (git metadata).
- **Instead of a ticket, the reason itself**: "dbt-core 1.11.12 rejects sqlparse 0.6" rather than "see T007". A link to an upstream issue (`duckdb-iceberg#1145`) is allowed: it's external and stable.
- **ADR004 rather than an edit of ADR001**: the immutability rule of `docs/adr/README.md` applies, even for one sentence. It's also the first test of the supersede path.

## Notes

- On 2026-10-16, a search in `*.py`, `*.toml`, `*.yml`, `*.sql` finds one mention: `tasks.toml` (`audit-python` description).
- References in docs when tickets leave the repo: out of scope, to handle with the migration.

## Outcome
