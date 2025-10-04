from __future__ import annotations
import re, requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict, Any
import pycountry

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def _fetch_html(url: str, timeout: int = 25) -> str:
    try:
        r = requests.get(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
        }, timeout=timeout)
        if r.status_code >= 400:
            return ""
        return r.text or ""
    except Exception:
        return ""

def _parse_date(text: str) -> Optional[datetime]:
    if not text: return None
    text = text.strip()
    for fmt in ("%Y-%m-%d","%d %b %Y","%d %B %Y","%d/%m/%Y"):
        try: return datetime.strptime(text, fmt)
        except ValueError: pass
    m = re.search(r"(\d{1,2})[\/\-\s](\d{1,2})[\/\-\s](\d{2,4})", text)
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
        return _parse_date(f"{int(d1)} {mon} {yr}"), _parse_date(f"{int(d2)} {mon} {yr}")
    pats = [r"(\d{1,2}\s+[A-Za-z]{3,9}\s+20\d{2})", r"(20\d{2}-\d{2}-\d{2})", r"(\d{1,2}/\d{1,2}/20\d{2})"]
    found = []
    for p in pats: found += re.findall(p, t)
    if len(found) >= 2: return _parse_date(found[0]), _parse_date(found[1])
    return (None, None)

def _iso3_to_country(iso3: str) -> Optional[str]:
    try:
        c = pycountry.countries.get(alpha_3=iso3.upper())
        return c.name if c else None
    except Exception:
        return None

def _grade_from_slug(slug: str) -> Optional[str]:
    m = re.search(r"j\d{2,3}", slug.lower())
    return m.group(0).upper() if m else None

def _slug_to_city(slug: str) -> Optional[str]:
    parts = slug.split("-")
    if parts and re.match(r"j\d+", parts[0].lower()):
        parts = parts[1:]
    city = " ".join(parts)
    return city.title() if city else None

def _label_value(soup: BeautifulSoup, label: str) -> Optional[str]:
    pat = re.compile(rf"^\s*{re.escape(label)}\s*:?\s*$", re.I)
    for t in soup.find_all(string=pat):
        p = t.parent
        sib = p.find_next(string=lambda s: s and s.strip() and not pat.match(s.strip()))
        if sib:
            return " ".join(sib.strip().split())
        link = p.find_next("a")
        if link and link.get_text(strip=True):
            return link.get_text(strip=True)
    return None

def scrape_public(url: str) -> Dict[str, Any]:
    slug = country_code = year = None
    m = re.search(r"/tournament/([^/]+)/([a-z]{3})/(\d{4})/[^/]+/?", url, re.I)
    if m:
        slug, cc, y = m.groups()
        year = int(y); country_code = cc.upper()
    city = _slug_to_city(slug) if slug else None
    grade = _grade_from_slug(slug or "")
    country = _iso3_to_country(country_code) if country_code else None

    name = None; start_date = end_date = surface = venue = None
    entry_deadline = withdrawal_deadline = sign_in_main = sign_in_qual = None
    first_qualifying_day = first_main_day = None
    td_name = td_email = official_ball = tournament_key = None
    venue_name = venue_address = venue_website = None

    html = _fetch_html(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        og = soup.find("meta", attrs={"property":"og:title"})
        if og and og.get("content"): name = og.get("content").strip()
        if not name and soup.title: name = soup.title.get_text(strip=True)

        def meta(name_or_prop):
            el = soup.find("meta", attrs={"property": name_or_prop}) or soup.find("meta", attrs={"name": name_or_prop})
            return el.get("content", "").strip() if el and el.get("content") else None
        desc = meta("description") or meta("og:description") or ""
        s,e = _extract_two_dates(desc)
        if not (s and e):
            text = soup.get_text(" ", strip=True)
            s2,e2 = _extract_two_dates(text)
            s = s or s2; e = e or e2
        start_date, end_date = s, e

        entry_deadline       = _label_value(soup, "Entry deadline")
        withdrawal_deadline  = _label_value(soup, "Withdrawal deadline")
        sign_in_main         = _label_value(soup, "Single Main Draw Sign-in date/time")
        sign_in_qual         = _label_value(soup, "Singles Qualifying sign-in date/time")
        first_qualifying_day = _label_value(soup, "First day of Singles Qualifying")
        first_main_day       = _label_value(soup, "First day of Singles Main Draw")
        td_name              = _label_value(soup, "Tournament Director name")
        td_email             = _label_value(soup, "Tournament Director email")
        official_ball        = _label_value(soup, "Official ball")
        tournament_key       = _label_value(soup, "Tournament key")
        venue_name           = _label_value(soup, "Venue Name")
        venue_address        = _label_value(soup, "Venue Address")
        venue_website        = _label_value(soup, "Venue Website")

        if not venue_name:
            vh = soup.find(string=re.compile(r"^\s*Tournament Venue\s*$", re.I))
            if vh:
                sec = vh.parent
                cand = sec.find_next(string=lambda s: s and s.strip())
                if cand: venue_name = " ".join(cand.strip().split())

    return {
        "name": name or (grade or "ITF") + (f" {city}" if city else ""),
        "grade": grade, "year": year,
        "city": city, "country_code": country_code, "country": country,
        "start_date": start_date.date() if start_date else None,
        "end_date": end_date.date() if end_date else None,
        "surface": surface, "venue": venue,
        "entry_deadline": entry_deadline,
        "withdrawal_deadline": withdrawal_deadline,
        "sign_in_main": sign_in_main,
        "sign_in_qual": sign_in_qual,
        "first_qualifying_day": first_qualifying_day,
        "first_main_day": first_main_day,
        "tournament_director_name": td_name,
        "tournament_director_email": td_email,
        "official_ball": official_ball,
        "tournament_key": tournament_key,
        "venue_name": venue_name,
        "venue_address": venue_address,
        "venue_website": venue_website,
        "itf_link": url, "apply_url": url,
        "notes": "Public scrape (URL fallback when page body is blocked).",
    }

