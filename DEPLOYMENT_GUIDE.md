# OmniFy Cloud Connect - Deployment Guide

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.12 or higher
- **Node.js**: 18.x or higher
- **Yarn**: 1.22.x or higher
- **PostgreSQL**: 14+ (via Supabase)

### Required Accounts
1. **Supabase Account**: For database hosting
2. **AI Provider Account**: At least one of:
   - OpenAI
   - Anthropic
   - Google (Gemini)
   - X.AI (Grok)
   - OpenRouter

### Optional Platform Accounts
3. **Meta for Developers**: For Meta Ads integration
4. **Google Cloud Platform**: For Google Ads integration
5. **TikTok for Business**: For TikTok Ads integration
6. **Shopify Partners**: For Shopify integration

## 🚀 Deployment Options

### Option 1: Local Development
### Option 2: Docker Deployment
### Option 3: Production Deployment (Cloud)

---

## 🔧 Option 1: Local Development Deployment

### Step 1: Clone Repository
```bash
# If deploying from existing code
cd /app

# Verify structure
ls -la
# Should see: backend/, omnify-brain/, docs/, etc.
```

### Step 2: Database Setup (Supabase)

#### 2.1: Create Supabase Project
1. Go to https://supabase.com
2. Click "New Project"
3. Fill in details:
   - Name: `omnify-cloud-connect`
   - Database Password: (generate strong password)
   - Region: (closest to your users)
4. Click "Create new project"
5. Wait for provisioning (2-3 minutes)

#### 2.2: Get Supabase Credentials
1. In Supabase dashboard, go to **Settings > API**
2. Copy:
   - `Project URL` (SUPABASE_URL)
   - `anon public` key (NEXT_PUBLIC_SUPABASE_ANON_KEY)
   - `service_role` key (SUPABASE_SERVICE_KEY)

#### 2.3: Run Database Migration
1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Open `/app/backend/database/migrations/001_api_keys_schema.sql`
4. Copy entire content
5. Paste into SQL Editor
6. Click **Run**
7. Verify success (should see "Success. No rows returned")

### Step 3: Backend Setup

```bash
cd /app/backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed:', fastapi.__version__)"
```

#### 3.1: Configure Backend Environment
```bash
# Edit .env file
nano .env  # or use your preferred editor

# Update these values:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
ENCRYPTION_KEY=cY2Up-kcTL9j8513t-E-MF88FeUbZSUXdd3jvWdw3Kc=  # Already generated

# Save and exit
```

#### 3.2: Test Backend
```bash
# Start backend server
python server.py

# Should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8001

# In another terminal, test health endpoint
curl http://localhost:8001/api/health
# Expected: {"status": "healthy", ...}

# Test API keys endpoint
curl http://localhost:8001/api-keys/health
# Expected: {"status": "healthy", "service": "api_key_service"}
```

### Step 4: Frontend Setup

```bash
cd /app/omnify-brain

# Install dependencies
yarn install

# This will take 2-5 minutes
# Should see: "success Saved lockfile."
```

#### 4.1: Configure Frontend Environment
```bash
# Edit .env.local
nano .env.local

# Update these values:
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

NEXTAUTH_SECRET=SPBtZe32M/9bAj1OZPHmwDfWy56sJGTlbyrIk+m7CjM=  # Already set
NEXTAUTH_URL=http://localhost:3000

NEXT_PUBLIC_API_URL=http://localhost:8001

# Save and exit
```

#### 4.2: Test Frontend
```bash
# Start development server
yarn dev

# Should see:
# ready - started server on 0.0.0.0:3000, url: http://localhost:3000
# event - compiled client and server successfully

# Open browser to http://localhost:3000
# You should see the landing page
```

### Step 5: Verify Deployment

#### 5.1: Backend Health Checks
```bash
# Test all health endpoints
curl http://localhost:8001/api/health
curl http://localhost:8001/api-keys/health
curl http://localhost:8001/platforms/health
curl http://localhost:8001/ai/health

# All should return {"status": "healthy"}
```

#### 5.2: Frontend Navigation
1. Navigate to http://localhost:3000
2. Click "Get Started" or "Sign In"
3. Should see login page
4. After login, should see dashboard

#### 5.3: End-to-End Test
1. Go to http://localhost:3000/settings/api-keys
2. Add an OpenAI API key
3. Click "Test Connection"
4. Should see "OpenAI connection successful"
5. Go to dashboard
6. Should see data loading

### Step 6: Configure Supervisor (Keep Services Running)

