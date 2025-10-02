# planx-itf-v16 (Playwright + curl)

- Dockerfile installs curl for HEALTHCHECK and Playwright chromium.
- Use as Docker Web Service on Render.
- Health Check Path: `/health`
- Optional persistence: `DATABASE_URL=sqlite:////data/planx_itf.db` and mount `/data`.
