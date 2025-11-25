# Omnify Brain - Production Action Plan

## Overview

This document outlines the action plan to take Omnify Brain from demo to production-ready SaaS.

**Current State**: Demo working with seed data, single tenant  
**Target State**: Multi-tenant SaaS with real ad platform integrations  
**Estimated Timeline**: 4-6 weeks for MVP launch

---

## Phase 1: Authentication & Multi-tenancy (Week 1)

### 1.1 Set Up NextAuth with Supabase Auth
**Effort**: 2 days | **Priority**: P0

**Tasks**:
- [ ] Install NextAuth.js and Supabase Auth adapter
- [ ] Create auth pages: `/login`, `/signup`, `/forgot-password`
- [ ] Configure OAuth providers (Google, optional: Microsoft)
- [ ] Set up email/password authentication
- [ ] Create middleware to protect routes

**Files to Create**:
```
src/app/api/auth/[...nextauth]/route.ts
src/app/(auth)/login/page.tsx
src/app/(auth)/signup/page.tsx
src/lib/auth.ts
src/middleware.ts
```

**Acceptance Criteria**:
- Users can sign up with email or Google
- Users are redirected to login if not authenticated
- Session persists across page refreshes

### 1.2 Organization Management
**Effort**: 1 day | **Priority**: P0

**Tasks**:
- [ ] Create organization on first user signup
- [ ] Link users to organizations
- [ ] Add organization switcher (for users in multiple orgs)
- [ ] Update data service to filter by user's organization

**Database Changes**:
```sql
-- Link auth.users to our users table
ALTER TABLE users ADD COLUMN auth_id UUID REFERENCES auth.users(id);
CREATE INDEX idx_users_auth_id ON users(auth_id);
```

**Acceptance Criteria**:
- New signup creates organization + user
- All data queries scoped to user's organization
- Users only see their own data

### 1.3 Role-Based Access Control
**Effort**: 1 day | **Priority**: P1

**Tasks**:
- [ ] Implement role checks (admin, member, viewer)
- [ ] Admin can invite team members
- [ ] Admin can manage API credentials
- [ ] Viewer has read-only access

**Acceptance Criteria**:
- Admins can invite users via email
- Role permissions enforced on UI and API

---

## Phase 2: Onboarding Flow (Week 1-2)

### 2.1 Onboarding Wizard
**Effort**: 2 days | **Priority**: P0

**Tasks**:
- [ ] Create multi-step onboarding wizard
- [ ] Step 1: Company info (name, industry, revenue range)
- [ ] Step 2: Connect ad platforms (OAuth flows)
- [ ] Step 3: Initial data sync
- [ ] Step 4: First brain cycle + dashboard

**Files to Create**:
```
src/app/onboarding/page.tsx
src/app/onboarding/steps/CompanyInfo.tsx
src/app/onboarding/steps/ConnectPlatforms.tsx
src/app/onboarding/steps/SyncData.tsx
src/app/onboarding/steps/Complete.tsx
src/components/onboarding/OnboardingWizard.tsx
```

**UI Flow**:
```
Signup → Onboarding Wizard → Dashboard
         ├─ Company Info
         ├─ Connect Meta Ads
         ├─ Connect Google Ads (optional)
         ├─ Sync Data (progress bar)
         └─ View First Insights
```

**Acceptance Criteria**:
- New users guided through setup
- At least one ad platform connected
- First brain cycle runs automatically
- User lands on dashboard with real data

---

## Phase 3: Ad Platform Connectors (Week 2-3)

### 3.1 Meta Ads Connector
**Effort**: 3-4 days | **Priority**: P0

**Tasks**:
- [ ] Register Meta App (developers.facebook.com)
- [ ] Implement OAuth 2.0 flow for Meta
- [ ] Create Meta Ads API service
- [ ] Fetch: campaigns, ad sets, ads, insights
- [ ] Map Meta data to our schema
- [ ] Store credentials securely (encrypted)
- [ ] Handle token refresh

**Files to Create**:
```
src/lib/connectors/meta/oauth.ts
src/lib/connectors/meta/api.ts
src/lib/connectors/meta/sync.ts
src/app/api/connectors/meta/callback/route.ts
src/app/api/connectors/meta/sync/route.ts
```

