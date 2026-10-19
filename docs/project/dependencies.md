# How to manage the dependencies

How to write version specifiers in the components' `pyproject.toml`, where each dependency is declared, and how to upgrade. Why: [ADR001](../adr/ADR001-lock-is-the-source-of-truth.md). The rules differ between an **application**, installed from its lock, and a **library**, installed by someone else's resolver. This repo is an application; the library rules are for a package extracted from it, such as a standalone Nessie client (T005).

## Components

The dependencies live in the `pyproject.toml` of the component that imports or runs them ([components](architecture.md#components)), not in the root one, which only lists the components.

- **Add one** with `uv add --package <component> <pkg>`. A package used by several components is declared in each, with the same floor (the locked version).
- **A component that uses another** declares it like a package, with `{ workspace = true }` in `[tool.uv.sources]`.
- **Check what a component declares**: the shared `.venv` holds every component's dependencies, so an import a component doesn't declare still works in it. `--exact` removes from the `.venv` what the component doesn't declare, then runs the command:

  ```bash
  uv run --exact --package orchestration pipeline --help
  uv run --exact --package transformation dbt parse
  uv run --exact --package exploration python -P -c "import lakehouse_client.lake"
  uv sync    # put every component back
  ```

  `python -P`: Python run from the repository root also sees the component folders (`orchestration/`, `stack/`…) as namespace packages, which would hide a missing dependency on another component. Entry points (`pipeline`, `dbt`…) don't have that problem.

## Rules for both

- **Floors with `>=`, nothing else.** No `~=`, no `==`, no upper bound by default.
- **`~=` is an upper bound in disguise**, and its meaning depends on how many components you write: `~=2.33` means `>=2.33, <3`, `~=2.33.0` means `>=2.33.0, <2.34`. It also assumes SemVer, which many dependencies don't follow:
  - `pyarrow` ships a major at every release (24, 25, 26): `~=24.0` blocks every upgrade.
  - `fsspec` and `s3fs` use calendar versions (2026.9.0): `~=2026.9` blocks at the turn of the year.
  - `pyiceberg` is 0.x: a minor may break, a major doesn't exist yet.
- **An upper bound only for an observed incompatibility**, with a comment stating the incompatibility (what breaks, from which version), removed once it's fixed. A preventive cap blocks fixes for everyone downstream. In T007, `dbt-core` 1.11.12 declared `sqlparse<0.6` and blocked the `sqlparse` security fix until dbt-core 1.11.14 lifted the cap.
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
- **No dependency on the application**: a Nessie client takes its configuration as arguments, not from `lakehouse_client.settings`.
- **Its own version follows SemVer**, starting at 0.x while the API settles: a 0.x minor may break, and says so in the changelog. 1.0 once the API is stable; from then on, a breaking change is a major.
- **A changelog** with one entry per release, and the supported Python versions declared in `requires-python` and tested in CI.

## Upgrade procedure (application)

When: before each talk, on a vulnerability alert, or for a feature you need. Each wave of upgrades is a ticket.

1. See what's behind: `uv tree --depth 1 --outdated --all-groups`.
2. Upgrade one package at a time, never everything at once: `uv lock --upgrade-package <pkg>`. A transitive dependency can be upgraded the same way. To stay on a release line, name the version: `--upgrade-package dbt-core==1.11.16`.
3. Read what uv changed (`Updated`, `Added`, `Removed` lines). A new dependency or a major you didn't ask for is a reason to stop and choose.
4. Raise the floors to the new locked versions, in every component's `pyproject.toml` that declares the package (`grep -rn '"<pkg>' --include=pyproject.toml .`), then `uv lock` (no version may change).
5. Check for vulnerabilities (`mise run audit-python`, below), then run the end-to-end check from [`CLAUDE.md`](../../CLAUDE.md#running-things).

## Vulnerability check

**Scope: the Python dependencies only.** The container images the stack runs (Nessie, Nessie CLI, Postgres, Silo, mc) are not audited by anything in this repo: see T011.

```bash
mise run audit-python
```

The task runs `uv audit`, which reads `uv.lock` directly and checks every package of every dependency group, on all platforms, against the [OSV database](#background-the-osv-database). It exits 1 when a vulnerability is found, 2 on a usage error. It needs the network, so it's not part of the end-to-end check: run it in the upgrade procedure and when finishing a ticket that changes `uv.lock`.

- **Preview command.** `uv audit` is experimental in uv (still the case in uv 0.13.1, 2026-10-16); the task passes `--preview-features audit-command` to silence the warning printed at every run. uv stays on `latest` in `mise.toml`: if an upgrade changes the interface, the task fails with exit 2 and gets fixed then. A change of behaviour without an error (what gets audited by default, for instance) would go unnoticed: check the "Preview features" section of the uv release notes when the task's output looks different.
- Before T013, the task exported the lock to `pylock.toml` and ran `pip-audit` against OSV. On the lock from before T007, both tools reported the same 109 vulnerabilities in the same 12 packages (2026-10-16). OSV rather than pip-audit's default PyPI service, which reported 100.
- No vulnerability is ignored. To accept one, add an option to the task in `tasks.toml`, with a comment giving the reason (no fix released, not reachable from our code…): `--ignore-until-fixed <ID>` while no fix exists (the audit fails again once one is released), `--ignore <ID>` to accept it for good.

The Red Hat Dependency Analytics extension in VS Code uses its own sources and may report differently; T007 used both.

The same extension suggests Red Hat Trusted Libraries, an index where Red Hat rebuilds popular packages from source with signed provenance. It's useful where supply-chain provenance is a requirement; here it would tie installs to a Red Hat account for the same code, so the repo stays on PyPI.

## Background: the OSV database

OSV (Open Source Vulnerabilities) names two things:

- **The OSV format**: a JSON schema describing a vulnerability by package and affected or fixed versions. Maintained by the OpenSSF Vulnerability Disclosures Working Group ([ossf/osv-schema](https://github.com/ossf/osv-schema)); the OpenSSF is a Linux Foundation project.
- **[osv.dev](https://osv.dev)**: the database `uv audit` queries. It writes no advisories: it aggregates the databases that publish in the OSV format, and serves them through a free API with no account and no rate limit ([FAQ](https://google.github.io/osv.dev/faq/)). Google launched it in 2021; its code lives under the `google` GitHub organization and runs on GCP ([google/osv.dev](https://github.com/google/osv.dev)), but the docs name no operating team.

For Python packages, the main sources aggregated (list in [`source.yaml`](https://github.com/google/osv.dev/blob/master/source.yaml)):

| Source | IDs | Kept by | Content |
|---|---|---|---|
| [PyPA Advisory Database](https://github.com/pypa/advisory-database) | `PYSEC-` | the PyPA community | Mostly NVD CVEs mapped to PyPI packages by a tool, then triaged by hand; contributions by pull request |
| [GitHub Advisory Database](https://github.com/github/advisory-database) | `GHSA-` | GitHub | Advisories reviewed by GitHub; the database behind Dependabot |
| [PSF Advisory Database](https://github.com/psf/advisory-database) | `PSF-` | Python Software Foundation | CPython, pip |
| [OpenSSF Malicious Packages](https://github.com/ossf/malicious-packages) | `MAL-` | OpenSSF | Malicious packages |

These sources overlap: many entries trace back to the same NVD CVEs, and one vulnerability often carries several IDs (`aliases`). PyPI's own JSON API shows OSV data too, `PYSEC` entries only as far as its example shows ([docs](https://docs.pypi.org/api/json/)), which likely explains why pip-audit's PyPI service reported fewer vulnerabilities than OSV (not checked entry by entry).

Free alternatives (Trivy, Grype, OSV-Scanner) draw on the same upstream sources for Python; databases with their own research (Snyk, Safety, Sonatype OSS Index, the Red Hat extension above) need an account. Trivy and Grype also scan container images, a lead for T011.

Checked on 2026-10-16 against the linked pages, except: the license of the osv.dev data (not found) and the sources of Trivy, Grype and the commercial databases (from memory).
