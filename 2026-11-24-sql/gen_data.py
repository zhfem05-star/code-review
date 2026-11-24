"""staging.raw_orders에 대량 데이터를 추가하는 SQL(bulk.sql)을 만든다.
사용법: python gen_data.py [일수=90] [하루당_행수=20000]
  -> psql -d dw -f bulk.sql
"""
import sys

days = int(sys.argv[1]) if len(sys.argv) > 1 else 90
per_day = int(sys.argv[2]) if len(sys.argv) > 2 else 20000

sql = f"""SET TIME ZONE 'Asia/Seoul';
INSERT INTO staging.raw_orders (order_id, customer_id, status, amount, currency, event_ts, loaded_at)
SELECT 1000000 + g,
       (random() * 50000)::bigint,
       (ARRAY['created','paid','refunded','cancelled'])[1 + (random() * 3)::int],
       round((random() * 200)::numeric, 2),
       (ARRAY['KRW','USD','JPY'])[1 + (random() * 2)::int],
       d + (random() * interval '20 hours'),
       d + interval '2 hours' + (random() * interval '20 hours')
FROM generate_series(1, {days * per_day}) AS g,
     LATERAL (SELECT timestamptz '2026-11-24 00:00+09' - ((g % {days}) || ' days')::interval AS d) t;
ANALYZE staging.raw_orders;
"""
with open("bulk.sql", "w", encoding="utf-8") as f:
    f.write(sql)
print(f"bulk.sql 생성: {days}일 x {per_day}행 = {days * per_day:,}행")
