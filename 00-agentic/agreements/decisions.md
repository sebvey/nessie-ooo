# Decisions

Two ADR series, one process (`00-agentic/processes/adr.md`): project decisions in `docs/adr/` (`ADR001`…), decisions on the agentic layer in `00-agentic/adr/` (`A001`…).

- Before changing something an ADR covers, read it. If the work would contradict an accepted ADR, stop and ask.
- When a ticket takes a decision that passes the three tests of the process, draft the ADR (status `proposed`) on the ticket branch, in the right series, and say so in the report.
- An ADR stands on its own: it states, dated, the few facts that would change the decision if they changed. Detailed evidence (test tables, logs, procedures) stays in a doc or ticket, cited, never copied.
- An accepted ADR changes only through the process: a new ADR when the substance changes, an `Amended` edit for form only. Propose either, never apply it without the developer's validation.
