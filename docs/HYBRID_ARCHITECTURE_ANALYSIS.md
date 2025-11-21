# 🔀 Hybrid Architecture Analysis
## Monolithic + Microservices Coexistence Strategy

**Date**: November 21, 2025  
**Goal**: Enable both monolithic and microservices deployment from the same codebase  
**Use Case**: Demo flexibility - show both deployment models

---

## ✅ Current Codebase Analysis

### What Makes Coexistence Possible

#### 1. **Independent Route Modules** ✅
- **Status**: All routes are `APIRouter` instances
- **Location**: `backend/api/*.py` (56 route files)
- **Independence**: Each router can be included/excluded independently
- **Pattern**: `router = APIRouter(prefix="/api/...", tags=[...])`

**Example**:
```python
# backend/api/auth_routes.py
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
# Can be used in monolith OR microservice
```

#### 2. **Service Layer Independence** ✅
- **Status**: Services are Python classes with dependency injection
- **Location**: `backend/services/*.py` (60+ service files)
- **Independence**: Services receive dependencies via constructor
- **Pattern**: `def __init__(self, db: AsyncIOMotorDatabase)`

**Example**:
```python
# backend/services/auth_service.py
class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # No global state dependencies
```

#### 3. **Database Dependency Injection** ✅
- **Status**: Services receive database via dependency injection
- **Pattern**: `get_database()` function or constructor injection
- **Flexibility**: Can use same DB or separate DBs per service

#### 4. **No Hard-Coded Service Dependencies** ✅
- **Status**: Routes don't call other services directly
- **Pattern**: All communication via database or HTTP
- **Flexibility**: Can add service-to-service HTTP calls when needed

---

## 🎯 Hybrid Architecture Design

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED CODEBASE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Route Modules │  │   Services   │  │    Models    │     │
│  │  (56 files)   │  │  (60 files)  │  │  (Pydantic)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  MONOLITH    │  │ MICROSERVICE │  │ MICROSERVICE │
│  Entry Point │  │ Entry Point  │  │ Entry Point  │
│              │  │              │  │              │
│ agentkit_    │  │ services/    │  │ services/    │
│ server.py    │  │ auth/        │  │ integrations/ │
│              │  │ app.py       │  │ app.py       │
│ All routes   │  │ Auth routes  │  │ Integration  │
│ in one app   │  │ only         │  │ routes only  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🔧 Implementation Strategy

### Phase 1: Service Grouping (Define Service Boundaries)

Create a service registry that groups routes by service:

```python
# backend/core/service_registry.py
"""
Service Registry - Groups routes by service for microservices deployment
"""

from typing import Dict, List
from enum import Enum

class ServiceType(str, Enum):
    """Service types for deployment"""
    AUTH = "auth"
    INTEGRATIONS = "integrations"
    AGENTKIT = "agentkit"
    ANALYTICS = "analytics"
    ONBOARDING = "onboarding"
    ML = "ml"
    INFRASTRUCTURE = "infrastructure"

# Service route mapping
SERVICE_ROUTES: Dict[ServiceType, List[str]] = {
    ServiceType.AUTH: [
        "api.auth_routes",
        "api.legal_routes",
        "api.email_verification_routes",
        "api.mfa_routes",
        "api.rbac_routes",
        "api.session_routes",
    ],
    ServiceType.INTEGRATIONS: [
        "api.triplewhale_routes",
        "api.triplewhale_oauth_routes",
        "api.hubspot_routes",
        "api.hubspot_oauth_routes",
        "api.klaviyo_routes",
        "api.google_ads_oauth_routes",
        "api.meta_ads_oauth_routes",
        "api.linkedin_ads_oauth_routes",
        "api.tiktok_ads_oauth_routes",
        "api.youtube_ads_oauth_routes",
        "api.shopify_oauth_routes",
        "api.stripe_oauth_routes",
        "api.gohighlevel_oauth_routes",
    ],
    ServiceType.AGENTKIT: [
        "api.agentkit_routes",
        "api.workflow_routes",
    ],
    ServiceType.ANALYTICS: [
        "api.dashboard_routes",
        "api.metrics_routes",
        "api.brain_modules_routes",
        "api.advanced_analytics_routes",
        "api.advanced_reporting_routes",
    ],
    ServiceType.ONBOARDING: [
        "api.client_onboarding_routes",
        "api.onboarding_routes",
    ],
    ServiceType.ML: [
        "api.predictive_routes",
        "api.predictive_intelligence_routes",
        "api.ai_ml_enhancements_routes",
    ],
    ServiceType.INFRASTRUCTURE: [
        "api.kong_routes",
        "api.temporal_routes",
        "api.airbyte_routes",
        "api.kafka_routes",
        "api.metabase_routes",
    ],
}

# Service dependencies (what services each service needs)
SERVICE_DEPENDENCIES: Dict[ServiceType, List[ServiceType]] = {
    ServiceType.AUTH: [],
    ServiceType.INTEGRATIONS: [ServiceType.AUTH],  # Needs auth for user context
    ServiceType.AGENTKIT: [ServiceType.AUTH],
    ServiceType.ANALYTICS: [ServiceType.AUTH, ServiceType.INTEGRATIONS],
    ServiceType.ONBOARDING: [ServiceType.AUTH],
    ServiceType.ML: [ServiceType.AUTH, ServiceType.ANALYTICS],
    ServiceType.INFRASTRUCTURE: [],
}

def get_routes_for_service(service_type: ServiceType) -> List[str]:
    """Get list of route modules for a service"""
    return SERVICE_ROUTES.get(service_type, [])

def get_service_dependencies(service_type: ServiceType) -> List[ServiceType]:
    """Get dependencies for a service"""
    return SERVICE_DEPENDENCIES.get(service_type, [])
```

