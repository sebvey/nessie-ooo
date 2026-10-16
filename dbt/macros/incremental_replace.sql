{#- Incremental strategy `replace`: replace all of the table's rows with the model's result.

    DuckDB's Iceberg extension can't recreate a table the way the `table` materialization does
    (create, then rename in the same transaction: the REST catalog refuses to mix table updates with
    renames), nor run `CREATE OR REPLACE TABLE` (duckdb/duckdb-iceberg#784). A delete then an insert
    in one transaction gives a full refresh as a single Iceberg commit on the branch. -#}
{% macro get_incremental_replace_sql(arg_dict) -%}
    {#- Columns matched by name: dbt can't list an attached Iceberg table's columns. -#}
    {%- set target = arg_dict["target_relation"] -%}
    delete from {{ target }};
    insert into {{ target }} by name
    select * from {{ arg_dict["temp_relation"] }}
{%- endmacro %}
