from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime

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

# Mock data for development
MOCK_PLATFORMS = [
    {"id": "marktplaats", "name": "Marktplaats", "enabled": True},
    {"id": "autoscout24", "name": "AutoScout24", "enabled": True},
    {"id": "mobile_de", "name": "Mobile.de", "enabled": True},
    {"id": "facebook", "name": "Facebook Marketplace", "enabled": False},
    {"id": "ebay_kleinanzeigen", "name": "eBay Kleinanzeigen", "enabled": False},
]

MOCK_STATS = {
    "total_listings": 142,
    "new_today": 8,
    "platforms_active": 3,
    "last_scan": datetime.now().isoformat()
}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Auto Notify Bot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/platforms",
            "/api/platforms/{platform_id}/config",
            "/api/stats",
            "/api/listings",
            "/api/scrape/test"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/platforms")
async def get_platforms():
    """Get all available platforms"""
    return {"platforms": MOCK_PLATFORMS}


@app.get("/api/platforms/{platform_id}/config")
async def get_platform_config(platform_id: str):
    """Get configuration schema for a specific platform"""
    configs = {
        "marktplaats": {
            "fields": [
                {"name": "search_query", "type": "text", "label": "Search Query", "required": True},
                {"name": "min_price", "type": "number", "label": "Min Price (€)", "required": False},
                {"name": "max_price", "type": "number", "label": "Max Price (€)", "required": False},
                {"name": "category", "type": "select", "label": "Category", "required": True,
                 "options": ["auto's", "motoren", "caravans"]},
            ]
        },
        "autoscout24": {
            "fields": [
                {"name": "make", "type": "text", "label": "Make", "required": True},
                {"name": "model", "type": "text", "label": "Model", "required": False},
                {"name": "min_year", "type": "number", "label": "Min Year", "required": False},
                {"name": "max_price", "type": "number", "label": "Max Price (€)", "required": False},
            ]
        },
        "mobile_de": {
            "fields": [
                {"name": "make", "type": "text", "label": "Make", "required": True},
                {"name": "model", "type": "text", "label": "Model", "required": False},
                {"name": "min_year", "type": "number", "label": "Min Year", "required": False},
                {"name": "max_mileage", "type": "number", "label": "Max Mileage (km)", "required": False},
            ]
        }
    }
    
    if platform_id not in configs:
        return {"error": "Platform not found"}, 404
    
    return {"platform_id": platform_id, "config": configs[platform_id]}


@app.post("/api/platforms/{platform_id}/config")
async def save_platform_config(platform_id: str, config: Dict[str, Any]):
    """Save configuration for a specific platform"""
    return {
        "success": True,
        "message": f"Configuration saved for {platform_id}",
        "config": config
    }


@app.get("/api/stats")
async def get_stats():
    """Get statistics"""
    return MOCK_STATS


@app.get("/api/listings")
async def get_listings(limit: int = 50, offset: int = 0):
    """Get recent listings"""
    mock_listings = [
        {
            "id": f"listing_{i}",
            "title": f"BMW 3 Series {2015 + i}",
            "price": 15000 + (i * 1000),
            "platform": MOCK_PLATFORMS[i % len(MOCK_PLATFORMS)]["id"],
            "url": f"https://example.com/listing_{i}",
            "image": f"https://via.placeholder.com/300x200?text=Car+{i}",
            "created_at": datetime.now().isoformat()
        }
        for i in range(min(limit, 10))
    ]
    
    return {
        "listings": mock_listings,
        "total": 142,
        "limit": limit,
        "offset": offset
    }


@app.post("/api/scrape/test")
async def test_scrape(data: Dict[str, Any]):
    """Test scraping with provided configuration"""
    platform = data.get("platform")
    config = data.get("config", {})
    
    return {
        "success": True,
        "message": f"Test scrape completed for {platform}",
        "results": {
            "found": 5,
            "sample": [
                {
                    "title": "Test Car 1",
                    "price": 12000,
                    "url": "https://example.com/test1"
                },
                {
                    "title": "Test Car 2",
                    "price": 15000,
                    "url": "https://example.com/test2"
                }
            ]
        },
        "config_used": config
    }


@app.get("/api/notifications/settings")
async def get_notification_settings():
    """Get notification settings"""
    return {
        "telegram": {
            "enabled": True,
            "chat_id": "716446644",
            "token_configured": True
        },
        "email": {
            "enabled": False,
            "address": ""
        }
    }


@app.post("/api/notifications/settings")
async def save_notification_settings(settings: Dict[str, Any]):
    """Save notification settings"""
    return {
        "success": True,
        "message": "Notification settings saved",
        "settings": settings
    }


@app.post("/api/notifications/test")
async def test_notification():
    """Send a test notification"""
    return {
        "success": True,
        "message": "Test notification sent successfully"
    }
