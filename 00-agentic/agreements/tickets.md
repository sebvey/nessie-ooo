# Tickets

The ticket workflow, whatever stores the tickets. Where tickets live and how each operation is done (filing, changing status, ticking a criterion, closing), the ticket reference and how it shows in branch names and commit subjects: the backend file the project imports in its `CLAUDE.md`. Statuses and the ticket template: `00-agentic/processes/tickets.md`.

- **Entry point**: a new idea, follow-up or problem found along the way becomes a ticket in Backlog, never a widening of the ticket in progress. The agent proposes it (a title and a few lines of why) and files it only once the developer agrees; a request from the developer to file one is that agreement.
  - In a discussion with the developer (refining, a question): propose it in the conversation, when it comes up.
  - While implementing on its own: note it at once in the current ticket's Notes (`Follow-up to propose: …`), and propose it in the finishing report, after the criteria.
- **Refining** a backlog ticket (scope, acceptance criteria) is a discussion: propose, and only set it to Ready once the user agrees.
- **What to work on**: only a Ready ticket, unless the user asks otherwise.
- **Starting**: check the working tree is clean, switch to an up-to-date `main` if needed, create the ticket's branch (named as the backend says), and set the ticket to In progress.
- **Working**: tick each acceptance criterion in the ticket as soon as it is met and verified, with how in a few words (`- [x] … (pipeline run, 2026-10-16)`); details go in the Outcome. Untick it if a later change breaks it. A criterion met only in part stays unticked, with what's missing.
- **Finishing**: check every acceptance criterion again (all ticked, or the gap stated), report them one by one in the message (criterion, state, how verified, what wasn't), and **wait for the user's validation**. Then close the ticket as done (Outcome filled), set the ticket's `proposed` ADRs to `accepted`, squash the branch into one commit (subject as the backend says) rebased on `main`, and fast-forward `main`.
- **Never delete a ticket**: an abandoned one is closed with an Outcome saying why.
- **Small work without a ticket** (a fix, an ADR amendment, a few lines asked for directly): on a branch `X666-<object>` (`X666-amend-a001`: the ticket-like ID says there is no ticket), committed there, reported, and merged into `main` (fast-forward) only after the developer's explicit validation. Nothing is committed directly on `main`.
- **Commit only your own files**: stage the paths you created or changed, never a whole folder that may hold the developer's untracked files.
- **References**: name tickets by their reference in tickets, commits, branches, docs and ADRs. **Never in code or config** (comments, task descriptions, console output): tickets are a separate concern and will leave the repo. Write the reason itself instead ("dbt-core 1.11.12 rejects sqlparse 0.6", not "see" a ticket); a link to an upstream issue is fine.
