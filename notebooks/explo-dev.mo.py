import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from pyiceberg.catalog import load_catalog
    import polars as pl
    from datetime import date
    return date, load_catalog, pl


@app.cell
def _(load_catalog):
    catalog = load_catalog("dev")
    taxi_dataset_table = catalog.load_table("ooo.taxi_dataset")
    taxi_dataset_lf = taxi_dataset_table.to_polars()
    return taxi_dataset_lf, taxi_dataset_table


@app.cell
def _(date, pl, taxi_dataset_lf):
    (
        taxi_dataset_lf
        .filter(
            pl.col("tpep_pickup_datetime").is_between(lower_bound=date(2022,1,1), upper_bound=date(2022,7,1),closed='left')
        )
        .with_columns(
            pl.col("tpep_pickup_datetime").dt.date().alias("pickup_date")
        )
        .group_by("pickup_date")
        .agg(
            pl.col("tip_amount").mean().alias("tip_amount_mean"),
            pl.col("trip_distance").sum().alias("trip_distance_sum"),
            pl.len().alias("trip_count"),
        )
        .sort("pickup_date")
        .collect()
    )
    return


@app.cell
def _(taxi_dataset_table):
    if False:
        with taxi_dataset_table.update_schema() as update:
            update.rename_column("airport_fee", "Airport_fee")
    return


@app.cell
def _(taxi_dataset_table):
    taxi_dataset_table.schemas()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
