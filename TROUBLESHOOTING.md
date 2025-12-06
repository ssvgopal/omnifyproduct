# Troubleshooting Guide - OmniFy Cloud Connect

## 🆘 Quick Diagnostics

### Is the problem with Backend or Frontend?

```bash
# Test backend
curl http://localhost:8001/api/health
# Expected: {"status": "healthy"}

# Test frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK
```

---

## 🔧 Common Issues & Solutions

## Issue 1: Backend Won't Start

### Symptom:
```bash
python server.py
# Error: ModuleNotFoundError: No module named 'fastapi'
```

### Solution:
```bash
# Install dependencies
cd /app/backend
pip install -r requirements.txt

# If pip fails, try:
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"
```

---

### Symptom:
```bash
python server.py
# Error: SUPABASE_URL environment variable not set
```

### Solution:
```bash
# Check .env file exists
ls -la /app/backend/.env

# If missing, copy from example
cp /app/backend/.env.example /app/backend/.env

# Edit with your values
nano /app/backend/.env

# Add:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
ENCRYPTION_KEY=cY2Up-kcTL9j8513t-E-MF88FeUbZSUXdd3jvWdw3Kc=

# Save and retry
python server.py
```

---

### Symptom:
```bash
python server.py
# Error: Address already in use (port 8001)
```

### Solution:
```bash
# Find process using port 8001
lsof -i :8001
# or
netstat -tulpn | grep 8001

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn server:app --host 0.0.0.0 --port 8002
```

---

## Issue 2: Frontend Won't Start

### Symptom:
```bash
yarn dev
# Error: command not found: yarn
```

### Solution:
```bash
# Install Yarn
npm install -g yarn

# Verify installation
yarn --version

# Retry
yarn dev
```

---

### Symptom:
```bash
yarn dev
# Error: Cannot find module 'next'
```

### Solution:
```bash
# Remove node_modules and reinstall
cd /app/omnify-brain
rm -rf node_modules yarn.lock
yarn install

# This may take 2-5 minutes
# Then retry
yarn dev
```

---

### Symptom:
```bash
yarn dev
# Error: Port 3000 is already in use
```

### Solution:
```bash
# Option 1: Kill process on port 3000
lsof -i :3000
kill -9 <PID>

# Option 2: Use different port
PORT=3001 yarn dev

# Update backend to use new port if needed
```

---

## Issue 3: Database Connection Failed

### Symptom:
```python
# Backend logs:
ERROR: Could not connect to Supabase
supabase.exceptions.AuthenticationError
```

### Solution:

**Step 1: Verify Supabase credentials**
```bash
# Check .env file
cat /app/backend/.env | grep SUPABASE

# Should show:
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
```

**Step 2: Test connection manually**
```python
python3 << EOF
import os
from supabase import create_client

os.environ['SUPABASE_URL'] = 'https://your-project.supabase.co'
os.environ['SUPABASE_SERVICE_KEY'] = 'your-key'

try:
    supabase = create_client(
        os.environ['SUPABASE_URL'],
        os.environ['SUPABASE_SERVICE_KEY']
    )
    result = supabase.table('organizations').select('*').limit(1).execute()
    print('✅ Connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
EOF
```

**Step 3: Check Supabase project status**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Check if project is paused (unpause if needed)
4. Verify API keys haven't been regenerated

---

## Issue 4: API Keys Not Saving

### Symptom:
User clicks "Save" on API key, but it doesn't persist

### Debug:

**Step 1: Check backend logs**
```bash
tail -f /var/log/supervisor/backend.err.log
# or if running directly:
# Check terminal output
```

**Step 2: Test API directly**
```bash
curl -X POST http://localhost:8001/api-keys/save \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "openai",
    "key_name": "api_key",
    "key_value": "sk-test123"
  }'

# Should return: {"success": true, ...}
```

**Step 3: Check database migration**
```sql
-- In Supabase SQL Editor
SELECT * FROM api_keys LIMIT 1;

-- If error: "relation api_keys does not exist"
-- Run migration: /app/backend/database/migrations/001_api_keys_schema.sql
```

