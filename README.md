# planx-itf-v15 (Playwright)

Scrapes ITF pages reliably by rendering JS via Playwright.

## Render Deployment (Docker)
- Create a **Docker** Web Service.
- Health Check: `/health`
- Optional persistence: add `DATABASE_URL=sqlite:////data/planx_itf.db` and mount `/data`.

## Endpoints
- `GET /health`
- `POST /scrape?seed_url=...`
- `GET /tournaments?limit=50`
