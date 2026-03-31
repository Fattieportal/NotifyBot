from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auto Notify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import main app routes
try:
    from main import app as main_app
    # Copy all routes from main_app to app
    app.router.routes = main_app.router.routes
except Exception as e:
    print(f"Could not import main app: {e}")
    
    @app.get("/")
    async def root():
        return {"message": "Auto Notify API", "status": "running"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

# Vercel handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
