# Nessie operations: merge, rollback, cleanup, access

## Merge and conflicts

- Optimistic concurrency: a merge fails if a table changed on both the source and the target since their common ancestor. Verified: two branches appending to `raw.orders`, the second merge is rejected with `REFERENCE_CONFLICT` ("The following keys have been changed in conflict: 'raw.orders'"). Nessie never merges the rows of an Iceberg table: rebuild the second branch from the new target and merge again.
- Merge behaviors, per merge or per table: `NORMAL` (fail on conflict), `FORCE` (the source wins), `DROP` (the source's change is dropped, the target keeps its version).
- Transplant (cherry-pick) applies chosen commits to another branch.

## Rollback

Reassign the branch: `ASSIGN BRANCH main TO <tag>` or `TO main AT COMMIT <hash>`. Nothing is copied; the branch simply points to an older commit, hence to older `metadata.json` files. This is catalog-level time travel, for every table at once.

## Cleanup

- Dropping a table or a branch removes pointers, not files.
- Don't run Iceberg's `expire_snapshots` or `remove_orphan_files` on Nessie tables: each `metadata.json` only knows its current snapshot (see [history](nessie-history.md)), so these procedures would delete files that other commits or branches still use.
- Use **Nessie GC** (garbage collector), a separate program: a jar (Java 17) or the `ghcr.io/projectnessie/nessie-gc` image, with its own JDBC database. It reads every ref through the Nessie API, marks the files still reachable, then sweeps the rest. It isn't triggered through the Nessie API. Retention is a cutoff policy, per ref if needed (`--default-cutoff`, `--cutoff <regex>=<policy>`). The Nessie docs present it as the replacement for expire snapshots and orphan file removal.
- Compaction (rewriting small files) is an ordinary Iceberg write: done on a branch, it's a commit like any other.

## Access control

- Enable `nessie.server.authentication.enabled` and `nessie.server.authorization.enabled`, then write rules `nessie.server.authorization.rules.<id>=<CEL expression>` on the operation, ref, role and path.
- A merge into `main` is checked like a direct commit to `main` (`canCommitChangeAgainstReference`): you can't allow "merges only". Protecting `main` means restricting who can write to it at all, for example only a pipeline identity.
- Rollback needs the `ASSIGN_REFERENCE_TO_HASH` permission on the branch.
