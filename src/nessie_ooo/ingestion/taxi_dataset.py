import polars as pl
from pyiceberg.catalog import load_catalog

from nessie_ooo.catalog.table_specs import taxi_dataset

import argparse
import re


def parse_args() -> str:
    parser = argparse.ArgumentParser(
        description="Ingest a monthly yellow taxi dataset into Nessie via PyIceberg."
    )
    parser.add_argument(
        "year_month",
        help="Year-month in YYYY-MM format (e.g., 2025-01)",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}", args.year_month):
        raise ValueError("year_month must be in YYYY-MM format, e.g., 2025-01")
    return args.year_month


def main() -> None:
    year_month = parse_args()
    src_url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year_month}.parquet"

    catalog = load_catalog("dev")

    src_df: pl.DataFrame = pl.read_parquet(src_url).with_columns(
        [
            pl.col("tpep_pickup_datetime").dt.cast_time_unit("us"),
            pl.col("tpep_dropoff_datetime").dt.cast_time_unit("us"),
        ]
    )

    table = catalog.load_table(taxi_dataset.id)
    table.append(src_df.to_arrow())


if __name__ == "__main__":
    main()
