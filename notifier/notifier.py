"""
[Slack 알림]
분석 리포트 요약을 Slack Webhook으로 전송
"""
import os
import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send(message: str) -> None:
    if not SLACK_WEBHOOK_URL:
        raise ValueError("SLACK_WEBHOOK_URL 환경변수가 설정되지 않았습니다.")

    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        SLACK_WEBHOOK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as res:
        if res.status != 200:
            raise RuntimeError(f"Slack 전송 실패: {res.status}")


def build_message(report_path: Path, date_str: str) -> str:
    if not report_path.exists():
        return f"[{date_str}] 리포트 생성 실패 — 파일 없음"

    content = report_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    summary_lines = []
    for line in lines:
        if line.startswith("## "):
            summary_lines.append(f"\n*{line[3:]}*")
        elif line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. "):
            summary_lines.append(f"  {line}")

    summary = "\n".join(summary_lines[:20])

    return (
        f":bar_chart: *시스템 운영 현황 일일 리포트* ({date_str})\n"
        f"{summary}\n\n"
        f":memo: 전체 리포트: `data/downloads/{date_str}/report.md`"
    )


def run(report_path: Path, date_str: str) -> None:
    message = build_message(report_path, date_str)
    send(message)
    print(f"[notify] Slack 전송 완료")


if __name__ == "__main__":
    from datetime import datetime
    from pathlib import Path

    date_str = datetime.now().strftime("%Y%m%d")
    report_path = Path(f"./data/downloads/{date_str}/report.md")
    run(report_path, date_str)