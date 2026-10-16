# T012 Audit without the hash warning

`mise run audit-python` (T010) prints a warning at every run: with `--require-hashes` and the OSV service, pip-audit only checks that hashes are present. A warning that always shows trains people to ignore warnings. Exporting the lock as `pylock.toml` (PEP 751) and auditing it with `pip-audit --locked` avoids it: tested on 2026-10-16, no warning, same results (109 vulnerabilities and exit 1 on the lock from before T007, none and exit 0 on the current lock).

## Acceptance criteria

- [ ] `mise run audit-python` prints no warning on the current lock and exits 0.
- [ ] On the lock from before T007 (`git show f0aaa66~1:uv.lock`) it still reports the vulnerabilities and exits non-zero.
- [ ] It leaves no file in the repo.
- [ ] The "Vulnerability check" section of `docs/project/dependency-policy.md` matches the new task; the hash warning note is gone.

## Outcome
