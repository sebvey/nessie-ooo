# T021 `NESSIE_BRANCH=<branch> mise exec` doesn't target another branch

`CLAUDE.md` says: to target another branch, `NESSIE_BRANCH=<branch> mise exec -- ...`. It doesn't work when `mise.local.toml` sets `NESSIE_BRANCH`: mise overrides the shell's value (checked on 2026-10-16, `NESSIE_BRANCH=x mise exec -- sh -c 'echo $NESSIE_BRANCH'` prints the value from `mise.local.toml`). What works: `mise exec -- env NESSIE_BRANCH=<branch> <command>`. Fix the instruction, and check `docs/project/working-on-a-branch.md` and the tasks for the same assumption.

Area: agentic

## Acceptance criteria

- [x] `CLAUDE.md` gives the form that works, `mise exec -- env NESSIE_BRANCH=<branch> <command>`, checked by running it with `NESSIE_BRANCH` set in `mise.local.toml`. (`echo` run, 2026-10-16)
- [x] `00-agentic/agreements/boundaries.md` says that a one-command value goes after `mise exec --`, since mise overrides the shell's environment with its own config. (reread)
- [x] `docs/project/working-on-a-branch.md` and the mise tasks are checked for the same assumption, and fixed if needed. (doc: one-command form added; `dbt-inspect`: prefix inside the task's shell, works, simulated with `sh -c`, 2026-10-16)

## Outcome

Done on 2026-10-16.

- `CLAUDE.md`: one-command branch override is now `mise exec -- env NESSIE_BRANCH=<branch> <command>`, with why the prefix form fails. The wrong form had survived two moves of that line (T015 and the principle/application split) without being run.
- `00-agentic/agreements/boundaries.md`: a one-command value goes after the tool that loads the environment.
- `docs/project/working-on-a-branch.md`: the one-command form, next to the `mise.local.toml` way.
- Checked: with `NESSIE_BRANCH` in `mise.local.toml`, the prefix form prints the local value and the `env` form prints the override. `dbt-inspect` sets the variable inside its own shell, after mise, so it works.
- Not verified: `dbt-inspect` itself was not run (simulated with `mise exec -- sh -c 'NESSIE_BRANCH=… sh -c …'`); behaviour with a `.env` file or without the variable in `mise.local.toml` was not tested.
