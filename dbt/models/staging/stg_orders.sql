select
    order_id,
    order_ts,
    cast(order_ts as date) as order_date,
    customer_id,
    product,
    amount,
    quantity
from {{ source('raw', 'orders') }}
