# 🤖 Legacy Monitor Agent - 시스템 점검 자동화

> 매일 대시보드에 들어가 확인하던 점검 업무를, Playwright + Airflow + LLM으로 자동화

<br>

## 🔑 한눈에 보기

- **문제** : legacy-monitor 대시보드를 매일 사람이 직접 열어보고 점검했음
- **해결** : Airflow가 매일 정해진 시간에, Playwright로 대시보드에 로그인해서 엑셀을 내려받고, LLM(llama3.2)이 분석 리포트를 쓰고, Slack으로 요약을 보내줌
- **결과물(이 저장소)** : 점검 → 분석 → 알림까지 한 번에 끝나는 자동화 파이프라인

<br>

## 📌 왜 만들었나

유지보수 사업을 하면서 시스템 기능 일일점검을 매일 반복하고 있었습니다. 그런데 사람이 직접 화면을 하나하나 확인하다 보니 바쁘거나 정신없을 때는 놓치는 부분이 생겼습니다.

이 문제를 해결하고 싶었습니다. 그래서 Playwright로 점검 화면 확인과 데이터 다운로드를 자동화해서 사람이 놓치는 부분이 없게 만들었습니다. 다운로드한 데이터는 Ollama(llama3.2)로 분석해서 리포트로 정리하고 그 결과를 Slack으로 바로 받아볼 수 있게 했습니다. 이 모든 과정은 Airflow가 매일 정해진 시간에 자동으로 실행합니다.

<br>

## 🔗 전체 흐름

```
[Airflow] 매일 09:30 DAG 실행 (legacy_monitor_daily)
     │
     ▼
[scraper.py] Playwright로 legacy-monitor 대시보드 로그인
     │        배치 / 민원 / 에러로그 화면에서 엑셀 3개 다운로드
     ▼
[analyzer.py] 다운로드한 엑셀을 읽어서 Ollama(llama3.2)에 분석 요청
     │         요약 / 주요 이슈 / 개선 권고사항이 담긴 report.md 생성
     ▼
[notifier.py] report.md 요약을 Slack Webhook으로 전송
     │
     ▼
담당자는 Slack 메시지 하나로 오늘 점검 결과를 바로 확인
```

각 단계는 scrape_excel → analyze_report → slack_notify 3개의 Airflow Task로 이어져 있고, 하나라도 실패하면 5분 뒤 자동으로 1번 재시도합니다.

<br>

## 🚀 주요 기능

| 기능 | 설명 |
|------|------|
| 엑셀 자동 다운로드 | Playwright가 대시보드에 로그인해서 배치/민원/에러로그 엑셀을 매일 날짜별 폴더에 저장 |
| LLM 분석 리포트 생성 | 다운로드한 엑셀을 Ollama(llama3.2)에 넘겨 전체 현황 요약, 주요 이슈, 개선 권고사항을 한국어로 작성 |
| Slack 알림 | 리포트에서 핵심 요약만 뽑아 Slack 메시지로 전송 |
| 스케줄 자동화 | Airflow DAG로 매일 정해진 시간에 전체 과정을 자동 실행, 실패 시 재시도 |

<br>

## 🛠 기술 스택

| 분류 | 기술 | 왜 썼는지 |
|------|------|----------|
| 자동화/스케줄러 | Apache Airflow 2.10.2 | 매일 정해진 시간에 실행하고, 실패 시 재시도까지 관리하기 위해 |
| 화면 자동 점검 | Playwright | 로그인이 필요한 화면에서 사람이 하던 클릭·다운로드를 그대로 자동화 |
| 데이터 분석 | Ollama (llama3.2) | 로컬에서 무료로 실행 가능한 LLM으로 엑셀 데이터를 자연어 리포트로 변환 |
| 엑셀 처리 | pandas, openpyxl | 다운로드한 엑셀을 읽어서 LLM에 넘길 텍스트로 변환 |
| 알림 | Slack Incoming Webhook | 담당자가 대시보드에 안 들어가도 결과를 바로 받아보게 하려고 |
| 실행 환경 | Docker Compose | Airflow + PostgreSQL을 한 번에 띄우기 위해 |

<br>

## 📁 프로젝트 구조

```
legacy-monitor-agent/
├── airflow/dags/
│   └── legacy_monitor_dag.py   # 스케줄 정의, scrape → analyze → notify 순서 연결
├── scraper/
│   └── scraper.py              # 대시보드 로그인 + 배치/민원/에러로그 엑셀 다운로드
├── analyzer/
│   └── analyzer.py             # 엑셀 읽기 + Ollama 분석 요청 + report.md 생성
├── notifier/
│   └── notifier.py             # report.md 요약 + Slack Webhook 전송
├── docker-compose.yml           # Airflow(webserver/scheduler) + PostgreSQL 구성
├── Dockerfile                   # Airflow 이미지에 Playwright, Ollama 클라이언트 등 설치
├── requirements.txt
└── .env.example                 # 사이트 접속 정보, Ollama, Slack 설정값
```

ℹ️ agent/ 폴더는 Spring Boot 초기 스캐폴드만 있고 아직 실제 로직은 없습니다. 향후 확장을 위해 남겨둔 상태입니다.

<br>

## ⚙️ 실행 방법

### 사전 준비
- Docker Desktop
- legacy-monitor 대시보드가 로컬에서 실행 중이어야 함 (http://localhost:8080)
- Ollama 설치 후 모델 다운로드
```
ollama pull llama3.2
```
- Slack Incoming Webhook URL (알림 받을 채널)

### 1. 환경변수 설정
```
cp .env.example .env
```
.env에 실제 SLACK_WEBHOOK_URL을 입력합니다. (나머지 값은 기본값 그대로 사용 가능)

### 2. 실행
```
docker compose up --build
```

### 3. Airflow 접속
```
http://localhost:8081
```
- 아이디: admin
- 비밀번호: admin1234

DAG 목록에서 legacy_monitor_daily를 찾아 켜두면 매일 09:30에 자동 실행됩니다. 바로 확인하고 싶다면 DAG를 수동으로 트리거(▶ 버튼)하면 됩니다.

### 4. 결과 확인
- 다운로드한 엑셀 / 분석 리포트: ./data/downloads/{날짜}/
- 점검 요약: 등록해 둔 Slack 채널

<br>

## 📈 만들면서 신경 쓴 부분

- 역할별로 파일을 완전히 분리 : 다운로드(scraper), 분석(analyzer), 알림(notifier)을 각각 독립 실행 가능한 스크립트로 분리해서 하나만 따로 테스트하거나 교체하기 쉽게 구성
- 날짜별 폴더 구조 : 다운로드/리포트를 data/downloads/{날짜} 형태로 쌓아서 나중에 지난 점검 이력도 그대로 남게 함
- LLM 교체를 염두에 둔 구조 : analyzer.py에서 모델 이름만 .env로 분리해서 Ollama 모델을 바꾸거나 추후 Claude/GPT API로 교체하기 쉽게 구성
- DAG는 얇게, 로직은 각 스크립트에 : legacy_monitor_dag.py는 실행 순서만 정의하고 실제 동작은 scraper/analyzer/notifier에서 각각 담당 (Airflow에 종속되지 않는 구조)
- 실패 시 자동 재시도 : Task 실패 시 5분 뒤 1회 재시도하도록 설정해서 일시적인 네트워크 오류 등에 대응
