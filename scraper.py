from __future__ import annotations
import re, requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any
import pycountry

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

def _parse_date(text: str) -> Optional[datetime]:
    if not text: return None
    text = text.strip()
    for fmt in ("%Y-%m-%d","%d %b %Y","%d %B %Y","%d/%m/%Y"):
        try: return datetime.strptime(text, fmt)
        except ValueError: pass
    m = re.search(r"(\d{1,2})[\-/ ](\d{1,2})[\-/ ](\d{2,4})", text)
    if m:
        d,mn,y = m.groups(); y = y if len(y)==4 else f"20{y}"
        try: return datetime.strptime(f"{d}/{mn}/{y}", "%d/%m/%Y")
        except ValueError: return None
    return None

def _extract_two_dates(text: str):
    if not text: return (None, None)
    t = text.replace("–","-").replace("—","-")
    m = re.search(r"\b(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-z]{3,9})\s+(20\d{2})", t)
    if m:
        d1, d2, mon, yr = m.groups()
        s = f"{int(d1)} {mon} {yr}"; e = f"{int(d2)} {mon} {yr}"
        return _parse_date(s), _parse_date(e)
    pats = [r"(\d{1,2}\s+[A-Za-z]{3,9}\s+20\d{2})", r"(20\d{2}-\d{2}-\d{2})", r"(\d{1,2}/\d{1,2}/20\d{2})"]
    found = []
    for p in pats: found += re.findall(p, t)
    if len(found) >= 2:
        return _parse_date(found[0]), _parse_date(found[1])
    return (None, None)

def _iso3_to_country(iso3: str) -> Optional[str]:
    if not iso3: return None
    try:
        c = pycountry.countries.get(alpha_3=iso3.upper())
        return c.name if c else None
    except Exception:
        return None

def _slug_to_city(slug: str) -> Optional[str]:
    if not slug: return None
    parts = slug.split("-")
    if parts and re.match(r"j\d+", parts[0].lower()):
        parts = parts[1:]
    city = " ".join(parts)
    return city.title() if city else None

def _grade_from_slug_or_title(slug: str, title: str) -> Optional[str]:
    m = re.search(r"j\d{2,3}", slug.lower()) or re.search(r"J\d{2,3}", title or "", re.I)
    return m.group(0).upper() if m else None

def _fetch_html(url: str, timeout: int = 25) -> str:
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def scrape_public(url: str) -> Dict[str, Any]:
    html = _fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    meta_title = soup.find("meta", attrs={"property":"og:title"})
    name = (meta_title.get("content", "").strip() if meta_title and meta_title.get("content") else None)
    if not name and soup.title: name = soup.title.get_text(strip=True)

    m = re.search(r"/tournament/([^/]+)/([a-z]{3})/(\d{4})/([^/]+)/?", url, re.I)
    city = country = grade = None
    year = None
    country_code = None
    if m:
        slug, cc, y, key = m.groups()
        year = int(y)
        country_code = cc.upper()
        country = _iso3_to_country(country_code)
        grade = _grade_from_slug_or_title(slug, name or "")
        city = _slug_to_city(slug)

    def meta(name_or_prop):
        el = soup.find("meta", attrs={"property": name_or_prop}) or soup.find("meta", attrs={"name": name_or_prop})
        return el.get("content", "").strip() if el and el.get("content") else None

    desc = meta("description") or meta("og:description") or ""
    s, e = _extract_two_dates(desc)
    if not (s and e):
        text = soup.get_text(" ", strip=True)
        s2, e2 = _extract_two_dates(text)
        s = s or s2; e = e or e2

    surface = None
    venue = None

    data = {
        "name": name or (grade or "ITF") + (f" {city}" if city else ""),
        "grade": grade,
        "year": year,
        "city": city,
        "country_code": country_code,
        "country": country,
        "start_date": s.date() if s else None,
        "end_date": e.date() if e else None,
        "surface": surface,
        "venue": venue,
        "itf_link": url,
        "apply_url": url,
        "notes": "Public scrape only; full details require IPIN login.",
    }
    return data
