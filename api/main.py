"""
FastAPI Backend voor Auto Notify Web App

Endpoints:
- /api/platforms - Platform configuratie
- /api/scrape - Trigger scrape
- /api/listings - Get listings
- /api/stats - Dashboard stats
- /api/notifications - Notificatie config
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

# Import scrapers from original bot
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(title="Auto Notify API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In productie: specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class PlatformCriteria(BaseModel):
    platform: str
    enabled: bool
    criteria: Dict[str, Any]
    check_interval_minutes: int = 15

class ScrapeRequest(BaseModel):
    platform: str
    test_mode: bool = True

class NotificationConfig(BaseModel):
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    discord_enabled: bool = False
    discord_webhook_url: Optional[str] = None
    email_enabled: bool = False

# ==================== PLATFORM CONFIGS ====================

PLATFORM_SCHEMAS = {
    "marktplaats": {
        "name": "Marktplaats.nl",
        "fields": [
            {"name": "keywords", "type": "text", "label": "Zoekwoorden", "required": True},
            {"name": "price_min", "type": "number", "label": "Min Prijs (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Prijs (€)", "required": False},
            {"name": "year_min", "type": "number", "label": "Min Bouwjaar", "required": False},
            {"name": "year_max", "type": "number", "label": "Max Bouwjaar", "required": False},
            {"name": "mileage_max", "type": "number", "label": "Max Kilometers", "required": False},
            {"name": "postcode", "type": "text", "label": "Postcode", "required": False},
            {"name": "distance_km", "type": "number", "label": "Afstand (km)", "required": False},
        ]
    },
    "autoscout": {
        "name": "AutoScout24",
        "fields": [
            {"name": "make", "type": "select", "label": "Merk", "required": True,
             "options": ["BMW", "Audi", "Mercedes-Benz", "Volkswagen", "Toyota", "Honda"]},
            {"name": "model", "type": "text", "label": "Model", "required": False},
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
        "name": "Mobile.de",
        "fields": [
            {"name": "make", "type": "text", "label": "Merk", "required": True},
            {"name": "model", "type": "text", "label": "Model", "required": False},
            {"name": "price_min", "type": "number", "label": "Min Preis (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Preis (€)", "required": False},
            {"name": "year_min", "type": "number", "label": "Min Baujahr", "required": False},
            {"name": "mileage_max", "type": "number", "label": "Max Kilometerstand", "required": False},
            {"name": "zip_code", "type": "text", "label": "Postleitzahl (DE)", "required": False},
            {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
        ]
    },
    "ebay_kleinanzeigen": {
        "name": "eBay Kleinanzeigen",
        "fields": [
            {"name": "keywords", "type": "text", "label": "Suchbegriffe", "required": True},
            {"name": "category", "type": "text", "label": "Kategorie", "default": "216", "required": False},
            {"name": "price_min", "type": "number", "label": "Min Preis (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Preis (€)", "required": False},
            {"name": "zip_code", "type": "text", "label": "Postleitzahl", "required": False},
            {"name": "radius_km", "type": "number", "label": "Umkreis (km)", "required": False},
        ]
    },
    "facebook": {
        "name": "Facebook Marketplace",
        "fields": [
            {"name": "query", "type": "text", "label": "Search Query", "required": True},
            {"name": "price_min", "type": "number", "label": "Min Price (€)", "required": False},
            {"name": "price_max", "type": "number", "label": "Max Price (€)", "required": False},
            {"name": "location", "type": "text", "label": "Location", "required": False},
            {"name": "radius_km", "type": "number", "label": "Radius (km)", "required": False},
        ],
        "warning": "⚠️ Experimental - Requires Facebook login, may result in account restrictions"
    }
}

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {"message": "Auto Notify API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/platforms")
async def get_platforms():
    """Get all platform schemas for dynamic form generation"""
    return {
        "platforms": PLATFORM_SCHEMAS
    }

@app.get("/api/platforms/{platform_name}/schema")
async def get_platform_schema(platform_name: str):
    """Get schema for specific platform"""
    if platform_name not in PLATFORM_SCHEMAS:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    return PLATFORM_SCHEMAS[platform_name]

@app.post("/api/platforms/{platform_name}/validate")
async def validate_criteria(platform_name: str, criteria: Dict[str, Any]):
    """Validate criteria for platform"""
    if platform_name not in PLATFORM_SCHEMAS:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    schema = PLATFORM_SCHEMAS[platform_name]
    errors = []
    
    # Validate required fields
    for field in schema["fields"]:
        if field.get("required") and field["name"] not in criteria:
            errors.append(f"Field '{field['label']}' is required")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    return {"valid": True, "errors": []}

@app.post("/api/platforms/{platform_name}/build-url")
async def build_search_url(platform_name: str, criteria: Dict[str, Any]):
    """Build search URL from criteria"""
    # Import scraper dynamically
    try:
        if platform_name == "marktplaats":
            from scrapers.marktplaats import MarktplaatsScraper
            # Create temporary scraper instance to build URL
            # (We'll implement this method in scrapers)
            url = _build_marktplaats_url(criteria)
        elif platform_name == "autoscout":
            url = _build_autoscout_url(criteria)
        elif platform_name == "mobile_de":
            url = _build_mobile_de_url(criteria)
        elif platform_name == "ebay_kleinanzeigen":
            url = _build_ebay_url(criteria)
        elif platform_name == "facebook":
            url = _build_facebook_url(criteria)
        else:
            raise HTTPException(status_code=404, detail="Platform not found")
        
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scrape/test")
async def test_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Test scrape for platform (returns first 5 results)"""
    # This will trigger actual scraper but limit results
    # For now, return mock data
    return {
        "success": True,
        "platform": request.platform,
        "results_count": 3,
        "listings": [
            {
                "id": "1",
                "title": "BMW 320d Efficient Dynamics",
                "price": 11750.00,
                "location": "Utrecht",
                "url": "https://example.com/1",
                "image_url": "https://via.placeholder.com/400x300",
                "posted_date": "Vandaag, 15:23"
            },
            {
                "id": "2",
                "title": "BMW 320d xDrive Touring",
                "price": 13900.00,
                "location": "Amsterdam",
                "url": "https://example.com/2",
                "image_url": "https://via.placeholder.com/400x300",
                "posted_date": "Gisteren, 10:15"
            },
            {
                "id": "3",
                "title": "BMW 320d M Sport",
                "price": 14500.00,
                "location": "Rotterdam",
                "url": "https://example.com/3",
                "image_url": "https://via.placeholder.com/400x300",
                "posted_date": "2 dagen geleden"
            }
        ]
    }

