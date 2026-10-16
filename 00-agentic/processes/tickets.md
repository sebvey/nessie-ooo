# Ticket process

What a ticket holds and what each status takes, whatever stores the tickets. When to take one and how to deliver it is the workflow, in [`agreements/tickets.md`](../agreements/tickets.md). Where tickets live and how to file, move and close them: the backend the project imports (local Markdown files: [`ticket-backends/local.md`](../ticket-backends/local.md)).

## Statuses

| Status | What it takes to be here |
|---|---|
| Backlog | Nothing: a title and a few lines are enough. Every new ticket starts here. |
| Ready | A clear goal and **acceptance criteria**. Implementation details are optional. |
| In progress | Work has started. Each acceptance criterion is ticked when it is verified. |
| Done | Finished or abandoned: every criterion ticked (or the gap stated in the Outcome), and the Outcome added (what changed, where, anything left aside, and what wasn't verified), or an Outcome saying why it was dropped. |

Never delete a ticket: an abandoned one goes to Done with an Outcome saying why.

## Ticket template

A title, then these sections, in the form the backend stores them (a file, an issue body):

```markdown
<Why: the problem or the goal, in a few lines.>

<Area: agentic   (a ticket on the agentic layer only, see "Area" below)>

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

A ticket on the agentic layer (`00-agentic/`: rules, processes, agent infra) carries an `Area: agentic` line under its first paragraph. Tickets on the layer and on the project share one backend; the line lets them be filtered, and becomes a label in a backend that has labels.
