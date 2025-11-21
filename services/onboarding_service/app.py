"""
Onboarding Service - Standalone FastAPI app for client onboarding
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

ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

load_dotenv(ROOT_DIR / '.env')

from backend.core.service_registry import ServiceType, get_service_port, get_service_description
from backend.core.config_validator import ConfigValidator

from api import (
    client_onboarding_routes,
    onboarding_routes,
)

logger = logging.getLogger(__name__)
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db
    
    logger.info("Validating environment configuration...")
    ConfigValidator.validate_and_exit(exit_on_critical=True)
    
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'omnify_cloud')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable not set")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    agentkit_server_module = types.ModuleType('agentkit_server')
    agentkit_server_module.db = db
    sys.modules['agentkit_server'] = agentkit_server_module
    
    logger.info("✅ Onboarding Service started")
    yield
    
    client.close()
    logger.info("Onboarding Service stopped")

service_type = ServiceType.ONBOARDING
app = FastAPI(
    title=f"Omnify {service_type.value.title()} Service",
    description=get_service_description(service_type),
    version="1.0.0",
    lifespan=lifespan
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(client_onboarding_routes.router)
app.include_router(onboarding_routes.router)

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

