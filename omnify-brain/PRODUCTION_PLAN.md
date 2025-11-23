# Production Implementation Plan - Omnify Brain

**Strategy**: Keep MVP Demo Separate + Build Full Production  
**Timeline**: 6 weeks  
**Status**: Ready to Execute

---

## 1. Separation Strategy

### Directory Structure
```
omnify-brain/
├── demo/                    # MVP Demo (Isolated, Static)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── scripts/
│   ├── package.json        # Minimal dependencies
│   └── README.md
│
├── src/                     # Production App (Full SaaS)
│   ├── app/
│   │   ├── (auth)/         # Login, signup
│   │   ├── (dashboard)/    # Protected routes
│   │   └── api/            # All API routes
│   ├── components/
│   ├── lib/
│   └── middleware.ts       # Route protection
│
├── tests/                   # Test suite
├── supabase/               # Database migrations
└── package.json            # Production dependencies
```

---

## 2. Implementation Phases

### **PHASE 0: Restructure (Day 1)**
Move current MVP to `demo/` directory

**Tasks**:
- [ ] Create `demo/` directory
- [ ] Move MVP files: `app/`, `components/`, `lib/`, `scripts/`, `data/`
- [ ] Create `demo/package.json` with minimal deps
- [ ] Test demo works independently
- [ ] Git commit: "Separate MVP demo"

**Commands**:
```bash
mkdir demo
mv src/{app,components,lib,data} demo/
mv scripts demo/
cd demo && npm init -y
npm install next react react-dom tailwindcss
```

---

### **PHASE 1: Foundation (Week 1)**

#### Day 1-2: Environment & Database
- [ ] Create Supabase project
- [ ] Deploy schema: `supabase/migrations/001_initial_schema.sql`
- [ ] Create `.env.local` with credentials
- [ ] Create `scripts/seed-production.ts`
- [ ] Seed test data (org, users, 90 days metrics)

#### Day 3-4: Authentication
- [ ] Configure NextAuth.js: `src/app/api/auth/[...nextauth]/route.ts`
- [ ] Create login page: `src/app/(auth)/login/page.tsx`
- [ ] Create signup page: `src/app/(auth)/signup/page.tsx`
- [ ] Add middleware: `src/middleware.ts` (protect routes)
- [ ] Test auth flow

#### Day 5: Database Layer
- [ ] Create `src/lib/db/queries.ts` (reusable queries)
- [ ] Create `src/lib/db/mutations.ts` (reusable mutations)
- [ ] Add TypeScript types from Supabase
- [ ] Create `src/lib/utils/validation.ts`

---

### **PHASE 2: Core Features (Week 2)**

#### Day 6-7: Brain Service
- [ ] Create `src/lib/services/brain-service.ts`
- [ ] Implement `computeBrainState(orgId)` using production modules
- [ ] Create API: `src/app/api/brain/compute/route.ts`
- [ ] Create API: `src/app/api/brain/state/route.ts`
- [ ] Add caching to `brain_states` table

#### Day 8-9: Production Dashboard
- [ ] Create `src/lib/hooks/useBrainState.ts` (SWR hook)
- [ ] Build `src/app/(dashboard)/page.tsx` (fetch real data)
- [ ] Update dashboard components to use production data
- [ ] Add persona context integration
- [ ] Test end-to-end flow

#### Day 10: Error Handling
- [ ] Create `src/components/shared/ErrorBoundary.tsx`
- [ ] Create `src/components/shared/LoadingState.tsx`
- [ ] Add toast notifications (sonner)
- [ ] Add Sentry error tracking

---

### **PHASE 3: Platform Integrations (Week 3)**

#### Day 11-12: Credentials UI
- [ ] Create `src/app/(dashboard)/settings/integrations/page.tsx`
- [ ] Build `src/components/integrations/PlatformCard.tsx`
- [ ] Add OAuth flow for Meta/Google/TikTok
- [ ] Add API key input for Shopify
- [ ] Store encrypted credentials

#### Day 13-14: Manual Sync
- [ ] Create sync UI with progress indicator
- [ ] Display sync job history
- [ ] Add error handling for failed syncs
- [ ] Test with real API credentials

#### Day 15: Scheduled Syncs
- [ ] Create `src/app/api/cron/daily-sync/route.ts`
- [ ] Configure Vercel Cron (daily at 2 AM)
- [ ] Add email notifications for failures
- [ ] Add retry logic

---

### **PHASE 4: AI Integration (Week 4)**

#### Day 16-17: AI-Powered Oracle
- [ ] Update `src/lib/brain/oracle.ts` to use OpenAI
- [ ] Replace rule-based fatigue with AI analysis
- [ ] Add anomaly detection
- [ ] Add confidence scoring

#### Day 18-19: AI-Powered Curiosity
- [ ] Update `src/lib/brain/curiosity.ts` to use Anthropic
- [ ] Generate natural language recommendations
- [ ] Add strategic insights
- [ ] Add impact forecasting

#### Day 20: AI Executive Summary
- [ ] Add executive summary generation
- [ ] Display in TopBar
- [ ] Add persona-specific summaries

---

### **PHASE 5: Polish (Week 5)**

#### Day 21-22: Historical Analytics
- [ ] Install Recharts
- [ ] Create `src/components/dashboard/MetricsChart.tsx`
- [ ] Add date range picker
- [ ] Create `/analytics` page with trends

#### Day 23-24: Onboarding
- [ ] Create `src/components/onboarding/WelcomeWizard.tsx`
- [ ] Add platform connection wizard
- [ ] Add initial sync progress
- [ ] Add tutorial tooltips

#### Day 25: Mobile Responsiveness
- [ ] Test on mobile devices
- [ ] Fix responsive issues
- [ ] Add mobile navigation

