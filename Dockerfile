FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libzbar0 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 프로젝트 주요 파일 복사
COPY app.py /app/app.py
COPY src /app/src
COPY .streamlit /app/.streamlit
# COPY .env /app/.env
COPY rf_full_pipeline_v1.pkl /app/rf_full_pipeline_v1.pkl
COPY rf_full_pipeline_v2.pkl /app/rf_full_pipeline_v2.pkl
COPY data /app/data

ENV PYTHONPATH=/app:/app/src:$PYTHONPATH

# Streamlit 설정 (컨테이너 안에서 8502 포트로 띄울 것)
ENV STREAMLIT_SERVER_PORT=8502 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 컨테이너에서 여는 포트
EXPOSE 8502

# Streamlit 실행 (명시적으로 포트/주소 지정)
CMD ["streamlit", "run", "app.py", "--server.port=8502", "--server.address=0.0.0.0"]
