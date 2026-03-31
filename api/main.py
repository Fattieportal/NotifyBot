from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List
from datetime import datetime, date
import os
import httpx
from mangum import Mangum
from supabase import create_client, Client

app = FastAPI(
    title="Auto Notify Bot API",
    description="API for monitoring car listings across multiple platforms",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_supabase: Optional[Client] = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise HTTPException(status_code=500, detail="Supabase not configured")
        _supabase = create_client(url, key)
    return _supabase

PLATFORM_FIELDS = {
    "marktplaats": [
        {"name": "keywords", "type": "text", "label": "Zoekwoorden", "required": True, "placeholder": "bijv. BMW 3 serie"},
        {"name": "price_min", "type": "number", "label": "Min Prijs (euro)", "required": False},
        {"name": "price_max", "type": "number", "label": "Max Prijs (euro)", "required": False},
        {"name": "year_min", "type": "number", "label": "Min Bouwjaar", "required": False},
        {"name": "year_max", "type": "number", "label": "Max Bouwjaar", "required": False},
        {"name": "mileage_max", "type": "number", "label": "Max Kilometers", "required": False},
        {"name": "postcode", "type": "text", "label": "Postcode", "required": False, "placeholder": "bijv. 1234AB"},
        {"name": "distance_km", "type": "number", "label": "Afstand (km)", "required": False},
    ],
    "autoscout24": [
        {"name": "make", "type": "select", "label": "Merk", "required": True, "options": ["BMW", "Audi", "Mercedes-Benz", "Volkswagen", "Toyota", "Honda", "Ford", "Opel"]},
        {"name": "model", "type": "text", "label": "Model", "required": False, "placeholder": "bijv. 3 Serie"},
        {"name": "price_min", "type": "number", "label": "Min Prijs (euro)", "required": False},
        {"name": "price_max", "type": "number", "label": "Max Prijs (euro)", "required": False},
        {"name": "year_min", "type": "number", "label": "Min Bouwjaar", "required": False},
        {"name": "year_max", "type": "number", "label": "Max Bouwjaar", "required": False},
        {"name": "mileage_max", "type": "number", "label": "Max Kilometers", "required": False},
        {"name": "fuel_type", "type": "select", "label": "Brandstof", "required": False, "options": ["Diesel", "Petrol", "Electric", "Hybrid"]},
    ],
    "mobile_de": [
        {"name": "make", "type": "text", "label": "Merk", "required": True, "placeholder": "bijv. BMW"},
        {"name": "model", "type": "text", "label": "Model", "required": False},
        {"name": "price_min", "type": "number", "label": "Min Preis (euro)", "required": False},
        {"name": "price_max", "type": "number", "label": "Max Preis (euro)", "required": False},
        {"name": "year_min", "type": "number", "label": "Min Baujahr", "required": False},
        {"name": "mileage_max", "type": "number", "label": "Max Kilometerstand", "required": False},
        {"name": "zip_code", "type": "text", "label": "Postleitzahl (DE)", "required": False},
        {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
    ],
    "facebook": [
        {"name": "keywords", "type": "text", "label": "Zoekwoorden", "required": True},
        {"name": "price_max", "type": "number", "label": "Max Prijs (euro)", "required": False},
        {"name": "location", "type": "text", "label": "Locatie", "required": False},
        {"name": "radius_km", "type": "number", "label": "Afstand (km)", "required": False},
    ],
    "ebay_kleinanzeigen": [
        {"name": "keywords", "type": "text", "label": "Suchbegriffe", "required": True},
        {"name": "price_min", "type": "number", "label": "Min Preis (euro)", "required": False},
        {"name": "price_max", "type": "number", "label": "Max Preis (euro)", "required": False},
        {"name": "zip_code", "type": "text", "label": "Postleitzahl", "required": False},
        {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
    ],
}


@app.get("/")
async def root():
    return {"message": "Auto Notify Bot API", "version": "2.0.0-FILTER-FIX", "status": "running"}


FALLBACK_PLATFORMS = [
    {"id": "marktplaats", "name": "Marktplaats", "enabled": True, "config": {}},
    {"id": "autoscout24", "name": "AutoScout24", "enabled": True, "config": {}},
    {"id": "mobile_de", "name": "Mobile.de", "enabled": False, "config": {}},
    {"id": "facebook", "name": "Facebook Marketplace", "enabled": False, "config": {}},
    {"id": "ebay_kleinanzeigen", "name": "eBay Kleinanzeigen", "enabled": False, "config": {}},
]


@app.get("/health")
async def health():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supabase_url_set": bool(url),
        "supabase_key_set": bool(key),
    }


@app.get("/api/debug")
async def debug():
    """Debug endpoint to check environment variables"""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    return {
        "version": "b67ed24",
        "supabase_url_set": bool(url),
        "supabase_url_prefix": url[:30] if url else None,
        "supabase_key_set": bool(key),
        "env_keys": [k for k in os.environ.keys() if "SUPA" in k.upper() or "DATABASE" in k.upper()],
    }


@app.get("/api/platforms")
async def get_platforms():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")

    # If Supabase not configured, return fallback with fields
    if not url or not key:
        platforms = [
            {**p, "fields": PLATFORM_FIELDS.get(p["id"], [])}
            for p in FALLBACK_PLATFORMS
        ]
        return {"platforms": platforms, "source": "fallback"}

    try:
        sb = get_supabase()
        result = sb.table("platforms").select("*").execute()
        platforms = []
        for row in result.data:
            platform_id = row["id"]
            platforms.append({
                "id": platform_id,
                "name": row["name"],
                "enabled": row["enabled"],
                "config": row.get("config", {}),
                "fields": PLATFORM_FIELDS.get(platform_id, []),
            })
        return {"platforms": platforms, "source": "supabase"}
    except Exception as e:
        # On Supabase error, return fallback so UI still works
        platforms = [
            {**p, "fields": PLATFORM_FIELDS.get(p["id"], [])}
            for p in FALLBACK_PLATFORMS
        ]
        return {"platforms": platforms, "source": "fallback", "error": str(e)}


@app.get("/api/stats")
async def get_stats():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")

    if not url or not key:
        return {
            "total_listings": 0,
            "new_today": 0,
            "platforms_active": 2,
            "last_scan": None,
            "source": "fallback",
        }

    try:
        sb = get_supabase()

        total_result = sb.table("listings").select("id", count="exact").execute()
        total = total_result.count or 0

        today = date.today().isoformat()
        today_result = sb.table("listings").select("id", count="exact").gte("created_at", today).execute()
        new_today = today_result.count or 0

        active_result = sb.table("platforms").select("id", count="exact").eq("enabled", True).execute()
        platforms_active = active_result.count or 0

        last_result = sb.table("listings").select("created_at").order("created_at", desc=True).limit(1).execute()
        last_scan = last_result.data[0]["created_at"] if last_result.data else None

        return {
            "total_listings": total,
            "new_today": new_today,
            "platforms_active": platforms_active,
            "last_scan": last_scan,
            "source": "supabase",
        }
    except Exception as e:
        return {
            "total_listings": 0,
            "new_today": 0,
            "platforms_active": 0,
            "last_scan": None,
            "source": "fallback",
            "error": str(e),
        }


@app.get("/api/listings")
async def get_listings(limit: int = 50, offset: int = 0):
    try:
        sb = get_supabase()
        result = sb.table("listings").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        total_result = sb.table("listings").select("id", count="exact").execute()
        return {
            "listings": result.data,
            "total": total_result.count or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/config")
async def save_config(data: Dict[str, Any]):
    try:
        sb = get_supabase()
        platform_id = data.get("platform")
        config = data.get("config", {})
        enabled = data.get("enabled", True)

        platform_names = {
            "marktplaats": "Marktplaats.nl",
            "autoscout24": "AutoScout24",
            "mobile_de": "Mobile.de",
            "facebook": "Facebook Marketplace",
            "ebay_kleinanzeigen": "eBay Kleinanzeigen",
        }
        sb.table("platforms").upsert({
            "id": platform_id,
            "name": platform_names.get(platform_id, platform_id),
            "config": config,
            "enabled": enabled,
            "updated_at": datetime.now().isoformat(),
        }).execute()

        return {"success": True, "message": f"Config saved for {platform_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/listings/clear")
async def clear_listings():
    """Verwijder alle listings uit de database (reset voor nieuwe zoekopdracht)"""
    try:
        sb = get_supabase()
        # Delete all rows by filtering on a condition that's always true
        result = sb.table("listings").delete().gte("id", 0).execute()
        return {"success": True, "message": "Alle listings verwijderd"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape/test")
async def test_scrape(data: Dict[str, Any]):
    return {
        "success": True,
        "message": "Test scrape completed (demo mode)",
        "results": {"found": 0, "listings": []}
    }


@app.post("/api/notifications/config")
async def save_notification_config(data: Dict[str, Any]):
    return {"success": True, "message": "Notification config saved"}


@app.post("/api/notifications/test")
async def test_notification(data: Dict[str, Any]):
    notification_type = data.get("type", "telegram")

    if notification_type == "telegram":
        token = data.get("token") or data.get("telegram_token")
        chat_id = data.get("chat_id") or data.get("telegram_chat_id")

        if not token or not chat_id:
            raise HTTPException(status_code=400, detail="Bot Token en Chat ID zijn verplicht")

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": "✅ <b>Test notificatie van Notify Bot!</b>\n\nJe Telegram notificaties werken correct.",
                        "parse_mode": "HTML",
                    },
                    timeout=10,
                )
            result = resp.json()
            if result.get("ok"):
                return {"success": True, "message": "Test bericht verstuurd naar Telegram!"}
            else:
                return {"success": False, "error": result.get("description", "Onbekende fout van Telegram")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return {"success": False, "error": f"Notification type '{notification_type}' nog niet ondersteund"}


# ── Cron / Scraping ───────────────────────────────────────────

async def scrape_marktplaats(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape Marktplaats via hun interne search API"""
    params = {
        "l1CategoryId": "91",   # Auto's
        "sortBy": "SORT_INDEX",
        "sortOrder": "DECREASING",
        "searchInTitleAndDescription": "true",
        "limit": "30",
    }
    if criteria.get("keywords"):
        params["query"] = criteria["keywords"]
    if criteria.get("price_min"):
        params["priceFrom"] = str(int(criteria["price_min"]))
    if criteria.get("price_max"):
        params["priceTo"] = str(int(criteria["price_max"]))
    if criteria.get("year_min"):
        params["constructionYearFrom"] = str(criteria["year_min"])
    if criteria.get("year_max"):
        params["constructionYearTo"] = str(criteria["year_max"])
    if criteria.get("mileage_max"):
        params["mileageTo"] = str(int(criteria["mileage_max"]))
    if criteria.get("postcode"):
        params["postcode"] = criteria["postcode"]
    if criteria.get("distance_km"):
        params["distanceMeters"] = str(int(criteria["distance_km"]) * 1000)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://www.marktplaats.nl/lrp/api/search",
            params=params,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    listings = []
    for item in data.get("listings", []):
        price_info = item.get("priceInfo", {})
        price_cents = price_info.get("priceCents", 0)
        price = price_cents / 100 if price_cents else 0

        listing_id = str(item.get("itemId", ""))
        title = item.get("title", "")
        url = "https://www.marktplaats.nl" + item.get("vipUrl", "")
        location = item.get("location", {}).get("cityName", "")
        image_url = ""
        pictures = item.get("pictures", [])
        if pictures:
            image_url = pictures[0].get("mediumUrl", "") or pictures[0].get("extraExtraLargeUrl", "")

        # Extraheer year en mileage uit attributes
        year = None
        mileage = None
        for attr in item.get("attributes", []):
            key = attr.get("key", "")
            val = attr.get("value", "")
            if key == "constructionYear":
                try:
                    year = int(val)
                except (ValueError, TypeError):
                    pass
            elif key == "mileage":
                try:
                    mileage = int(str(val).replace(".", "").replace(",", "").replace(" ", ""))
                except (ValueError, TypeError):
                    pass

        listings.append({
            "listing_id": listing_id,
            "platform": "marktplaats",
            "title": title,
            "price": price,
            "year": year,
            "mileage": mileage,
            "url": url,
            "location": location,
            "image_url": image_url,
        })

    return listings


async def scrape_autoscout24(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape AutoScout24 via hun search API"""
    params = {
        "atype": "C",       # Cars
        "desc": "0",
        "sort": "age",
        "size": "20",
        "page": "1",
        "cy": "NL",
    }
    if criteria.get("make"):
        params["mmvmk0"] = criteria["make"].upper()
    if criteria.get("model"):
        params["mmvmo0"] = criteria["model"]
    if criteria.get("price_min"):
        params["pricefrom"] = str(int(criteria["price_min"]))
    if criteria.get("price_max"):
        params["priceto"] = str(int(criteria["price_max"]))
    if criteria.get("year_min"):
        params["fregfrom"] = str(criteria["year_min"])
    if criteria.get("year_max"):
        params["fregto"] = str(criteria["year_max"])
    if criteria.get("mileage_max"):
        params["kmto"] = str(int(criteria["mileage_max"]))
    if criteria.get("fuel_type"):
        fuel_map = {"Diesel": "D", "Petrol": "B", "Electric": "E", "Hybrid": "H"}
        params["fuel"] = fuel_map.get(criteria["fuel_type"], "")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://www.autoscout24.nl/lst",
            params=params,
            headers=headers,
        )
        resp.raise_for_status()

    from bs4 import BeautifulSoup
    import re, json as _json
    soup = BeautifulSoup(resp.text, "lxml")

    listings = []
    # AutoScout24 embeds listing data in a __NEXT_DATA__ script tag
    script = soup.find("script", {"id": "__NEXT_DATA__"})
    if script:
        try:
            next_data = _json.loads(script.string)
            articles = (
                next_data.get("props", {})
                .get("pageProps", {})
                .get("listings", [])
            )
            for item in articles:
                vehicle = item.get("vehicle", {})
                listing_id = str(item.get("id", ""))
                title = f"{vehicle.get('make', '')} {vehicle.get('model', '')} {vehicle.get('modelVersionInput', '')}".strip()
                price = item.get("pricing", {}).get("price", {}).get("value", 0) or 0
                year = vehicle.get("firstRegistration", {}).get("year") or vehicle.get("constructionYear")
                mileage_raw = vehicle.get("mileage", {}).get("value")
                mileage = int(mileage_raw) if mileage_raw else None
                url = "https://www.autoscout24.nl/aanbod/" + listing_id
                location_data = item.get("location", {})
                location = location_data.get("city", "") or location_data.get("countryCode", "")
                images = item.get("images", [])
                image_url = images[0].get("url", "") if images else ""

                if not listing_id:
                    continue
                listings.append({
                    "listing_id": f"as24_{listing_id}",
                    "platform": "autoscout24",
                    "title": title,
                    "price": float(price),
                    "year": int(year) if year else None,
                    "mileage": mileage,
                    "url": url,
                    "location": location,
                    "image_url": image_url,
                })
        except Exception:
            pass

    return listings


async def scrape_ebay_kleinanzeigen(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape eBay Kleinanzeigen (Kleinanzeigen.de) via HTML"""
    from bs4 import BeautifulSoup
    import re

    query = criteria.get("keywords", "auto")
    base_url = "https://www.kleinanzeigen.de/s-autos"
    search_url = f"{base_url}/{query.replace(' ', '-')}/k0c216"

    params = {}
    if criteria.get("price_min"):
        params["minPrice"] = str(int(criteria["price_min"]))
    if criteria.get("price_max"):
        params["maxPrice"] = str(int(criteria["price_max"]))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        resp = await client.get(search_url, params=params, headers=headers)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    listings = []

    for article in soup.select("article.aditem")[:30]:
        listing_id = article.get("data-adid", "")
        if not listing_id:
            continue

        title_el = article.select_one(".ellipsis")
        title = title_el.get_text(strip=True) if title_el else ""

        price_el = article.select_one(".aditem-main--middle--price-shipping--price")
        price = 0.0
        if price_el:
            price_text = price_el.get_text(strip=True).replace(".", "").replace(",", ".").replace("€", "").strip()
            try:
                price = float(re.sub(r"[^\d.]", "", price_text))
            except ValueError:
                price = 0.0

        link_el = article.select_one("a.ellipsis") or article.select_one("h2 a")
        url = ("https://www.kleinanzeigen.de" + link_el["href"]) if link_el and link_el.get("href") else ""

        location_el = article.select_one(".aditem-main--top--left")
        location = location_el.get_text(strip=True) if location_el else ""

        img_el = article.select_one("img")
        image_url = img_el.get("src", "") if img_el else ""

        listings.append({
            "listing_id": f"ebay_{listing_id}",
            "platform": "ebay_kleinanzeigen",
            "title": title,
            "price": price,
            "year": None,
            "mileage": None,
            "url": url,
            "location": location,
            "image_url": image_url,
        })

    return listings


async def scrape_mobile_de(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Scrape Mobile.de via hun search API"""
    from bs4 import BeautifulSoup
    import re, json as _json

    params = {
        "isSearchRequest": "true",
        "scopeId": "C",
        "sortOption.sortBy": "creationTime",
        "sortOption.sortOrder": "DESCENDING",
        "pageNumber": "1",
        "pageSize": "25",
    }
    if criteria.get("make"):
        params["makeModelVariant1.makeId"] = criteria["make"].upper()
    if criteria.get("model"):
        params["makeModelVariant1.modelDescription"] = criteria["model"]
    if criteria.get("price_min"):
        params["minPrice"] = str(int(criteria["price_min"]))
    if criteria.get("price_max"):
        params["maxPrice"] = str(int(criteria["price_max"]))
    if criteria.get("year_min"):
        params["minFirstRegistrationDate"] = f"{criteria['year_min']}-01-01"
    if criteria.get("mileage_max"):
        params["maxMileage"] = str(int(criteria["mileage_max"]))
    if criteria.get("zip_code"):
        params["zipcode"] = criteria["zip_code"]
    if criteria.get("radius_km"):
        params["radius"] = str(int(criteria["radius_km"]))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "de-DE,de;q=0.9",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            "https://suchen.mobile.de/fahrzeuge/search.html",
            params=params,
            headers=headers,
        )
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    listings = []

    for article in soup.select("div.cBox-body--resultitem")[:25]:
        link_el = article.select_one("a.link--muted")
        if not link_el:
            continue
        href = link_el.get("href", "")
        listing_id_match = re.search(r"id=(\d+)", href)
        listing_id = listing_id_match.group(1) if listing_id_match else ""
        if not listing_id:
            continue

        title_el = article.select_one("h2.headline-block") or article.select_one(".headline-block")
        title = title_el.get_text(strip=True) if title_el else ""

        price_el = article.select_one(".price-block") or article.select_one("span.h3")
        price = 0.0
        if price_el:
            price_text = price_el.get_text(strip=True).replace(".", "").replace(",", ".").replace("€", "").strip()
            try:
                price = float(re.sub(r"[^\d.]", "", price_text))
            except ValueError:
                price = 0.0

        url = href if href.startswith("http") else "https://suchen.mobile.de" + href

        # Year from "EZ" (Erstzulassung) field
        year = None
        ez_el = article.select_one(".rbt-regDate") or article.find(string=re.compile(r"EZ \d{2}/\d{4}"))
        if ez_el:
            year_match = re.search(r"(\d{4})", str(ez_el))
            if year_match:
                year = int(year_match.group(1))

        # Mileage from km field
        mileage = None
        km_el = article.select_one(".rbt-mileage") or article.find(string=re.compile(r"[\d\.]+\s*km"))
        if km_el:
            km_match = re.search(r"([\d\.]+)\s*km", str(km_el))
            if km_match:
                try:
                    mileage = int(km_match.group(1).replace(".", ""))
                except ValueError:
                    pass

        location_el = article.select_one(".seller-address") or article.select_one(".rbt-seller-info")
        location = location_el.get_text(strip=True) if location_el else ""

        img_el = article.select_one("img")
        image_url = img_el.get("src", "") if img_el else ""

        listings.append({
            "listing_id": f"mobile_{listing_id}",
            "platform": "mobile_de",
            "title": title,
            "price": price,
            "year": year,
            "mileage": mileage,
            "url": url,
            "location": location,
            "image_url": image_url,
        })

    return listings


def passes_filter(listing: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """Controleer of een listing voldoet aan alle ingestelde criteria."""
    price = listing.get("price") or 0
    year = listing.get("year")
    mileage = listing.get("mileage")

    # Prijs filter — sla advertenties zonder prijs (0 = bieden) over als price_max ingesteld is
    if config.get("price_max"):
        if price == 0 or price > float(config["price_max"]):
            return False
    if config.get("price_min"):
        if price == 0 or price < float(config["price_min"]):
            return False

    # Bouwjaar filter
    if config.get("year_min") and year is not None:
        if year < int(config["year_min"]):
            return False
    if config.get("year_max") and year is not None:
        if year > int(config["year_max"]):
            return False

    # Kilometerstand filter
    if config.get("mileage_max") and mileage is not None:
        if mileage > int(config["mileage_max"]):
            return False

    return True


async def send_telegram_notification(token: str, chat_id: str, listing: Dict[str, Any]):
    """Stuur een Telegram notificatie voor een nieuwe advertentie"""
    price_str = f"€{listing['price']:,.0f}" if listing.get("price") else "Prijs onbekend"
    location_str = f"📍 {listing['location']}" if listing.get("location") else ""

    text = (
        f"🚗 <b>Nieuwe advertentie gevonden!</b>\n\n"
        f"<b>{listing['title']}</b>\n"
        f"💶 {price_str}\n"
        f"{location_str}\n\n"
        f"🔗 <a href='{listing['url']}'>Bekijk advertentie</a>"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False},
        )


@app.get("/api/cron/scrape")
@app.post("/api/cron/scrape")
async def cron_scrape(request: Request):
    """
    Vercel cron job - draait elke 15 minuten automatisch.
    Scrapet actieve platforms en stuurt Telegram notificaties voor nieuwe advertenties.
    """
    results = {"scraped": 0, "new": 0, "notified": 0, "errors": []}

    # Haal Telegram credentials op uit env vars
    tg_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not tg_token or not tg_chat_id:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN en TELEGRAM_CHAT_ID niet ingesteld in Vercel env vars"}

    # Haal actieve platforms op uit Supabase
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_ANON_KEY")

    if not sb_url or not sb_key:
        return {"success": False, "error": "Supabase niet geconfigureerd"}

    try:
        sb = get_supabase()
        platforms_result = sb.table("platforms").select("*").eq("enabled", True).execute()
        platforms = platforms_result.data
    except Exception as e:
        return {"success": False, "error": f"Supabase fout: {str(e)}"}

    for platform in platforms:
        platform_id = platform.get("id")
        config = platform.get("config") or {}

        if not config:
            continue  # Geen criteria ingesteld, overslaan

        try:
            # Kies de juiste scraper op basis van platform_id
            if platform_id == "marktplaats":
                listings = await scrape_marktplaats(config)
            elif platform_id == "autoscout24":
                listings = await scrape_autoscout24(config)
            elif platform_id == "ebay_kleinanzeigen":
                listings = await scrape_ebay_kleinanzeigen(config)
            elif platform_id == "mobile_de":
                listings = await scrape_mobile_de(config)
            else:
                continue  # Onbekend platform, overslaan

            results["scraped"] += len(listings)

            for listing in listings:
                listing_id = listing["listing_id"]
                if not listing_id:
                    continue

                # Client-side filter
                if not passes_filter(listing, config):
                    continue

                # Check of advertentie al bekend is in Supabase
                existing = sb.table("listings").select("id").eq("listing_id", listing_id).execute()
                if existing.data:
                    continue  # Al bekend, overslaan

                # Sla op in Supabase
                sb.table("listings").insert({
                    "listing_id": listing_id,
                    "platform": platform_id,
                    "title": listing.get("title", ""),
                    "price": listing.get("price"),
                    "year": listing.get("year"),
                    "mileage": listing.get("mileage"),
                    "url": listing.get("url", ""),
                    "location": listing.get("location", ""),
                    "image_url": listing.get("image_url", ""),
                    "created_at": datetime.now().isoformat(),
                }).execute()
                results["new"] += 1

                # Stuur Telegram notificatie
                await send_telegram_notification(tg_token, tg_chat_id, listing)
                results["notified"] += 1

        except Exception as e:
            results["errors"].append(f"{platform_id}: {str(e)}")

    results["success"] = True
    results["timestamp"] = datetime.now().isoformat()
    return results


handler = Mangum(app, lifespan="off")
