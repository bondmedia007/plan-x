FROM mcr.microsoft.com/playwright/python:v1.46.0-focal

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN playwright install --with-deps chromium

EXPOSE 8000
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8000}/health || exit 1
CMD ["sh","-c","uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
