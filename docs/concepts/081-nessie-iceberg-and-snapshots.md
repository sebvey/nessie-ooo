This document explains precisely and reliably how Project Nessie (used as an Iceberg REST catalog) interacts with PyIceberg (the Iceberg engine), and why only the latest snapshot is visible even after multiple appends.

This is not a bug, and it is not caused by snapshot expiration. It is a design choice.

⸻

1. The two layers (never mix them)

There are two independent versioning systems in your setup:

1.1 Iceberg (table layer)

Iceberg tracks snapshots inside the table metadata:
* each append / overwrite / delete → new snapshot
* snapshots are immutable
* snapshots normally accumulate
* snapshot history is stored in metadata.json

This is table-internal history.

⸻

1.2 Nessie (catalog layer)

Nessie tracks catalog commits:
* each commit records which metadata file a table points to
* commits live outside the table
* commits form a Git-like graph (branches, tags, hashes)

This is catalog-level history.

⸻

2. What happens WITHOUT Nessie

With a classic Iceberg catalog (Hive, Glue, JDBC):
* each append creates a snapshot
* the new metadata file contains ALL previous snapshots
* loading the table returns the full snapshot list

Result:

metadata.json
  snapshots: [s1, s2, s3]

Iceberg time-travel works directly.

⸻

3. What changes when Nessie is the catalog

When Nessie is used as an Iceberg REST catalog, the rules change.

Critical design decision (this is the key)

Nessie deliberately exposes only ONE Iceberg snapshot per commit.

Each Nessie commit corresponds to exactly one Iceberg snapshot.

This means:
* the table does have snapshots
* but the REST view only exposes the snapshot for the selected commit

⸻

4. What PyIceberg actually receives

When PyIceberg loads a table via Nessie REST:
* it calls GET /v1/tables/{table}
* Nessie returns a metadata view
* that metadata contains exactly one snapshot

Even if:
* multiple snapshots exist logically
* snapshot-loading-mode=all is set

Nessie intentionally ignores returning historical snapshots.

This ensures:
* strong consistency between Nessie commits and Iceberg snapshots
* no ambiguity between “catalog time-travel” and “table time-travel”

⸻

5. Why snapshot-loading-mode=all has no effect

snapshot-loading-mode is a client-side hint.

It works only if the server supports returning all snapshots.

Nessie’s Iceberg REST implementation does not:
* it always returns the snapshot associated with the current commit
* historical snapshots are not included in the response

So:

PyIceberg:  "please send all snapshots"
Nessie:     "no, here is the snapshot for this commit"

Your configuration is read — it just cannot override server behavior.

⸻

6. Why Nessie restore / checkout works

When you run:
* nessie log
* nessie checkout <hash>
* nessie restore

Nessie changes which commit is active.

That commit:
* points to an older metadata file
* exposes the snapshot associated with that commit

So you observe:
* different table contents
* even though Iceberg itself shows only one snapshot

This is catalog time-travel, not Iceberg snapshot time-travel.

⸻

7. Important consequence (this is intentional)

With Nessie REST:
* Iceberg snapshot history is not meant to be consumed directly
* Nessie commit history is the authoritative timeline

In other words:

When using Nessie REST, you should think in terms of Nessie commits, not Iceberg snapshot lists.

⸻

8. What this means for your expectations

This WILL work
* nessie log
* restoring older commits
* branching / tagging at catalog level
* reproducible table states via commits

This will NOT work
* listing all snapshots from metadata.json
* Iceberg time-travel via snapshot IDs
* relying on snapshot accumulation in a single metadata file

⸻

9. This is not a limitation, it is a tradeoff

Nessie chose:
* strong catalog-level versioning
* one snapshot per commit
* deterministic table state per commit

Instead of:
* exposing long snapshot chains
* mixing snapshot GC and catalog history

This design avoids subtle correctness bugs.

⸻

10. Final mental model (keep this)

Nessie:
  versions the catalog
  = commits, branches, tags

Iceberg (under Nessie REST):
  exposes ONE snapshot per commit

If you want Iceberg-native snapshot history, you must:
* use a non-Nessie catalog
* or accept that Nessie commits replace snapshot history for inspection

⸻

One-sentence takeaway

With Nessie as an Iceberg REST catalog, snapshot history is intentionally hidden; Nessie commits are the history.
