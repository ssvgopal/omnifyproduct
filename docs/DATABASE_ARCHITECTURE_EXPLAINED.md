# Database Architecture: MongoDB vs Supabase

## Overview

This codebase uses **two different databases** for **two different applications**:

1. **MongoDB** - Used by the **backend Python/FastAPI application** (legacy/enterprise system)
2. **Supabase (PostgreSQL)** - Used by the **omnify-brain Next.js frontend** (new MVP/production system)

---

## 🍃 MongoDB - Backend Enterprise System

### **Where It's Used**
- **Location**: `backend/` directory
- **Application**: Python FastAPI backend server
- **Purpose**: Enterprise-grade marketing automation platform

### **Technology Stack**
- **Database**: MongoDB (NoSQL document database)
- **Driver**: Motor (async MongoDB driver for Python)
- **Connection**: `AsyncIOMotorClient`
- **Database Name**: `omnify_cloud` (configurable)

### **What It Stores**
MongoDB is used for the **comprehensive enterprise platform** with:

| Collection | Purpose |
|------------|---------|
| `users` | User accounts and profiles |
| `organizations` | Multi-tenant organization data |
| `subscriptions` | Billing and subscription information |
| `agentkit_agents` | AgentKit AI agent configurations |
| `agentkit_executions` | AgentKit workflow execution logs |
| `agentkit_workflows` | Workflow definitions |
| `audit_logs` | System audit trail |
| `compliance_checks` | Compliance tracking |
| `scheduled_workflows` | Scheduled job definitions |
| `analytics_data` | Analytics and reporting data |
| `usage_quotas` | Resource usage limits |
| `team_invitations` | Team member invitations |

### **Key Features**
- ✅ **Multi-tenant architecture** (organizations, users, subscriptions)
- ✅ **AgentKit integration** (AI agent workflows)
- ✅ **Platform integrations** (GoHighLevel, HubSpot, TripleWhale, etc.)
- ✅ **Advanced features** (predictive intelligence, automation, reporting)
- ✅ **Enterprise security** (OIDC, OPA policies, audit logging)

### **Configuration**
```python
# backend/agentkit_server.py
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'omnify_cloud')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]
```

### **Files Using MongoDB**
- `backend/agentkit_server.py` - Main server
- `backend/database/mongodb_schema.py` - Schema definitions
- `backend/services/*.py` - All backend services
- `backend/api/*.py` - All API routes

---

## 🐘 Supabase (PostgreSQL) - Frontend MVP System

### **Where It's Used**
- **Location**: `omnify-brain/` directory
- **Application**: Next.js frontend application
- **Purpose**: Production-ready SaaS MVP for "Omnify Brain"

### **Technology Stack**
- **Database**: Supabase (PostgreSQL)
- **Client**: `@supabase/supabase-js`
- **Auth**: Supabase Auth (integrated with NextAuth)
- **Database Type**: PostgreSQL (relational)

### **What It Stores**
Supabase is used for the **new MVP/production system** with:

| Table | Purpose |
|-------|---------|
| `organizations` | Multi-tenant organizations |
| `users` | User accounts (linked to Supabase Auth) |
| `channels` | Marketing channels (Meta, Google, TikTok, etc.) |
| `campaigns` | Marketing campaigns |
| `creatives` | Ad creatives |
| `daily_metrics` | Time-series performance data |
| `cohorts` | Customer cohort LTV data |
| `brain_states` | Cached brain module outputs |
| `api_credentials` | Encrypted platform API credentials |
| `sync_jobs` | Data sync job tracking |
| `action_logs` | Action execution audit log |

### **Key Features**
- ✅ **NextAuth integration** (email/password + Google OAuth)
- ✅ **Multi-tenant data isolation** (organization-scoped queries)
- ✅ **Real-time platform sync** (Meta Ads, Google Ads, TikTok, Shopify)
- ✅ **Brain module processing** (MEMORY, ORACLE, CURIOSITY)
- ✅ **Action execution** (pause creative, shift budget)
- ✅ **Row Level Security (RLS)** for data isolation

### **Configuration**
```typescript
// omnify-brain/src/lib/db/supabase.ts
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
export const supabaseAdmin = createClient(supabaseUrl, SUPABASE_SERVICE_ROLE_KEY)
```

