from pyiceberg.catalog import load_catalog
import polars as pl

catalog = load_catalog("dev")


catalog.create_namespace_if_not_exists("ooo")


print(f'{catalog.table_exists("ooo.taxi_dataset")=}')

src_url = (
    "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-01.parquet"
)


# use_pyarrow: because it parse timestamps to µs / polars to ns, which is not accepted by pyiceberg
src_df: pl.DataFrame = pl.read_parquet(src_url, use_pyarrow=True)

table = catalog.create_table_if_not_exists(
    "ooo.taxi_dataset",
    schema=src_df.schema.to_arrow(),
)


table.append(src_df.to_arrow())
