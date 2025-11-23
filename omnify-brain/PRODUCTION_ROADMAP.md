# Production Implementation Plan - Omnify AI Marketing Brain

## Goal
Transform the MVP demo into a **production-ready SaaS** with real-time data ingestion, persistent storage, and AI-powered insights.

## Architecture Overview

### Current (MVP)
- Static JSON data
- TypeScript brain modules (client-side)
- No external dependencies

### Target (Production)
- **Real-time API integrations** (Meta, Google, TikTok, Shopify)
- **Supabase database** for persistent storage
- **AI/ML services** (OpenAI/Anthropic) for advanced insights
- **Authentication** (NextAuth.js)
- **Webhooks** for real-time data updates
- **Background jobs** for data processing

---

## Phase 1: Database & Authentication (Week 1)

### 1.1 Supabase Setup
- [ ] Create Supabase project
- [ ] Define database schema (see below)
- [ ] Set up Row Level Security (RLS) policies
- [ ] Create database migrations

### 1.2 Database Schema

```sql
-- Organizations (Multi-tenant)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  organization_id UUID REFERENCES organizations(id),
  role TEXT CHECK (role IN ('admin', 'member', 'viewer')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketing Channels
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id),
  name TEXT NOT NULL,
  platform TEXT CHECK (platform IN ('Meta', 'Google', 'TikTok', 'Shopify', 'Email')),
  external_id TEXT, -- Platform-specific ID
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily Metrics (Time-series data)
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id),
  date DATE NOT NULL,
  spend NUMERIC(12,2),
  revenue NUMERIC(12,2),
  impressions INTEGER,
  clicks INTEGER,
  conversions INTEGER,
  roas NUMERIC(10,2),
  cpa NUMERIC(10,2),
  ctr NUMERIC(5,4),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(channel_id, date)
);

-- Creatives
CREATE TABLE creatives (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id),
  name TEXT NOT NULL,
  external_id TEXT,
  status TEXT CHECK (status IN ('active', 'paused', 'archived')),
  launch_date DATE,
  spend NUMERIC(12,2),
  revenue NUMERIC(12,2),
  roas NUMERIC(10,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain State (Cached outputs)
CREATE TABLE brain_states (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id),
  memory_output JSONB,
  oracle_output JSONB,
  curiosity_output JSONB,
  computed_at TIMESTAMPTZ DEFAULT NOW()
);

-- API Credentials (Encrypted)
CREATE TABLE api_credentials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id),
  platform TEXT NOT NULL,
  credentials JSONB, -- Encrypted
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 1.3 Authentication
- [ ] Install NextAuth.js
- [ ] Configure email/password provider
- [ ] Add Google OAuth (optional)
- [ ] Implement session management
- [ ] Create protected routes

---

## Phase 2: Marketing Platform Integrations (Week 2-3)

### 2.1 Meta Ads Integration
**API**: [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis)

**Required Credentials**:
- `META_ADS_ACCESS_TOKEN`
- `META_ADS_ACCOUNT_ID`

**Endpoints to Integrate**:
- `/insights` - Get campaign/ad set/ad performance
- `/campaigns` - List campaigns
- `/adsets` - List ad sets
- `/ads` - List ads with creative data

**Implementation**:
```typescript
// src/lib/integrations/meta-ads.ts
export class MetaAdsClient {
  async fetchInsights(dateRange: { start: string; end: string }) {
    // Fetch daily metrics
  }
  
  async fetchCreatives() {
    // Fetch creative performance
  }
}
```

### 2.2 Google Ads Integration
**API**: [Google Ads API](https://developers.google.com/google-ads/api/docs/start)

**Required Credentials**:
- `GOOGLE_ADS_CLIENT_ID`
- `GOOGLE_ADS_CLIENT_SECRET`
- `GOOGLE_ADS_REFRESH_TOKEN`
- `GOOGLE_ADS_CUSTOMER_ID`

**Implementation**:
```typescript
// src/lib/integrations/google-ads.ts
export class GoogleAdsClient {
  async fetchCampaignMetrics(dateRange) {
    // Use Google Ads Query Language (GAQL)
  }
}
```

### 2.3 TikTok Ads Integration
**API**: [TikTok Marketing API](https://business-api.tiktok.com/portal/docs)

**Required Credentials**:
- `TIKTOK_ADS_ACCESS_TOKEN`
- `TIKTOK_ADS_ADVERTISER_ID`

### 2.4 Shopify Integration
**API**: [Shopify Admin API](https://shopify.dev/docs/api/admin-rest)

**Required Credentials**:
- `SHOPIFY_STORE_URL`
- `SHOPIFY_ACCESS_TOKEN`

**Endpoints**:
- `/orders.json` - Fetch order data for revenue attribution
- `/customers.json` - Customer LTV calculation

### 2.5 Data Ingestion Pipeline
- [ ] Create `/api/ingest/[platform]` endpoints
- [ ] Implement rate limiting (respect API limits)
- [ ] Add error handling & retry logic
- [ ] Store raw data in `daily_metrics` table
- [ ] Schedule daily sync jobs (cron or Vercel Cron)

---

## Phase 3: AI/ML Services Integration (Week 3-4)

### 3.1 OpenAI Integration
**Use Cases**:
- **Creative Fatigue Analysis**: Analyze ad copy/images for saturation
- **Anomaly Detection**: Identify unusual patterns in metrics
- **Natural Language Insights**: Generate executive summaries

**Implementation**:
```typescript
// src/lib/ai/openai-client.ts
import OpenAI from 'openai';

