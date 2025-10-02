from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import init_db, SessionLocal, list_tournaments, upsert_tournament
from scraper import scrape_tournament

app = FastAPI(title="PlanX ITF API", version="14.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def _startup(): init_db()

@app.get("/health")
def health(): return {"status":"ok","version":app.version}

@app.get("/tournaments")
def get_tournaments(limit: int = 100, offset: int = 0):
    with SessionLocal() as s:
        rows = list_tournaments(s, limit=limit, offset=offset)
        to = lambda r: {"id":r.id,"name":r.name,"grade":r.grade,"category":r.category,
                        "start_date": r.start_date.isoformat() if r.start_date else None,
                        "end_date": r.end_date.isoformat() if r.end_date else None,
                        "city": r.city,"country": r.country,"venue": r.venue,
                        "latitude": r.latitude,"longitude": r.longitude,"has_physio": r.has_physio,
                        "gender": r.gender,"itf_link": r.itf_link,
                        "qualifying_start": r.qualifying_start.isoformat() if r.qualifying_start else None,
                        "qualifying_end": r.qualifying_end.isoformat() if r.qualifying_end else None,
                        "surface": r.surface,"notes": r.notes}
        return {"items":[to(r) for r in rows]}

@app.post("/scrape")
def scrape(seed_url: str = Query(..., description="ITF tournament page URL")):
    try:
        data = scrape_tournament(seed_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scrape failed: {e}")
    with SessionLocal() as s:
        saved = upsert_tournament(s, data)
        return {"id": saved.id, "saved": True, "data": data}
