# T021 `NESSIE_BRANCH=<branch> mise exec` doesn't target another branch

`CLAUDE.md` says: to target another branch, `NESSIE_BRANCH=<branch> mise exec -- ...`. It doesn't work when `mise.local.toml` sets `NESSIE_BRANCH`: mise overrides the shell's value (checked on 2026-10-16, `NESSIE_BRANCH=x mise exec -- sh -c 'echo $NESSIE_BRANCH'` prints the value from `mise.local.toml`). What works: `mise exec -- env NESSIE_BRANCH=<branch> <command>`. Fix the instruction, and check `docs/project/working-on-a-branch.md` and the tasks for the same assumption.

Area: agentic

## Acceptance criteria

- [ ] `CLAUDE.md` gives the form that works, `mise exec -- env NESSIE_BRANCH=<branch> <command>`, checked by running it with `NESSIE_BRANCH` set in `mise.local.toml`.
- [ ] `00-agentic/agreements/boundaries.md` says that a one-command value goes after `mise exec --`, since mise overrides the shell's environment with its own config.
- [ ] `docs/project/working-on-a-branch.md` and the mise tasks are checked for the same assumption, and fixed if needed.

## Outcome
