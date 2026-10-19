# exploration

A marimo notebook to look at the data of Nessie branches: pick one or more branches, browse their tables, query them with DuckDB, side by side. It reads only: every branch is attached read-only.

## Run

```bash
mise run ui-exploration   # opens explore.mo.py in marimo, in the browser
```

- Pick Nessie branches in the selector (branches only, not tags; `main` by default). **Refresh branches** re-reads the list from Nessie and keeps the selection.
- DuckDB attaches each selected branch's catalog as `lake_<branch>`, every character other than a letter, a digit or `_` replaced by `_`: `main` is `lake_main`, `pipeline-ko-153541` is `lake_pipeline_ko_153541`. The notebook shows the mapping.
- Browse the tables and their columns in marimo's Data sources panel (the `(x)` icon on the left), under `DuckDB (con)`. Nothing is loaded in advance: DuckDB reads the files from Silo at query time.
- Query them in the SQL cell as `lake_<branch>.<namespace>.<table>` (`SELECT * FROM lake_main.raw.orders WHERE amount < 0`).

Comparing two branches, both selected (the orders a red run added, absent from `main`):

```sql
SELECT k.* FROM lake_pipeline_ko_153541.raw.orders k
ANTI JOIN lake_main.raw.orders m USING (order_id)
```

The notebook ignores `NESSIE_BRANCH`: the branches are the ones picked in its selector. `marimo edit` saves the SQL cell into the file, so an exploration leaves a diff in git.

## Files

```text
explore.mo.py    the notebook
```

## Depends on

[`lakehouse-client`](../lakehouse-client/README.md) (branch list from the Nessie API, DuckDB with the branches attached). Package: `marimo[sql]`. Not a Python package: its `pyproject.toml` only carries dependencies.