**Step 4: Check encryption key**
```bash
# Verify encryption key is set
grep ENCRYPTION_KEY /app/backend/.env

# Should show a 44-character key
# If missing, generate new one:
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"

# Add to .env and restart backend
```

---

## Issue 5: "Connection Test Failed" for OpenAI

### Symptom:
User enters valid OpenAI key, but test fails

### Possible Causes:

**Cause 1: Invalid API Key Format**
```bash
# OpenAI keys should start with 'sk-'
# Length: 48-56 characters
# Example: sk-proj-abc123def456...

# If key doesn't match format, get new one from:
# https://platform.openai.com/api-keys
```

**Cause 2: No Credits in OpenAI Account**
```bash
# Check billing: https://platform.openai.com/account/billing
# Add $5-10 credit
# Retry test
```

**Cause 3: API Key Revoked**
```bash
# In OpenAI dashboard, check if key is active
# If revoked, generate new key
```

**Cause 4: Network/Firewall Issue**
```bash
# Test OpenAI API directly from server
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-key"

# Should return list of models
# If timeout or connection refused, check firewall
```

---

## Issue 6: Dashboard Shows $0 for All Metrics

### Symptom:
Memory card shows: Spend: $0, Revenue: $0, ROAS: 0x

### Debug:

**Step 1: Check if data sync ran**
```bash
# Query database
curl -X POST http://localhost:8001/platforms/unified-metrics \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'

# If returns empty or error, data not synced yet
```

**Step 2: Manually trigger sync**
```bash
curl -X POST http://localhost:8001/platforms/sync/all \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "days": 7
  }'

# Wait for response (10-30 seconds)
# Check result
```

**Step 3: Verify platform API keys configured**
```bash
curl http://localhost:8001/api-keys/list/default-org-id

# Should show at least one marketing platform:
# meta_ads, google_ads, tiktok, or shopify
```

**Step 4: Check platform connection**
```bash
# Test Meta Ads
curl -X POST http://localhost:8001/api-keys/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "platform": "meta_ads"
  }'

# Should return: {"success": true, "connected": true}
```

---

## Issue 7: AI Recommendations Not Showing

### Symptom:
Curiosity card shows "Configure AI API keys to get recommendations"

### Solution:

**Step 1: Configure AI provider**
```bash
# At minimum, need one of:
# - OpenAI
# - Anthropic
# - Gemini
# - Grok
# - OpenRouter

# Go to http://localhost:3000/settings/api-keys
# Add OpenAI key (easiest option)
```

**Step 2: Test AI connection**
```bash
curl -X POST http://localhost:8001/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "organization_id": "default-org-id",
    "messages": [{"role": "user", "content": "test"}],
    "provider": "openai"
  }'

# Should return AI response
```

**Step 3: Ensure performance data exists**
```bash
# Recommendations require data to analyze
# Run sync first:
curl -X POST http://localhost:8001/platforms/sync/all \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id", "days": 7}'

# Then refresh dashboard
```

---

## Issue 8: Campaigns Page Empty

### Symptom:
"No campaigns found" message on /campaigns page

### Debug:

**Step 1: Check platform connections**
```bash
# List configured platforms
curl http://localhost:8001/api-keys/list/default-org-id

# Should show meta_ads or google_ads
```

**Step 2: Test campaign fetch**
```bash
# Meta Ads
curl -X POST http://localhost:8001/platforms/meta-ads/campaigns \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'

# Google Ads
curl -X POST http://localhost:8001/platforms/google-ads/campaigns \
  -H "Content-Type: application/json" \
  -d '{"organization_id": "default-org-id"}'

# Should return list of campaigns
```

**Step 3: Check account has campaigns**
```bash
# Log into Meta Ads Manager or Google Ads
# Verify you have active campaigns
# If no campaigns, create test campaign first
```

---

## Issue 9: Supervisor Services Not Running

### Symptom:
```bash
sudo supervisorctl status
# backend    FATAL
# frontend   STOPPED
```

