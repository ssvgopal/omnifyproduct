# Omnify Brain - Implementation Plan V2

## Product Pillars Summary

| Pillar | Description | Status |
|--------|-------------|--------|
| 1. Auth & Orgs | Multi-tenant, roles, sessions | 🔴 Not Started |
| 2. Data Ingestion | Ad platform connectors | 🔴 Not Started |
| 3. Brain Modules | MEMORY, ORACLE, CURIOSITY | 🟢 Complete |
| 4. Operations | Quotas, settings, admin | 🔴 Not Started |

---

## Phase 1: Auth, Sessions & Onboarding (Week 1)

### 1.1 Supabase Auth Integration
**Effort**: 2 days | **Priority**: P0

**Backend Tasks**:
- [ ] Configure Supabase Auth (email/password + Google OAuth)
- [ ] Create `/api/auth/signup` - creates user + organization
- [ ] Create `/api/auth/invite` - admin invites team members
- [ ] Add `auth_id` column to users table linking to `auth.users`
- [ ] Update NextAuth to use Supabase Auth adapter
- [ ] Middleware: protect routes, extract `organizationId` from session

**Frontend Tasks**:
- [ ] `/login` - email/password + Google sign-in
- [ ] `/signup` - name, email, company, password
- [ ] `/forgot-password` - request reset link
- [ ] `/reset-password` - reset form after Supabase link

**Files**:
```
src/app/(auth)/login/page.tsx
src/app/(auth)/signup/page.tsx
src/app/(auth)/forgot-password/page.tsx
src/app/api/auth/[...nextauth]/route.ts
src/lib/auth.ts
src/middleware.ts
```

**API Contracts**:
```typescript
// POST /api/auth/signup
Request: { name, email, password, companyName }
Response: { success, userId, organizationId }

// Session object
{ id, email, organizationId, role: 'admin'|'member'|'viewer' }
```

**Validation**:
- Login with valid credentials → redirect to dashboard
- Session persists on refresh
- 401 on protected routes without auth

---

### 1.2 Onboarding Wizard
**Effort**: 2 days | **Priority**: P0

**Frontend Tasks**:
- [ ] `/onboarding` - multi-step wizard
- [ ] Step 1: Company info (industry, ad spend band, goals)
- [ ] Step 2: Connect platforms (Meta/Google/TikTok/Shopify only)
- [ ] Step 3: Initial sync + brain run (progress UI)
- [ ] Redirect to `/dashboard` on complete

**Backend Tasks**:
- [ ] `POST /api/onboarding/company` - save org profile
- [ ] `POST /api/onboarding/connectors` - mark chosen platforms
- [ ] `POST /api/onboarding/brain-init` - trigger first brain cycle

**Files**:
```
src/app/onboarding/page.tsx
src/app/onboarding/steps/CompanyInfo.tsx
src/app/onboarding/steps/ConnectPlatforms.tsx
src/app/onboarding/steps/SyncData.tsx
src/components/onboarding/OnboardingWizard.tsx
src/app/api/onboarding/company/route.ts
src/app/api/onboarding/brain-init/route.ts
```

**Validation**:
- New user redirected to onboarding after first login
- Only Meta/Google/TikTok/Shopify shown
- Brain cycle runs, user lands on dashboard with data

---

## Phase 2: Brain + Dashboard (Week 2)

### 2.1 Dashboard Shell
**Effort**: 2 days | **Priority**: P0

**Frontend Tasks**:
- [ ] Global shell: top nav, user menu, optional sidebar
- [ ] Header: org name, user email, role badge
- [ ] MEMORY card: spend, revenue, blended ROAS, LTV:ROAS
- [ ] ORACLE card: risk score, risk level, # risks
- [ ] CURIOSITY card: top action, action count
- [ ] Quick actions: Analytics, Campaigns, Settings
- [ ] Persona toggle (Sarah/Jason/Emily)

**Backend Tasks**:
- [ ] `GET /api/brain/state` - latest brain_states (no recompute)
- [ ] `GET /api/brain/history` - paginated past runs (later)

**API Contracts**:
```typescript
// GET /api/brain/state?organizationId=xxx
Response: {
  timestamp, organizationId,
  memory: { totals, channels, ltvFactor },
  oracle: { globalRiskLevel, globalRiskScore, risks },
  curiosity: { topActions, totalOpportunity }
}
```

**Validation**:
- Dashboard loads with brain data
- Persona toggle changes microcopy
- No 401/500 errors in console

---

### 2.2 Analytics Section
**Effort**: 2 days | **Priority**: P1

**Frontend Tasks**:
- [ ] Overview tab: time range picker, org-level charts
- [ ] Channels tab: table with KPIs, platform filters
- [ ] Creatives tab: list/grid with fatigue indicators
- [ ] Drill-down view for single creative

**Backend Tasks**:
- [ ] `GET /api/analytics/summary` - org KPIs over date range
- [ ] `GET /api/analytics/channels` - channel list + metrics
- [ ] `GET /api/analytics/creatives` - creative list + risk tags

**API Contracts**:
```typescript
// GET /api/analytics/summary?from=2024-01-01&to=2024-01-31
Response: { spend, revenue, roas, conversions, trends }

// GET /api/analytics/channels
Response: { channels: [{ id, name, platform, spend, revenue, roas, trend }] }

// GET /api/analytics/creatives
Response: { creatives: [{ id, name, channel, spend, roas, fatigueScore }] }
```

---

## Phase 3: Storage + Uploads (Week 2-3)