```bash
# Supervisor should already be configured
# Check status
sudo supervisorctl status

# Should see:
# backend    RUNNING
# frontend   RUNNING

# If not running, start them
sudo supervisorctl start all

# Restart services
sudo supervisorctl restart all
```

---

## 🐳 Option 2: Docker Deployment

### Step 1: Install Docker
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Verify installation
docker --version
docker-compose --version
```

### Step 2: Create Docker Compose File
```yaml
# docker-compose.yml (create in /app)
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./backend:/app/backend
    restart: unless-stopped

  frontend:
    build:
      context: ./omnify-brain
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
      - NEXT_PUBLIC_API_URL=http://backend:8001
    depends_on:
      - backend
    restart: unless-stopped
```

### Step 3: Build and Run
```bash
cd /app

# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Option 3: Production Deployment (Cloud)

### Deployment Platforms

#### Option 3A: Vercel (Frontend) + Railway (Backend)

**Frontend (Vercel):**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd /app/omnify-brain
vercel

# Follow prompts
# Set environment variables in Vercel dashboard
```

**Backend (Railway):**
```bash
# Install Railway CLI
npm install -g railway

# Login
railway login

# Initialize project
cd /app/backend
railway init

# Deploy
railway up

# Set environment variables
railway variables set SUPABASE_URL=...
railway variables set SUPABASE_SERVICE_KEY=...
```

#### Option 3B: AWS (EC2 + RDS)

**1. Launch EC2 Instance:**
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (2 vCPU, 4 GB RAM)
- Security Group: Allow ports 22, 80, 443, 3000, 8001

**2. Setup Server:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3-pip nodejs npm git -y

# Install Yarn
npm install -g yarn

# Clone repository
git clone https://github.com/your-org/omnify-cloud-connect.git
cd omnify-cloud-connect

# Follow Local Development steps above
```

**3. Configure Nginx (Reverse Proxy):**
```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/omnify
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/omnify /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

**4. Setup SSL (Let's Encrypt):**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

**5. Setup Process Manager (PM2):**
```bash
# Install PM2
npm install -g pm2

# Start backend
cd /app/backend
pm2 start server.py --name omnify-backend --interpreter python3

# Start frontend
cd /app/omnify-brain
pm2 start "yarn dev" --name omnify-frontend

# Save PM2 config
pm2 save

# Setup startup script
pm2 startup
# Follow the command it outputs
```

---

## 🔍 Post-Deployment Verification

### 1. Health Check Endpoints
```bash
# Backend
curl https://your-domain.com/api/health
curl https://your-domain.com/api-keys/health
curl https://your-domain.com/platforms/health
curl https://your-domain.com/ai/health

# All should return 200 OK with {"status": "healthy"}
```

### 2. Database Connection
```bash
# Test from backend
curl -X POST https://your-domain.com/api-keys/list/default-org-id

# Should return list of configured platforms (empty if none configured)
```

### 3. Frontend Accessibility
```bash
# Check landing page
curl -I https://your-domain.com/
# Should return 200 OK

# Check dashboard (requires auth)
curl -I https://your-domain.com/dashboard
# Should redirect to login or return 200 if authenticated
```

### 4. API Integration Test
```bash
# Save an API key (replace with actual values)
curl -X POST https://your-domain.com/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openai",
    "key_name": "api_key",
    "key_value": "sk-test123",
    "is_active": true
  }'

# Test connection
curl -X POST https://your-domain.com/api-keys/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openai"
  }'
```

---

## 📊 Monitoring & Logging

### Application Logs

**Backend Logs:**
```bash
# Local development
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/backend.out.log

# Docker
docker-compose logs -f backend

# PM2
pm2 logs omnify-backend
```

**Frontend Logs:**
```bash
# Local development
tail -f /var/log/supervisor/frontend.err.log

# Docker
docker-compose logs -f frontend

# PM2
pm2 logs omnify-frontend
```

### Performance Monitoring

**Setup Prometheus + Grafana (Optional):**
```bash
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  depends_on:
    - prometheus
```

---

## 🔄 Update & Rollback

### Update Deployment
```bash
# Pull latest code
git pull origin main

# Update backend
cd /app/backend
pip install -r requirements.txt
sudo supervisorctl restart backend

# Update frontend
cd /app/omnify-brain
yarn install
sudo supervisorctl restart frontend
```

### Rollback
```bash
# Git rollback
git log  # Find commit to rollback to
git checkout <commit-hash>

# Restart services
sudo supervisorctl restart all
```

---

## 🆘 Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

---

## 📞 Support

For deployment issues:
- Check logs first
- Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Contact: support@omnify.ai

---

**Last Updated**: January 2025
