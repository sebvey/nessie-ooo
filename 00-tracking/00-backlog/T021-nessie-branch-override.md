# T021 `NESSIE_BRANCH=<branch> mise exec` doesn't target another branch

`CLAUDE.md` says: to target another branch, `NESSIE_BRANCH=<branch> mise exec -- ...`. It doesn't work when `mise.local.toml` sets `NESSIE_BRANCH`: mise overrides the shell's value (checked on 2026-10-16, `NESSIE_BRANCH=x mise exec -- sh -c 'echo $NESSIE_BRANCH'` prints the value from `mise.local.toml`). What works: `mise exec -- env NESSIE_BRANCH=<branch> <command>`. Fix the instruction, and check `docs/project/working-on-a-branch.md` and the tasks for the same assumption.

Area: agentic
