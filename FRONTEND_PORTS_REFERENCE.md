# Frontend Ports Reference

## 🎯 Port Assignments (Fixed)

To avoid conflicts, each frontend now runs on a different port:

| Application | Port | URL | Status |
|-------------|------|-----|--------|
| **Omnify Brain (Production)** | 3000 | http://localhost:3000 | ✅ Active |
| **Omnify Brain (Demo)** | 3001 | http://localhost:3001 | ✅ Active |
| Frontend (Legacy) | 3100 | http://localhost:3100 | ⚠️ Legacy |
| Frontend Admin (Legacy) | 3200 | http://localhost:3200 | ⚠️ Legacy |
| Frontend User (Legacy) | 3300 | http://localhost:3300 | ⚠️ Legacy |

---

## 🚀 Quick Start

### Omnify Brain (Current Production Architecture)
```bash
# Demo (Port 3001)
cd omnify-brain/demo
npm install
npm run demo

# Production (Port 3000)
cd omnify-brain
npm install
npm run dev
```

### Legacy Frontends (If Needed)
First, fix the port conflicts:

**Windows**:
```bash
.\scripts\fix-frontend-ports.bat
```

**Linux/Mac**:
```bash
chmod +x scripts/fix-frontend-ports.sh
./scripts/fix-frontend-ports.sh
```

Then run each frontend:
```bash
# Frontend (Port 3100)
cd frontend
npm install
npm start

# Frontend Admin (Port 3200)
cd frontend-admin
npm install
npm start

# Frontend User (Port 3300)
cd frontend-user
npm install
npm start
```

---

## ⚠️ Important Notes

### Architecture Conflict
The legacy frontends (`frontend/`, `frontend-admin/`, `frontend-user/`) reference:
- AgentKit
- GoHighLevel
- Composio
- Omnify Cloud Connect

These are **NOT** part of the current **Omnify Brain** architecture.

### Recommendation
**Option 1 (Recommended)**: Archive legacy frontends, focus on Omnify Brain
```bash
mkdir _archive
mv frontend _archive/
mv frontend-admin _archive/
mv frontend-user _archive/
```

**Option 2**: Keep both but rename and document separately

**Option 3**: Migrate legacy features into Omnify Brain (Next.js architecture)

See `ARCHITECTURE_CLARIFICATION.md` for detailed analysis.

---

## 🔍 What Each Frontend Does

### Omnify Brain (Active Development)
**Location**: `omnify-brain/`
- **Purpose**: Marketing intelligence platform
- **Features**: 
  - MEMORY module (Attribution & ROI)
  - ORACLE module (Predictive analytics)
  - CURIOSITY module (Prescriptive actions)
  - Platform integrations (Meta, Google, TikTok, Shopify)
  - AI-powered insights (OpenAI, Anthropic)
- **Tech**: Next.js 15, Supabase, NextAuth.js
- **Status**: ✅ Production-ready

### Frontend (Legacy)
**Location**: `frontend/`
- **Purpose**: Main integration UI (unclear if active)
- **Features**: AgentKit/GoHighLevel integrations
- **Tech**: React 19 (CRA), Axios
- **Status**: ⚠️ Outdated, references old architecture

### Frontend Admin (Legacy)
**Location**: `frontend-admin/`
- **Purpose**: Admin panel (unclear if active)
- **Features**: Unknown (likely admin functions)
- **Tech**: React 19 (CRA)
- **Status**: ⚠️ Outdated

### Frontend User (Legacy)
**Location**: `frontend-user/`
- **Purpose**: User panel (unclear if active)
- **Features**: Unknown (likely user functions)
- **Tech**: React 19 (CRA)
- **Status**: ⚠️ Outdated

---

## 📊 Current State

### Working (Production-Ready)
- ✅ Omnify Brain Demo (Port 3001)
- ✅ Omnify Brain Production (Port 3000)

### Needs Decision
- ⚠️ Frontend (Port 3100) - Keep or archive?
- ⚠️ Frontend Admin (Port 3200) - Keep or archive?
- ⚠️ Frontend User (Port 3300) - Keep or archive?

---

## 🎯 Recommended Action

1. **Clarify product strategy**: Are we building one product or two?
2. **If Omnify Brain only**: Archive legacy frontends
3. **If both products**: Separate clearly and document

See `ARCHITECTURE_CLARIFICATION.md` for full analysis and recommendations.

---

## 🚨 Port Conflict Resolution

### Before (Problem)
All frontends defaulted to port 3000:
- Omnify Brain → 3000 ❌ CONFLICT
- Frontend → 3000 ❌ CONFLICT
- Frontend Admin → 3000 ❌ CONFLICT
- Frontend User → 3000 ❌ CONFLICT

### After (Fixed)
Each has unique port:
- Omnify Brain → 3000 ✅
- Omnify Brain Demo → 3001 ✅
- Frontend → 3100 ✅
- Frontend Admin → 3200 ✅
- Frontend User → 3300 ✅

All can run simultaneously without conflicts!

---

## 📝 Next Steps

1. Review `ARCHITECTURE_CLARIFICATION.md`
2. Decide on product strategy
3. Either:
   - Archive legacy frontends (if not needed)
   - Or fix ports and continue development (if needed)
4. Update documentation to reflect decision
5. Clean up repository structure

**Need help deciding?** Review the detailed analysis in `ARCHITECTURE_CLARIFICATION.md`.
