# Nessie details: behavior and operations

## What Nessie is, and is not

- It is a catalog with version control: content keys (`raw.orders`) point to table metadata, and
  every change is a commit on a branch.
- It is not storage: data and metadata files live in the warehouse (S3, Silo here).
- It is not a compute engine: PyIceberg, dbt/DuckDB, Spark, Trino… read and write the files.
  Through Iceberg REST, Nessie does write the `metadata.json` files itself.

## Content keys and commits

- A **content key** identifies an entry: namespace, Iceberg table, Iceberg view.
- A **commit** updates one or more keys atomically. Engines going through Iceberg REST produce one
  commit per table operation, with a generated message (`Update ICEBERG_TABLE raw.orders`). A merge
  produces a single commit on the target, whatever the number of tables.
- Each commit has a hash and a parent; a brand-new `main` sits on the "no ancestor" hash
  (`2e1cfa82…`), and Nessie refuses to merge into a branch without history ("No common ancestor").
  That's why `mise run stack-up` creates the namespaces on `main` first.

## Refs

- **Branch**: mutable, moves with commits, can be merged, reassigned or dropped.
- **Tag**: points to a commit; reassigning one is possible (`ASSIGN TAG`) but meant to be
  exceptional.
- Reading a tag or a commit hash gives a reproducible view of every table at once.

## Merge and conflicts

- Optimistic concurrency: a merge fails if a key changed on both the source and the target since
  their common ancestor. Verified here: two branches appending to `raw.orders`, the second merge is
  rejected with `REFERENCE_CONFLICT` ("The following keys have been changed in conflict:
  'raw.orders'"). Nessie never merges the rows of an Iceberg table: the fix is to rebuild the second
  branch from the new `main`.
- Merge behaviors (per merge or per key): `NORMAL` (fail on conflict), `FORCE` (the source wins),
  `DROP` (the source's change is dropped, the target keeps its version).
- Transplant (cherry-pick) applies chosen commits to another branch.

## Rollback

- `ASSIGN BRANCH main TO release-…` (or `TO main AT COMMIT <hash>`) moves `main` back. Nothing is
  copied: `main` simply points to an older commit, hence to older `metadata.json` files.
- This is catalog-level time travel. Iceberg snapshot time travel doesn't apply under Nessie (see
  [Iceberg snapshots under Nessie](081-nessie-iceberg-and-snapshots.md)).

## Cleanup (maintenance)

- Dropping a table or a branch removes pointers, not files.
- Don't run Iceberg's `expire_snapshots` or `remove_orphan_files` on Nessie tables: each
  `metadata.json` only knows its current snapshot, so these procedures would delete files that other
  commits or branches still use.
- Use **Nessie GC** (garbage collector), a separate program (jar or `ghcr.io/projectnessie/nessie-gc`
  image, with its own JDBC database). It reads every ref through the Nessie API, marks the files still
  reachable, then sweeps the rest. Retention is a cutoff policy, per ref if needed (`--default-cutoff`,
  `--cutoff <regex>=<policy>`). The Nessie docs present it as the replacement for expire snapshots and
  orphan file removal.
- Compaction (rewriting small files) is an ordinary Iceberg write: done on a branch, it's a commit
  like any other.

## Access control

- `nessie.server.authentication.enabled` and `nessie.server.authorization.enabled`, then rules
  `nessie.server.authorization.rules.<id>=<CEL expression>` on the operation, ref, role and path.
- A merge into `main` is checked like a direct commit to `main` (`canCommitChangeAgainstReference`):
  you can't allow "merges only". Protecting `main` means restricting who can write to it at all, for
  example only the pipeline's identity.
- Both are disabled in the local stack.
