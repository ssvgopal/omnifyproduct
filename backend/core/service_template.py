"""
Service Template - Standard patterns for service entry points
Use this as a reference when creating new services
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.middleware.service_auth_middleware import ServiceAuthMiddleware
from backend.core.structured_logging import configure_structured_logging, CorrelationIDMiddleware
from backend.core.metrics import get_metrics_response
from backend.core.service_registry import ServiceType
import os

# Configure structured logging
configure_structured_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    json_output=os.getenv("ENVIRONMENT", "development") == "production"
)

# Create app
app = FastAPI(title="Service Name", version="1.0.0")

# Add correlation ID middleware
app.middleware("http")(CorrelationIDMiddleware())

# Add CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if os.getenv("ENVIRONMENT") == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add service authentication middleware (only in microservices mode)
if os.getenv("DEPLOYMENT_MODE") == "microservices":
    app.add_middleware(ServiceAuthMiddleware, enabled=True)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics_response()

# Health check with dependencies
@app.get("/health")
async def health():
    """Health check with dependency verification"""
    # Implement health checks here
    pass

