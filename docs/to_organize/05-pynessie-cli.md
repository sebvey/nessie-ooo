# `pynessie` CLI guide

Use `pynessie` to explore and manage Nessie branches, tags, commits, and table entries without writing Spark code. It talks to the Nessie REST API (port 19120) and mirrors Git-style flows.

## Config location and overrides
- Default location (using `confuse` and XDG): `~/.config/nessie/config.yaml` on Linux/macOS; `%APPDATA%\\nessie\\config.yaml` on Windows (or under `XDG_CONFIG_HOME` if set).
- Override the config directory via env: `export NESSIEDIR=/path/to/dir` (CLI reads/writes `config.yaml` there).

## Install and point to your server
```bash
uv tool install pynessie --with "marshmallow<4"
nessie remote add local http://localhost:19120/api/v2
nessie remote show      # verify the remote
nessie config show      # see default branch and settings
```


## Everyday commands
- List refs: `nessie branch list` and `nessie tag list`
- Create branch from main: `nessie branch create feature/test -r main`
- Create tag at a commit: `nessie tag create v1 --hash <commit-hash>`
- Show log: `nessie log` (current ref) or `nessie log main`
- Show current default ref: `nessie config show`
- List catalog entries: `nessie content list --ref main`
- Show a specific entry: `nessie content view --ref main nessie.demo_weather`
- Diff two refs: `nessie diff --from main --to feature/test`
- Merge a branch into main: `nessie merge feature/test -b main`
- Cherry-pick a commit: `nessie cherry-pick <commit-hash> -b main`

## How it interacts with Iceberg
- When Spark writes an Iceberg table, Nessie records a commit with the new table metadata pointer on the active ref.
- `pynessie` lets you inspect and manipulate those refs and commits (e.g., create a branch before an experiment, merge after validation, roll back by resetting to an earlier commit).
- To align Spark with a ref you explore via `pynessie`, set `spark.sql.catalog.nessie.ref=<branch>` before reads/writes.

## Examples
- Create a feature branch, write on it in Spark, then merge:
  1. `nessie branch create feature/test -r main`
  2. In Spark config: `.config("spark.sql.catalog.nessie.ref", "feature/test")`
  3. After writes: `nessie diff --from main --to feature/test` then `nessie merge feature/test -b main`
- Inspect table entries:
  - `nessie content list --ref main`
  - `nessie content view --ref main nessie.demo_weather`
- Restore to a previous commit:
  - Find commit: `nessie log main`
  - Point branch to it: `nessie branch assign main --hash <commit-hash>`

## Troubleshooting
- Auth disabled by default in the local stack; if you enable it, see `nessie config` flags (`--username/--password` or bearer token).
- Endpoint errors: recheck the remote URL (`http://localhost:19120/api/v2`) and container status.
- Diff/log empty: ensure you have written at least one table via Spark to generate commits.
