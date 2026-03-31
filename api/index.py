from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from datetime import datetime
from mangum import Mangum

app = FastAPI(
    title="Auto Notify Bot API",
    description="API for monitoring car listings across multiple platforms",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Full platform schemas with fields
PLATFORM_SCHEMAS = {
    "marktplaats": {
        "id": "marktplaats",
        "name": "Marktplaats.nl",
        "enabled": True,
        "fields": [
            {"name": "keywords", "type": "text", "label": "Zoekwoorden", "required": True, "placeholder": "bijv. BMW 3 serie"},
            {"name": "price_min", "type": "number", "label": "Min Prijs (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Prijs (€)", "required": False},
            {"name": "year_min", "type": "number", "label": "Min Bouwjaar", "required": False},
            {"name": "year_max", "type": "number", "label": "Max Bouwjaar", "required": False},
            {"name": "mileage_max", "type": "number", "label": "Max Kilometers", "required": False},
            {"name": "postcode", "type": "text", "label": "Postcode", "required": False, "placeholder": "bijv. 1234AB"},
            {"name": "distance_km", "type": "number", "label": "Afstand (km)", "required": False},
        ]
    },
    "autoscout24": {
        "id": "autoscout24",
        "name": "AutoScout24",
        "enabled": True,
        "fields": [
            {"name": "make", "type": "select", "label": "Merk", "required": True,
             "options": ["BMW", "Audi", "Mercedes-Benz", "Volkswagen", "Toyota", "Honda", "Ford", "Opel"]},
            {"name": "model", "type": "text", "label": "Model", "required": False, "placeholder": "bijv. 3 Serie"},
            {"name": "price_min", "type": "number", "label": "Min Prijs (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Prijs (€)", "required": False},
            {"name": "year_min", "type": "number", "label": "Min Bouwjaar", "required": False},
            {"name": "year_max", "type": "number", "label": "Max Bouwjaar", "required": False},
            {"name": "mileage_max", "type": "number", "label": "Max Kilometers", "required": False},
            {"name": "fuel_type", "type": "select", "label": "Brandstof", "required": False,
             "options": ["Diesel", "Petrol", "Electric", "Hybrid"]},
        ]
    },
    "mobile_de": {
        "id": "mobile_de",
        "name": "Mobile.de",
        "enabled": True,
        "fields": [
            {"name": "make", "type": "text", "label": "Merk", "required": True, "placeholder": "bijv. BMW"},
            {"name": "model", "type": "text", "label": "Model", "required": False},
            {"name": "price_min", "type": "number", "label": "Min Preis (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Preis (€)", "required": False},
            {"name": "year_min", "type": "number", "label": "Min Baujahr", "required": False},
            {"name": "mileage_max", "type": "number", "label": "Max Kilometerstand", "required": False},
            {"name": "zip_code", "type": "text", "label": "Postleitzahl (DE)", "required": False},
            {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
        ]
    },
    "facebook": {
        "id": "facebook",
        "name": "Facebook Marketplace",
        "enabled": False,
        "fields": [
            {"name": "keywords", "type": "text", "label": "Zoekwoorden", "required": True},
            {"name": "price_max", "type": "number", "label": "Max Prijs (€)", "required": False},
            {"name": "location", "type": "text", "label": "Locatie", "required": False},
            {"name": "radius_km", "type": "number", "label": "Afstand (km)", "required": False},
        ]
    },
    "ebay_kleinanzeigen": {
        "id": "ebay_kleinanzeigen",
        "name": "eBay Kleinanzeigen",
        "enabled": False,
        "fields": [
            {"name": "keywords", "type": "text", "label": "Suchbegriffe", "required": True},
            {"name": "price_min", "type": "number", "label": "Min Preis (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Preis (€)", "required": False},
            {"name": "zip_code", "type": "text", "label": "Postleitzahl", "required": False},
            {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
        ]
    },
}

@app.get("/")
async def root():
    return {
        "message": "Auto Notify Bot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/platforms")
async def get_platforms():
    return {"platforms": list(PLATFORM_SCHEMAS.values())}

@app.get("/api/stats")
async def get_stats():
    return {
        "total_listings": 142,
        "new_today": 8,
        "platforms_active": 3,
        "last_scan": datetime.now().isoformat()
    }

@app.get("/api/listings")
async def get_listings(limit: int = 50):
    mock_listings = [
        {
            "id": f"listing_{i}",
            "title": f"BMW 3 Series {2015 + i}",
            "price": 15000 + (i * 1000),
            "platform": "marktplaats",
            "url": f"https://example.com/listing_{i}",
            "created_at": datetime.now().isoformat()
        }
        for i in range(min(limit, 10))
    ]
    return {"listings": mock_listings, "total": 142}

@app.get("/api/platforms/{platform_id}/config")
async def get_platform_config(platform_id: str):
    platform = PLATFORM_SCHEMAS.get(platform_id)
    if not platform:
        return {"platform_id": platform_id, "config": {"fields": []}}
    return {"platform_id": platform_id, "config": platform}

@app.post("/api/scrape/test")
async def test_scrape(data: Dict[str, Any]):
    return {
        "success": True,
        "message": f"Test scrape completed",
        "results": {"found": 5}
    }

@app.post("/api/notifications/config")
async def save_notification_config(data: Dict[str, Any]):
    return {"success": True, "message": "Notification config saved"}

@app.post("/api/notifications/test")
async def test_notification(data: Dict[str, Any]):
    return {"success": True, "message": "Test notification sent"}

@app.post("/api/config")
async def save_config(data: Dict[str, Any]):
    return {"success": True, "message": "Configuration saved", "config": data}

# Vercel serverless handler
handler = Mangum(app, lifespan="off")

@app.get("/")
async def root():
    return {
        "message": "Auto Notify Bot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/platforms")
async def get_platforms():
    return {"platforms": MOCK_PLATFORMS}

@app.get("/api/stats")
async def get_stats():
    return {
        "total_listings": 142,
        "new_today": 8,
        "platforms_active": 3,
        "last_scan": datetime.now().isoformat()
    }

@app.get("/api/listings")
async def get_listings(limit: int = 50):
    mock_listings = [
        {
            "id": f"listing_{i}",
            "title": f"BMW 3 Series {2015 + i}",
            "price": 15000 + (i * 1000),
            "platform": "marktplaats",
            "url": f"https://example.com/listing_{i}",
            "created_at": datetime.now().isoformat()
        }
        for i in range(min(limit, 10))
    ]
    return {"listings": mock_listings, "total": 142}

@app.get("/api/platforms/{platform_id}/config")
async def get_platform_config(platform_id: str):
    configs = {
        "marktplaats": {
            "fields": [
                {"name": "search_query", "type": "text", "label": "Search Query", "required": True},
                {"name": "min_price", "type": "number", "label": "Min Price (€)", "required": False},
                {"name": "max_price", "type": "number", "label": "Max Price (€)", "required": False},
            ]
        },
        "autoscout24": {
            "fields": [
                {"name": "make", "type": "text", "label": "Make", "required": True},
                {"name": "model", "type": "text", "label": "Model", "required": False},
            ]
        }
    }
    return {"platform_id": platform_id, "config": configs.get(platform_id, {"fields": []})}

@app.post("/api/scrape/test")
async def test_scrape(data: Dict[str, Any]):
    return {
        "success": True,
        "message": f"Test scrape completed",
        "results": {"found": 5}
    }

# Vercel serverless handler
handler = Mangum(app, lifespan="off")
