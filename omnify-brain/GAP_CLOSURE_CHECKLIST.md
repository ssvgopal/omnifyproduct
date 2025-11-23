# Gap Closure Checklist - Omnify Brain

**Purpose**: Track all missing features and gaps identified in implementation analysis  
**Status**: 🔴 Not Started → 🟡 In Progress → 🟢 Complete

---

## Critical Gaps (Must Fix)

### 1. Dashboard Not Using Production Components 🔴
**Current**: Dashboard reads from `brain-state.json` (static file)  
**Required**: Dashboard fetches from Supabase and uses production brain modules

- [ ] Create `src/lib/services/brain-service.ts`
- [ ] Create `src/app/api/brain/state/route.ts`
- [ ] Create `src/app/api/brain/compute/route.ts`
- [ ] Create `src/lib/hooks/useBrainState.ts` (SWR hook)
- [ ] Update `src/app/(dashboard)/page.tsx` to use production data
- [ ] Test end-to-end: Supabase → Brain → Dashboard

**Acceptance Criteria**:
- ✅ Dashboard shows real data from Supabase
- ✅ Brain cycle runs on production data
- ✅ No references to static JSON files

---

### 2. No Authentication 🔴
**Current**: No login, no user management  
**Required**: Full authentication with NextAuth.js

- [ ] Install NextAuth.js dependencies
- [ ] Create `src/app/api/auth/[...nextauth]/route.ts`
- [ ] Configure email/password provider
- [ ] Create `src/app/(auth)/login/page.tsx`
- [ ] Create `src/app/(auth)/signup/page.tsx`
- [ ] Create `src/middleware.ts` (route protection)
- [ ] Add session management
- [ ] Test login/logout flow

**Acceptance Criteria**:
- ✅ Users can sign up with email/password
- ✅ Users can log in
- ✅ Protected routes redirect to login
- ✅ Session persists across page refreshes

---

### 3. No Environment Configuration 🔴
**Current**: `.env` file doesn't exist  
**Required**: All environment variables configured

- [ ] Run `scripts/setup-env.sh`
- [ ] Create Supabase project
- [ ] Fill in Supabase credentials
- [ ] Generate NextAuth secret
- [ ] Fill in CRON_SECRET
- [ ] Test environment validation

**Acceptance Criteria**:
- ✅ `.env.local` exists with all required variables
- ✅ App starts without environment errors
- ✅ Supabase connection works

---

### 4. No Production Data 🔴
**Current**: Supabase database is empty  
**Required**: Database seeded with test data

- [ ] Deploy `supabase/migrations/001_initial_schema.sql`
- [ ] Create `scripts/seed-production.ts`
- [ ] Seed test organization
- [ ] Seed test users (Sarah, Jason, Emily)
- [ ] Seed channels (Meta, Google, TikTok)
- [ ] Seed 90 days of metrics
- [ ] Verify data in Supabase dashboard

**Acceptance Criteria**:
- ✅ Database schema deployed
- ✅ Test data exists in all tables
- ✅ Can query data successfully

---

## High Priority Gaps

### 5. Persona Context Not Wired 🔴
**Current**: PersonaToggle changes state but cards don't adapt  
**Required**: Cards show persona-specific microcopy

- [ ] Update `MemoryCard.tsx` with persona-specific text
- [ ] Update `OracleCard.tsx` with persona-specific text
- [ ] Update `CuriosityCard.tsx` with persona-specific text
- [ ] Test all three personas (Sarah, Jason, Emily)

**Acceptance Criteria**:
- ✅ Sarah sees strategic/high-level content
- ✅ Jason sees analytical/risk-focused content
- ✅ Emily sees tactical/action-focused content

---

### 6. No Error Boundaries 🔴
**Current**: Errors crash the entire app  
**Required**: Graceful error handling

- [ ] Create `src/components/shared/ErrorBoundary.tsx`
- [ ] Wrap dashboard in ErrorBoundary
- [ ] Add error logging (Sentry)
- [ ] Test error scenarios

**Acceptance Criteria**:
- ✅ API failures show error message (not crash)
- ✅ Errors logged to Sentry
- ✅ User can recover from errors