**API Endpoints Needed**:
- `GET /api/connectors/meta/auth` - Start OAuth
- `GET /api/connectors/meta/callback` - OAuth callback
- `POST /api/connectors/meta/sync` - Trigger sync
- `GET /api/connectors/meta/status` - Sync status

**Data to Fetch**:
```
Campaigns → campaigns table
Ad Sets → (map to campaigns)
Ads → creatives table
Insights → daily_metrics table
  - spend, impressions, clicks, conversions
  - frequency, cpm, cpc, ctr
```

**Acceptance Criteria**:
- User can connect Meta Ads account
- Historical data (30 days) imported
- Daily metrics populated correctly
- Creatives with performance data

### 3.2 Google Ads Connector
**Effort**: 3-4 days | **Priority**: P1

**Tasks**:
- [ ] Register Google Cloud project
- [ ] Enable Google Ads API
- [ ] Implement OAuth 2.0 flow
- [ ] Create Google Ads API service
- [ ] Fetch: campaigns, ad groups, ads, metrics
- [ ] Map Google data to our schema

**Files to Create**:
```
src/lib/connectors/google/oauth.ts
src/lib/connectors/google/api.ts
src/lib/connectors/google/sync.ts
src/app/api/connectors/google/callback/route.ts
```

**Acceptance Criteria**:
- User can connect Google Ads account
- Data imported and mapped correctly

### 3.3 Shopify Connector (for LTV/Cohorts)
**Effort**: 2-3 days | **Priority**: P1

**Tasks**:
- [ ] Create Shopify App (partners.shopify.com)
- [ ] Implement OAuth flow
- [ ] Fetch: orders, customers
- [ ] Calculate cohort LTV (30d, 60d, 90d)
- [ ] Populate cohorts table

**Data to Calculate**:
```
Orders + Customers → Cohort Analysis
- Group by acquisition month
- Calculate LTV at 30/60/90/180 days
- Track repeat purchase rate
- Identify acquisition channel (UTM)
```

**Acceptance Criteria**:
- Cohorts populated from real order data
- LTV drift detection works with real data

### 3.4 TikTok Ads Connector
**Effort**: 2-3 days | **Priority**: P2

**Tasks**:
- [ ] Register TikTok for Business app
- [ ] Implement OAuth flow
- [ ] Fetch campaigns, ads, metrics
- [ ] Map to our schema

---

## Phase 4: Scheduled Jobs & Automation (Week 3)

### 4.1 Daily Data Sync
**Effort**: 1 day | **Priority**: P0

**Tasks**:
- [ ] Set up cron job (Vercel Cron or external)
- [ ] Sync all connected platforms daily
- [ ] Run brain cycle after sync
- [ ] Store sync job status

**Cron Schedule**:
```
0 6 * * * - 6 AM UTC daily
1. For each organization with active connections:
   a. Sync Meta Ads (if connected)
   b. Sync Google Ads (if connected)
   c. Sync TikTok Ads (if connected)
   d. Sync Shopify (if connected)
2. Run brain cycle
3. Save brain state
4. Send alerts if high-risk detected
```

**Files to Create**:
```
src/app/api/cron/daily-sync/route.ts
src/lib/jobs/sync-all.ts
src/lib/jobs/run-brain-cycle.ts
```

**Acceptance Criteria**:
- Data refreshes daily without manual intervention
- Brain insights always up-to-date

### 4.2 Email Alerts
**Effort**: 1 day | **Priority**: P2

**Tasks**:
- [ ] Set up email provider (Resend, SendGrid)
- [ ] Create alert templates
- [ ] Send alerts on high-risk detection
- [ ] Weekly summary email

**Alert Triggers**:
- Creative fatigue > 70% probability
- ROI decay > 20%
- LTV drift > 15%
- Global risk level = RED

---

## Phase 5: Action Execution (Week 4)

### 5.1 One-Click Actions
**Effort**: 3-4 days | **Priority**: P1

**Tasks**:
- [ ] Implement "Pause Creative" action (Meta API)
- [ ] Implement "Adjust Budget" action (Meta API)
- [ ] Add confirmation modal before execution
- [ ] Log all actions taken
- [ ] Show action history

