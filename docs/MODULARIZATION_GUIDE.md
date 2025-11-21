# 🔧 Modularization Guide
## How to Extract Services for K8s/Cloud Functions Deployment

**Date**: November 21, 2025  
**Purpose**: Step-by-step guide to extract services for independent deployment

---

## 🎯 Current vs. Target Architecture

### Current (Monolithic)
```
Single FastAPI App
├── All Routes (33 modules)
├── All Services (60 modules)
└── Shared Global State
```

### Target (Microservices)
```
Auth Service          Integration Service      AgentKit Service
├── auth_routes       ├── triplewhale_routes  ├── agentkit_routes
├── legal_routes      ├── hubspot_routes      ├── workflow_routes
└── email_routes      └── klaviyo_routes      └── execution_routes
```

---

## 📋 Service Extraction Plan

### Service Boundaries Identified

1. **Auth Service** (High Priority)
   - Routes: `auth_routes`, `legal_routes`, `email_verification_routes`, `mfa_routes`, `rbac_routes`, `session_routes`
   - Services: `auth_service`, `email_verification_service`, `mfa_service`, `rbac_service`
   - Dependencies: MongoDB, JWT, SendGrid

2. **Integration Service** (High Priority)
   - Routes: `triplewhale_routes`, `hubspot_routes`, `klaviyo_routes`, `google_ads_oauth_routes`, `meta_ads_oauth_routes`, etc.
   - Services: All platform clients and adapters
   - Dependencies: MongoDB, OAuth2, API keys

3. **AgentKit Service** (Medium Priority)
   - Routes: `agentkit_routes`, `workflow_routes`
   - Services: `agentkit_service`, `real_agentkit_adapter`, `omnify_core_agents`
   - Dependencies: MongoDB, OpenAI API

4. **Analytics Service** (Medium Priority)
   - Routes: `dashboard_routes`, `metrics_routes`, `brain_modules_routes`
   - Services: Analytics and reporting services
   - Dependencies: MongoDB, Redis

5. **Client Onboarding Service** (Low Priority - Can stay in main)
   - Routes: `client_onboarding_routes`, `onboarding_routes`
   - Services: `client_onboarding_service`
   - Dependencies: MongoDB, File storage

---

## 🔧 Step-by-Step: Extract Auth Service

### Step 1: Create Service Directory Structure

```bash
services/
└── auth-service/
    ├── app.py              # FastAPI app for auth service
    ├── Dockerfile          # Service-specific Dockerfile
    ├── requirements.txt    # Only auth dependencies
    └── k8s/
        ├── deployment.yaml
        └── service.yaml
```

### Step 2: Create Service-Specific FastAPI App

```python
# services/auth-service/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Import only auth-related routes
from backend.api.auth_routes import router as auth_router
from backend.api.legal_routes import router as legal_router
from backend.api.email_verification_routes import router as email_verification_router
from backend.api.mfa_routes import router as mfa_router
from backend.api.rbac_routes import router as rbac_router
from backend.api.session_routes import router as session_router

# Import core utilities
from backend.core.config_validator import ConfigValidator
from backend.core.auth import get_current_user

load_dotenv()

app = FastAPI(
    title="Omnify Auth Service",
    description="Authentication, authorization, and legal document service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    
    # Shutdown
    client.close()
    logger.info("Auth Service stopped")

app.router.lifespan_context = lifespan

# Include only auth-related routes
app.include_router(auth_router)
app.include_router(legal_router)
app.include_router(email_verification_router)
app.include_router(mfa_router)
app.include_router(rbac_router)
app.include_router(session_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "auth"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 3: Create Service Dockerfile

```dockerfile
# services/auth-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy only what's needed
COPY services/auth-service/ ./services/auth-service/
COPY backend/api/auth_routes.py backend/api/legal_routes.py \
     backend/api/email_verification_routes.py backend/api/mfa_routes.py \
     backend/api/rbac_routes.py backend/api/session_routes.py \
     backend/api/
COPY backend/services/auth_service.py backend/services/email_verification_service.py \
     backend/services/mfa_service.py backend/services/rbac_service.py \
     backend/services/session_service.py backend/services/
COPY backend/core/ backend/core/
COPY backend/models/ backend/models/
COPY backend/database/ backend/database/

