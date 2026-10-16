# ADR001 `uv.lock` is the source of truth; `pyproject.toml` has `>=` floors equal to the locked versions and no preventive upper bound

- Status: accepted
- Date: 2026-10-16
- Tickets: T007, T008
- Basis: investigated

## Context

This repo is an application: nobody installs it as a dependency, `uv sync` installs what `uv.lock` says. Before T008 the specifiers in `pyproject.toml` were inconsistent (`pyarrow>=17.0` and `numpy>=2.0` while 24.0.0 and 2.4.0 were locked and tested). The dependencies follow different version schemes: `pyarrow` ships a major at every release, `fsspec` and `s3fs` use calendar versions, `pyiceberg` is 0.x. In T007, `dbt-core` 1.11.12 declared `sqlparse<0.6` and blocked a `sqlparse` security fix until dbt-core 1.11.14 lifted that cap.

## Decision

- `uv.lock` is committed and is the source of truth for what runs.
- Each direct dependency in `pyproject.toml` (dependencies and groups) has a `>=` floor equal to its locked version, copied in full. Every deliberate upgrade raises the floor in the same commit.
- No upper bound, except for an observed incompatibility, with a comment naming the ticket. `[build-system]` keeps its bound because the lock doesn't cover the build backend.
- Upgrades go one package at a time (`uv lock --upgrade-package`), procedure in [dependency-policy.md](../project/dependency-policy.md).

## Alternatives ruled out

- `~=` (compatible release): an upper bound whose meaning depends on the number of components, and which assumes SemVer. It would block every `pyarrow` upgrade and stop `fsspec` at the turn of the year.
- Floors only where the code needs them (the library rule): floors drift below what was tested and say nothing true.
- Preventive upper bounds: the lock already prevents surprise upgrades; caps only block fixes, as T007 showed.
- `uv lock --upgrade` in bulk: too many changes at once to tell which one broke something.

## Consequences

- Floors are mechanical to maintain and always match a tested state.
- A floor isn't a compatibility promise for older versions: nobody tests them, and nobody needs to for an application.
- Installing without the lock (`pip install .`) gets the latest versions, untested together. Not a supported path.

## Revisit when

- Part of the repo becomes a library installed by others: it follows the library rules of the policy instead.
- A dependency breaks on a new release often enough that a cap becomes cheaper than fixing.
