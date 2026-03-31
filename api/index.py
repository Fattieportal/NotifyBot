from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path to import from web-app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web-app', 'api'))

from main import app as fastapi_app

# Export for Vercel
app = fastapi_app
