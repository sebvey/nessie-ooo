# T016 Parallel-safe numbering for ADRs and tickets

An ADR's ID is the highest existing one in its series plus one (`00-agentic/processes/adr.md`), and the ADR is drafted on the ticket branch. Two agents working in parallel, each on its own branch or worktree, would both pick the same next ID (`ADR004`, `A004`) and only find out when the second branch is rebased on `main`. Ticket IDs (`T<nnn>`) follow the same rule and have the same problem. Think through a numbering that holds when several agents write in parallel.

Area: agentic

## Notes

- Leads, not examined yet:
  - Reserve the ID on `main` before starting (a commit that adds the draft ADR or ticket), so the second agent sees it.
  - Draft without a number (`ADR-draft-<slug>.md`) and assign the ID when the branch is squashed onto `main`; references in the ticket and docs must then be renamed at that point.
  - IDs that can't collide (date or timestamp based, short random suffix), at the cost of readability and order.
  - Renumber on rebase: detect the clash when rebasing and take the next free ID.
- Same question for tickets created in parallel, e.g. two sessions each adding a backlog ticket.
- Whatever is chosen, the rule goes in `00-agentic/processes/adr.md` and `00-agentic/processes/tickets.md`, and may be worth an `A` ADR.
