# planx-itf-v16: Playwright + curl installed
FROM mcr.microsoft.com/playwright/python:v1.46.0-focal

WORKDIR /app

# Ensure curl is available for HEALTHCHECK
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure browsers are installed
RUN playwright install --with-deps chromium

EXPOSE 8000
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8000}/health || exit 1
CMD ["sh","-c","uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
