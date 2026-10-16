# Dependency policy

How to write version specifiers in `pyproject.toml` and how to upgrade. Why: [ADR001](../adr/ADR001-lock-is-the-source-of-truth.md). The rules differ between an **application**, installed from its lock, and a **library**, installed by someone else's resolver. This repo is an application; the library rules are for a package extracted from it, such as a standalone Nessie client (T005).

## Rules for both

- **Floors with `>=`, nothing else.** No `~=`, no `==`, no upper bound by default.
- **`~=` is an upper bound in disguise**, and its meaning depends on how many components you write: `~=2.33` means `>=2.33, <3`, `~=2.33.0` means `>=2.33.0, <2.34`. It also assumes SemVer, which many dependencies don't follow:
  - `pyarrow` ships a major at every release (24, 25, 26): `~=24.0` blocks every upgrade.
  - `fsspec` and `s3fs` use calendar versions (2026.9.0): `~=2026.9` blocks at the turn of the year.
  - `pyiceberg` is 0.x: a minor may break, a major doesn't exist yet.
- **An upper bound only for an observed incompatibility**, with a comment naming the ticket, removed when the ticket is closed. A preventive cap blocks fixes for everyone downstream. In T007, `dbt-core` 1.11.12 declared `sqlparse<0.6` and blocked the `sqlparse` security fix until dbt-core 1.11.14 lifted the cap.
- **`requires-python`**: a floor, no cap (`>=3.13`).

## Application (this repo)

`uv.lock` is the source of truth: it's committed, and `uv sync` installs exactly what it says. The specifiers in `pyproject.toml` only document what the code was tested with.

- **Floor = the locked version** of each direct dependency (`dependencies` and the dependency groups), copied in full: `requests>=2.34.2`. It's the version the end-to-end check ran with. It's mechanical, and it's what `uv add` writes by default.
- **The floor moves with the lock**: every deliberate upgrade raises it to the new locked version, in the same commit.
- **Exception: `[build-system]`.** The build backend isn't in the lock, so it keeps the upper bound uv recommends for its own backend (`uv_build>=0.9.21,<0.10.0`).
- **The application has no version of its own.** `version = "0.1.0"` stays as it is: nobody installs the repo by version. A git tag marks a state worth coming back to, such as the one shown in a talk.
- **No dependency cooldown** (`[tool.uv] exclude-newer = "1 week"`, which ignores releases younger than the duration). An arbitrary choice, not investigated, open to challenge: [ADR002](../adr/ADR002-no-dependency-cooldown.md).

## Library (a package others install)

The library's lock only serves its own development: users never see it. The specifiers are all they get, so each floor must be true.

- **Floor = the oldest version the code needs**, for a reason you can name: an API used, a bug or security fix. The precision follows the reason: `MAJOR.minor` for a feature, the full version for a fix (`requests>=2.33.0` excludes PYSEC-2026-2275). For a 0.x dependency, `0.minor`.
- **Test both ends in CI**: the highest versions (`uv lock --upgrade`) and the floors (`uv lock --resolution lowest-direct`). An untested floor is a guess.
- **As few dependencies as possible**; optional features go in extras (`pip install nessie-client[async]`).
- **No upper bound, even on 0.x**, unless a release is known to break; then cap it and fix it fast, since every day under the cap pins your users.
- **No dependency on the application**: a Nessie client takes its configuration as arguments, not from `nessie_demo.settings`.
- **Its own version follows SemVer**, starting at 0.x while the API settles: a 0.x minor may break, and says so in the changelog. 1.0 once the API is stable; from then on, a breaking change is a major.
- **A changelog** with one entry per release, and the supported Python versions declared in `requires-python` and tested in CI.

## Upgrade procedure (application)

When: before each talk, on a vulnerability alert, or for a feature you need. Each wave of upgrades is a ticket.

1. See what's behind: `mise exec -- uv tree --depth 1 --outdated --all-groups`.
2. Upgrade one package at a time, never everything at once: `mise exec -- uv lock --upgrade-package <pkg>`. A transitive dependency can be upgraded the same way. To stay on a release line, name the version: `--upgrade-package dbt-core==1.11.16`.
3. Read what uv changed (`Updated`, `Added`, `Removed` lines). A new dependency or a major you didn't ask for is a reason to stop and choose.
4. Raise the floors in `pyproject.toml` to the new locked versions, then `mise exec -- uv lock` (no version may change).
5. Check for vulnerabilities (`mise run audit-python`, below), then run the end-to-end check from [`CLAUDE.md`](../../CLAUDE.md#running-things).

## Vulnerability check

**Scope: the Python dependencies only.** The container images the stack runs (Nessie, Nessie CLI, Postgres, Silo, mc) are not audited by anything in this repo: see T011.

```bash
mise run audit-python
```

The task exports `uv.lock` (every package, all dependency groups, with hashes) to a temporary directory and runs `pip-audit` on it against the OSV database. It exits non-zero when a vulnerability is found. It needs the network, so it's not part of the end-to-end check: run it in the upgrade procedure and when finishing a ticket that changes `uv.lock`.

- OSV rather than pip-audit's default PyPI service: on the lock from before T007, OSV reported 109 vulnerabilities and PyPI 100, in the same 12 packages (2026-10-16).
- The warning that hashes are only checked for presence with OSV is harmless: uv checks them at install.
- No vulnerability is ignored. To accept one that has no fix, add `--ignore-vuln <ID>` to the task in `tasks.toml`, with a comment naming the ticket that accepted it.

The Red Hat Dependency Analytics extension in VS Code uses its own sources and may report differently; T007 used both.

The same extension suggests Red Hat Trusted Libraries, an index where Red Hat rebuilds popular packages from source with signed provenance. It's useful where supply-chain provenance is a requirement; here it would tie installs to a Red Hat account for the same code, so the repo stays on PyPI.
