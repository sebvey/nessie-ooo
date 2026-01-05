from pyiceberg.catalog import load_catalog
from nessie_ooo.catalog.table_specs import taxi_dataset, default


def main():
    catalog = load_catalog("dev")

    # Will raise NamespaceAlreadyExistsError if namespace already exists
    catalog.create_namespace("ooo")

    catalog.create_table(
        identifier="ooo.taxi_dataset",
        schema=taxi_dataset.schema,
        partition_spec=taxi_dataset.partition_spec,
        sort_order=taxi_dataset.sort_order,
        properties=default.properties,
    )

if __name__ == "__main__":
    main()
