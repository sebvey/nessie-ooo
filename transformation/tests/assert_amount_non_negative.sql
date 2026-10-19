-- Fails (returns rows) if any order has a negative amount.
-- The `--ko` ingestion injects negative amounts to trip this test on purpose.
select order_id, amount
from {{ ref('stg_orders') }}
where amount < 0
