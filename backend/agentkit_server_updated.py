"""
AgentKit-First Server for Omnify Cloud Connect
Main FastAPI application with AgentKit integration and comprehensive tracing
"""

from fastapi import FastAPI, Depends, Request, Response, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Import tracing middleware
from middleware.tracing_middleware import TracingMiddleware, PerformanceMonitoringMiddleware, SecurityHeadersMiddleware

# Import routes
from api.agentkit_routes import router as agentkit_router
from api.auth_routes import router as auth_router
from api.admin_routes import router as admin_router

# Import services
from services.agentkit_service import AgentKitService
from services.auth_service import AuthService
from services.structured_logging import logger
from database.mongodb_schema import MongoDBSchema

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
    logger.info("🚀 Starting Omnify Cloud Connect (AgentKit-First) with comprehensive tracing...")

    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

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
    logger.info("✅ Database schema initialized")

    # Initialize AgentKit service
    agentkit_api_key = os.environ.get('AGENTKIT_API_KEY', '')
    agentkit_service = AgentKitService(db=db, agentkit_api_key=agentkit_api_key)
    logger.info("✅ AgentKit service initialized")

    # Initialize Auth service
    jwt_secret = os.environ.get('JWT_SECRET_KEY', 'omnify-cloud-connect-secret-key-change-in-production')
    jwt_algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
    auth_service = AuthService(db=db, jwt_secret=jwt_secret, jwt_algorithm=jwt_algorithm)
    logger.info("✅ Auth service initialized")

    # Initialize log collection for admin dashboard
    await db.logs.create_index([("timestamp", -1)])
    await db.logs.create_index([("level", 1)])
    await db.logs.create_index([("context.user_id", 1)])
    await db.logs.create_index([("context.workflow_id", 1)])
    await db.logs.create_index([("event_type", 1)])
    logger.info("✅ Log indexes created for admin dashboard")

    logger.info("🎉 Omnify Cloud Connect started successfully with full observability")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Omnify Cloud Connect...")
    client.close()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Omnify Cloud Connect (AgentKit-First)",
    version="2.0.0",
    description="Enterprise campaign intelligence platform powered by OpenAI AgentKit with comprehensive tracing and monitoring",
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

# Add comprehensive tracing middleware
app.add_middleware(TracingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=1000.0)
app.add_middleware(SecurityHeadersMiddleware)


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
app.include_router(admin_router)


# ========== CORE API ENDPOINTS ==========

