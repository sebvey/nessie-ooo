https://projectnessie.org/nessie-latest/cli/#repl-commands

# Nessie CLI / REPL – Accurate Training Sheet (Doc-backed)

This document is a **precise, doc-aligned training sheet** for the **current Nessie CLI / REPL** (the SQL-like interface).

It deliberately avoids **any legacy `pynessie` CLI syntax** and only uses commands that exist in the **official Nessie CLI documentation**.

---

## 1. How to explore the CLI

Inside the Nessie REPL:

```sql
HELP;
```

This lists all available commands.

For any command:

```sql
HELP <COMMAND>;
```

Examples:

```sql
HELP SHOW LOG;
HELP CREATE BRANCH;
HELP MERGE;
```

**Rule:** when in doubt, `HELP` is the source of truth.

---

## 2. Inspecting the current reference ("where am I?")

### Show the current reference (branch or tag)

```sql
SHOW REFERENCE;
```

This prints:

* current reference name
* type (BRANCH or TAG)
* current commit hash

### Show a specific reference

```sql
SHOW REFERENCE dev;
```

---

## 3. Switching references (checkout equivalent)

### Switch to a branch (rw) / tag (read only)

```sql
USE BRANCH dev;
USE TAG v1;
```

When using a tag:

* you are in detached mode
* you cannot commit

---

## 4. Listing references

### List all branches and tags

```sql
LIST REFERENCES;
```

This shows:

* all branches
* all tags
* their HEAD commit hashes

---

## 5. Inspecting commit history

### Show log on current reference

```sql
SHOW LOG;
```

### Show log on a specific branch or tag

```sql
SHOW LOG ON BRANCH dev;
SHOW LOG ON TAG v1;
```

### Limit history

```sql
SHOW LOG LIMIT 20;
SHOW LOG ON BRANCH dev LIMIT 10;
```

### Log relative to a specific commit

```sql
SHOW LOG ON BRANCH dev AT COMMIT <hash> LIMIT 5;
```

---

## 6. Creating branches and tags

### Create a branch from the current reference

```sql
CREATE BRANCH dev;
```

### Create a tag from the current reference

```sql
CREATE TAG v1;
```

### Create from another reference

```sql
CREATE BRANCH dev FROM BRANCH main;
CREATE TAG v1 FROM BRANCH dev;
```

### Create from a specific commit

```sql
CREATE TAG v1 FROM BRANCH dev AT COMMIT <hash>;
```

---

## 7. Deleting branches and tags

### Delete a branch

```sql
DROP BRANCH dev;
```

### Delete a tag

```sql
DROP TAG v1;
```

Tags are immutable by design; deleting and recreating is the only way to “move” one.

---

## 8. Merging branches

### Merge into the current branch

If you are on `main`:

```sql
MERGE BRANCH dev;
```

### Explicit target branch

```sql
MERGE BRANCH dev INTO main;
```

### Dry-run merge

```sql
MERGE DRY BRANCH dev INTO main;
```

### Merge behaviors

```sql
MERGE BRANCH dev INTO main BEHAVIOR NORMAL;
MERGE BRANCH dev INTO main BEHAVIOR FORCE;
MERGE BRANCH dev INTO main BEHAVIOR DROP;
```

Behavior meanings:

* **NORMAL**: fail on conflicts
* **FORCE**: source wins
* **DROP**: drop conflicting keys

---

## 9. Assigning references (advanced / dangerous)

### Move a branch pointer

```sql
ASSIGN BRANCH dev TO BRANCH main;
```

### Assign a tag to a specific commit

```sql
ASSIGN TAG v1 TO BRANCH dev AT COMMIT <hash>;
```

Use with care — this rewrites reference pointers.

---

## 10. Commit messages (important clarification)

* Commits created by **engines (PyIceberg via REST)** have **auto-generated messages**
* Examples:

  * `Update ICEBERG_TABLE ooo.taxi_dataset`
  * `delete namespace ooo`

Human-authored messages belong to **catalog operations** (merge, assign, tag) performed in the CLI.

---

## 11. Operational discipline (recommended)

* Use **PyIceberg** only for data mutations
* Use **Nessie CLI** for:

  * branching strategy
  * merges
  * tagging meaningful states
* Treat Nessie commits as the authoritative timeline

---

## Final rule to remember

> **If a command is not visible via `HELP`, it does not exist.**

This rule prevents 99% of mistakes when working with th
