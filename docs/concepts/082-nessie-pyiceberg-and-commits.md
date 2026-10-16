# Commits: Nessie, Iceberg REST and PyIceberg

Who creates the commits you see in `SHOW LOG`, and why their messages look technical.

## What a Nessie commit is

A catalog-level change on one branch: "from now on, these keys point to these metadata files". It
has a hash, a parent, a message and optional authors. It doesn't contain data or Iceberg snapshots,
only pointers.

## What PyIceberg does when it writes

1. Loads the table through the Iceberg REST catalog (the branch is in the URI).
2. Writes new Parquet files and manifests to the warehouse.
3. Sends a REST commit: "apply these metadata updates, provided the table is still at the state I
   read" (requirements).

PyIceberg doesn't know about branches, commit messages or authors. The Iceberg REST spec has no field
for them.

## What Nessie does with it

Nessie checks the requirements, writes the new `metadata.json`, and records one commit on the branch
with a generated message:

```text
Update ICEBERG_TABLE raw.orders
Create ICEBERG_TABLE marts.daily_orders
update namespace raw
```

So a pipeline run shows several technical commits on its branch, then a single merge commit on
`main` (`Merged pipeline-171742 at <hash>`).

## Where meaning comes from

Through Iceberg REST you can't set messages or authors. Meaning comes from the catalog operations,
which do go through the Nessie API or CLI:
- the **branch name** (`pipeline-HHMMSS`, `pipeline-HHMMSS-bad`);
- the **merge** into `main`, which is the promotion;
- the **tag** (`release-HHMMSS`), which marks a validated state.

In this repo, `src/nessie_demo/nessie.py` does those three through the Nessie API; PyIceberg and dbt
only write data.

## Takeaway

Engines write data and Nessie turns each write into a commit. People and pipelines give the history
its meaning with branches, merges and tags.
