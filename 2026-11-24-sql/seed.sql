-- seed.sql : 스키마 생성 + 테스트 데이터 (PostgreSQL 15)
-- 실행: psql -d dw -f seed.sql   (다시 실행하면 전부 초기화됨)
SET TIME ZONE 'Asia/Seoul';

DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS dw CASCADE;
CREATE SCHEMA staging;
CREATE SCHEMA dw;

CREATE TABLE staging.raw_orders (
    order_id     BIGINT        NOT NULL,
    customer_id  BIGINT        NOT NULL,
    status       TEXT          NOT NULL,
    amount       NUMERIC(12,2) NOT NULL,
    currency     CHAR(3)       NOT NULL,
    event_ts     TIMESTAMPTZ   NOT NULL,
    loaded_at    TIMESTAMPTZ   NOT NULL DEFAULT now()
);
CREATE INDEX idx_raw_orders_loaded_at ON staging.raw_orders (loaded_at);

CREATE TABLE dw.fx_rates (
    currency   CHAR(3)  NOT NULL,
    rate_date  DATE     NOT NULL,
    krw_rate   NUMERIC(12,4) NOT NULL,
    PRIMARY KEY (currency, rate_date)
);

CREATE TABLE dw.fact_orders (
    order_id    BIGINT PRIMARY KEY,
    customer_id BIGINT        NOT NULL,
    status      TEXT          NOT NULL,
    amount_krw  NUMERIC(14,2),
    order_date  DATE          NOT NULL,
    updated_at  TIMESTAMPTZ   NOT NULL
);
CREATE INDEX idx_fact_orders_order_date ON dw.fact_orders (order_date);

CREATE TABLE dw.daily_revenue (
    order_date   DATE PRIMARY KEY,
    order_count  INT,
    revenue_krw  NUMERIC(16,2),
    refund_rate  NUMERIC(5,4)
);

-- 환율 (11/20 금, 11/23 월)
INSERT INTO dw.fx_rates VALUES
  ('USD', '2026-11-20', 1388.5000),
  ('USD', '2026-11-23', 1392.0000),
  ('JPY', '2026-11-20',    9.1500),
  ('JPY', '2026-11-23',    9.2000);

-- 전날 배치로 이미 적재된 주문
INSERT INTO dw.fact_orders VALUES
  (90, 9, 'paid', 69425.00, '2026-11-22', '2026-11-22 10:00+09');

-- staging: 11/22 적재분
INSERT INTO staging.raw_orders VALUES
  (90, 9, 'created', 50.00, 'USD', '2026-11-22 09:58+09', '2026-11-22 12:00+09'),
  (90, 9, 'paid',    50.00, 'USD', '2026-11-22 10:00+09', '2026-11-22 12:00+09');

-- staging: 11/23 적재분
INSERT INTO staging.raw_orders VALUES
  (101, 1, 'created',    50.00, 'USD', '2026-11-23 10:00+09', '2026-11-23 12:00+09'),
  (101, 1, 'paid',       50.00, 'USD', '2026-11-23 10:05+09', '2026-11-23 12:00+09'),
  (102, 2, 'created', 30000.00, 'KRW', '2026-11-23 11:00+09', '2026-11-23 12:00+09'),
  (102, 2, 'paid',    30000.00, 'KRW', '2026-11-23 11:01+09', '2026-11-23 12:00+09'),
  (103, 3, 'paid',       20.00, 'USD', '2026-11-23 12:00+09', '2026-11-23 20:00+09'),
  (103, 3, 'refunded',   20.00, 'USD', '2026-11-23 18:00+09', '2026-11-23 20:00+09'),
  (104, 4, 'paid',     5000.00, 'JPY', '2026-11-23 13:00+09', '2026-11-23 14:00+09'),
  (105, 5, 'paid',       80.00, 'USD', '2026-11-22 21:00+09', '2026-11-23 12:00+09'),
  (106, 6, 'paid',    15000.00, 'KRW', '2026-11-23 14:00+09', '2026-11-23 15:00+09'),
  (107, 7, 'paid',       10.00, 'USD', '2026-11-23 15:00+09', '2026-11-23 20:00+09'),
  (107, 7, 'refunded',   10.00, 'USD', '2026-11-23 16:00+09', '2026-11-23 20:00+09'),
  (108, 8, 'created',    30.00, 'USD', '2026-11-23 16:30+09', '2026-11-23 20:00+09'),
  (108, 8, 'paid',       30.00, 'USD', '2026-11-23 16:31+09', '2026-11-23 20:00+09'),
  (109, 9, 'paid',     2000.00, 'JPY', '2026-11-23 17:00+09', '2026-11-23 20:00+09'),
  (110, 1, 'paid',    42000.00, 'KRW', '2026-11-23 19:00+09', '2026-11-23 20:00+09');

ANALYZE;
