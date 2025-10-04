# planx-itf-public-v1

Public-mode ITF scraper (no login). It extracts what's visible without authentication:
- name (from og:title / title)
- grade (J60/J100/etc, from URL or title)
- year, city (from URL path)
- country (ISO-3 → name)
- dates (best-effort from meta description / visible text)
- apply_url (same as the page URL)
- itf_link (same as page)
- surface/venue best-effort (often not public)

## Deploy on Render

**Option A — Python service (simplest)**
- Environment: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`
- (Recommended) Attach a **Persistent Disk** at `/data` and set:
  - `DATABASE_URL=sqlite:////data/planx_itf.db`

**Option B — Docker (included)**
- Environment: Docker
- Health check: `/health`
- The Dockerfile already runs uvicorn.

## Test
Replace with your Render URL:
```
curl -sS https://<your-render-url>/health
curl -X POST "https://<your-render-url>/scrape?seed_url=https://www.itftennis.com/en/tournament/j60-christchurch/nzl/2025/j-j60-nzl-2025-002/"
curl -sS "https://<your-render-url>/tournaments?limit=10"
```
