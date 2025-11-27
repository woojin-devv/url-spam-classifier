FROM python:3.11-slim

# 로그 버퍼 안 쌓이게
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1) 의존성 먼저 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN pip install --upgrade streamlit


# 2) 앱 코드 복사
COPY . .

# Streamlit 기본 포트
EXPOSE 8501

# Streamlit 실행
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
