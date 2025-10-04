# planx-itf-public-v3

Public-only ITF scraper (no login). Captures all publicly visible tournament fields:
- basics (name, grade, year, city/country, start/end dates)
- public details (entry/withdrawal deadlines, sign-in times, first-day lines,
  tournament director name/email, official ball, tournament key)
- venue (name, address, website)
- `apply_url` == page URL

## Render (Python service)
- Build: `pip install -r requirements.txt`
- Start: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- Health path: `/health`
- Persistent Disk at `/data` and set:
  - `DATABASE_URL=sqlite:////data/planx_itf.db`

## Test
curl -sS https://<your-url>/health
curl -X POST "https://<your-url>/scrape?seed_url=https://www.itftennis.com/en/tournament/j60-christchurch/nzl/2025/j-j60-nzl-2025-002/"
curl -sS "https://<your-url>/tournaments?limit=5"

