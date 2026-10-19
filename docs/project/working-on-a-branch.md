# Working on your own branch

Run your `dbt build` on a Nessie branch of your own, without touching `main`. Prerequisite: the stack is running (`mise run stack-up`).

## 1. Create the branch

```bash
mise run cli
```

Then in the REPL:

```sql
CREATE BRANCH my-branch FROM main;
```

## 2. Point dbt at the branch

In `mise.local.toml` (repo root, ignored by git):

```toml
[env]
NESSIE_BRANCH = "my-branch"
```

dbt now reads and writes on `my-branch`, from the repo root or from `transformation/`:

```bash
mise exec -- uv run dbt build
```

Check the active branch: `mise env | grep NESSIE_BRANCH`.

For a single command on another branch, without editing `mise.local.toml`, set the variable after `mise exec --`: `mise exec -- env NESSIE_BRANCH=other-branch uv run dbt build`. A prefix (`NESSIE_BRANCH=other-branch mise exec -- …`) doesn't work: mise overrides it with the value from `mise.local.toml`.

Without `NESSIE_BRANCH`, `transformation/profiles.yml` falls back to `main`: dbt then writes straight to `main`. The pipeline (`pipeline-ok`, `pipeline-ko`) and `dbt-inspect` set the variable themselves, so `mise.local.toml` doesn't affect them.

The notebook ignores this variable: pick the branch in its selector.

## 3. Drop the branch

Set `NESSIE_BRANCH = "main"` back in `mise.local.toml`, then in the REPL (`mise run cli`):

```sql
DROP BRANCH my-branch;
```
