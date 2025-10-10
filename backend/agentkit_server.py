"""
AgentKit-First Server for Omnify Cloud Connect
Main FastAPI application with AgentKit integration
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import routes
from api.agentkit_routes import router as agentkit_router
from api.auth_routes import router as auth_router

# Import services
from services.agentkit_service import AgentKitService
from services.auth_service import AuthService
from database.mongodb_schema import MongoDBSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Global variables
db = None
agentkit_service = None
auth_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global db, agentkit_service
    
    # Startup
    logger.info("Starting Omnify Cloud Connect (AgentKit-First)...")
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'omnify_cloud')
    
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable not set")
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Initialize database schema
    schema_manager = MongoDBSchema(db)
    await schema_manager.initialize_schema()
    logger.info("Database schema initialized")
    
    # Initialize AgentKit service
    agentkit_api_key = os.environ.get('AGENTKIT_API_KEY', '')
    agentkit_service = AgentKitService(db=db, agentkit_api_key=agentkit_api_key)
    logger.info("AgentKit service initialized")
    
    # Initialize Auth service
    jwt_secret = os.environ.get('JWT_SECRET_KEY', 'omnify-cloud-connect-secret-key-change-in-production')
    jwt_algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
    auth_service = AuthService(db=db, jwt_secret=jwt_secret, jwt_algorithm=jwt_algorithm)
    logger.info("Auth service initialized")
    
    logger.info("✅ Omnify Cloud Connect started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Omnify Cloud Connect...")
    client.close()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Omnify Cloud Connect (AgentKit-First)",
    version="2.0.0",
    description="Enterprise campaign intelligence platform powered by OpenAI AgentKit",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for AgentKit service
def get_agentkit_service() -> AgentKitService:
    """Dependency to get AgentKit service"""
    if agentkit_service is None:
        raise RuntimeError("AgentKit service not initialized")
    return agentkit_service


def get_db():
    """Dependency to get database"""
    if db is None:
        raise RuntimeError("Database not initialized")
    return db


# Include routers
app.include_router(auth_router)
app.include_router(agentkit_router)


# ========== CORE API ENDPOINTS ==========

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Omnify Cloud Connect - AgentKit-First Architecture",
        "version": "2.0.0",
        "architecture": "AgentKit-First (No Cloud Functions)",
        "status": "operational",
        "features": [
            "Creative Intelligence Agent",
            "Marketing Automation Agent",
            "Client Management Agent",
            "Analytics Agent",
            "Workflow Orchestration",
            "SOC 2 Compliance",
            "Multi-tenant Isolation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "services": {
            "database": db_status,
            "agentkit": "operational",
            "api": "operational"
        },
        "timestamp": "2025-10-10T12:00:00Z"
    }


@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Omnify Cloud Connect API",
        "version": "2.0.0",
        "architecture": "AgentKit-First",
        "database": "MongoDB",
        "cloud_functions": "None (AgentKit handles orchestration)",
        "endpoints": {
            "agents": "/api/agentkit/agents",
            "workflows": "/api/agentkit/workflows",
            "executions": "/api/agentkit/executions",
            "compliance": "/api/agentkit/compliance",
            "metrics": "/api/agentkit/metrics"
        },
        "documentation": "/docs"
    }


# ========== ORGANIZATION SETUP ENDPOINT ==========

@app.post("/api/organizations/setup")
async def setup_organization(
    organization_data: dict,
    db=Depends(get_db)
):
    """Set up a new organization with default agents"""
    try:
        organization_id = organization_data.get("organization_id")
        user_id = organization_data.get("user_id")
        
        if not organization_id or not user_id:
            return {"error": "organization_id and user_id required"}, 400
        
        # Create organization
        org_doc = {
            "organization_id": organization_id,
            "name": organization_data.get("name"),
            "slug": organization_data.get("slug"),
            "owner_id": user_id,
            "subscription_tier": organization_data.get("subscription_tier", "starter"),
            "created_at": "2025-10-10T12:00:00Z"
        }
        await db.organizations.insert_one(org_doc)
        
        # Create default agents
        schema_manager = MongoDBSchema(db)
        default_agents = await schema_manager.create_default_data(
            organization_id=organization_id,
            user_id=user_id
        )
        
        logger.info(f"Organization {organization_id} set up with {len(default_agents)} agents")
        
        return {
            "success": True,
            "organization_id": organization_id,
            "agents_created": len(default_agents),
            "agents": [agent["agent_id"] for agent in default_agents]
        }
    
    except Exception as e:
        logger.error(f"Error setting up organization: {str(e)}")
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "agentkit_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