**Files to Create**:
```
src/lib/actions/pause-creative.ts
src/lib/actions/adjust-budget.ts
src/app/api/actions/execute/route.ts
src/components/dashboard/ActionConfirmModal.tsx
```

**Safety Features**:
- Confirmation required before execution
- Undo window (where possible)
- Audit log of all actions
- Daily action limits

**Acceptance Criteria**:
- User clicks "Execute" → Creative paused in Meta
- Action logged with timestamp and user
- Success/failure feedback shown

---

## Phase 6: Deployment & Infrastructure (Week 4)

### 6.1 Deploy to Vercel
**Effort**: 0.5 days | **Priority**: P0

**Tasks**:
- [ ] Connect GitHub repo to Vercel
- [ ] Configure environment variables
- [ ] Set up custom domain
- [ ] Enable Vercel Analytics

**Environment Variables**:
```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
NEXTAUTH_SECRET
NEXTAUTH_URL
META_APP_ID
META_APP_SECRET
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
```

### 6.2 Monitoring & Logging
**Effort**: 0.5 days | **Priority**: P1

**Tasks**:
- [ ] Set up error tracking (Sentry)
- [ ] Add structured logging
- [ ] Create health check endpoint
- [ ] Set up uptime monitoring

---

## Phase 7: Polish & Launch Prep (Week 5-6)

### 7.1 UI/UX Improvements
**Effort**: 2-3 days | **Priority**: P1

**Tasks**:
- [ ] Loading states and skeletons
- [ ] Error boundaries and fallbacks
- [ ] Mobile responsive design
- [ ] Dark mode support
- [ ] Accessibility audit (a11y)

### 7.2 Documentation
**Effort**: 1-2 days | **Priority**: P1

**Tasks**:
- [ ] User guide / Help center
- [ ] API documentation
- [ ] Video tutorials (Loom)
- [ ] FAQ page

### 7.3 Landing Page
**Effort**: 1-2 days | **Priority**: P1

**Tasks**:
- [ ] Marketing landing page
- [ ] Pricing page
- [ ] Demo request form
- [ ] Customer testimonials (placeholder)

---

## Timeline Summary

```
Week 1: Authentication + Onboarding
        ├─ NextAuth setup (2 days)
        ├─ Organization management (1 day)
        └─ Onboarding wizard (2 days)

Week 2: Meta Ads Connector
        ├─ OAuth flow (1 day)
        ├─ API integration (2 days)
        └─ Data sync (1 day)

Week 3: Google Ads + Automation
        ├─ Google connector (3 days)
        ├─ Daily cron job (1 day)
        └─ Email alerts (1 day)

Week 4: Actions + Deployment
        ├─ Action execution (3 days)
        ├─ Vercel deployment (0.5 day)
        └─ Monitoring setup (0.5 day)

Week 5-6: Polish + Launch
        ├─ UI improvements (2 days)
        ├─ Documentation (2 days)
        ├─ Landing page (2 days)
        └─ Beta testing + fixes
```

---

## Success Metrics

### Launch Criteria (MVP)
- [ ] 3+ beta customers onboarded
- [ ] Meta Ads integration working
- [ ] Daily automated brain cycles
- [ ] < 2s dashboard load time
- [ ] Zero critical bugs

### Post-Launch KPIs
- Customer activation rate (complete onboarding)
- Daily active users
- Actions executed per user
- Time to first insight
- Customer retention (30-day)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Meta API rate limits | Implement backoff, cache data |
| OAuth token expiry | Auto-refresh tokens, alert on failure |
| Data sync failures | Retry logic, manual sync button |
| Action execution errors | Confirmation modal, undo capability |
| Slow dashboard | Server-side caching, optimize queries |

---

## Immediate Next Steps

1. **Today**: Decide on Week 1 priorities
2. **Tomorrow**: Start NextAuth implementation
3. **This Week**: Complete auth + basic onboarding
4. **Next Week**: Meta Ads connector

---

*Document Version*: 1.0  
*Created*: November 2025  
*Owner*: Omnify Team