---

### Phase 2: Create Service-Specific Entry Points

Create minimal FastAPI apps for each service:

```python
# services/auth_service/app.py
"""
Auth Service - Standalone FastAPI app for authentication
Can be deployed as microservice OR included in monolith
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
import logging

from backend.core.service_registry import ServiceType, get_routes_for_service
from backend.core.config_validator import ConfigValidator

logger = logging.getLogger(__name__)

# Load environment
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

# Global state (minimal)
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for auth service"""
    global db
    
    # Validate config
    ConfigValidator.validate_and_exit(exit_on_critical=True)
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'omnify_cloud')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    logger.info("✅ Auth Service started")
    yield
    
    client.close()
    logger.info("Auth Service stopped")

# Create app
app = FastAPI(
    title="Omnify Auth Service",
    description="Authentication, authorization, and legal documents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth-related routes
from backend.api import (
    auth_routes,
    legal_routes,
    email_verification_routes,
    mfa_routes,
    rbac_routes,
    session_routes,
)

app.include_router(auth_routes.router)
app.include_router(legal_routes.router)
app.include_router(email_verification_routes.router)
app.include_router(mfa_routes.router)
app.include_router(rbac_routes.router)
app.include_router(session_routes.router)

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "auth",
        "routes": len(app.routes)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
```

---

### Phase 3: Update Monolith to Support Selective Loading

Modify `agentkit_server.py` to support both modes:

```python
# backend/agentkit_server.py (updated)
import os
from fastapi import FastAPI

# ... existing imports ...

# NEW: Deployment mode detection
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "monolith")  # or "microservices"
SERVICE_NAME = os.getenv("SERVICE_NAME", None)  # e.g., "auth", "integrations"

app = FastAPI(title="Omnify Cloud Connect")

# ... existing lifespan setup ...

# NEW: Conditional route loading
if DEPLOYMENT_MODE == "monolith" or SERVICE_NAME is None:
    # Monolith mode: Include all routes
    app.include_router(auth_router)
    app.include_router(legal_router)
    app.include_router(agentkit_router)
    # ... all other routes ...
    
elif DEPLOYMENT_MODE == "microservices" and SERVICE_NAME:
    # Microservices mode: Include only specified service routes
    from backend.core.service_registry import ServiceType, get_routes_for_service
    
    service_type = ServiceType(SERVICE_NAME)
    route_modules = get_routes_for_service(service_type)
    
    # Dynamically import and include routes
    for route_module in route_modules:
        module = __import__(route_module, fromlist=['router'])
        app.include_router(module.router)
```

---

### Phase 4: Create Service Dockerfiles

Create Dockerfiles that work for both modes:

```dockerfile
# services/auth_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared code
COPY backend/ ./backend/
COPY services/auth_service/ ./services/auth_service/

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set deployment mode
ENV DEPLOYMENT_MODE=microservices
ENV SERVICE_NAME=auth

# Run service-specific app OR monolith
CMD ["python", "-m", "services.auth_service.app"]
```

