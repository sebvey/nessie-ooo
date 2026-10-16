# T007 Fix dependency vulnerabilities

A Red Hat Dependency Analytics scan (VS Code extension, 2026-10-16) reports vulnerabilities in 5 of the direct dependencies, mostly transitive, with a remediation available for each.

## Acceptance criteria

- [ ] A new Red Hat Dependency Analytics scan shows no vulnerability that has a remediation; any remaining one is listed in the Outcome with the reason.
- [ ] Only the packages needed for the fix are upgraded (a major version only if it's the only fix); the lower bounds in `pyproject.toml` match the new minimum versions.
- [ ] End-to-end check passes: `stack-reset`, `stack-up`, `pipeline --no-pause` merges, `pipeline --bad --no-pause` doesn't and leaves `main` unchanged.
- [ ] `mise run notebook` still opens and queries a branch.

## Notes

- **Facts dated 2026-10-16**: re-run the scan when starting, to work from current results.
- Scan total, without duplicates: **49 vulnerabilities** (1 critical, 12 high, 23 medium, 13 low, 0 unknown). The per-dependency counts below add up to more (22 high, 29 medium): most likely a shared transitive dependency is counted under each direct dependency that pulls it.

| Dependency | Locked version | Direct | Transitive |
|---|---|---|---|
| `pyiceberg` | 0.10.0 | 0 | 43 (1 critical, 9 high, 20 medium, 13 low) |
| `requests` | 2.32.5 | 1 (medium) | 7 (5 high, 2 medium) |
| `dbt-duckdb` | 1.10.1 | 0 | 13 (8 high, 5 medium) |
| `pydantic-settings` | 2.12.0 | 0 | 1 (medium) |
| `rich` | 14.2.0 | 0 | 1 (low) |

- Every direct dependency is behind its latest release (`uv tree --depth 1 --outdated`, 2026-10-16): `dbt-duckdb` 1.10.1 -> 1.11.0, `duckdb` 1.4.3 -> 1.5.6, `pyiceberg` 0.10.0 -> 0.12.0, `requests` 2.32.5 -> 2.34.2, `pydantic-settings` 2.12.0 -> 2.16.0, `rich` 14.2.0 -> 15.0.0, `pyarrow` 24.0.0 -> 26.0.0, `numpy` 2.4.0 -> 2.5.4, `pandas` 3.0.3 -> 3.0.6.
- Approach agreed: upgrade per package (`uv lock --upgrade-package <pkg>`), not `uv lock --upgrade`; `duckdb` isn't in the scan and stays put (T001's ground). Then the end-to-end check from `CLAUDE.md`. Watch the majors (`rich` 15) and the pyiceberg / dbt-duckdb plugins, which rely on internal APIs (`target_to_df`, `union_by_name`).
- Related: [T001](T001-drop-pyiceberg-with-duckdb-2.md) changes the DuckDB version; [T005](T005-refactor-python-package.md) reviews the dependency list (`pandas`, `numpy`). Fixing vulnerabilities shouldn't wait for either.
- No CI scan for now: re-run the scan in VS Code at the end of the ticket.
