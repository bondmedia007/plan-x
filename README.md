# planx-itf-public-v2

Public-mode ITF scraper (no login). Extracts public fields only and never 500s.

## Render (Python service)
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- (Recommended) Persistent Disk at `/data` and set:
  - `DATABASE_URL=sqlite:////data/planx_itf.db`

## Test
curl -sS https://<your-url>/health
curl -X POST "https://<your-url>/scrape?seed_url=https://www.itftennis.com/en/tournament/j60-christchurch/nzl/2025/j-j60-nzl-2025-002/"
curl -sS "https://<your-url>/tournaments?limit=10"