---

### 7. No Loading States 🔴
**Current**: No feedback during data fetching  
**Required**: Loading indicators

- [ ] Create `src/components/shared/LoadingState.tsx`
- [ ] Add skeleton loaders to cards
- [ ] Add loading spinner to sync operations
- [ ] Test loading states

**Acceptance Criteria**:
- ✅ Loading indicators show during data fetch
- ✅ Skeleton loaders match final UI
- ✅ No layout shift when data loads

---

### 8. Platform Integration UI Missing 🔴
**Current**: No way to connect platforms  
**Required**: Credentials management UI

- [ ] Create `src/app/(dashboard)/settings/integrations/page.tsx`
- [ ] Create `src/components/integrations/PlatformCard.tsx`
- [ ] Add OAuth flow for Meta
- [ ] Add OAuth flow for Google
- [ ] Add OAuth flow for TikTok
- [ ] Add API key input for Shopify
- [ ] Store encrypted credentials in Supabase

**Acceptance Criteria**:
- ✅ Users can connect Meta Ads via OAuth
- ✅ Users can connect Google Ads via OAuth
- ✅ Users can connect TikTok Ads via OAuth
- ✅ Users can enter Shopify credentials
- ✅ Credentials stored encrypted

---

### 9. No Manual Sync UI 🔴
**Current**: No way to trigger data sync  
**Required**: Manual sync with progress indicator

- [ ] Add "Sync Now" button to integrations page
- [ ] Create sync progress indicator
- [ ] Display sync job history
- [ ] Show sync errors
- [ ] Test with real API credentials

**Acceptance Criteria**:
- ✅ Users can trigger manual sync
- ✅ Progress indicator shows sync status
- ✅ Sync history displayed
- ✅ Errors shown with actionable messages

---

### 10. No Scheduled Syncs 🔴
**Current**: No automated data updates  
**Required**: Daily scheduled syncs

- [ ] Create `src/app/api/cron/daily-sync/route.ts`
- [ ] Configure Vercel Cron (daily at 2 AM)
- [ ] Add email notifications for failures
- [ ] Add retry logic with exponential backoff
- [ ] Test cron endpoint

**Acceptance Criteria**:
- ✅ Cron job runs daily at 2 AM
- ✅ All platforms synced automatically
- ✅ Email sent on sync failure
- ✅ Failed syncs retry with backoff

---

## Medium Priority Gaps

### 11. AI Not Integrated 🟡
**Current**: AI clients exist but not used  
**Required**: AI-powered insights

- [ ] Update `oracle.ts` to use OpenAI for fatigue analysis
- [ ] Update `curiosity.ts` to use Anthropic for recommendations
- [ ] Add executive summary generation
- [ ] Add anomaly detection
- [ ] Test with real API keys

**Acceptance Criteria**:
- ✅ Creative fatigue uses AI analysis
- ✅ Recommendations use AI generation
- ✅ Executive summary displayed
- ✅ Anomalies detected and highlighted

---

### 12. No Historical Charts 🔴
**Current**: Dashboard shows current state only  
**Required**: Historical trend visualization

- [ ] Install Recharts
- [ ] Create `src/components/dashboard/MetricsChart.tsx`
- [ ] Add date range picker
- [ ] Create `/analytics` page
- [ ] Display 30/60/90 day trends

**Acceptance Criteria**:
- ✅ Charts show ROAS trends over time
- ✅ Charts show spend/revenue trends
- ✅ Date range picker works
- ✅ Charts are responsive

---

### 13. No Onboarding Flow 🔴
**Current**: New users see empty dashboard  
**Required**: Guided onboarding wizard

- [ ] Create `src/components/onboarding/WelcomeWizard.tsx`
- [ ] Add platform connection wizard
- [ ] Add initial sync progress indicator
- [ ] Add tutorial tooltips
- [ ] Test first-time user experience

**Acceptance Criteria**:
- ✅ New users see welcome wizard
- ✅ Wizard guides through platform connection
- ✅ Initial sync shows progress
- ✅ Tutorial highlights key features

