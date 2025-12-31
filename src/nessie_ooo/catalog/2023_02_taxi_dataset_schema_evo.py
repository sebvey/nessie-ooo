from pyiceberg.catalog import load_catalog

catalog = load_catalog("dev")
taxi_dataset_table = catalog.load_table("ooo.taxi_dataset")

with taxi_dataset_table.update_schema() as update:
    update.rename_column("airport_fee", "Airport_fee")
