"""input.txt의 시나리오마다 실제 urllib3 Retry가 계산하는 대기 시간을 출력한다.
time.sleep은 가짜로 바꿔서 실제로 기다리지 않고, 기다리려던 시간만 기록한다.
사용법: pip install "urllib3==2.2.3"  후  python trace.py input.txt
"""
import sys
from unittest import mock

from urllib3.util.retry import Retry, RequestHistory
from urllib3 import HTTPResponse


def parse(line):
    name, factor, jitter, hist, ra = [p.strip() for p in line.split("|")]
    history = tuple(
        RequestHistory("GET", "/x", None, None, "/next" if h == "R" else None)
        for h in hist.split()
    )
    headers = {} if ra == "-" else {"Retry-After": ra}
    return name, float(factor), float(jitter), history, headers


def main(path):
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    for line in lines:
        name, factor, jitter, history, headers = parse(line)
        retry = Retry(total=10, backoff_factor=factor, backoff_jitter=jitter, history=history)
        response = HTTPResponse(status=503, headers=headers) if headers else None
        slept = []
        with mock.patch("urllib3.util.retry.time.sleep", side_effect=slept.append):
            try:
                retry.sleep(response)
                result = f"sleep 호출: {slept if slept else '없음'}"
            except Exception as e:
                result = f"예외: {type(e).__name__}: {e}"
        print(f"{name:>3} | backoff={retry.get_backoff_time():<8.3f} | {result}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python trace.py input.txt")
        sys.exit(1)
    main(sys.argv[1])
