import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).parent
KST = timezone(timedelta(hours=9))  # 한국은 서머타임이 없어서 고정 오프셋으로 충분

# 언어별로 만들 코드 파일 (java는 두 번째 인자로 public 클래스명을 받음)
FILES = {
    "java": lambda cls: [f"{cls}.java"],
    "cpp": lambda _: ["main.cpp"],
    "python": lambda _: ["main.py"],
    "sql": lambda _: ["query.sql", "seed.sql"],
}


def create(lang: str, class_name: str = "Main"):
    if lang not in FILES:
        print(f"지원 언어: {', '.join(FILES)}")
        sys.exit(1)

    timestamp = datetime.now(KST).strftime("%Y-%m-%d")
    folder = ROOT / f"{timestamp}-{lang}"
    if folder.exists():
        print(f"이미 존재합니다: {folder}")
        return

    folder.mkdir()
    for name in ["input.txt", "코드리뷰.txt", *FILES[lang](class_name)]:
        (folder / name).write_text("", encoding="utf-8")

    print(f"생성 완료: {folder}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python new.py java [클래스명] | cpp | python | sql")
        sys.exit(1)
    create(sys.argv[1].lower(), *sys.argv[2:3])
