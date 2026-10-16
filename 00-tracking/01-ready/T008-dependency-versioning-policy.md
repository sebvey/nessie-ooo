# T008 Dependency versioning policy

T007 raised the question of how to write version specifiers in `pyproject.toml` (`>=` or `~=`, how many components) and how to upgrade. Today the floors are inconsistent: `pyarrow>=17.0` and `numpy>=2.0` claim compatibility nobody tested (locked: 24.0.0 and 2.4.0). The Nessie client (`src/nessie_demo/nessie.py`) may become its own package ([T005](../00-backlog/T005-refactor-python-package.md)), so the policy must also cover a library.

## Acceptance criteria

- [ ] `docs/project/dependency-policy.md` describes the policy for an application (this repo) and for a library, and the upgrade procedure; it's linked from `docs/README.md` and `CLAUDE.md`.
- [ ] Every floor in `pyproject.toml` (dependencies and the `explore` group) equals the locked version; no upper bound except where the policy allows one.
- [ ] `uv.lock` keeps the same package versions (only the recorded specifiers change).
- [ ] End-to-end check passes: `stack-reset`, `stack-up`, `pipeline --no-pause` merges, `pipeline --bad --no-pause` doesn't and leaves `main` unchanged.

## Notes

- Agreed on 2026-10-16: the lock is the source of truth for the application; `>=` floors, no `~=`; upper bounds only for an observed incompatibility; raise the floors to the tested (locked) versions.
- Example of what upper bounds cost: in T007, `dbt-core` 1.11.12 declared `sqlparse<0.6` and blocked the `sqlparse` security fix until dbt-core 1.11.14.

## Outcome
