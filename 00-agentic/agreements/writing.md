# Writing

- Everything in the repo is in **English**: code, comments, docstrings, console output, docs, tickets, and commit messages. `CLAUDE.md` names the project's exceptions.
- Markdown: no hard wrapping. One line per paragraph or list item; let the editor wrap.
- **Names don't collide**: one term per concept. When a tool comes in (GitHub, Claude Code, a CLI), check its vocabulary against ours; on a collision, say so at once and propose a rename or a qualifier. Settled ones:
  - the way a ticket goes from an idea to done is the *ticket loop*, never "workflow" or "the loop" alone: tools use both words for their own things (GitHub's Project workflows and GitHub Actions workflows, Claude Code's `/loop`);
  - a *project* is the repository that adopts the layer; GitHub's board is a *GitHub Project*.