@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "Omnify Cloud Connect - AgentKit-First Architecture with Comprehensive Tracing",
        "version": "2.0.0",
        "architecture": "AgentKit-First (No Cloud Functions)",
        "tracing": "Full observability enabled",
        "status": "operational",
        "features": [
            "Creative Intelligence Agent",
            "Marketing Automation Agent",
            "Client Management Agent",
            "Analytics Agent",
            "Workflow Orchestration",
            "SOC 2 Compliance",
            "Multi-tenant Isolation",
            "Comprehensive Tracing & Logging",
            "Admin Analysis Dashboard",
            "Real-time Performance Monitoring"
        ],
        "observability": {
            "logs": "Structured JSON with correlation IDs",
            "tracing": "Distributed request tracing",
            "monitoring": "Performance and error tracking",
            "dashboard": "Admin interface for issue analysis",
            "retention": "30 days log retention"
        }
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with tracing"""
    start_time = datetime.utcnow()

    health_status = {
        "status": "healthy",
        "services": {
            "database": "unknown",
            "agentkit": "operational",
            "api": "operational",
            "tracing": "operational"
        },
        "metrics": {
            "response_time_ms": None,
            "uptime": "unknown",
            "version": "2.0.0"
        },
        "timestamp": start_time.isoformat()
    }

    try:
        # Check database connection
        if db is not None:
            await db.command("ping")
            health_status["services"]["database"] = "healthy"
        else:
            health_status["services"]["database"] = "not_initialized"
            health_status["status"] = "degraded"

    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=e)
        health_status["services"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"

    # Calculate response time
    end_time = datetime.utcnow()
    response_time = (end_time - start_time).total_seconds() * 1000
    health_status["metrics"]["response_time_ms"] = round(response_time, 2)

    # Log health check
    logger.info(
        f"Health check completed: {health_status['status']}",
        event_type='health_check',
        status=health_status['status'],
        response_time_ms=response_time
    )

    return health_status


@app.get("/api/info")
async def api_info():
    """API information endpoint with tracing details"""
    return {
        "name": "Omnify Cloud Connect API",
        "version": "2.0.0",
        "architecture": "AgentKit-First with Comprehensive Tracing",
        "database": "MongoDB with structured logging",
        "cloud_functions": "None (AgentKit handles orchestration)",
        "tracing": {
            "middleware": "Request tracing, performance monitoring, security headers",
            "logging": "Structured JSON with correlation IDs",
            "aggregation": "Loki + Grafana stack",
            "retention": "30 days",
            "analysis": "Admin dashboard with automated insights"
        },
        "endpoints": {
            "agents": "/api/agentkit/agents",
            "workflows": "/api/agentkit/workflows",
            "executions": "/api/agentkit/executions",
            "compliance": "/api/agentkit/compliance",
            "metrics": "/api/agentkit/metrics",
            "admin": "/api/admin/logs",
            "health": "/health"
        },
        "documentation": "/docs",
        "observability": "/api/admin/system-health"
    }


# ========== LOGGING ENDPOINTS ==========

@app.post("/api/logs/frontend")
async def receive_frontend_logs(request: Request):
    """Receive logs from frontend applications"""
    try:
        log_data = await request.json()

        # Add server timestamp and source
        log_data['timestamp'] = datetime.utcnow().isoformat()
        log_data['source'] = 'frontend'
        log_data['_id'] = None  # Let MongoDB generate

        # Store in database
        await db.logs.insert_one(log_data)

        return {"status": "received"}

    except Exception as e:
        logger.error(f"Failed to receive frontend logs: {str(e)}", exc_info=e)
        raise HTTPException(status_code=500, detail="Failed to process logs")


# ========== ORGANIZATION SETUP ENDPOINT ==========

@app.post("/api/organizations/setup")
async def setup_organization(
    organization_data: dict,
    db=Depends(get_db)
):
    """Set up a new organization with default agents and tracing"""
    start_time = datetime.utcnow()

    try:
        organization_id = organization_data.get("organization_id")
        user_id = organization_data.get("user_id")

        if not organization_id or not user_id:
            logger.warning("Organization setup failed: missing required fields",
                         event_type='organization_setup_failed',
                         organization_id=organization_id,
                         user_id=user_id)
            return {"error": "organization_id and user_id required"}, 400

        # Create organization
        org_doc = {
            "organization_id": organization_id,
            "name": organization_data.get("name"),
            "slug": organization_data.get("slug"),
            "owner_id": user_id,
            "subscription_tier": organization_data.get("subscription_tier", "starter"),
            "created_at": datetime.utcnow().isoformat(),
            "tracing_enabled": True
        }
        await db.organizations.insert_one(org_doc)

        # Create default agents
        schema_manager = MongoDBSchema(db)
        default_agents = await schema_manager.create_default_data(
            organization_id=organization_id,
            user_id=user_id
        )

        # Log successful setup
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(
            f"Organization {organization_id} set up successfully",
            event_type='organization_setup_complete',
            organization_id=organization_id,
            user_id=user_id,
            agents_created=len(default_agents),
            duration_ms=round(duration_ms, 2)
        )

        return {
            "success": True,
            "organization_id": organization_id,
            "agents_created": len(default_agents),
            "agents": [agent["agent_id"] for agent in default_agents],
            "tracing_enabled": True
        }

    except Exception as e:
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(
            f"Error setting up organization: {str(e)}",
            event_type='organization_setup_error',
            organization_id=organization_data.get("organization_id"),
            user_id=organization_data.get("user_id"),
            duration_ms=round(duration_ms, 2),
            exc_info=e
        )
        return {"error": str(e)}, 500


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))

    # Configure uvicorn logging to work with our structured logging
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr"
            }
        },
        "root": {
            "handlers": ["default"],
            "level": "INFO"
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False
            }
        }
    }

    uvicorn.run(
        "agentkit_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
        log_config=log_config
    )
