# Concepts

General knowledge about Iceberg and Nessie, valid outside this repository. How this repository applies it: [Architecture overview](../project/architecture.md). Read in this order:

1. [Iceberg metadata](iceberg-metadata.md): `metadata.json`, snapshots, manifests, data files.
2. [Nessie overview](nessie-overview.md): what Nessie is, refs and commits, how a branch is selected through Iceberg REST.
3. [History under Nessie](nessie-history.md): Nessie commits versus Iceberg snapshots, who creates which commit.
4. [Nessie operations](nessie-operations.md): merge and conflicts, rollback, cleanup with Nessie GC, access control.
5. [Nessie deployment](nessie-deployment.md): runtimes and version stores.