---

### **PHASE 6: Testing & Launch (Week 6)**

#### Day 26-27: Testing
- [ ] Write unit tests for brain modules
- [ ] Write integration tests for API routes
- [ ] Write E2E tests (Playwright)
- [ ] Achieve 80% code coverage

#### Day 28-29: Deployment
- [ ] Deploy to Vercel (staging)
- [ ] Configure custom domain
- [ ] Set up monitoring (Sentry, LogRocket)
- [ ] Load testing

#### Day 30: Launch
- [ ] Deploy to production
- [ ] Monitor for errors
- [ ] Gather user feedback

---

## 3. Gap Closure Checklist

### Authentication (❌ → ✅)
- [ ] NextAuth.js configured
- [ ] Login/signup pages
- [ ] Session management
- [ ] Route protection middleware
- [ ] Password reset flow

### Production Dashboard (❌ → ✅)
- [ ] Fetches from Supabase (not JSON)
- [ ] Uses production brain modules
- [ ] Real-time data updates
- [ ] Error boundaries
- [ ] Loading states

### Platform Integrations (⚠️ → ✅)
- [ ] Credentials management UI
- [ ] OAuth flows working
- [ ] Manual sync functional
- [ ] Scheduled syncs running
- [ ] Webhook endpoints

### AI Integration (⚠️ → ✅)
- [ ] OpenAI integrated in Oracle
- [ ] Anthropic integrated in Curiosity
- [ ] Executive summaries generated
- [ ] Anomaly detection working

### UI Enhancements (❌ → ✅)
- [ ] Historical charts (Recharts)
- [ ] Date range picker
- [ ] Mobile responsive
- [ ] Export functionality (PDF)
- [ ] Persona-specific microcopy

### Testing (❌ → ✅)
- [ ] Unit tests (80% coverage)
- [ ] Integration tests
- [ ] E2E tests (Playwright)
- [ ] Load testing

### Monitoring (❌ → ✅)
- [ ] Sentry error tracking
- [ ] LogRocket session replay
- [ ] Vercel Analytics
- [ ] Uptime monitoring

### Billing (❌ → ✅)
- [ ] Stripe integration
- [ ] Subscription plans
- [ ] Usage tracking
- [ ] Billing dashboard

---

## 4. Key Files to Create

### Authentication
```
src/app/api/auth/[...nextauth]/route.ts
src/app/(auth)/login/page.tsx
src/app/(auth)/signup/page.tsx
src/middleware.ts
src/lib/auth/auth-config.ts
```

### Production Dashboard
```
src/app/(dashboard)/page.tsx
src/lib/hooks/useBrainState.ts
src/lib/services/brain-service.ts
src/app/api/brain/compute/route.ts
src/app/api/brain/state/route.ts
```

### Integrations
```
src/app/(dashboard)/settings/integrations/page.tsx
src/components/integrations/PlatformCard.tsx
src/components/integrations/OAuthFlow.tsx
src/app/api/cron/daily-sync/route.ts
```

### Error Handling
```
src/components/shared/ErrorBoundary.tsx
src/components/shared/LoadingState.tsx
src/lib/utils/error-handling.ts
```

### Testing
```
tests/unit/brain/memory.test.ts
tests/integration/api/sync.test.ts
tests/e2e/dashboard.spec.ts
```

---

## 5. Environment Variables

### Required for Production
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Auth
NEXTAUTH_SECRET=
NEXTAUTH_URL=

# Meta Ads
META_ADS_ACCESS_TOKEN=
META_ADS_ACCOUNT_ID=

# Google Ads
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=

# TikTok Ads
TIKTOK_ADS_ACCESS_TOKEN=
TIKTOK_ADS_ADVERTISER_ID=

# Shopify
SHOPIFY_STORE_URL=
SHOPIFY_ACCESS_TOKEN=

# AI Services
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Monitoring
SENTRY_DSN=
LOGROCKET_APP_ID=

# Cron
CRON_SECRET=
```

---

## 6. Deployment Strategy

### Demo Deployment
```bash
cd demo
npm run build
vercel --prod --name omnify-brain-demo
```

### Production Deployment
```bash
npm run build
npm run test
vercel --prod --name omnify-brain
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy-prod.yml
name: Deploy Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install
      - run: npm run test
      - run: npm run build
      - run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 7. Success Metrics

### Week 1
- ✅ Authentication working
- ✅ Database seeded
- ✅ Dashboard shows real data

### Week 2
- ✅ Brain cycle runs on production data
- ✅ Error handling in place
- ✅ Loading states implemented

### Week 3
- ✅ At least 2 platforms connected
- ✅ Manual sync working
- ✅ Scheduled syncs running

### Week 4
- ✅ AI insights generating
- ✅ Anomaly detection working
- ✅ Executive summaries displayed

### Week 5
- ✅ Historical charts working
- ✅ Mobile responsive
- ✅ Onboarding flow complete

### Week 6
- ✅ 80% test coverage
- ✅ Deployed to production
- ✅ Monitoring active

---

## 8. Risk Mitigation

### High Risk Items
1. **API Rate Limits**: Implement exponential backoff
2. **Data Loss**: Daily backups of Supabase
3. **Auth Vulnerabilities**: Security audit before launch
4. **AI Costs**: Set spending limits on OpenAI/Anthropic

### Rollback Plan
- Keep demo version always deployable
- Use feature flags for new features
- Database migrations are reversible
- Vercel allows instant rollback

---

## Next Steps

1. **Run Phase 0** (Day 1): Execute restructure script
2. **Set up Supabase** (Day 1): Create project and deploy schema
3. **Start Phase 1** (Day 2): Begin authentication implementation

**Ready to begin?** Start with:
```bash
./scripts/migrate-to-production.sh
```