---

### Phase 5: Create Deployment Scripts

Create scripts for easy switching:

```python
# scripts/deploy_monolith.py
"""Deploy as monolith"""
import os
os.environ["DEPLOYMENT_MODE"] = "monolith"
os.environ["SERVICE_NAME"] = ""

# Run main server
from backend.agentkit_server import app
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

```python
# scripts/deploy_microservice.py
"""Deploy as microservice"""
import sys
import os

service_name = sys.argv[1]  # e.g., "auth"
os.environ["DEPLOYMENT_MODE"] = "microservices"
os.environ["SERVICE_NAME"] = service_name

# Run service-specific app
if service_name == "auth":
    from services.auth_service.app import app
elif service_name == "integrations":
    from services.integrations_service.app import app
# ... etc

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📋 Service Grouping Plan

### Service 1: Auth Service
**Routes**:
- `auth_routes`
- `legal_routes`
- `email_verification_routes`
- `mfa_routes`
- `rbac_routes`
- `session_routes`

**Dependencies**: None (base service)

**Port**: 8001

---

### Service 2: Integrations Service
**Routes**:
- `triplewhale_routes` + `triplewhale_oauth_routes`
- `hubspot_routes` + `hubspot_oauth_routes`
- `klaviyo_routes`
- `google_ads_oauth_routes`
- `meta_ads_oauth_routes`
- `linkedin_ads_oauth_routes`
- `tiktok_ads_oauth_routes`
- `youtube_ads_oauth_routes`
- `shopify_oauth_routes`
- `stripe_oauth_routes`
- `gohighlevel_oauth_routes`

**Dependencies**: Auth Service (for user context)

**Port**: 8002

---

### Service 3: AgentKit Service
**Routes**:
- `agentkit_routes`
- `workflow_routes`

**Dependencies**: Auth Service

**Port**: 8003

---

### Service 4: Analytics Service
**Routes**:
- `dashboard_routes`
- `metrics_routes`
- `brain_modules_routes`
- `advanced_analytics_routes`
- `advanced_reporting_routes`

**Dependencies**: Auth Service, Integrations Service

**Port**: 8004

---

### Service 5: Onboarding Service
**Routes**:
- `client_onboarding_routes`
- `onboarding_routes`

**Dependencies**: Auth Service

**Port**: 8005

---

### Service 6: ML Service
**Routes**:
- `predictive_routes`
- `predictive_intelligence_routes`
- `ai_ml_enhancements_routes`

**Dependencies**: Auth Service, Analytics Service

**Port**: 8006

---

### Service 7: Infrastructure Service
**Routes**:
- `kong_routes`
- `temporal_routes`
- `airbyte_routes`
- `kafka_routes`
- `metabase_routes`

**Dependencies**: None

**Port**: 8007

---

## 🚀 Deployment Scenarios

### Scenario 1: Monolith (Current)
```bash
# Environment
DEPLOYMENT_MODE=monolith

# Run
python -m backend.agentkit_server

# Or Docker
docker run -e DEPLOYMENT_MODE=monolith omnify-api:latest
```

**Result**: Single FastAPI app with all routes

---

### Scenario 2: Microservices (K8s)
```bash
# Auth Service
kubectl apply -f k8s/services/auth-service.yaml

# Integrations Service
kubectl apply -f k8s/services/integrations-service.yaml

# ... etc
```

**Result**: Each service runs independently

---

### Scenario 3: Hybrid (Demo)
```bash
# Run monolith for most services
DEPLOYMENT_MODE=monolith python -m backend.agentkit_server

# Run specific service as microservice (e.g., for demo)
DEPLOYMENT_MODE=microservices SERVICE_NAME=auth python -m services.auth_service.app
```

**Result**: Mix of monolith and microservices

---

## 🔄 Inter-Service Communication

### Option 1: HTTP (For Microservices)
```python
# backend/core/service_client.py
import httpx
import os

class ServiceClient:
    """Client for calling other services"""
    
    SERVICES = {
        'auth': os.getenv('AUTH_SERVICE_URL', 'http://auth-service:80'),
        'integrations': os.getenv('INTEGRATIONS_SERVICE_URL', 'http://integrations-service:80'),
    }
    
    async def call_auth_service(self, endpoint: str, method: str = 'GET', data: dict = None):
        """Call auth service"""
        if os.getenv('DEPLOYMENT_MODE') == 'monolith':
            # In monolith, call directly
            from backend.api.auth_routes import router
            # Use internal function call
            return await self._call_internal(router, endpoint, data)
        else:
            # In microservices, call via HTTP
            url = f"{self.SERVICES['auth']}{endpoint}"
            async with httpx.AsyncClient() as client:
                return await client.request(method, url, json=data)
```

