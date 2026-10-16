# T013 Audit with `uv audit`

uv has its own audit command, `uv audit` (preview, in the installed uv 0.12.19). It reads `uv.lock` directly, so `audit-python` would no longer need the `pylock.toml` export (T012) nor a separate `uvx pip-audit`. Switch to it when we want to try it: no need to wait for it to leave preview on this project.

## Acceptance criteria

- [x] `mise run audit-python` runs `uv audit` on `uv.lock`, with no `pylock.toml` export and no pip-audit, and prints no preview warning.
- [x] The task exits 0 on the current lock, and non-zero on the lock from before T007, reporting the same 12 packages as pip-audit did.
- [x] Same scope as before: all dependency groups, the same packages as `uv export --all-groups`.
- [x] The "Vulnerability check" section of `docs/project/dependency-policy.md` describes `uv audit` against OSV, how to accept a vulnerability (`--ignore` or `--ignore-until-fixed`, with a comment giving the reason), and the preview risk with uv kept on `latest`.
- [x] The dated facts of this ticket (latest uv version, preview status of `uv audit`) are re-verified against the uv release notes when the ticket is finished.

## Decisions (refinement, 2026-10-16)

- **uv stays on `latest`**, the task passes `--preview-features audit-command`. If a uv upgrade breaks the interface, the task fails loudly (see the exit codes below); it runs by hand, not in CI. Remaining risk: a silent change of behaviour (default scope, for instance), stated in the doc. Ruled out: pinning uv in `mise.toml`, which freezes the whole toolchain for one preview command.
- **pip-audit is dropped**, along with the `pylock.toml` export.
- **No ADR**: switching audit tools is easy to reverse and confined to one task (fails test 2 of `00-agentic/processes/adr.md`). A paragraph in `dependency-policy.md` is enough.

## Notes

- Quick look on 2026-10-16: `uv audit --frozen` finds the same 109 vulnerabilities in 12 packages as pip-audit on the lock from before T007 (exit 1), none on the current lock (exit 0). It audits all dependency groups by default (111 packages, `explore` included).
- Extras over pip-audit: `--ignore-until-fixed <ID>` (ignore only while no fix exists), "adverse project statuses" (deprecated or archived projects), `json` and `sarif` output ([Astral announcement](https://astral.sh/blog/uv-audit)).
- Preview: uv warns at every run unless `--preview-features audit-command` is passed, and the interface may change.
- Investigated on 2026-10-16 (uv 0.12.19, commands run):
  - Exit codes: 0 when clean, 1 when a vulnerability is found (lock from before T007), 2 on an unknown option (clap usage error). So a broken interface and a finding are told apart by the exit code.
  - An unknown preview feature name (if `audit-command` were renamed) only warns, exit unchanged: the preview warning would come back, nothing breaks.
  - Platform: 111 packages with `--python-platform` linux, windows and macos alike, and 111 without it on macOS, Windows-only `colorama` included. `uv audit` doesn't seem to filter on the current platform. Package counts match `uv export --all-groups` (111); names not compared one by one.
  - `--service-format` only accepts `osv`, the database the current task already uses.
- To update: the task in `tasks.toml`, the "Vulnerability check" section of `docs/project/dependency-policy.md`.

## Outcome

- `audit-python` in `tasks.toml` now runs `uv audit --frozen --preview-features audit-command`; the `pylock.toml` export and `uvx pip-audit` are gone. The "Vulnerability check" section of `docs/project/dependency-policy.md` is rewritten accordingly (preview risk, `--ignore-until-fixed` / `--ignore`, the pip-audit comparison kept as history).
- Checked on 2026-10-16 with uv 0.12.19: exit 0 and 111 packages on the current lock, no warning; exit 1 on the lock from before T007, with the same 109 vulnerabilities in the same 12 packages as `pip-audit` against OSV (both compared as JSON); exit 2 on an unknown option.
- Re-verified on 2026-10-16: latest uv is 0.13.1 (2026-10-14), and `uv audit` is still a preview feature (release notes of 0.12.22, 0.12.24, 0.13.0, 0.13.1). The task runs unchanged with uv 0.13.1 (run through `uvx --from uv==0.13.1`).
- Left aside: mise still resolves `uv = "latest"` to the installed 0.12.19; upgrading uv is the developer's call.
- Not verified: the audited package names one by one (`uv audit` only reports counts, matched at 111 with the export); the behaviour of `--ignore` and `--ignore-until-fixed` (read from `uv audit --help`, not run); platform coverage beyond the 111 count on linux, windows and macos with `colorama` included.
