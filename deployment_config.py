"""
Production Deployment Configuration for OmnifyProduct
Docker, Kubernetes, and cloud deployment configurations
"""

# Docker Configuration
dockerfile_content = '''
# Multi-stage Docker build for OmnifyProduct
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r omnify && useradd -r -g omnify omnify

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R omnify:omnify /app

# Switch to non-root user
USER omnify

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["uvicorn", "agentkit_server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
'''

# Docker Compose for development and staging
docker_compose_content = '''
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-secret-key}
      - AGENTKIT_API_KEY=${AGENTKIT_API_KEY:-your-agentkit-key}
      - ENVIRONMENT=development
    volumes:
      - ./logs:/app/logs
    depends_on:
      - mongodb
      - redis
    restart: unless-stopped

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD:-password}
      - MONGO_INITDB_DATABASE=omnify
    volumes:
      - mongodb_data:/data/db
      - ./docker/mongo-init:/docker-entrypoint-initdb.d
    restart: unless-stopped

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  mongodb_data:
  redis_data:
'''

# Kubernetes Deployment Configuration
k8s_deployment_content = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omnifyproduct-api
  namespace: production
  labels:
    app: omnifyproduct
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omnifyproduct
      component: api
  template:
    metadata:
      labels:
        app: omnifyproduct
        component: api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: api
        image: omnifyproduct/api:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: MONGO_URL
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: mongo-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: redis-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: jwt-secret
        - name: AGENTKIT_API_KEY
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: agentkit-api-key
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
      securityContext:
        fsGroup: 1000
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - omnifyproduct
              topologyKey: kubernetes.io/hostname

---
apiVersion: v1
kind: Service
metadata:
  name: omnifyproduct-api
  namespace: production
  labels:
    app: omnifyproduct
    component: api
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: omnifyproduct
    component: api

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: omnifyproduct-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "60"
spec:
  tls:
  - hosts:
    - api.omnifyproduct.com
    secretName: omnifyproduct-tls
  rules:
  - host: api.omnifyproduct.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: omnifyproduct-api
            port:
              number: 80
'''

# Kubernetes MongoDB StatefulSet
mongodb_k8s_content = '''
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: production
  labels:
    app: omnifyproduct
    component: database
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: omnifyproduct
      component: database
  template:
    metadata:
      labels:
        app: omnifyproduct
        component: database
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
          name: mongodb
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: mongo-username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: omnifyproduct-secrets
              key: mongo-password
        - name: MONGO_INITDB_DATABASE
          value: omnify
        volumeMounts:
        - name: mongodb-data
          mountPath: /data/db
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - mongo
            - --eval
            - "db.adminCommand('ping')"
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          exec:
            command:
            - mongo
            - --eval
            - "db.adminCommand('ping')"
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      securityContext:
        fsGroup: 1000
        runAsUser: 1000
  volumeClaimTemplates:
  - metadata:
      name: mongodb-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi

---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: production
  labels:
    app: omnifyproduct
    component: database
spec:
  type: ClusterIP
  ports:
  - port: 27017
    targetPort: 27017
    protocol: TCP
    name: mongodb
  selector:
    app: omnifyproduct
    component: database
'''

# Kubernetes ConfigMap for configuration
configmap_content = '''
apiVersion: v1
kind: ConfigMap
metadata:
  name: omnifyproduct-config
  namespace: production
  labels:
    app: omnifyproduct
data:
  # Application configuration
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  WORKERS: "4"

  # Security configuration
  CORS_ORIGINS: "https://omnifyproduct.com,https://app.omnifyproduct.com"
  RATE_LIMIT_PER_MINUTE: "1000"
  SESSION_TIMEOUT_MINUTES: "60"

  # Database configuration (URLs come from secrets)
  MONGO_DATABASE: "omnify"
  REDIS_DATABASE: "0"

  # Feature flags
  ENABLE_ANALYTICS: "true"
  ENABLE_COMPLIANCE_CHECKING: "true"
  ENABLE_WORKFLOW_SCHEDULING: "true"

  # Performance settings
  MAX_WORKFLOW_EXECUTION_TIME: "300"
  WORKFLOW_STEP_TIMEOUT: "60"
  MAX_CONCURRENT_WORKFLOWS: "10"
'''

# Kubernetes Secrets
secrets_content = '''
apiVersion: v1
kind: Secret
metadata:
  name: omnifyproduct-secrets
  namespace: production
  labels:
    app: omnifyproduct
type: Opaque
data:
  # Database credentials (base64 encoded)
  mongo-url: bW9uZ29kYjovL21vbmdvZGI6MjcwMTcvb21uaWZ5
  mongo-username: YWRtaW4=
  mongo-password: cGFzc3dvcmQ=
  redis-url: cmVkaXM6Ly9yZWRpczo2Mzc5LzA=
  redis-password: cmVkaXNwYXNz

  # API keys (base64 encoded)
  jwt-secret: c2VjcmV0LWp3dC1rZXktZm9yLXByb2R1Y3Rpb24=
  agentkit-api-key: YWdlbnRraXQtYXBpLWtleS1mb3ItcHJvZHVjdGlvbg==

  # External service credentials
  sentry-dsn: aHR0cHM6Ly91c2VyQGRzbi5zZW50cnkuaW8vcHJvamVjdA==
  cloudinary-url: Y2xvdWRpbmFyeTovL2FwaV9rZXk6YXBpX3NlY3JldEBjbG91ZGluYXJ5LmNvbQ==

  # Email service
  smtp-username: c21kcC11c2VybmFtZQ==
  smtp-password: c21kcC1wYXNzd29yZA==

  # Monitoring
  datadog-api-key: ZGF0YWRvZy1hcGkta2V5