export class OmnifyAI {
  async analyzeCreativeFatigue(creative: CreativeData) {
    const prompt = `Analyze this ad creative performance...`;
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }]
    });
    return response.choices[0].message.content;
  }
}
```

### 3.2 Anthropic (Claude) Integration
**Use Cases**:
- **Long-form analysis**: Deep-dive reports
- **Multi-step reasoning**: Complex budget optimization

**Implementation**:
```typescript
// src/lib/ai/anthropic-client.ts
import Anthropic from '@anthropic-ai/sdk';

export class ClaudeAnalyzer {
  async generateBudgetRecommendations(data: BrainState) {
    // Use Claude for strategic recommendations
  }
}
```

### 3.3 Enhanced Brain Modules
**Upgrade Oracle Module**:
- Replace rule-based fatigue detection with AI analysis
- Use embeddings for creative similarity detection
- Implement time-series forecasting (Prophet or ARIMA)

**Upgrade Curiosity Module**:
- Use AI to generate natural language action descriptions
- Implement reinforcement learning for action ranking (future)

---

## Phase 4: Real-time Features (Week 4-5)

### 4.1 Webhooks
- [ ] Implement webhook endpoints for platform events
- [ ] Meta Ads: Campaign status changes
- [ ] Shopify: New orders (for real-time revenue)

### 4.2 Background Jobs
- [ ] Set up job queue (BullMQ or Vercel Cron)
- [ ] Daily data sync job (runs at 2 AM)
- [ ] Brain cycle job (runs after data sync)
- [ ] Email alerts for critical risks

### 4.3 Real-time Dashboard
- [ ] Add WebSocket support (Supabase Realtime)
- [ ] Live metric updates
- [ ] Push notifications for high-urgency actions

---

## Phase 5: Polish & Launch (Week 5-6)

### 5.1 UI Enhancements
- [ ] Add historical trend charts (Recharts)
- [ ] Implement date range picker
- [ ] Add export functionality (PDF reports)
- [ ] Mobile responsiveness

### 5.2 Onboarding Flow
- [ ] OAuth connection wizard for each platform
- [ ] Initial data sync progress indicator
- [ ] First-time user tutorial

### 5.3 Billing & Subscriptions
- [ ] Integrate Stripe
- [ ] Implement usage-based pricing tiers
- [ ] Add billing dashboard

---

## Environment Variables (Production)

```bash
# Database
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx

# Auth
NEXTAUTH_SECRET=xxx
NEXTAUTH_URL=https://app.omnify.ai

# Meta Ads
META_ADS_ACCESS_TOKEN=xxx
META_ADS_ACCOUNT_ID=act_xxx

# Google Ads
GOOGLE_ADS_CLIENT_ID=xxx
GOOGLE_ADS_CLIENT_SECRET=xxx
GOOGLE_ADS_REFRESH_TOKEN=xxx
GOOGLE_ADS_CUSTOMER_ID=xxx-xxx-xxxx

# TikTok Ads
TIKTOK_ADS_ACCESS_TOKEN=xxx
TIKTOK_ADS_ADVERTISER_ID=xxx

# Shopify
SHOPIFY_STORE_URL=xxx.myshopify.com
SHOPIFY_ACCESS_TOKEN=xxx

# AI Services
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

---

## Deployment Strategy

### Staging Environment
- Deploy to Vercel (staging branch)
- Use test API credentials
- Seed with sample data

### Production Environment
- Deploy to Vercel (main branch)
- Enable Vercel Cron for scheduled jobs
- Set up monitoring (Sentry, LogRocket)
- Configure custom domain

---

## Success Metrics

- [ ] **Data Freshness**: Metrics updated within 24 hours
- [ ] **Prediction Accuracy**: Oracle predictions validated against actual outcomes
- [ ] **User Engagement**: Daily active users, session duration
- [ ] **Action Adoption**: % of recommended actions executed by users