### 3.1 File Upload Infrastructure
**Effort**: 1 day | **Priority**: P1

**Backend Tasks**:
- [ ] Configure Supabase Storage buckets (creatives, avatars, logos)
- [ ] `POST /api/upload/creative` - upload creative image/video
- [ ] `POST /api/upload/avatar` - user profile picture
- [ ] `POST /api/upload/logo` - org logo (admin only)
- [ ] Return signed URLs (not public URLs)
- [ ] Update DB: `creatives.metadata.file_path`, etc.

**Frontend Tasks**:
- [ ] CreativeUpload component with progress
- [ ] Avatar upload in user settings
- [ ] Logo upload in org settings (admin)

**Validation**:
```bash
# Test upload with token
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.jpg" -F "creativeId=test-123"
```
- 200 OK, file in Supabase Storage, path in DB

---

## Phase 4: Connectors + Actions (Week 3-4)

### 4.1 Platform Connectors
**Effort**: 3-4 days per platform | **Priority**: P0

**Platforms (MVP)**: Meta, Google, TikTok, Shopify

**Backend Tasks per Platform**:
- [ ] `GET /api/connectors/{platform}/auth` - start OAuth
- [ ] `GET /api/connectors/{platform}/callback` - OAuth callback
- [ ] `POST /api/connectors/{platform}/sync` - trigger sync
- [ ] `GET /api/connectors/{platform}/status` - sync status
- [ ] Store credentials in `api_credentials` (encrypted)
- [ ] Map platform data to our schema

**Frontend Tasks**:
- [ ] `/settings/integrations` - list connected platforms
- [ ] Connect/Disconnect buttons per platform
- [ ] Status badges (Connected, Needs reauth, Error)
- [ ] "Sync now" button

**Validation**:
- Click Connect → OAuth flow → callback → status = Connected
- Non-MVP platform returns 400 "MVP supports Meta/Google/TikTok/Shopify only"

---

### 4.2 Action Execution
**Effort**: 2 days | **Priority**: P1

**Backend Tasks**:
- [ ] `POST /api/actions/execute` - execute action
- [ ] Validate user/org + action type
- [ ] Call platform API (or simulate in MVP)
- [ ] Log to `action_logs` table

**Frontend Tasks**:
- [ ] Action list from Curiosity recommendations
- [ ] "Execute" button with confirmation modal
- [ ] Success/failure feedback
- [ ] Action history view

**API Contract**:
```typescript
// POST /api/actions/execute
Request: { actionType: 'pause_creative'|'adjust_budget', targetId, targetType }
Response: { success, actionId, message }
```

**Validation**:
```bash
curl -X POST http://localhost:3000/api/actions/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"actionType":"pause_creative","targetId":"creative-123","targetType":"creative"}'
```
- 200 OK, action_logs entry created

---

## Phase 5: Settings & Admin (Week 4)

### 5.1 Organization Settings
- [ ] Company name, logo, brand color
- [ ] Time zone, currency, reporting window
- [ ] Notification preferences

### 5.2 User Management
- [ ] User list (email, role)
- [ ] Invite user (admin only)
- [ ] Change role

### 5.3 Usage & Quotas
- [ ] Display current plan
- [ ] Usage vs quota (brain runs, channels, storage)
- [ ] Link to billing (later)

---

## Database Migrations Needed

```sql
-- Migration 006: Auth integration
ALTER TABLE users ADD COLUMN auth_id UUID REFERENCES auth.users(id);
CREATE INDEX idx_users_auth_id ON users(auth_id);

-- Migration 007: Action logs
CREATE TABLE action_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id),
  user_id UUID REFERENCES users(id),
  action_type TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migration 008: Org metadata
ALTER TABLE organizations ADD COLUMN metadata JSONB DEFAULT '{}';
ALTER TABLE users ADD COLUMN metadata JSONB DEFAULT '{}';
```

---

## API Route Summary

| Route | Method | Description |
|-------|--------|-------------|
| `/api/auth/signup` | POST | Create user + org |
| `/api/auth/invite` | POST | Invite team member |
| `/api/brain-cycle` | POST | Run brain cycle |
| `/api/brain/state` | GET | Get latest brain state |
| `/api/analytics/summary` | GET | Org KPIs |
| `/api/analytics/channels` | GET | Channel metrics |
| `/api/analytics/creatives` | GET | Creative metrics |
| `/api/connectors/{platform}/auth` | GET | Start OAuth |
| `/api/connectors/{platform}/callback` | GET | OAuth callback |
| `/api/connectors/{platform}/sync` | POST | Trigger sync |
| `/api/integrations` | GET | List all integrations |
| `/api/actions/execute` | POST | Execute action |
| `/api/upload/creative` | POST | Upload creative |
| `/api/upload/avatar` | POST | Upload avatar |
| `/api/upload/logo` | POST | Upload logo |
| `/api/org` | GET/PUT | Org profile |
| `/api/users` | GET | List users |
| `/api/users/invite` | POST | Send invite |

---

## Timeline Summary

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Auth + Onboarding | Login, signup, onboarding wizard |
| 2 | Dashboard + Analytics | Brain dashboard, analytics views |
| 2-3 | Storage | File uploads, Supabase Storage |
| 3-4 | Connectors | Meta, Google, TikTok, Shopify |
| 4 | Actions + Settings | Execute actions, org settings |
| 5 | Hardening | Tests, docs, polish |

---

## Immediate Next Step

**Start with Phase 1.1: Supabase Auth Integration**

Ready to begin?
