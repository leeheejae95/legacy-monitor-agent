"""
[자동화 스케줄]
매일 09:30 실행 — Playwright 다운로드 → Ollama 분석 → 리포트 생성 → Slack 알림
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scraper.scraper import run as scrape
from analyzer.analyzer import run as analyze
from notifier.notifier import run as notify

default_args = {
    "owner": "legacy-monitor",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="legacy_monitor_daily",
    default_args=default_args,
    description="데모사이트 데이터 수집 및 분석",
    schedule="30 9 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["legacy-monitor"],
) as dag:

    def scrape_task(**context):
        date_str = context["ds_nodash"]
        files = scrape() # scraper.py의 run() 실행
        print(f"[DAG] 다운로드 완료: {list(files.values())}")

    def analyze_task(**context):
        date_str = context["ds_nodash"]
        report = analyze(date_str) # analyzer.py의 run() 실행
        print(f"[DAG] 리포트 생성: {report}")

    def notify_task(**context):
        from pathlib import Path
        date_str = context["ds_nodash"]
        report_path = Path(f"/opt/airflow/data/downloads/{date_str}/report.md")
        notify(report_path, date_str) # notifier.py의 run() 실행
        print(f"[DAG] Slack 알림 전송 완료")

    t1 = PythonOperator(
        task_id="scrape_excel",
        python_callable=scrape_task,
    )

    t2 = PythonOperator(
        task_id="analyze_report",
        python_callable=analyze_task,
    )

    t3 = PythonOperator(
        task_id="slack_notify",
        python_callable=notify_task,
    )

    t1 >> t2 >> t3