### **Files Using Supabase**
- `omnify-brain/src/lib/db/supabase.ts` - Client setup
- `omnify-brain/src/app/api/**/*.ts` - All API routes
- `omnify-brain/src/lib/brain/*-production.ts` - Brain modules
- `omnify-brain/supabase/migrations/*.sql` - Database migrations

---

## 🔄 Why Two Databases?

### **Historical Context**

1. **MongoDB (Backend)** - **Original Enterprise System**
   - Built as a comprehensive marketing automation platform
   - Uses Python/FastAPI backend
   - Designed for enterprise customers
   - Includes AgentKit, advanced ML, complex workflows

2. **Supabase (Frontend)** - **New MVP System**
   - Built as a focused MVP for "Omnify Brain"
   - Uses Next.js full-stack application
   - Designed for specific use case (marketing intelligence)
   - Simpler, more focused architecture

### **Current State**

These are **two separate applications**:

```
┌─────────────────────────────────────────────────────────┐
│                    OMNIFY PRODUCT SUITE                    │
├───────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────┐    ┌──────────────────────┐  │
│  │  Enterprise Backend   │    │   Brain MVP Frontend │  │
│  │  (Python/FastAPI)     │    │   (Next.js)          │  │
│  │                       │    │                      │  │
│  │  MongoDB              │    │  Supabase (PostgreSQL)│  │
│  │  • AgentKit           │    │  • Brain Modules     │  │
│  │  • ML Models          │    │  • Platform Sync     │  │
│  │  • Complex Workflows  │    │  • Action Execution │  │
│  │  • Enterprise Features│    │  • Simple MVP        │  │
│  └──────────────────────┘    └──────────────────────┘  │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### **Migration Path**

The **production action plan** we just implemented uses **Supabase** for the new MVP system. The MongoDB backend remains for the enterprise platform.

---

## 📊 Comparison Table

| Aspect | MongoDB (Backend) | Supabase (Frontend) |
|--------|-------------------|---------------------|
| **Database Type** | NoSQL (Document) | SQL (PostgreSQL) |
| **Application** | Python/FastAPI | Next.js/TypeScript |
| **Purpose** | Enterprise platform | MVP SaaS |
| **Complexity** | High (56 services) | Medium (focused MVP) |
| **Features** | AgentKit, ML, Workflows | Brain modules, Sync, Actions |
| **Auth** | Custom JWT/OIDC | Supabase Auth + NextAuth |
| **Multi-tenancy** | Organization-based | Organization-based |
| **Data Model** | Flexible documents | Structured relational |
| **Migrations** | Python scripts | SQL migrations |
| **Location** | `backend/` | `omnify-brain/` |

---

## 🎯 Which One Should You Use?

### **Use MongoDB (Backend) if:**
- ✅ You need the full enterprise platform
- ✅ You want AgentKit AI workflows
- ✅ You need complex ML models
- ✅ You're building advanced automation
- ✅ You need the comprehensive feature set

### **Use Supabase (Frontend) if:**
- ✅ You're building the "Omnify Brain" MVP
- ✅ You want a simpler, focused architecture
- ✅ You need quick deployment (Next.js + Supabase)
- ✅ You want built-in auth and real-time features
- ✅ You're following the production action plan

---

## 🔧 Setup Instructions

### **MongoDB Setup**
```bash
# 1. Set environment variable
export MONGO_URL="mongodb://localhost:27017"
export DB_NAME="omnify_cloud"

# 2. Start backend server
cd backend
python agentkit_server.py
```

### **Supabase Setup**
```bash
# 1. Create Supabase project at supabase.com
# 2. Set environment variables
export NEXT_PUBLIC_SUPABASE_URL="https://xxx.supabase.co"
export NEXT_PUBLIC_SUPABASE_ANON_KEY="your_anon_key"
export SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# 3. Run migrations
# In Supabase SQL Editor, run:
# - supabase/migrations/003_add_auth_id.sql
# - supabase/migrations/004_add_action_logs.sql

# 4. Start frontend
cd omnify-brain
npm run dev
```

---

## 📚 Related Documentation

- **MongoDB Backend**: `docs/BACKEND_STARTUP_GUIDE.md`
- **Supabase Frontend**: `omnify-brain/docs/IMPLEMENTATION_SUMMARY.md`
- **User Registration**: `docs/USER_REGISTRATION_FLOW.md` (MongoDB)
- **Production Plan**: `omnify-brain/docs/IMPLEMENTATION_SUMMARY.md` (Supabase)

---

**Last Updated**: November 2025  
**Status**: Both systems active, serving different purposes