### Solution:

**Step 1: Check supervisor config**
```bash
cat /etc/supervisor/conf.d/omnify.conf

# Should have entries for backend and frontend
```

**Step 2: Check logs for errors**
```bash
# Backend logs
tail -50 /var/log/supervisor/backend.err.log

# Frontend logs
tail -50 /var/log/supervisor/frontend.err.log

# Look for error messages
```

**Step 3: Restart services**
```bash
# Reload supervisor config
sudo supervisorctl reread
sudo supervisorctl update

# Restart all
sudo supervisorctl restart all

# Check status
sudo supervisorctl status
# Should show RUNNING
```

**Step 4: Start manually if needed**
```bash
# Backend
cd /app/backend
python server.py &

# Frontend
cd /app/omnify-brain
yarn dev &
```

---

## Issue 10: High Memory Usage

### Symptom:
Server running slow, high RAM usage

### Debug:

**Step 1: Check memory usage**
```bash
free -h
# Look at "used" vs "available"

top
# Press M to sort by memory
# Look for processes using most RAM
```

**Step 2: Check for memory leaks**
```bash
# Backend process
ps aux | grep python
# Check RSS (memory) column

# Frontend process
ps aux | grep node
# Check RSS column
```

**Step 3: Restart services**
```bash
sudo supervisorctl restart all

# Monitor memory after restart
watch -n 5 free -h
```

**Step 4: Scale resources if needed**
- Upgrade server RAM (minimum 4GB recommended)
- Add swap space if needed

---

## Issue 11: CORS Errors in Browser Console

### Symptom:
```
Access to fetch at 'http://localhost:8001/api/...' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

### Solution:

**Step 1: Check backend CORS config**
```python
# In /app/backend/server.py
# Verify CORS_ORIGINS includes frontend URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Step 2: Add production URL**
```python
# For production, add your domain
allow_origins=[
    "http://localhost:3000",
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

**Step 3: Restart backend**
```bash
sudo supervisorctl restart backend
```

---

## 🔍 Diagnostic Commands

### Quick Health Check Script

```bash
#!/bin/bash
# health_check.sh

echo "🔍 OmniFy Health Check"
echo "====================="

# Backend health
echo -n "Backend API: "
if curl -s http://localhost:8001/api/health | grep -q "healthy"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Frontend
echo -n "Frontend: "
if curl -s -I http://localhost:3000 | grep -q "200"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Database
echo -n "Database: "
if curl -s -X POST http://localhost:8001/api-keys/list/default-org-id | grep -q "organization_id"; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Services
echo -n "Supervisor: "
if sudo supervisorctl status | grep -q "RUNNING"; then
    echo "✅ Services running"
else
    echo "⚠️ Check services"
fi

echo ""
echo "Full status:"
sudo supervisorctl status
```

### Run Diagnostic
```bash
chmod +x health_check.sh
./health_check.sh
```

---

## 📞 Getting Help

### Before Contacting Support:

1. **Check logs:**
   - Backend: `/var/log/supervisor/backend.err.log`
   - Frontend: `/var/log/supervisor/frontend.err.log`

2. **Run health check:**
   ```bash
   ./health_check.sh
   ```

3. **Gather info:**
   - Error message (exact text)
   - Steps to reproduce
   - Browser console errors (F12 > Console)
   - System info: `uname -a`

### Support Channels:

- **Documentation**: Check all .md files in /app/
- **GitHub Issues**: (if open source)
- **Email**: support@omnify.ai
- **Community**: Discord (coming soon)

### What to Include in Support Request:

```
Subject: [Issue] Brief description

Environment:
- OS: Ubuntu 22.04 / macOS / Windows
- Python: 3.12
- Node: 18.x
- Deployment: Local / Docker / Production

Issue:
- What were you trying to do?
- What happened instead?
- Error message: [paste full error]

Steps to Reproduce:
1. Step one
2. Step two
3. Error occurs

Logs:
[Paste relevant log lines]

Screenshots:
[Attach if helpful]
```

---

**Last Updated**: January 2025
