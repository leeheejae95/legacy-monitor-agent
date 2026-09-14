"""
[데이터 분석]
Playwright가 다운로드한 엑셀 파일을 읽어 llama3.2로 분석 후 리포트 생성
"""
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import ollama
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2") # LLM 변경시 .env파일수정후 변경
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "./data/downloads")).resolve()


def read_excel(path: Path) -> str:
    df = pd.read_excel(path)
    return df.to_string(index=False)


def analyze(subject: str, data: str) -> str:
    prompt = f"""
다음은 공공기관 시스템 운영 현황 데이터입니다. 한국어로 분석 리포트를 작성해 주세요.

[분석 대상: {subject}]
{data}

아래 형식으로 작성해 주세요.
1. 전체 현황 요약
2. 주요 이슈 (있을 경우)
3. 개선 권고사항
"""
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def run(date_str: str | None = None) -> Path:
    if date_str is None:
        date_str = datetime.now().strftime("%Y%m%d")

    data_dir = DOWNLOAD_DIR / date_str
    if not data_dir.exists():
        raise FileNotFoundError(f"다운로드 폴더 없음: {data_dir}")

    targets = {
        "배치 처리 결과": data_dir / "batch.xlsx",
        "민원 처리 현황": data_dir / "civil.xlsx",
        "시스템 에러 로그": data_dir / "error_log.xlsx",
    }

    sections: list[str] = [f"# 시스템 운영 현황 분석 리포트 ({date_str})\n"]

    for subject, path in targets.items():
        if not path.exists():
            print(f"[skip] {path} 없음")
            continue
        print(f"[analyze] {subject}")
        data = read_excel(path)
        result = analyze(subject, data)
        sections.append(f"## {subject}\n\n{result}\n")

    report_path = data_dir / "report.md"
    report_path.write_text("\n".join(sections), encoding="utf-8")
    print(f"[report] {report_path}")
    return report_path


if __name__ == "__main__":
    run()