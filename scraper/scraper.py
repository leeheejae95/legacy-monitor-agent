"""
[데이터 수집]
demo-site 자동 로그인 후 3개 페이지 엑셀 다운로드
"""
import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from dotenv import load_dotenv

load_dotenv()

SITE_URL = os.getenv("SITE_URL", "http://localhost:8080")
USERNAME = os.getenv("SITE_USERNAME", "admin")
PASSWORD = os.getenv("SITE_PASSWORD", "admin1234")
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "./data/downloads")).resolve()


def login(page: Page) -> None:
    page.goto(f"{SITE_URL}/login")
    page.fill("#username", USERNAME)
    page.fill("#password", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url(f"{SITE_URL}/batch", timeout=10_000)


def download_excel(page: Page, path: str, filename: str) -> Path:
    page.goto(f"{SITE_URL}{path}")
    date_str = datetime.now().strftime("%Y%m%d")
    save_path = DOWNLOAD_DIR / date_str
    save_path.mkdir(parents=True, exist_ok=True)

    with page.expect_download() as dl_info:
        page.click("a:has-text('엑셀 다운로드'), button:has-text('엑셀 다운로드')")
    download = dl_info.value
    dest = save_path / filename
    download.save_as(dest)
    print(f"[download] {dest}")
    return dest


def run() -> dict[str, Path]:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, Path] = {}

    with sync_playwright() as p: # playwright 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        login(page) # 로그인

        # 엑셀파일 다운로드
        results["batch"] = download_excel(page, "/batch", "batch.xlsx")
        results["civil"] = download_excel(page, "/civil", "civil.xlsx")
        results["error_log"] = download_excel(page, "/error-log", "error_log.xlsx")

        browser.close()

    return results


if __name__ == "__main__":
    files = run()
    for key, path in files.items():
        print(f"{key}: {path}")