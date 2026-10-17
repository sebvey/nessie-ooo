# Decisions

ADRs follow [`processes/adr.md`](../processes/adr.md), in the layer's folder, in the project's series, whose folder and IDs are named in the project's `CLAUDE.md`.

- Before changing something an ADR covers, read it. If the work would contradict an accepted ADR, stop and ask.
- When a ticket takes a decision that passes the three tests of the process, draft the ADR (status `proposed`) on the ticket branch and say so in the report.
- An ADR stands on its own: it states, dated, the few facts that would change the decision if they changed. Detailed evidence (test tables, logs, procedures) stays in a doc or ticket, cited, never copied.
- When an event happens that an ADR's "Revisit when" names (a move, a version change, a new backend), say so in the report and propose the review.
- An accepted ADR changes only through the process: a new ADR when the substance changes, an `Amended` edit for form only. Propose either, never apply it without the developer's validation.
