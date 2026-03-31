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

# Mock data
MOCK_PLATFORMS = [
    {"id": "marktplaats", "name": "Marktplaats", "enabled": True},
    {"id": "autoscout24", "name": "AutoScout24", "enabled": True},
    {"id": "mobile_de", "name": "Mobile.de", "enabled": True},
    {"id": "facebook", "name": "Facebook Marketplace", "enabled": False},
    {"id": "ebay_kleinanzeigen", "name": "eBay Kleinanzeigen", "enabled": False},
]

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
