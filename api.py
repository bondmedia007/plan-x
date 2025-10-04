from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import init_db, SessionLocal, list_tournaments, upsert_by_link
from scraper import scrape_public

app = FastAPI(title="PlanX ITF (Public Mode)", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def _startup(): init_db()

@app.get("/health")
def health(): return {"status":"ok","version":app.version,"mode":"public"}

@app.get("/tournaments")
def get_tournaments(limit: int = 100, offset: int = 0):
    with SessionLocal() as s:
        rows = list_tournaments(s, limit=limit, offset=offset)
        def ser(r):
            return {
                "id": r.id, "name": r.name, "grade": r.grade, "year": r.year,
                "city": r.city, "country_code": r.country_code, "country": r.country,
                "start_date": r.start_date.isoformat() if r.start_date else None,
                "end_date": r.end_date.isoformat() if r.end_date else None,
                "surface": r.surface, "venue": r.venue,
                "itf_link": r.itf_link, "apply_url": r.apply_url,
                "notes": r.notes,
            }
        return {"items":[ser(x) for x in rows]}

@app.post("/scrape")
def scrape(seed_url: str = Query(..., description="ITF tournament page URL")):
    try:
        data = scrape_public(seed_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scrape failed: {e}")
    with SessionLocal() as s:
        saved = upsert_by_link(s, data)
        return {"id": saved.id, "saved": True, "data": data}