# Install dependencies
COPY requirements-auth.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run service
CMD ["uvicorn", "services.auth_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 4: Create K8s Deployment

```yaml
# services/auth-service/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omnify-auth-service
  labels:
    app: auth-service
    tier: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth
        image: omnify/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: omnify-secrets
              key: MONGO_URL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: omnify-secrets
              key: JWT_SECRET_KEY
        - name: SENDGRID_API_KEY
          valueFrom:
            secretKeyRef:
              name: omnify-secrets
              key: SENDGRID_API_KEY
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
spec:
  selector:
    app: auth-service
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

---

## ☁️ Cloud Functions Example

### Google Cloud Functions

```python
# functions/auth/signup/main.py
from google.cloud import functions_v2
import functions_framework
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json

# Lazy import to reduce cold start
_auth_service = None

def get_auth_service():
    global _auth_service
    if _auth_service is None:
        from backend.services.auth_service import AuthService
        from backend.database.mongodb_schema import MongoDBSchema
        db = MongoDBSchema()
        _auth_service = AuthService(db)
    return _auth_service

@functions_framework.http
def signup_handler(request):
    """Cloud Function handler for user signup"""
    try:
        # Parse request
        data = request.get_json()
        
        # Get service (lazy loaded)
        auth_service = get_auth_service()
        
        # Process signup
        result = auth_service.create_user(data)
        
        return JSONResponse(
            status_code=201,
            content={"success": True, "user_id": result["user_id"]}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

### AWS Lambda

```python
# functions/auth/signup/lambda_function.py
import json
from backend.services.auth_service import AuthService
from backend.database.mongodb_schema import MongoDBSchema

def lambda_handler(event, context):
    """Lambda handler for user signup"""
    try:
        # Parse event
        body = json.loads(event['body'])
        
        # Initialize service
        db = MongoDBSchema()
        auth_service = AuthService(db)
        
        # Process signup
        result = auth_service.create_user(body)
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'success': True,
                'user_id': result['user_id']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
```

---

## 🔄 Inter-Service Communication

### Option 1: HTTP/REST (Recommended)

```python
# backend/core/service_client.py
import httpx
from typing import Dict, Any, Optional

class ServiceClient:
    """Client for inter-service communication"""
    
    SERVICES = {
        'auth': os.getenv('AUTH_SERVICE_URL', 'http://auth-service:80'),
        'integrations': os.getenv('INTEGRATIONS_SERVICE_URL', 'http://integrations-service:80'),
        'agentkit': os.getenv('AGENTKIT_SERVICE_URL', 'http://agentkit-service:80'),
    }
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Call another service"""
        base_url = self.SERVICES.get(service_name)
        if not base_url:
            raise ValueError(f"Service {service_name} not found")
        
        url = f"{base_url}{endpoint}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

### Option 2: Message Queue (For Async Operations)

```python
# Use Kafka/RabbitMQ for async communication
from services.kafka_eventing import kafka_service

async def send_event(service: str, event_type: str, data: Dict):
    """Send event to another service via message queue"""
    await kafka_service.publish_event(
        topic=f"{service}-events",
        event={
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

---

## 📊 Migration Strategy

### Phase 1: Extract High-Traffic Services (Week 1-2)
1. **Auth Service** - Most critical, high traffic
2. **Integration Service** - Independent, can scale separately

### Phase 2: Extract Compute-Intensive Services (Week 2-3)
1. **AgentKit Service** - ML/AI workloads
2. **Analytics Service** - Data processing

### Phase 3: Extract Event-Driven Services (Week 3-4)
1. **Email Service** → Cloud Functions
2. **File Processing** → Cloud Functions
3. **Webhooks** → Cloud Functions

### Phase 4: Complete Migration (Week 4-5)
1. Move remaining services
2. Add service mesh
3. Optimize inter-service communication

---

## ✅ Quick Reference: Service Extraction Checklist

For each service to extract:

- [ ] Create service directory (`services/{service-name}/`)
- [ ] Create service-specific FastAPI app
- [ ] Create service Dockerfile
- [ ] Create K8s manifests (deployment, service, HPA)
- [ ] Update service discovery/registry
- [ ] Create service client for inter-service calls
- [ ] Update main app to remove extracted routes
- [ ] Test service independently
- [ ] Update CI/CD pipeline
- [ ] Deploy to staging
- [ ] Monitor and adjust

---

**Status**: Architecture is **code-modular but deployment-monolithic**  
**Action**: Extract services as needed for scale

