# T012 Audit without the hash warning

`mise run audit-python` (T010) prints a warning at every run: with `--require-hashes` and the OSV service, pip-audit only checks that hashes are present. A warning that always shows trains people to ignore warnings. Exporting the lock as `pylock.toml` (PEP 751) and auditing it with `pip-audit --locked` avoids it: tested on 2026-10-16, no warning, same results (109 vulnerabilities and exit 1 on the lock from before T007, none and exit 0 on the current lock).

## Acceptance criteria

- [x] `mise run audit-python` prints no warning on the current lock and exits 0.
- [x] On the lock from before T007 (`git show f0aaa66~1:uv.lock`) it still reports the vulnerabilities and exits non-zero.
- [x] It leaves no file in the repo.
- [x] The "Vulnerability check" section of `docs/project/dependency-policy.md` matches the new task; the hash warning note is gone.

## Outcome

Done on 2026-10-16.

- `tasks.toml`: `audit-python` exports `uv.lock` with `uv export --format pylock.toml` to a temporary directory and runs `uvx pip-audit --locked --vulnerability-service osv` on it. `--require-hashes` and `--disable-pip` are gone, and so is the warning.
- Checked: current lock, no warning, exit 0; lock from before T007, 109 vulnerabilities in 12 packages, exit 1; no file left in the repo.
- `docs/project/dependency-policy.md`: the "Vulnerability check" section describes the pylock export; the note about the hash warning is removed.
- Not verified: `pip-audit --locked` with OSV doesn't check hash validity either; it no longer says so. Hashes are still checked by uv at install, which is what matters for what runs.
