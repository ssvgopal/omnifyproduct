# 🚀 OmniFy Production Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying OmniFy Cloud Connect to production using Docker, Kubernetes, and Helm charts.

## 🏗️ Architecture

### Production Stack
- **Backend**: FastAPI with Python 3.11
- **Frontend**: React with Nginx
- **Database**: MongoDB 7.0
- **Cache**: Redis 7.2
- **Queue**: Celery with Redis broker
- **Monitoring**: Prometheus + Grafana
- **Logging**: Loki + Promtail
- **Ingress**: Nginx Ingress Controller
- **SSL**: Let's Encrypt with cert-manager

### Deployment Options
1. **Docker Compose** (Development/Testing)
2. **Kubernetes** (Production)
3. **Helm Charts** (Production with templating)

---

## 🐳 Docker Compose Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 50GB disk space

### Quick Start
```bash
# Clone repository
git clone https://github.com/omnifyproduct/omnify.git
cd omnify

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env

# Start services
docker compose -f ops/docker/docker-compose.prod.yml up -d

# Check status
docker compose -f ops/docker/docker-compose.prod.yml ps

# View logs
docker compose -f ops/docker/docker-compose.prod.yml logs -f
```

### Environment Variables
```bash
# Database
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=omnify_secure_password_2024
MONGO_DATABASE=omnify
REDIS_PASSWORD=omnify_redis_secure_2024

# Application
SECRET_KEY=omnify_super_secret_key_change_in_production_2024
JWT_SECRET=omnify_jwt_secret_change_in_production_2024

# External APIs
OPENAI_API_KEY=your_openai_api_key
AGENTKIT_API_KEY=your_agentkit_api_key

# Platform Integrations
GOHIGHLEVEL_API_KEY=your_gohighlevel_api_key
META_ACCESS_TOKEN=your_meta_access_token
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_google_ads_developer_token
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret
GOOGLE_ADS_REFRESH_TOKEN=your_google_ads_refresh_token
GOOGLE_ADS_CUSTOMER_ID=your_google_ads_customer_id

# Monitoring
GRAFANA_PASSWORD=omnify_grafana_2024
```

---

## ☸️ Kubernetes Deployment

### Prerequisites
- Kubernetes cluster 1.24+
- kubectl configured
- Helm 3.0+
- cert-manager installed
- nginx-ingress-controller installed

### Namespace Setup
```bash
# Create namespace
kubectl create namespace omnify

# Create secrets
kubectl apply -f ops/k8s/omnify-secrets-template.yaml

# Deploy application
kubectl apply -f ops/k8s/omnify-deployment.yaml

# Check deployment status
kubectl get pods -n omnify
kubectl get services -n omnify
kubectl get ingress -n omnify
```

### Secrets Management
```bash
# Create secrets from template
cp ops/k8s/omnify-secrets-template.yaml ops/k8s/omnify-secrets.yaml

# Edit secrets with actual values
nano ops/k8s/omnify-secrets.yaml

# Apply secrets
kubectl apply -f ops/k8s/omnify-secrets.yaml
```

### Health Checks
```bash
# Check pod health
kubectl get pods -n omnify -o wide

# Check service endpoints
kubectl get endpoints -n omnify

# Check ingress status
kubectl describe ingress omnify-ingress -n omnify

# Test API health
curl -f https://api.omnify.com/health
```

---

## 🎯 Helm Chart Deployment

### Prerequisites
- Helm 3.0+
- Kubernetes cluster
- cert-manager installed
- nginx-ingress-controller installed

### Installation
```bash
# Add dependencies
helm dependency update ops/helm/

# Install with default values
helm install omnify ops/helm/ --namespace omnify --create-namespace

# Install with custom values
helm install omnify ops/helm/ \
  --namespace omnify \
  --create-namespace \
  --values ops/helm/values-production.yaml

# Upgrade existing installation
helm upgrade omnify ops/helm/ \
  --namespace omnify \
  --values ops/helm/values-production.yaml
```

### Custom Values
```bash
# Create production values
cp ops/helm/values.yaml ops/helm/values-production.yaml

# Edit production values
nano ops/helm/values-production.yaml

# Deploy with custom values
helm install omnify ops/helm/ \
  --namespace omnify \
  --create-namespace \
  --values ops/helm/values-production.yaml
```

### Helm Commands
```bash
# List releases
helm list -n omnify

# Get release status
helm status omnify -n omnify

# Get release values
helm get values omnify -n omnify

# Rollback release
helm rollback omnify 1 -n omnify

# Uninstall release
helm uninstall omnify -n omnify
```

---

## 🔧 Configuration

### Backend Configuration
```python
# Environment variables
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
API_WORKERS=4

# Database
MONGODB_URL=mongodb://admin:password@mongodb:27017/omnify?authSource=admin
REDIS_URL=redis://:password@redis:6379/0

# Security
SECRET_KEY=your_secret_key
JWT_SECRET=your_jwt_secret

# External APIs
OPENAI_API_KEY=your_openai_key
AGENTKIT_API_KEY=your_agentkit_key
```

### Frontend Configuration
```javascript
// Environment variables
REACT_APP_API_URL=https://api.omnify.com
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
```

