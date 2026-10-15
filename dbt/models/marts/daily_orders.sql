{{ config(location = "dbt/target/ext/" ~ this.identifier ~ ".parquet") }}

select
    order_date,
    count(*)          as n_orders,
    sum(amount)       as revenue,
    sum(quantity)     as items_sold,
    count(distinct customer_id) as unique_customers
from {{ ref('stg_orders') }}
group by order_date
order by order_date
