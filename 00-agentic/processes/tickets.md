# Ticket process

What a ticket holds and what each status takes, whatever stores the tickets. When to take one and how to deliver it is the ticket loop, in [`agreements/tickets.md`](../agreements/tickets.md). Where tickets live and how to file, move and close them: the backend the project imports (local Markdown files: [`ticket-backends/local.md`](../ticket-backends/local.md)).

## Statuses

| Status | What it takes to be here |
|---|---|
| Backlog | Nothing: a title and a few lines are enough. Every new ticket starts here. |
| Ready | A clear goal and **acceptance criteria**. Implementation details are optional. |
| In Progress | Work has started. Each acceptance criterion is ticked when it is verified. |
| Done | Finished or abandoned: every criterion ticked (or the gap stated in the Outcome), and the Outcome added (what changed, where, anything left aside, and what wasn't verified), or an Outcome saying why it was dropped. An analysis also has a decision noted for each proposed ticket. |

Never delete a ticket: an abandoned one goes to Done with an Outcome saying why.

## Ticket template

A title, then these sections, in the form the backend stores them (a file, an issue body):

```markdown
<Why: the problem or the goal, in a few lines.>

## Acceptance criteria

- [ ] <Observable result, checkable without reading the code>

## Notes

<Context, findings, leads, links. Optional.>

## Outcome

<Filled when the ticket goes to Done.>

- Not verified: <what, or "nothing">
```

In Backlog a ticket may skip the acceptance criteria. From Ready on they're required.

## Area

A project may tag tickets with an `Area: <name>` line under the first paragraph, to filter them (a label in a backend that has labels). The areas, if any, are named in the project's `CLAUDE.md`.

## Analysis tickets

An analysis ticket investigates a question (a bug's cause, an option worth taking, a tool's behaviour): its result is a finding, not a change to the repository. It is marked with a `Type: analysis` line under the first paragraph (a label in a backend that has labels), set when it is filed or, at the latest, when it is refined. A ticket without that line changes the repository.

Its deliverable is an **analysis report**, kept with the ticket (where: the backend), and its Outcome, which holds:

```markdown
## Outcome

<The finding in a few lines, and its basis: investigated, quick look or arbitrary.> Analysis report: <link or place>.

### Proposed tickets

- <Title>: <why, in a few lines>. → <decision, noted at validation: filed <ID> / merged into <ID> / dropped: why>

- Not verified: <what, or "nothing">
```

When the analysis leads nowhere, "Proposed tickets" says so in one line. A proposed ticket is filed in Backlog only, refined when it is picked.
