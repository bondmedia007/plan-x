FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8000}/health || exit 1
CMD ["sh","-c","uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]

