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
    catalog = load_catalog("default")
    taxi_dataset_table = catalog.load_table("ooo.taxi_dataset")
    taxi_dataset_lf = taxi_dataset_table.to_polars()
    return catalog, taxi_dataset_lf, taxi_dataset_table


@app.cell
def _(catalog):
    catalog.properties
    return


@app.cell
def _(date, pl, taxi_dataset_lf):
    (
        taxi_dataset_lf
        .filter(
            pl.col("tpep_pickup_datetime").is_between(
                lower_bound=date(2022,1,1),
                upper_bound=date(2023,1,1),
                closed='left',
            )
        )
        .with_columns(
            pl.col("tpep_pickup_datetime").dt.strftime("%Y-%m").alias("pickup_year_month")
        )
        .group_by("pickup_year_month")
        .agg(
            pl.col("tip_amount").mean().alias("tip_amount_mean"),
            pl.col("trip_distance").sum().alias("trip_distance_sum"),
            pl.len().alias("trip_count"),
        )
        .sort("pickup_year_month")
        .collect()
    )
    return


@app.cell
def _(taxi_dataset_table):
    taxi_dataset_table.inspect.snapshots()
    return


@app.cell
def _(taxi_dataset_table):
    taxi_dataset_table.current_snapshot().snapshot_id
    return


@app.cell
def _(taxi_dataset_table):
    taxi_dataset_table.manage_snapshots().create_tag(
        snapshot_id=taxi_dataset_table.current_snapshot().snapshot_id,
        tag_name="bad_one",
    ).commit()
    return


@app.cell
def _(taxi_dataset_table):
    taxi_dataset_table.inspect.entries()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
