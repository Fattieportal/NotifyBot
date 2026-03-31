from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import sys
import os

# Add web-app/api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web-app', 'api'))

# Import the main app from web-app/api/main.py
try:
    from main import app as fastapi_app
    from main import PLATFORM_SCHEMAS
except ImportError:
    # Fallback if import fails
    fastapi_app = FastAPI(title="Auto Notify API")
    
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @fastapi_app.get("/")
    async def root():
        return {"message": "Auto Notify API", "status": "running"}
    
    @fastapi_app.get("/health")
    async def health():
        return {"status": "healthy"}

# Export for Vercel
app = fastapi_app
