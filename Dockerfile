FROM apache/airflow:2.10.2-python3.12

USER root
RUN apt-get update && apt-get install -y \
    wget gnupg curl \
    && apt-get clean

USER airflow
RUN pip install --no-cache-dir \
    playwright==1.48.0 \
    ollama==0.3.3 \
    openpyxl==3.1.5 \
    "pandas>=2.1.2,<2.2" \
    python-dotenv==1.0.1

USER root
RUN /home/airflow/.local/bin/playwright install-deps chromium

USER airflow
RUN /home/airflow/.local/bin/playwright install chromium