# 🚀 Hybrid Deployment Guide
## Monolithic + Microservices Deployment

**Date**: November 21, 2025  
**Status**: Production Ready  
**Architecture**: Hybrid (Monolith + Microservices)

---

## 📋 Overview

The Omnify platform supports **three deployment modes** from the same codebase:

1. **Monolith** - All services in one container
2. **Microservices** - Each service in separate containers
3. **Hybrid** - Mix of monolith and microservices

---

## 🎯 Quick Start

### Monolith Deployment

```bash
# Windows (cmd)
docker-compose -f ops\docker\docker-compose.monolith.yml up --build

# Windows (Git Bash) / Linux / Mac
docker-compose -f ops/docker/docker-compose.monolith.yml up --build

# Or use script
scripts\deployment\deploy_monolith.sh  # Git Bash
```

**Access**:
- API: http://localhost:8000
- Frontend: http://localhost:3000

---

### Microservices Deployment

```bash
# Windows (cmd)
docker-compose -f ops\docker\docker-compose.microservices.yml up --build

# Windows (Git Bash) / Linux / Mac
docker-compose -f ops/docker/docker-compose.microservices.yml up --build

# Or use script
scripts\deployment\deploy_microservices.sh  # Git Bash
```

**Access**:
- Auth Service: http://localhost:8001
- Integrations Service: http://localhost:8002
- AgentKit Service: http://localhost:8003
- Analytics Service: http://localhost:8004
- Onboarding Service: http://localhost:8005
- ML Service: http://localhost:8006
- Infrastructure Service: http://localhost:8007
- Frontend: http://localhost:3000

---

### Hybrid Deployment

```bash
# Windows (cmd)
docker-compose -f ops\docker\docker-compose.hybrid.yml up --build

# Windows (Git Bash) / Linux / Mac
docker-compose -f ops/docker/docker-compose.hybrid.yml up --build

# Or use script
scripts\deployment\deploy_hybrid.sh  # Git Bash
```

**Access**:
- Monolith API: http://localhost:8000
- Integrations Service (Microservice): http://localhost:8002
- Frontend: http://localhost:3000

---

## 🔧 Service Details

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Monolith | 8000 | All services combined |
| Auth | 8001 | Authentication, legal, MFA, RBAC |
| Integrations | 8002 | Platform integrations |
| AgentKit | 8003 | Agents and workflows |
| Analytics | 8004 | Dashboards and metrics |
| Onboarding | 8005 | Client onboarding |
| ML | 8006 | Predictive intelligence |
| Infrastructure | 8007 | Kong, Temporal, Kafka, etc. |

---

## 🐳 Docker Commands

### Build Individual Service

```bash
# Build auth service
docker build -f services/auth_service/Dockerfile -t omnify/auth-service:latest .

# Build integrations service
docker build -f services/integrations_service/Dockerfile -t omnify/integrations-service:latest .
```

### Run Individual Service

```bash
# Run auth service
docker run -p 8001:8001 \
  -e DEPLOYMENT_MODE=microservices \
  -e SERVICE_NAME=auth \
  -e MONGO_URL=mongodb://localhost:27017 \
  omnify/auth-service:latest
```

---

## ☸️ Kubernetes Deployment

### Deploy All Services

```bash
# Apply all service manifests
kubectl apply -f k8s/services/

# Or deploy individually
kubectl apply -f k8s/services/auth-service.yaml
kubectl apply -f k8s/services/integrations-service.yaml
# ... etc
```

### Check Service Status

```bash
# List all services
kubectl get services

# Check pods
kubectl get pods -l service=auth
kubectl get pods -l service=integrations
```

---

## 🔄 Switching Between Modes

### From Monolith to Microservices

1. Stop monolith:
   ```bash
   docker-compose -f ops/docker/docker-compose.monolith.yml down
   ```

2. Start microservices:
   ```bash
   docker-compose -f ops/docker/docker-compose.microservices.yml up --build
   ```

### From Microservices to Monolith

1. Stop microservices:
   ```bash
   docker-compose -f ops/docker/docker-compose.microservices.yml down
   ```

2. Start monolith:
   ```bash
   docker-compose -f ops/docker/docker-compose.monolith.yml up --build
   ```

---

## 🧪 Testing

### Health Checks

```bash
# Monolith
curl http://localhost:8000/health

# Auth Service
curl http://localhost:8001/health

# Integrations Service
curl http://localhost:8002/health
```

### Service Discovery

In microservices mode, services communicate via HTTP. Service URLs are configured via environment variables:

```bash
AUTH_SERVICE_URL=http://auth-service:80
INTEGRATIONS_SERVICE_URL=http://integrations-service:80
# ... etc
```

---

## 📊 When to Use Each Mode

### Use Monolith When:
- ✅ Small to medium scale (< 1000 users)
- ✅ Simple deployment
- ✅ Development/testing
- ✅ Limited resources

### Use Microservices When:
- ✅ Large scale (> 1000 users)
- ✅ Need independent scaling
- ✅ Different load patterns per service
- ✅ Team autonomy

### Use Hybrid When:
- ✅ Demo flexibility
- ✅ Gradual migration
- ✅ Cost optimization
- ✅ Specific service scaling needs

---

## 🔍 Troubleshooting

### Service Not Starting

1. Check logs:
   ```bash
   docker-compose logs <service-name>
   ```

2. Check environment variables:
   ```bash
   docker-compose config
   ```

3. Verify MongoDB connection:
   ```bash
   docker-compose exec mongodb mongosh
   ```

### Port Conflicts

If ports are already in use, modify `docker-compose.*.yml` files to use different ports.

### Service Communication Issues

In microservices mode, ensure:
- Service URLs are correct
- Services are on the same Docker network
- Health checks are passing

---

## 📚 Additional Resources

- `docs/HYBRID_ARCHITECTURE_ANALYSIS.md` - Detailed architecture
- `docs/COEXISTENCE_FEASIBILITY_SUMMARY.md` - Coexistence analysis
- `backend/core/service_registry.py` - Service registry
- `backend/core/service_client.py` - Inter-service communication

---

**Status**: ✅ **PRODUCTION READY**  
**Last Updated**: November 21, 2025

