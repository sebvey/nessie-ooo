# T014 Keep ticket references out of code

Tickets are referenced in code, e.g. `tasks.toml`: "Container images are not audited (T011)". Ticketing is temporarily kept as Markdown files in the repo, but it's a separate concern from the code, and it will later move to GitHub or similar. Tickets should not be mentioned in code.

## Acceptance criteria

- [x] No ticket ID in code or config (`src/`, `dbt/`, `notebooks/`, `*.toml`, `*.yml`, `docker-compose.yml`): comments, task descriptions, console output. Checked with a search for `T0nn` outside `00-tracking/`, `docs/` and the Markdown files at the root.
- [x] `CLAUDE.md` states the rule in the tickets workflow: where ticket IDs belong (tickets, commits, branches, docs, ADRs) and where they don't (code and config), and what to write instead.
- [x] The rules that asked for a ticket in a code comment are rewritten: `docs/project/dependency-policy.md` (upper bound, `--ignore-vuln`).
- [x] ADR001 no longer asks for a ticket in a comment: the annotation detail moves to `docs/project/dependency-policy.md`, and ADR001 is amended in place with an `Amended` line.
- [x] `docs/adr/README.md` tells substance (new ADR) from form (amendment in place), says an ADR holds the decision and not the procedure, and its template has the optional `Amended` line; the ADR rule in `CLAUDE.md` matches. (Added during review, 2026-10-16.)

## Design (refined by the agent, the developer delegated it)

- **The line: code and config versus the rest.** Code and config must make sense on their own, whatever the ticket tool. Docs and ADRs may cite tickets: they record the project's history, and the IDs can be mapped when tickets move to GitHub. Commits and branches keep their ticket IDs (git metadata).
- **Instead of a ticket, the reason itself**: "dbt-core 1.11.12 rejects sqlparse 0.6" rather than "see T007". A link to an upstream issue (`duckdb-iceberg#1145`) is allowed: it's external and stable.
- **Amend ADR001 rather than supersede it** (changed during review): a first draft added ADR004 to supersede ADR001 for one sentence, which the developer rejected as pollution. The sentence was a procedure detail that didn't belong in an ADR; the ADR rules now tell substance from form.

## Notes

- On 2026-10-16, a search in `*.py`, `*.toml`, `*.yml`, `*.sql` finds one mention: `tasks.toml` (`audit-python` description).
- References in docs when tickets leave the repo: out of scope, to handle with the migration.

## Outcome

Done on 2026-10-16.

- `tasks.toml`: the `audit-python` description no longer names a ticket. A search for `T0nn` in code and config (outside `00-tracking/`, `docs/` and Markdown files) finds nothing.
- `CLAUDE.md`: the "References" rule says where ticket IDs belong (tickets, commits, branches, docs, ADRs) and where they don't (code and config), and to write the reason instead; the ADR rule follows the new substance/form lifecycle.
- `docs/project/dependency-policy.md`: an upper bound's comment states the incompatibility, an ignored vulnerability's comment gives the reason.
- `docs/adr/README.md`: substance (new ADR) versus form (amendment in place with an `Amended` line, validated by the developer), "the decision, not the procedure", optional `Amended` line in the template. ADR001 amended accordingly; the ADR004 drafted first was dropped during review.
- Not verified: the search covers `T0nn` IDs only; a ticket mentioned another way in code (a filename, "see the backlog") would not show up.