'''

# Horizontal Pod Autoscaler
hpa_content = '''
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: omnifyproduct-api-hpa
  namespace: production
  labels:
    app: omnifyproduct
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: omnifyproduct-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
'''

# Nginx Configuration for Load Balancing
nginx_config_content = '''
upstream omnifyproduct_api {
    server omnifyproduct-api:80;
    keepalive 32;
}

server {
    listen 80;
    server_name api.omnifyproduct.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.omnifyproduct.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/tls.crt;
    ssl_certificate_key /etc/nginx/ssl/tls.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # API endpoints
    location / {
        proxy_pass http://omnifyproduct_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://omnifyproduct_api/health;
        access_log off;
    }

    # API documentation
    location /docs {
        proxy_pass http://omnifyproduct_api/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Metrics endpoint for Prometheus
    location /metrics {
        stub_status on;
        access_log off;
        allow 10.0.0.0/8;
        deny all;
    }
}
'''

# CI/CD Pipeline Configuration (GitHub Actions)
github_actions_content = '''
name: Deploy OmnifyProduct to Production

on:
  push:
    branches: [ main, develop ]
    paths-ignore:
      - 'docs/**'
      - '*.md'
      - '.github/**'
  pull_request:
    branches: [ main ]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt

    - name: Run linting
      run: |
        flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
        black --check backend/
        isort --check-only backend/

    - name: Run tests with coverage
      env:
        MONGO_URL: mongodb://localhost:27017
        REDIS_URL: redis://localhost:6379
      run: |
        pip install pytest pytest-asyncio pytest-cov
        pytest tests/ --cov=backend --cov-report=xml --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-and-push
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    environment: staging

    steps:
    - name: Deploy to Kubernetes Staging
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
          k8s/ingress.yaml
        images: |
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        namespace: staging

  deploy-production:
    needs: build-and-push
    if: github.ref == 'refs/heads/main' || github.event_name == 'release'
    runs-on: ubuntu-latest
    environment: production

    steps:
    - name: Deploy to Kubernetes Production
      uses: azure/k8s-deploy@v4
      with:
        manifests: |
          k8s/deployment.yaml
          k8s/service.yaml
          k8s/ingress.yaml
        images: |
          ghcr.io/${{ github.repository }}:${{ github.sha }}
        namespace: production

  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write

    steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v3
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
'''

# Environment Configuration
env_example_content = '''
# OmnifyProduct Environment Configuration

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# Database Configuration
MONGO_URL=mongodb://username:password@mongodb:27017/omnify
MONGO_DATABASE=omnify
REDIS_URL=redis://:password@redis:6379/0

# Security Settings
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
CORS_ORIGINS=https://omnifyproduct.com,https://app.omnifyproduct.com

# AgentKit Configuration
AGENTKIT_API_KEY=your-agentkit-api-key
AGENTKIT_BASE_URL=https://api.agentkit.openai.com

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloudinary.com

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Rate Limiting
RATE_LIMIT_PER_MINUTE=1000

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_COMPLIANCE_CHECKING=true
ENABLE_WORKFLOW_SCHEDULING=true

# Performance Settings
MAX_WORKFLOW_EXECUTION_TIME=300
WORKFLOW_STEP_TIMEOUT=60
MAX_CONCURRENT_WORKFLOWS=10
'''

# Monitoring Configuration (Prometheus)
prometheus_content = '''
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'omnifyproduct-api'
    static_configs:
      - targets: ['omnifyproduct-api:8000']
    scrape_interval: 15s
    metrics_path: '/metrics'

  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s
'''

# Grafana Dashboard Configuration
grafana_dashboard_content = '''
{
  "dashboard": {
    "id": null,
    "title": "OmnifyProduct API Dashboard",
    "tags": ["omnifyproduct", "api"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(omnifyproduct_api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "id": 2,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(omnifyproduct_api_requests_total[5m])",
            "legendFormat": "Requests per second"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(omnifyproduct_api_errors_total[5m])",
            "legendFormat": "Errors per second"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Workflows",
        "type": "stat",
        "targets": [
          {
            "expr": "omnifyproduct_active_workflows",
            "legendFormat": "Active Workflows"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
'''

# Write all configuration files
with open('Dockerfile', 'w') as f:
    f.write(dockerfile_content)

with open('docker-compose.yml', 'w') as f:
    f.write(docker_compose_content)

with open('k8s/deployment.yaml', 'w') as f:
    f.write(k8s_deployment_content)

with open('k8s/mongodb.yaml', 'w') as f:
    f.write(mongodb_k8s_content)

with open('k8s/configmap.yaml', 'w') as f:
    f.write(configmap_content)

with open('k8s/secrets.yaml', 'w') as f:
    f.write(secrets_content)

with open('k8s/hpa.yaml', 'w') as f:
    f.write(hpa_content)

with open('nginx.conf', 'w') as f:
    f.write(nginx_config_content)

with open('.github/workflows/deploy.yml', 'w') as f:
    f.write(github_actions_content)

with open('.env.example', 'w') as f:
    f.write(env_example_content)

with open('prometheus.yml', 'w') as f:
    f.write(prometheus_content)

with open('grafana-dashboard.json', 'w') as f:
    f.write(grafana_dashboard_content)

print("All deployment configuration files created successfully!")
