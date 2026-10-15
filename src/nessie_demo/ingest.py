"""Generate a batch of synthetic 'orders' and APPEND it to raw.orders on a Nessie branch.

Each run adds fresh, random rows timestamped within the 5 seconds following generation, so
raw.orders grows over time and successive tags/commits capture a genuinely evolving dataset.

`--bad` injects dirty rows (negative amount, null customer) so the dbt tests fail on purpose,
which drives the 'no merge + alert' branch of the demo.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta

import numpy as np
import pyarrow as pa

from .catalog import append_table, branch_catalog, column_max

RAW_TABLE = "raw.orders"
ROWS_PER_RUN = 5

CUSTOMERS = [f"cust_{i:03d}" for i in range(1, 31)]  # 30 customers
PRODUCTS = [
    "book", "pen", "mug", "shirt", "cable",
    "charger", "notebook", "bottle", "backpack", "headset",
]  # 10 products


def generate(start_id: int, n_rows: int = ROWS_PER_RUN, bad: bool = False) -> pa.Table:
    rng = np.random.default_rng()  # fresh randomness each run
    now = datetime.now()

    order_ids = [start_id + 1 + i for i in range(n_rows)]
    order_ts = [now + timedelta(seconds=float(rng.uniform(0, 5))) for _ in range(n_rows)]
    customers = [CUSTOMERS[int(rng.integers(0, len(CUSTOMERS)))] for _ in range(n_rows)]
    products = [PRODUCTS[int(rng.integers(0, len(PRODUCTS)))] for _ in range(n_rows)]
    amounts = [round(float(rng.uniform(5, 200)), 2) for _ in range(n_rows)]
    quantities = [int(rng.integers(1, 11)) for _ in range(n_rows)]  # 1..10

    if bad:
        # Poison a couple of rows: negative amount + a null customer -> trips dbt tests.
        amounts[1] = -50.0
        customers[3] = None

    return pa.table(
        {
            "order_id": pa.array(order_ids, pa.int64()),
            "order_ts": pa.array(order_ts, pa.timestamp("us")),
            "customer_id": pa.array(customers, pa.string()),
            "product": pa.array(products, pa.string()),
            "amount": pa.array(amounts, pa.float64()),
            "quantity": pa.array(quantities, pa.int64()),
        }
    )


def ingest(branch: str, bad: bool = False, n_rows: int = ROWS_PER_RUN) -> pa.Table:
    """Append a batch to raw.orders on `branch` and return the appended rows."""
    catalog = branch_catalog(branch)
    start_id = column_max(catalog, RAW_TABLE, "order_id")  # continue ids across appends
    data = generate(start_id=start_id, n_rows=n_rows, bad=bad)
    append_table(catalog, RAW_TABLE, data)
    return data


def main() -> None:
    p = argparse.ArgumentParser(description="Append synthetic orders onto a Nessie branch.")
    p.add_argument("branch", help="target Nessie branch")
    p.add_argument("--bad", action="store_true", help="inject dirty rows that fail dbt tests")
    args = p.parse_args()
    n = ingest(args.branch, bad=args.bad).num_rows
    print(f"appended {n} rows to {RAW_TABLE} on branch '{args.branch}'" + (" [BAD DATA]" if args.bad else ""))


if __name__ == "__main__":
    main()
