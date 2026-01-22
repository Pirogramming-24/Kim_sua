# 1. 베이스 이미지
FROM python:3.11-slim

# 2. 작업 디렉토리
WORKDIR /app

# 3. 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 복사
COPY . .

# 6. 환경 변수
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 7. Django 개발 서버용 포트
EXPOSE 8000

# 8. 개발 서버 실행
# 0.0.0.0 바인딩 → 외부에서 접근 가능
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