### Monitoring Configuration
```yaml
# Prometheus configuration
prometheus:
  enabled: true
  server:
    persistentVolume:
      enabled: true
      size: 10Gi

# Grafana configuration
grafana:
  enabled: true
  adminPassword: your_password
  persistence:
    enabled: true
    size: 5Gi
```

---

## 📊 Monitoring & Observability

### Health Endpoints
- **Backend Health**: `https://api.omnify.com/health`
- **Frontend Health**: `https://app.omnify.com/`
- **Metrics**: `https://api.omnify.com/metrics`

### Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Loki**: Log aggregation
- **Promtail**: Log collection

### Access Monitoring
```bash
# Grafana
kubectl port-forward -n omnify svc/omnify-grafana 3000:3000
# Access: http://localhost:3000

# Prometheus
kubectl port-forward -n omnify svc/omnify-prometheus 9090:9090
# Access: http://localhost:9090
```

---

## 🔒 Security

### Security Best Practices
1. **Secrets Management**: Use Kubernetes secrets
2. **Network Policies**: Restrict pod communication
3. **Pod Security**: Run as non-root user
4. **Image Security**: Use specific image tags
5. **SSL/TLS**: Enable HTTPS with Let's Encrypt

### SSL Certificate Setup
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@omnify.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions
The CI/CD pipeline includes:
- **Code Quality**: Linting, formatting, type checking
- **Testing**: Unit tests, integration tests, security scans
- **Building**: Docker image creation
- **Deployment**: Automated deployment to staging/production

### Pipeline Stages
1. **Lint & Format**: Code quality checks
2. **Backend Tests**: Python tests with coverage
3. **Frontend Tests**: React tests and build
4. **Security Scan**: Vulnerability scanning
5. **Build & Push**: Docker image creation
6. **Deploy**: Kubernetes deployment
7. **Post-Deploy Tests**: Smoke tests

### Manual Deployment
```bash
# Trigger deployment
gh workflow run ci-cd.yml

# Check workflow status
gh run list

# View workflow logs
gh run view <run-id>
```

---

## 🔧 Troubleshooting

### Common Issues

#### Pod Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n omnify

# Check pod logs
kubectl logs <pod-name> -n omnify

# Check events
kubectl get events -n omnify --sort-by='.lastTimestamp'
```

#### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints -n omnify

# Check ingress status
kubectl describe ingress omnify-ingress -n omnify

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm -- nslookup omnify-backend-service.omnify.svc.cluster.local
```

#### Database Connection Issues
```bash
# Check MongoDB status
kubectl exec -it <mongodb-pod> -n omnify -- mongosh --eval "db.adminCommand('ping')"

# Check Redis status
kubectl exec -it <redis-pod> -n omnify -- redis-cli ping
```

### Log Analysis
```bash
# Backend logs
kubectl logs -f deployment/omnify-backend -n omnify

# Frontend logs
kubectl logs -f deployment/omnify-frontend -n omnify

# Celery logs
kubectl logs -f deployment/omnify-celery-worker -n omnify
```

---

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale backend
kubectl scale deployment omnify-backend --replicas=5 -n omnify

# Scale frontend
kubectl scale deployment omnify-frontend --replicas=3 -n omnify

# Scale celery workers
kubectl scale deployment omnify-celery-worker --replicas=4 -n omnify
```

### Vertical Scaling
```yaml
# Update resource limits in values.yaml
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

### Auto-scaling
```bash
# Check HPA status
kubectl get hpa -n omnify

# Update HPA
kubectl patch hpa omnify-backend-hpa -n omnify -p '{"spec":{"maxReplicas":20}}'
```

---

## 🔄 Backup & Recovery

### Database Backup
```bash
# MongoDB backup
kubectl exec -it <mongodb-pod> -n omnify -- mongodump --out /backup/$(date +%Y%m%d)

# Redis backup
kubectl exec -it <redis-pod> -n omnify -- redis-cli BGSAVE
```

### Application Backup
```bash
# Backup persistent volumes
kubectl get pv -n omnify

# Create backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-job
  namespace: omnify
spec:
  template:
    spec:
      containers:
      - name: backup
        image: busybox
        command: ["sh", "-c", "tar -czf /backup/app-backup.tar.gz /app/data"]
        volumeMounts:
        - name: app-data
          mountPath: /app/data
        - name: backup-volume
          mountPath: /backup
      volumes:
      - name: app-data
        persistentVolumeClaim:
          claimName: omnify-data-pvc
      - name: backup-volume
        persistentVolumeClaim:
          claimName: backup-pvc
      restartPolicy: Never
EOF
```

---

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and inline comments
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact team@omnify.com

### Emergency Contacts
- **On-call**: +1-XXX-XXX-XXXX
- **Email**: emergency@omnify.com
- **Slack**: #omnify-alerts

---

## 🎉 Success!

If you've followed this guide, you should now have:
- ✅ OmniFy running in production
- ✅ Monitoring and logging configured
- ✅ SSL certificates installed
- ✅ Auto-scaling enabled
- ✅ Backup procedures in place

**Welcome to OmniFy Cloud Connect!** 🚀