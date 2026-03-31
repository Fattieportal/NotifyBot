from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from datetime import datetime, date
import os
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
    return {"message": "Auto Notify Bot API", "version": "1.0.0", "status": "running"}


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

        sb.table("platforms").upsert({
            "id": platform_id,
            "config": config,
            "enabled": enabled,
            "updated_at": datetime.now().isoformat(),
        }).execute()

        return {"success": True, "message": f"Config saved for {platform_id}"}
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
    import httpx
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


handler = Mangum(app, lifespan="off")
