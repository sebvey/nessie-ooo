# lakehouse-client

The Python library the other components use to reach the lakehouse through a Nessie branch: the Nessie API for branches, tags and merges, the PyIceberg catalog, and DuckDB with the branch's catalog attached. It has no command of its own.

## Run

Nothing to run: other components import it.

```python
from lakehouse_client.nessie import Nessie
from lakehouse_client.catalog import branch_catalog
from lakehouse_client.lake import branch_lake

Nessie().create_branch("my-branch", from_ref="main")
branch_catalog("my-branch").load_table("raw.orders")          # PyIceberg
branch_lake("my-branch").sql("SELECT count(*) FROM lake.raw.orders")  # DuckDB
```

## Files

```text
src/lakehouse_client/
├─ settings.py    config (Nessie URIs, S3), read from the mise environment
├─ nessie.py      Nessie API v2 client: branch, merge, tag, delete, list, log
├─ catalog.py     PyIceberg catalog scoped to a branch: namespaces, append, overwrite, row count
└─ lake.py        DuckDB with the branch's catalog attached read-only as `lake` (reads the marts)
```

## Depends on

No other component. Packages: `requests` (Nessie API), `pyiceberg` and `pyarrow` (catalog), `duckdb` (lake), `pydantic-settings` (settings).

## Settings

`settings.py` reads the environment that mise exports: the Nessie and Silo endpoints from `mise.toml`, the Silo credentials from `mise.local.toml` ([which variables](../stack/README.md#credentials-and-settings)). Without one of them it stops at import and names the missing variables: run through mise.

## A branch in every URI

Every client puts the branch in the catalog URI (`http://localhost:19120/iceberg/<branch>`): `branch_catalog(branch)` for PyIceberg, `branch_lake(branch)` for DuckDB. Nothing reads or writes `main` unless it is the branch asked for. How a client reaches a branch: [Architecture overview](../docs/project/architecture.md#read-and-write-paths).

`lake.py` reads with DuckDB, the engine that writes the marts, because DuckDB deletes rows with position delete files that a reader must apply ([dbt on Iceberg](../transformation/dbt-on-iceberg.md#what-the-files-look-like)).

## Why a Nessie client of our own

`nessie.py` is a small class over the Nessie API v2, with only `requests`. `pynessie`, the former Python client, speaks API v1 and is unmaintained.
