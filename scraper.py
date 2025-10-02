from __future__ import annotations
import re, json, requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

class TournamentModel(BaseModel):
    name: str = Field(...)
    grade: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    city: Optional[str] = None
    country: Optional[str] = None
    venue: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    has_physio: Optional[bool] = None
    gender: Optional[str] = None
    itf_link: Optional[str] = None
    qualifying_start: Optional[datetime] = None
    qualifying_end: Optional[datetime] = None
    surface: Optional[str] = None
    notes: Optional[str] = None

def _parse_date(text: str) -> Optional[datetime]:
    if not text: return None
    text = text.strip()
    for fmt in ("%Y-%m-%d","%d %b %Y","%d %B %Y","%d/%m/%Y"):
        try: return datetime.strptime(text, fmt)
        except ValueError: pass
    m = re.search(r"(\d{1,2})[\-/ ](\d{1,2})[\-/ ](\d{2,4})", text)
    if m:
        d,mth,y = m.groups()
        y = y if len(y)==4 else f"20{y}"
        try: return datetime.strptime(f"{d}/{mth}/{y}", "%d/%m/%Y")
        except ValueError: return None
    return None

def _bool_from_text(text: str) -> Optional[bool]:
    if not text: return None
    t = text.lower()
    if any(x in t for x in ["yes","available","on site","onsite","provided"]): return True
    if any(x in t for x in ["no","not available","none"]): return False
    return None

def fetch_html(url: str, timeout: int = 20) -> str:
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout); r.raise_for_status(); return r.text

def parse_tournament_html(html: str, source_url: str) -> TournamentModel:
    soup = BeautifulSoup(html, "html.parser")
    def txt(sel: str): 
        el = soup.select_one(sel); 
        return el.get_text(strip=True) if el else None

    name=grade=category=city=country=venue=gender=surface=None
    start_date=end_date=qualifying_start=qualifying_end=None
    latitude=longitude=None; itf_link=None; has_physio=None

    # JSON-LD
    try:
        for tag in soup.select("script[type='application/ld+json']"):
            raw = (tag.string or "").strip()
            if not raw: continue
            data = json.loads(raw)
            items = data if isinstance(data, list) else [data]
            for obj in items:
                if isinstance(obj, dict) and obj.get("@type") in ("SportsEvent","Event"):
                    name = obj.get("name") or name
                    start_date = _parse_date(obj.get("startDate") or "") or start_date
                    end_date   = _parse_date(obj.get("endDate") or "") or end_date
                    loc = obj.get("location") or {}
                    if isinstance(loc, dict):
                        venue = loc.get("name") or venue
                        addr = loc.get("address") or {}
                        if isinstance(addr, dict):
                            city = addr.get("addressLocality") or city
                            country = addr.get("addressCountry") or country
    except Exception: pass

    # Fallbacks
    name = name or (soup.title.get_text(strip=True) if soup.title else None)
    grade = grade or txt(".event-meta .grade, .tournament-meta__grade, [data-field='grade']")
    category = category or txt(".event-meta .category, .tournament-meta__category, [data-field='category']")
    surface = surface or txt(".event-surface, .tournament-surface, [data-field='surface']")

    s_text = txt("[data-field='start-date'], [data-field='startDate'], .event-dates__start, .start-date")
    e_text = txt("[data-field='end-date'], [data-field='endDate'], .event-dates__end, .end-date")
    start_date = start_date or (_parse_date(s_text) if s_text else None)
    end_date = end_date or (_parse_date(e_text) if e_text else None)

    city = city or txt(".event-location .city, .tournament-location__city, [data-field='city']")
    country = country or txt(".event-location .country, .tournament-location__country, [data-field='country']")
    venue = venue or txt(".event-location .venue, .tournament-venue, [data-field='venue']")

    if not itf_link:
        a = soup.select_one("a[href*='itftennis.com']"); itf_link = a.get("href") if a else None

    q_s = txt(".qualifying-start, [data-field='qualifying-start'], [data-field='qualifyingStart']")
    q_e = txt(".qualifying-end, [data-field='qualifying-end'], [data-field='qualifyingEnd']")
    qualifying_start = _parse_date(q_s) if q_s else None
    qualifying_end = _parse_date(q_e) if q_e else None

    return TournamentModel(
        name=name or "Unknown Tournament", grade=grade, category=category,
        start_date=start_date, end_date=end_date, city=city, country=country, venue=venue,
        latitude=latitude, longitude=longitude, has_physio=has_physio, gender=gender,
        itf_link=itf_link, qualifying_start=qualifying_start, qualifying_end=qualifying_end,
        surface=surface, notes=f"Scraped from: {source_url}",
    )

def scrape_tournament(url: str) -> Dict[str, Any]:
    html = fetch_html(url); m = parse_tournament_html(html, url)
    to_date = lambda dt: None if dt is None else dt.date()
    return {"name": m.name, "grade": m.grade, "category": m.category,
            "start_date": to_date(m.start_date), "end_date": to_date(m.end_date),
            "city": m.city, "country": m.country, "venue": m.venue,
            "latitude": m.latitude, "longitude": m.longitude, "has_physio": m.has_physio,
            "gender": m.gender, "itf_link": m.itf_link,
            "qualifying_start": to_date(m.qualifying_start), "qualifying_end": to_date(m.qualifying_end),
            "surface": m.surface, "notes": m.notes}
