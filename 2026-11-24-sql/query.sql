-- load_orders.sql : 일일 주문 적재 + 일별 매출 집계
-- 실행: psql -d dw -v run_date=2026-11-23 -f load_orders.sql
\set ON_ERROR_STOP on

-- 1) staging → fact_orders 증분 upsert
WITH latest AS (
    SELECT DISTINCT ON (order_id)
           order_id, customer_id, status, amount, currency, event_ts
    FROM staging.raw_orders
    WHERE DATE(loaded_at) = :'run_date'
    ORDER BY order_id, event_ts
),
converted AS (
    SELECT l.order_id,
           l.customer_id,
           l.status,
           l.amount * r.krw_rate AS amount_krw,
           l.event_ts::date      AS order_date,
           l.event_ts
    FROM latest l
    LEFT JOIN dw.fx_rates r
           ON r.currency  = l.currency
          AND r.rate_date = l.event_ts::date
)
INSERT INTO dw.fact_orders (order_id, customer_id, status, amount_krw, order_date, updated_at)
SELECT order_id, customer_id, status, amount_krw, order_date, event_ts
FROM converted
ON CONFLICT (order_id) DO UPDATE
   SET status     = EXCLUDED.status,
       amount_krw = EXCLUDED.amount_krw,
       updated_at = EXCLUDED.updated_at
 WHERE dw.fact_orders.updated_at < EXCLUDED.updated_at;

-- 2) fact_orders → daily_revenue 집계
INSERT INTO dw.daily_revenue (order_date, order_count, revenue_krw, refund_rate)
SELECT order_date,
       COUNT(*),
       SUM(amount_krw) FILTER (WHERE status = 'paid'),
       COUNT(*) FILTER (WHERE status = 'refunded') / COUNT(*)
FROM dw.fact_orders
WHERE order_date = :'run_date'
GROUP BY order_date
ON CONFLICT (order_date) DO UPDATE
   SET order_count = dw.daily_revenue.order_count + EXCLUDED.order_count,
       revenue_krw = dw.daily_revenue.revenue_krw + EXCLUDED.revenue_krw,
       refund_rate = EXCLUDED.refund_rate;
