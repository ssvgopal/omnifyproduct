# Quick Start Guide - OmniFy Cloud Connect

## 🚀 Get Up and Running in 30 Minutes

This guide will get you from zero to a fully functional OmniFy Cloud Connect installation.

---

## ✅ Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Yarn installed (`yarn --version`)
- [ ] A Supabase account (free tier is fine)
- [ ] At least ONE API key ready:
  - OpenAI API key (recommended), OR
  - Google Gemini API key, OR
  - Anthropic API key

---

## 📦 Step 1: Setup Database (5 minutes)

### 1.1 Create Supabase Project
1. Go to https://supabase.com
2. Click "New Project"
3. Fill in name, password, region
4. Wait 2-3 minutes for provisioning

### 1.2 Get Credentials
- Settings > API
- Copy: Project URL, Anon Key, Service Role Key

### 1.3 Run Database Migration
- SQL Editor > New Query
- Copy from: /app/backend/database/migrations/001_api_keys_schema.sql
- Run
- Verify: 7 new tables created

---

## 🔧 Step 2: Backend (5 min)

```bash
cd /app/backend

# Update .env with your Supabase credentials
nano .env

# Install dependencies
pip install -r requirements.txt

# Start backend
python server.py

# Verify (new terminal):
curl http://localhost:8001/api/health
```

---

## 🎨 Step 3: Frontend (5 min)

```bash
cd /app/omnify-brain

# Update .env.local with Supabase credentials
nano .env.local

# Install dependencies
yarn install

# Start frontend
yarn dev

# Verify: http://localhost:3000
```

---

## 🔑 Step 4: Configure API Keys (10 min)

1. Navigate to http://localhost:3000/settings/api-keys
2. Add OpenAI key
3. Test connection
4. (Optional) Add Meta Ads or Google Ads

---

## 📊 Step 5: First Data Sync (5 min)

1. Go to http://localhost:3000/dashboard
2. Click "Sync Data"
3. Wait 10-30 seconds
4. View updated metrics

---

## ✅ Verification

- [ ] Backend running on 8001
- [ ] Frontend running on 3000
- [ ] At least 1 API key configured
- [ ] Dashboard showing data

**See full documentation in:** [All .md files in /app/]

---

**Last Updated**: January 2025
