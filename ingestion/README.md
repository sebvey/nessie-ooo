# ingestion

The demo's source system: it generates synthetic orders and appends them to `raw.orders` on a Nessie branch, through PyIceberg. With `--ko`, some rows are dirty on purpose, so the dbt tests fail.

## Run

The pipeline calls it at its step 2 ([orchestration](../orchestration/README.md#steps)). On its own, on a branch that exists:

```bash
uv run ingest <branch>        # 5 clean orders
uv run ingest <branch> --ko   # 5 orders, one with a negative amount, one with a null customer
```

## Files

```text
src/ingestion/
└─ ingest.py    generate the orders, append them to raw.orders (command `ingest`)
```

## Depends on

[`lakehouse-client`](../lakehouse-client/README.md) (PyIceberg catalog of the branch). Packages: `numpy` (random data), `pyarrow` (the batch).

## The data

Each run appends 5 orders to `raw.orders` (columns `order_id`, `customer_id`, `product`, `amount`, `quantity`, `order_ts`), timestamped within the seconds following the run, so the table grows from run to run. `order_id` continues from the highest one on the branch. `raw.orders` only ever gets appends, which is why its row count can be read from PyIceberg's snapshot summary.
