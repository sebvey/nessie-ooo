# Ticket process

How tickets are kept, in `00-tracking/`. When to take one and how to deliver it is the workflow, in [`agreements/tickets.md`](../agreements/tickets.md).

One Markdown file per ticket. The folder a ticket sits in is its status.

| Folder | Status | What it takes to be here |
|---|---|---|
| `00-backlog/` | Idea or draft | Nothing: a title and a few lines are enough. Every new ticket starts here. |
| `01-ready/` | Ready to start | A clear goal and **acceptance criteria**. Implementation details are optional. |
| `02-in-progress/` | Being worked on | Work has started. |
| `03-done/` | Finished or abandoned | Criteria ticked and an **Outcome** section, or an Outcome saying why it was dropped. |

## Changing a status

- Move the file with `git mv`; it keeps its name.
- While in `02-in-progress/`: tick each acceptance criterion when it is verified (workflow in [`agreements/tickets.md`](../agreements/tickets.md)).
- To `03-done/`: every criterion ticked (or the gap stated in the Outcome), and the Outcome added (what changed, where, anything left aside, and what wasn't verified).
- Never delete a ticket: an abandoned one goes to `03-done/` with an Outcome saying why.

## Ticket file

Name: `T<nnn>-<short-kebab-case-title>.md`, e.g. `T004-refactor-dbt-project.md`.

ID: the highest existing one, across all folders, plus one. Since tickets are never deleted, an ID is never reused. Other tickets, commits and docs refer to a ticket by its ID: `T004`.

```markdown
# T<nnn> <Title>

<Why: the problem or the goal, in a few lines.>

<Area: agentic   (a ticket on the agentic layer only, see "Area" below)>

## Acceptance criteria

- [ ] <Observable result, checkable without reading the code>

## Notes

<Context, findings, leads, links. Optional.>

## Outcome

<Filled when the ticket moves to 03-done/.>

- Not verified: <what, or "nothing">
```

In `00-backlog/` a ticket may skip the acceptance criteria. From `01-ready/` on they're required.

## Area

A ticket on the agentic layer (`00-agentic/`: rules, processes, agent infra) carries an `Area: agentic` line under its first paragraph. Tickets stay in one `00-tracking/`; the line lets them be filtered, and becomes a label when tickets move to GitHub.
