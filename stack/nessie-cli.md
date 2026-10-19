# Nessie CLI reference

The Nessie CLI is a SQL-like REPL on top of the Nessie API. Reference: https://projectnessie.org/nessie-latest/cli/. When in doubt, `HELP;` and `HELP <COMMAND>;` inside the REPL are the source of truth.

Start it connected to `main`:

```bash
mise run cli                          # interactive
mise run cli -c "LIST REFERENCES;"    # one command (needs a terminal)
```

The talk's guided REPL walkthrough (in French) is [`presentation/demo-cli.md`](../docs/presentation/demo-cli.md).

Every command ends with `;`. `<ref>` is a branch or tag name; `BRANCH` / `TAG` keywords are only needed where shown.

## Where am I, what exists

```sql
SHOW REFERENCE;                    -- current ref, type and hash
LIST REFERENCES;                   -- all branches and tags
LIST CONTENTS;                     -- namespaces and tables on the current ref
LIST CONTENTS ON pipeline-ko-120000;
USE BRANCH main;                   -- or USE TAG release-120000, USE REFERENCE <ref>
```

On a tag you are read-only.

## History

```sql
SHOW LOG;                          -- current ref
SHOW LOG ON main LIMIT 10;
SHOW LOG ON main AT COMMIT <hash> LIMIT 5;
```

## Create and drop refs

```sql
CREATE BRANCH dev;                                   -- from the current ref
CREATE BRANCH IF NOT EXISTS dev FROM main;
CREATE BRANCH investigate FROM main AT COMMIT <hash>;
CREATE BRANCH investigate FROM main AT TIMESTAMP 2026-10-15T10:00:00Z;
CREATE TAG release-manual FROM main;

DROP BRANCH dev;
DROP BRANCH IF EXISTS dev;
DROP TAG release-manual;
```

`FROM` takes a bare ref name: `FROM main`, not `FROM BRANCH main`.

## Merge

```sql
MERGE DRY BRANCH dev INTO main;     -- simulate, changes nothing
MERGE BRANCH dev INTO main;         -- without INTO: into the current ref
MERGE BRANCH dev INTO main BEHAVIOR FORCE;
```

Behaviors: `NORMAL` (default, fail on conflict), `FORCE` (the source wins), `DROP` (the source's change is dropped). `BEHAVIORS <key> = <kind> AND …` sets them per table.

## Rollback: reassign a ref

`ASSIGN` moves a branch or a tag to another state. Nothing is copied.

```sql
ASSIGN BRANCH main TO release-120000;           -- main back to a tag
ASSIGN BRANCH main TO main AT COMMIT <hash>;    -- main back to a commit
ASSIGN TAG release-manual TO main;              -- move a tag to main's head
```

## Commit messages

Commits written through Iceberg REST (PyIceberg, dbt) get generated messages (`Update ICEBERG_TABLE raw.orders`). Merges, tags and assignments are the catalog operations that carry meaning. See [history](../docs/concepts/nessie-history.md).

## Quit

```sql
EXIT;
```
