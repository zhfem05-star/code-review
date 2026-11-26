# 사용법: python gen_data.py <줄 수> [출력 파일]
# 예: python gen_data.py 1000000 big.log
import random
import sys
from datetime import datetime, timedelta

n = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
out = sys.argv[2] if len(sys.argv) > 2 else "big.log"

paths = ["/api/users", "/api/products", "/api/orders", "/health", "/api/login"]
paths += [f"/api/users/{i}" for i in range(1, 500)]
methods = ["GET", "GET", "GET", "POST", "PUT", "DELETE"]
statuses = [200] * 20 + [201, 204, 301, 400, 401, 404, 500, 503]

t = datetime(2026, 11, 26, 0, 0, 0)
random.seed(42)
with open(out, "w", encoding="utf-8") as f:
    for _ in range(n):
        t += timedelta(milliseconds=random.randint(1, 50))
        f.write(f"{t:%Y-%m-%dT%H:%M:%S} {random.choice(methods)} "
                f"{random.choice(paths)} {random.choice(statuses)} "
                f"{random.randint(1, 800)}\n")
print(f"{n} lines -> {out}")