### Option 2: Database (Current - Works for Both)
- Services communicate via shared MongoDB
- No changes needed
- Works in both monolith and microservices

---

## 📊 Comparison: Monolith vs Microservices

| Aspect | Monolith | Microservices | Hybrid |
|--------|----------|---------------|--------|
| **Deployment** | Single container | Multiple containers | Mix |
| **Scaling** | Scale entire app | Scale per service | Selective scaling |
| **Complexity** | Low | High | Medium |
| **Development** | Simple | Complex | Flexible |
| **Demo** | One endpoint | Multiple endpoints | Best of both |

---

## ✅ Implementation Checklist

### Phase 1: Foundation (Week 1)
- [ ] Create `backend/core/service_registry.py`
- [ ] Define service boundaries
- [ ] Document service dependencies

### Phase 2: Service Entry Points (Week 1-2)
- [ ] Create `services/auth_service/app.py`
- [ ] Create `services/integrations_service/app.py`
- [ ] Create `services/agentkit_service/app.py`
- [ ] Create `services/analytics_service/app.py`
- [ ] Create `services/onboarding_service/app.py`
- [ ] Create `services/ml_service/app.py`
- [ ] Create `services/infrastructure_service/app.py`

### Phase 3: Update Monolith (Week 2)
- [ ] Add `DEPLOYMENT_MODE` support to `agentkit_server.py`
- [ ] Add conditional route loading
- [ ] Test monolith mode still works

### Phase 4: Docker & K8s (Week 2-3)
- [ ] Create service-specific Dockerfiles
- [ ] Create K8s manifests for each service
- [ ] Create docker-compose for microservices
- [ ] Update existing docker-compose for monolith

### Phase 5: Inter-Service Communication (Week 3)
- [ ] Create `ServiceClient` for HTTP calls
- [ ] Add service discovery
- [ ] Test service-to-service calls

### Phase 6: Testing & Documentation (Week 3-4)
- [ ] Test monolith deployment
- [ ] Test microservices deployment
- [ ] Test hybrid deployment
- [ ] Update deployment docs
- [ ] Create demo scripts

---

## 🎯 Demo Scenarios

### Demo 1: Monolith
```bash
# Show single deployment
docker-compose -f docker-compose.monolith.yml up

# All services accessible via one endpoint
curl http://localhost:8000/api/auth/login
curl http://localhost:8000/api/integrations/triplewhale/connect
```

### Demo 2: Microservices
```bash
# Show multiple services
docker-compose -f docker-compose.microservices.yml up

# Each service on different port
curl http://localhost:8001/api/auth/login  # Auth service
curl http://localhost:8002/api/integrations/triplewhale/connect  # Integrations service
```

### Demo 3: Hybrid
```bash
# Show monolith + one microservice
docker-compose -f docker-compose.hybrid.yml up

# Most services in monolith
curl http://localhost:8000/api/auth/login

# One service as microservice (e.g., for scaling demo)
curl http://localhost:8001/api/integrations/triplewhale/connect
```

---

## 🎯 Conclusion

### Feasibility: ✅ **HIGHLY FEASIBLE**

**Why it works**:
1. ✅ Routes are already independent (`APIRouter`)
2. ✅ Services use dependency injection (no global state)
3. ✅ Database is externalized (MongoDB Atlas)
4. ✅ No hard-coded service dependencies

### Benefits:
- ✅ **Demo Flexibility**: Show both architectures
- ✅ **Gradual Migration**: Move services one at a time
- ✅ **Cost Optimization**: Run monolith for dev, microservices for prod
- ✅ **Team Autonomy**: Different teams can own different services

### Implementation Effort:
- **Phase 1-2**: 1-2 weeks (service entry points)
- **Phase 3-4**: 1 week (Docker/K8s)
- **Phase 5-6**: 1 week (testing/docs)

**Total**: 3-4 weeks for full hybrid capability

---

**Status**: ✅ **COEXISTENCE IS POSSIBLE**  
**Recommendation**: Implement hybrid architecture for maximum flexibility

