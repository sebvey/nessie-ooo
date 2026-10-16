# T013 Audit with `uv audit`

uv has its own audit command, `uv audit` (preview, in the installed uv 0.12.19). It reads `uv.lock` directly, so `audit-python` would no longer need the `pylock.toml` export (T012) nor a separate `uvx pip-audit`. Switch to it when we want to try it: no need to wait for it to leave preview on this project.

## Notes

- Quick look on 2026-10-16: `uv audit --frozen` finds the same 109 vulnerabilities in 12 packages as pip-audit on the lock from before T007 (exit 1), none on the current lock (exit 0). It audits all dependency groups by default (111 packages, `explore` included).
- Extras over pip-audit: `--ignore-until-fixed <ID>` (ignore only while no fix exists), "adverse project statuses" (deprecated or archived projects), `json` and `sarif` output ([Astral announcement](https://astral.sh/blog/uv-audit)).
- Preview: uv warns at every run unless `--preview-features audit-command` is passed, and the interface may change. With `uv = "latest"` in `mise.toml`, an uv upgrade could break the task: decide whether to pin uv, or accept it and fix when it breaks.
- To update: the task in `tasks.toml`, the "Vulnerability check" section of `docs/project/dependency-policy.md` (OSV through uv, how to accept a vulnerability with `--ignore` / `--ignore-until-fixed`), and possibly an ADR if the choice passes the tests (`00-agentic/processes/adr.md`).

## Outcome
