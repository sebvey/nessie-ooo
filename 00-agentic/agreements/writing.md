# Writing

- Everything in the repo is in **English**: code, comments, docstrings, console output, docs, tickets, and commit messages. `CLAUDE.md` names the project's exceptions. The conversation with the developer, reports and summaries included, is in the developer's language.
- Markdown: no hard wrapping. One line per paragraph or list item; let the editor wrap.
- **Docs say how things are now**: a doc, an agreement, `CLAUDE.md` describe the current state, not a former way, an option ruled out or a forecast. Why it is so and what was ruled out go in an ADR; what changed, in git and the tickets. A reason is written as it holds today.
- **Names don't collide**: one term per concept. When a tool comes in (GitHub, Claude Code, a CLI), check its vocabulary against ours; on a collision, say so at once and propose a rename or a qualifier. Settled ones:
  - the way a ticket goes from an idea to done is the *ticket loop*, never "workflow" or "the loop" alone: tools use both words for their own things (GitHub's Project workflows and GitHub Actions workflows, Claude Code's `/loop`);
  - a *project* is the repository that adopts the layer; GitHub's board is a *GitHub Project*.
