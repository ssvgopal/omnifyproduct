"""
Integrations Service - Standalone FastAPI app for platform integrations
Can be deployed as microservice OR included in monolith
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging
import types

# Add backend to path and set working directory
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

# Load environment
load_dotenv(ROOT_DIR / '.env')

from backend.core.service_registry import ServiceType, get_service_port, get_service_description
from backend.core.config_validator import ConfigValidator

# Import routes
from api import (
    triplewhale_routes,
    triplewhale_oauth_routes,
    hubspot_routes,
    hubspot_oauth_routes,
    klaviyo_routes,
    google_ads_oauth_routes,
    meta_ads_oauth_routes,
    linkedin_ads_oauth_routes,
    tiktok_ads_oauth_routes,
    youtube_ads_oauth_routes,
    shopify_oauth_routes,
    stripe_oauth_routes,
    gohighlevel_oauth_routes,
)

logger = logging.getLogger(__name__)

# Global state
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for integrations service"""
    global db
    
    logger.info("Validating environment configuration...")
    ConfigValidator.validate_and_exit(exit_on_critical=True)
    
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'omnify_cloud')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable not set")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Make db available for routes
    agentkit_server_module = types.ModuleType('agentkit_server')
    agentkit_server_module.db = db
    sys.modules['agentkit_server'] = agentkit_server_module
    
    logger.info("✅ Integrations Service started")
    yield
    
    client.close()
    logger.info("Integrations Service stopped")

# Create app
service_type = ServiceType.INTEGRATIONS
app = FastAPI(
    title=f"Omnify {service_type.value.title()} Service",
    description=get_service_description(service_type),
    version="1.0.0",
    lifespan=lifespan
)

# CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include integration routes
app.include_router(triplewhale_routes.router)
app.include_router(triplewhale_oauth_routes.router)
app.include_router(hubspot_routes.router)
app.include_router(hubspot_oauth_routes.router)
app.include_router(klaviyo_routes.router)
app.include_router(google_ads_oauth_routes.router)
app.include_router(meta_ads_oauth_routes.router)
app.include_router(linkedin_ads_oauth_routes.router)
app.include_router(tiktok_ads_oauth_routes.router)
app.include_router(youtube_ads_oauth_routes.router)
app.include_router(shopify_oauth_routes.router)
app.include_router(stripe_oauth_routes.router)
app.include_router(gohighlevel_oauth_routes.router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": service_type.value,
        "routes": len(app.routes),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    return {
        "service": service_type.value,
        "description": get_service_description(service_type),
        "status": "operational",
        "routes": len(app.routes)
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", get_service_port(service_type)))
    uvicorn.run(app, host="0.0.0.0", port=port)

