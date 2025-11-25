# Omnify Product Suite

**Marketing Intelligence Platform** - AI-powered marketing optimization for DTC brands

---

## 🎯 Active Development

### **Omnify Brain MVP** (`omnify-brain/`)

**Status**: ✅ **Production-Ready MVP**  
**Framework**: Next.js 15 (App Router)  
**Database**: Supabase (PostgreSQL)  
**Port**: 3000 (production), 3001 (demo)

**Features:**
- ✅ Multi-tenant SaaS architecture
- ✅ Authentication (NextAuth + Supabase Auth)
- ✅ Platform integrations (Meta Ads, Google Ads, TikTok Ads, Shopify)
- ✅ Brain modules (MEMORY, ORACLE, CURIOSITY)
- ✅ One-click actions (pause creative, shift budget)
- ✅ Persona-specific views (CMO, VP Growth, Director)

**Quick Start:**
```bash
cd omnify-brain
npm install
npm run dev
```

See `omnify-brain/README.md` for detailed setup instructions.

---

## 📦 Archived Components

### **Legacy Frontends** (`_archive/`)

The following frontends have been archived and are **not actively maintained**:

- `_archive/frontend-legacy/` - Legacy React 19 (CRA) with AgentKit/GoHighLevel integrations
- `_archive/frontend-admin/` - Legacy admin panel
- `_archive/frontend-user/` - Legacy user panel

**Why Archived:**
- Not aligned with MVP architecture (Next.js 15, Supabase)
- References deprecated platforms (AgentKit, GoHighLevel)
- Replaced by unified `omnify-brain/` frontend

### **Legacy Backend** (`backend/`)

**Status**: ⚠️ **Partially Deprecated**

The Python/FastAPI backend (`backend/`) uses MongoDB and contains:
- ✅ Active: Brain logic modules, platform adapters
- ❌ Deprecated: AgentKit, GoHighLevel, MongoDB-dependent services
- ❌ Archived: Advanced infrastructure (Kafka, Celery, Temporal)

**Note**: The MVP uses Supabase (PostgreSQL) exclusively. The backend is kept for reference but is not required for the MVP.

---

## 🏗️ Architecture

### **MVP Stack**

```
omnify-brain/ (Next.js 15)
├── Frontend: React + TypeScript + TailwindCSS
├── Backend: Next.js API Routes
├── Database: Supabase (PostgreSQL)
├── Auth: NextAuth.js + Supabase Auth
├── Storage: Supabase Storage (images/videos)
└── Deploy: Vercel
```

### **Platform Integrations**

**MVP Platforms Only:**
- Meta Ads
- Google Ads
- TikTok Ads
- Shopify

**Deprecated Platforms** (archived):
- AgentKit
- GoHighLevel
- TripleWhale
- HubSpot
- Klaviyo
- Stripe
- LinkedIn Ads
- YouTube Ads

---

## 📚 Documentation

### **Setup & Architecture**
- `omnify-brain/README.md` - MVP setup guide
- `docs/DATABASE_ARCHITECTURE_EXPLAINED.md` - MongoDB vs Supabase
- `docs/STORAGE_ARCHITECTURE_ANALYSIS.md` - File storage strategy
- `docs/FRONTEND_ARCHITECTURE_ANALYSIS.md` - Frontend structure

### **Implementation**
- `omnify-brain/docs/IMPLEMENTATION_SUMMARY.md` - Production implementation
- `docs/EXACT_CLEANUP_PLAN.md` - Cleanup roadmap
- `docs/SUPABASE_BACKEND_DELINKING_CONFIRMATION.md` - Architecture separation

### **Requirements**
- `RESEARCH_BRIEF_ALIGNMENT_ANALYSIS.md` - Research brief alignment
- `UNIFIED_GAP_ANALYSIS_AND_STRATEGIC_ROADMAP.md` - Gap analysis

---

## 🚀 Getting Started

### **For MVP Development**

1. **Set up Supabase:**
   - Create project at [supabase.com](https://supabase.com)
   - Run migrations from `omnify-brain/supabase/migrations/`

2. **Configure Environment:**
   ```bash
   cd omnify-brain
   cp .env.example .env.local
   # Add your Supabase credentials
   ```

3. **Install & Run:**
   ```bash
   npm install
   npm run dev
   ```

4. **Access:**
   - Production: http://localhost:3000
   - Demo: http://localhost:3001

### **For Legacy Backend** (Reference Only)

```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Note**: Backend is not required for MVP. MVP uses Supabase exclusively.

---

## 📊 Project Structure

```
omnifyproduct/
├── omnify-brain/          # ✅ ACTIVE - MVP Frontend
│   ├── src/               # Next.js app
│   ├── supabase/          # Database migrations
│   └── docs/              # MVP documentation
│
├── backend/               # ⚠️ PARTIALLY DEPRECATED
│   ├── services/          # Brain logic (active)
│   └── integrations/      # Platform adapters (some deprecated)
│
├── _archive/              # 📦 ARCHIVED
│   ├── frontend-legacy/   # Old React frontend
│   ├── frontend-admin/    # Old admin panel
│   ├── frontend-user/    # Old user panel
│   └── backend-deprecated/ # Deprecated backend code
│
└── docs/                  # Documentation
```

---

## 🎯 MVP Focus

**Target Market:**
- Revenue: $50M - $350M
- Industries: Beauty, Skincare, Supplements, Health & Wellness

**Personas:**
- **Sarah (CMO)** - Strategic view, explains to CEO/board
- **Jason (VP Growth)** - Revenue-focused, growth targets
- **Emily (Director)** - Daily campaign execution

**Value Proposition:**
- 20-40% waste reduction in ad spend
- Unified attribution across platforms
- Predictive risk detection
- Prescriptive action recommendations

---

## 📝 License

[Add your license here]

---

**Last Updated**: January 2025  
**Status**: MVP in active development
