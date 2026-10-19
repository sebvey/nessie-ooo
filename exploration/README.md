# exploration

A marimo notebook to look at the data of any Nessie branch: pick a branch, see its tables, query them with DuckDB. It reads only: nothing it does changes a branch.

## Run

```bash
mise run ui-exploration   # opens explore.mo.py in marimo, in the browser
```

- Pick a Nessie branch (branches only, not tags).
- DuckDB attaches the branch's catalog as `lake` and lists its tables with their row counts; nothing is loaded in advance.
- Query them in the SQL cell as `lake.<namespace>.<table>` (`SELECT * FROM lake.raw.orders WHERE amount < 0`).

The notebook ignores `NESSIE_BRANCH`: the branch is the one picked in its selector. `marimo edit` saves the SQL cell into the file, so an exploration leaves a diff in git.

## Files

```text
explore.mo.py    the notebook
```

## Depends on

[`lakehouse-client`](../lakehouse-client/README.md) (branch list from the Nessie API, DuckDB with the branch attached). Package: `marimo[sql]`. Not a Python package: its `pyproject.toml` only carries dependencies.
