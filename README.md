# planx-itf-v14
Improved scraper with JSON-LD parsing and Render-ready commands.

## Render (Python service)
Build Command: `pip install -r requirements.txt`
Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
Health Check: `/health`

## Render (Docker)
Use the included Dockerfile. Health Check `/health`.
