"""
Auth Service - Standalone FastAPI app for authentication
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

# Add backend to path and set working directory
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))
os.chdir(ROOT_DIR)

# Load environment
load_dotenv(ROOT_DIR / '.env')

from backend.core.service_registry import ServiceType, get_service_port, get_service_description
from backend.core.config_validator import ConfigValidator

# Import routes (using relative imports from backend directory)
from api import (
    auth_routes,
    legal_routes,
    email_verification_routes,
    mfa_routes,
    rbac_routes,
    session_routes,
)

logger = logging.getLogger(__name__)

# Global state (minimal)
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for auth service"""
    global db
    
    # Validate config
    logger.info("Validating environment configuration...")
    ConfigValidator.validate_and_exit(exit_on_critical=True)
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'omnify_cloud')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable not set")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Make db available globally for routes that import it from agentkit_server
    # Create a minimal agentkit_server module in memory
    import types
    agentkit_server_module = types.ModuleType('agentkit_server')
    agentkit_server_module.db = db
    sys.modules['agentkit_server'] = agentkit_server_module
    
    logger.info("✅ Auth Service started")
    yield
    
    client.close()
    logger.info("Auth Service stopped")

# Create app
service_type = ServiceType.AUTH
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

# Include auth-related routes
app.include_router(auth_routes.router)
app.include_router(legal_routes.router)
app.include_router(email_verification_routes.router)
app.include_router(mfa_routes.router)
app.include_router(rbac_routes.router)
app.include_router(session_routes.router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": service_type.value,
        "routes": len(app.routes),
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
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