---

### 14. Not Mobile Responsive 🔴
**Current**: Only tested on desktop  
**Required**: Works on mobile devices

- [ ] Test on mobile devices
- [ ] Fix responsive layout issues
- [ ] Add mobile navigation
- [ ] Test touch interactions
- [ ] Optimize for small screens

**Acceptance Criteria**:
- ✅ Dashboard usable on mobile
- ✅ All interactions work on touch
- ✅ No horizontal scrolling
- ✅ Text readable without zooming

---

### 15. No Export Functionality 🔴
**Current**: No way to export data  
**Required**: PDF/CSV export

- [ ] Add "Export" button to dashboard
- [ ] Generate PDF reports
- [ ] Generate CSV exports
- [ ] Test export functionality

**Acceptance Criteria**:
- ✅ Users can export dashboard as PDF
- ✅ Users can export metrics as CSV
- ✅ Exports include all relevant data

---

## Low Priority Gaps

### 16. No Tests 🔴
**Current**: Zero test coverage  
**Required**: 80% code coverage

- [ ] Set up Jest for unit tests
- [ ] Write tests for brain modules
- [ ] Write tests for API routes
- [ ] Set up Playwright for E2E tests
- [ ] Write E2E tests for critical flows
- [ ] Achieve 80% coverage

**Acceptance Criteria**:
- ✅ 80% unit test coverage
- ✅ All API routes tested
- ✅ E2E tests for auth, dashboard, sync

---

### 17. No Monitoring 🔴
**Current**: No error tracking or analytics  
**Required**: Production monitoring

- [ ] Set up Sentry for error tracking
- [ ] Set up LogRocket for session replay
- [ ] Add Vercel Analytics
- [ ] Set up uptime monitoring
- [ ] Test monitoring integrations

**Acceptance Criteria**:
- ✅ Errors logged to Sentry
- ✅ Sessions recorded in LogRocket
- ✅ Analytics tracking page views
- ✅ Uptime alerts configured

---

### 18. No Billing 🔴
**Current**: No payment system  
**Required**: Stripe integration

- [ ] Set up Stripe account
- [ ] Create subscription plans
- [ ] Add billing page
- [ ] Implement usage tracking
- [ ] Test payment flow

**Acceptance Criteria**:
- ✅ Users can subscribe
- ✅ Usage tracked and billed
- ✅ Billing dashboard shows invoices

---

## Progress Tracking

### Overall Status
- **Critical Gaps**: 0/4 complete (0%)
- **High Priority**: 0/6 complete (0%)
- **Medium Priority**: 0/5 complete (0%)
- **Low Priority**: 0/3 complete (0%)

**Total**: 0/18 complete (0%)

---

## Weekly Milestones

### Week 1: Foundation
- [ ] Gap 1: Dashboard using production data
- [ ] Gap 2: Authentication working
- [ ] Gap 3: Environment configured
- [ ] Gap 4: Production data seeded

### Week 2: Core Features
- [ ] Gap 5: Persona context wired
- [ ] Gap 6: Error boundaries added
- [ ] Gap 7: Loading states implemented
- [ ] Gap 11: AI integrated

### Week 3: Integrations
- [ ] Gap 8: Platform integration UI
- [ ] Gap 9: Manual sync working
- [ ] Gap 10: Scheduled syncs running

### Week 4: Polish
- [ ] Gap 12: Historical charts
- [ ] Gap 13: Onboarding flow
- [ ] Gap 14: Mobile responsive
- [ ] Gap 15: Export functionality

### Week 5: Quality
- [ ] Gap 16: Tests (80% coverage)
- [ ] Gap 17: Monitoring active

### Week 6: Launch
- [ ] Gap 18: Billing implemented
- [ ] Final QA and deployment

---

## Next Actions

1. **Run Phase 0**: Execute `scripts/migrate-to-production.sh`
2. **Set up Supabase**: Create project and deploy schema
3. **Configure Environment**: Run `scripts/setup-env.sh`
4. **Start Gap 1**: Implement production brain service

**Ready to start?** Begin with restructure script.
