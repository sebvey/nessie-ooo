# T014 Keep ticket references out of code

Tickets are referenced in code, e.g. `tasks.toml`: "Container images are not audited (T011)". Ticketing is temporarily kept as Markdown files in the repo, but it's a separate concern from the code, and it will later move to GitHub or similar. Tickets should not be mentioned in code.

## Notes

To do:
- Remove the existing mentions. On 2026-10-16, a search in `*.py`, `*.toml`, `*.yml`, `*.sql` finds one: `tasks.toml` (`audit-python` description).
- Make the rule clear and well structured in the Claude files (`CLAUDE.md`).

To settle when refining:
- Where the line is: code and config only, or docs too? Today `CLAUDE.md` asks to name tickets by ID in docs, `docs/project/` cites tickets (T001, T005, T007, T011), and ADRs have a `Tickets:` field.
- Rules that ask for a ticket in code comments, to rewrite: `docs/project/dependency-policy.md` (an upper bound "with a comment naming the ticket"; `--ignore-vuln` "with a comment naming the ticket that accepted it"). What replaces the ticket in such a comment: the reason itself?
- ADR001 says the same ("with a comment naming the ticket"). It's accepted, so it can't be edited: changing the rule means a new ADR that supersedes it.
- What happens to the ticket references in docs and ADRs when the tickets move out of the repo.

## Outcome