@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    # Mock data for now
    return {
        "total_listings": 127,
        "new_today": 15,
        "pending_notifications": 3,
        "platforms_active": 4,
        "per_platform": {
            "marktplaats": 45,
            "autoscout": 38,
            "mobile_de": 12,
            "ebay_kleinanzeigen": 32
        },
        "recent_activity": [
            {"platform": "marktplaats", "count": 2, "timestamp": "2026-03-31T14:20:00"},
            {"platform": "autoscout", "count": 1, "timestamp": "2026-03-31T14:15:00"},
        ]
    }

@app.get("/api/listings")
async def get_listings(
    platform: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Get listings from database"""
    # Mock data - implement actual DB query
    return {
        "total": 127,
        "limit": limit,
        "offset": offset,
        "listings": []
    }

@app.post("/api/notifications/config")
async def update_notification_config(config: NotificationConfig):
    """Update notification configuration"""
    # Save to database/config
    return {"success": True, "config": config}

@app.post("/api/notifications/test")
async def test_notification():
    """Send test notification"""
    # Use existing notifier
    return {"success": True, "message": "Test notification sent"}

# ==================== HELPER FUNCTIONS ====================

def _build_marktplaats_url(criteria: Dict[str, Any]) -> str:
    """Build Marktplaats URL from criteria"""
    base = "https://www.marktplaats.nl/l/auto-s/"
    params = []
    
    if "keywords" in criteria:
        params.append(f"query={criteria['keywords']}")
    if "price_min" in criteria:
        params.append(f"priceFrom={criteria['price_min']}")
    if "price_max" in criteria:
        params.append(f"priceTo={criteria['price_max']}")
    
    return base + "?" + "&".join(params) if params else base

def _build_autoscout_url(criteria: Dict[str, Any]) -> str:
    base = "https://www.autoscout24.nl/lst"
    make = criteria.get("make", "").lower().replace(" ", "-")
    model = criteria.get("model", "").lower().replace(" ", "-")
    
    if make and model:
        url = f"{base}/{make}/{model}"
    elif make:
        url = f"{base}/{make}"
    else:
        url = base
    
    params = []
    if "price_min" in criteria:
        params.append(f"pricefrom={criteria['price_min']}")
    
    return url + "?" + "&".join(params) if params else url

def _build_mobile_de_url(criteria: Dict[str, Any]) -> str:
    return "https://www.mobile.de/auto/search.html"

def _build_ebay_url(criteria: Dict[str, Any]) -> str:
    keywords = criteria.get("keywords", "auto").replace(" ", "+")
    return f"https://www.kleinanzeigen.de/s-autos/{keywords}/k0c216?format=rss"

def _build_facebook_url(criteria: Dict[str, Any]) -> str:
    return "https://www.facebook.com/marketplace/search"

# Entry point for Vercel
app = app
