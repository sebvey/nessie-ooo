# T008 Dependency versioning policy

T007 raised the question of how to write version specifiers in `pyproject.toml` (`>=` or `~=`, how many components) and how to upgrade. Today the floors are inconsistent: `pyarrow>=17.0` and `numpy>=2.0` claim compatibility nobody tested (locked: 24.0.0 and 2.4.0). The Nessie client (`src/nessie_demo/nessie.py`) may become its own package ([T005](../00-backlog/T005-refactor-python-package.md)), so the policy must also cover a library.

## Acceptance criteria

- [x] `docs/project/dependency-policy.md` describes the policy for an application (this repo) and for a library, and the upgrade procedure; it's linked from `docs/README.md` and `CLAUDE.md`.
- [x] Every floor in `pyproject.toml` (dependencies and the `explore` group) equals the locked version; no upper bound except where the policy allows one.
- [x] `uv.lock` keeps the same package versions (only the recorded specifiers change).
- [x] End-to-end check passes: `stack-reset`, `stack-up`, `pipeline --no-pause` merges, `pipeline --bad --no-pause` doesn't and leaves `main` unchanged.

## Notes

- Agreed on 2026-10-16: the lock is the source of truth for the application; `>=` floors, no `~=`; upper bounds only for an observed incompatibility; raise the floors to the tested (locked) versions.
- Example of what upper bounds cost: in T007, `dbt-core` 1.11.12 declared `sqlparse<0.6` and blocked the `sqlparse` security fix until dbt-core 1.11.14.

## Outcome

Done on 2026-10-16.

- `docs/project/dependency-policy.md`: rules for both cases (`>=` floors only, no `~=`, upper bounds only for an observed incompatibility), application rules (floors equal to the locked versions and moving with the lock, `[build-system]` as the only bounded exception, no version of its own, no dependency cooldown), library rules (justified floors tested with `--resolution lowest-direct`, SemVer from 0.x, changelog), upgrade procedure (before each talk, on alert, or for a needed feature), vulnerability check. Linked from `docs/README.md` and `CLAUDE.md`.
- `pyproject.toml`: floors raised to the locked versions (`pyarrow>=24.0.0`, `numpy>=2.4.0`, `requests>=2.34.2`, `marimo[sql]>=0.25.1`…). `uv.lock` only records the new specifiers: no package version changed.
- End-to-end check passed after a `stack-reset`.
- Follow-ups: T009 (ADR folder; the cooldown choice is arbitrary and must be recorded as such), T010 (`mise run audit`), T005 (yanked `numpy==2.4.0`, `uv_build` cap).
