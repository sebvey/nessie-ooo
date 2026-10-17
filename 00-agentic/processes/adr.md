# ADR process

One file per important decision: what was decided, why, what was ruled out, and how solid the basis is. A doc says how things are now; an ADR says why they are that way.

A project keeps one series: its folder and ID prefix are named in the project's `CLAUDE.md` (for example `docs/adr/`, `ADR001`, `ADR002`…).

Few ADRs, each worth reading: a choice that doesn't pass the three tests below goes elsewhere.

## What deserves an ADR

A decision that passes all three tests:

1. **Real alternatives**: at least one other option was weighed, or deliberately not examined (then the ADR says so).
2. **Costly to reverse, or bound to be re-opened**: without the ADR, someone would ask "why not X?" or redo the analysis.
3. **Outlives its ticket**: it constrains future work, not just the change at hand.

What goes elsewhere:

| Content | Where |
|---|---|
| Work to do | a ticket |
| How things are now | a doc |
| Working agreements (developer and agent) | the agreements imported by `CLAUDE.md` |
| Project conventions (language, running things) | `CLAUDE.md` |
| A local implementation choice | a code comment |

**One decision per ADR.** A ticket that takes several choices produces an ADR only for those that pass the tests.

**It stands on its own.** The facts the decision rests on are written in it, dated: the few that would change the decision if they changed, the ones "Revisit when" watches. Detailed evidence (test tables, logs, procedures) stays in a doc or ticket and is cited, never copied: it can disappear without weakening the ADR. A ticket is never the only place the evidence lives, since tickets will leave the repo.

**The decision, not the procedure.** An ADR holds the decision and its reasons. Whatever can change without questioning the decision (commands, formats, annotation conventions) goes in the doc, and the ADR links to it.

## Lifecycle

- **Naming**: `<prefix><nnn>-<short-kebab-case-title>.md` in the series' folder (`ADR001-…`). The ID is the highest existing one in the series plus one, never reused.
- **Written on the branch of the ticket that takes the decision**, with status `proposed`. It becomes `accepted` when the developer validates the ticket, in the ticket's squashed commit.
- **Index**: each series' folder has a `README.md` listing its ADRs (ID, decision, status). Add the row when drafting the ADR, and update its status there whenever the ADR's status changes.
- **Substance or form.** Test: could someone who agreed with the old version disagree with the new one?
  - **Substance** (the decision, an alternative or the basis changes): a new ADR that supersedes the old one. The two are linked both ways: the new one gets `Supersedes: <old ID>`, the old one's status becomes `superseded by <new ID>`, and it stays. Never deleted.
  - **Form** (wording, a dead link, a procedure detail that doesn't touch the decision): edit in place and add an `Amended` line to the header, with the date and what changed.
  - **Mechanical fix** (a link or path updated after a file moved, a typo): edit in place, no `Amended` line; it changes nothing for the reader.
  - An amendment is proposed and validated like a ticket: never applied alone.
- **Dated facts** (versions, issue status) are true on the ADR's date. Re-check them before relying on them; if they changed the decision, write a new ADR.

## Template

One screen at most: the self-standing facts are a few lines, not the evidence.

```markdown
# <ID> <The decision, as a sentence>

- Status: proposed | accepted | superseded by <ID>
- Date: <YYYY-MM-DD>
- Tickets: <ticket references>
- Basis: investigated (<how: test run, source read>) | quick look (<what was checked, what wasn't>) | arbitrary (<what wasn't examined>)
- Supersedes: <ID> (only when it replaces an earlier ADR)
- Amended: <YYYY-MM-DD>: <what changed> (optional, one line per amendment)

## Context

<The problem and the constraints, with dated facts.>

## Decision

<What we do.>

## Alternatives ruled out

- <Option>: <why not>.

## Consequences

<What it costs, what it makes easier, what it forbids.>

## Revisit when

<The event or fact that would re-open the decision.>
```

