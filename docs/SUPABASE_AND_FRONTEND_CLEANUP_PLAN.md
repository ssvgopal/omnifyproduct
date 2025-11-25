# Supabase Schema & Frontend Cleanup Plan

**Date**: January 2025  
**Status**: 🔴 **ACTION REQUIRED**  
**Purpose**: Remove deprecated schema elements and frontend code related to Phase 1-3 deprecation

---

## 🚨 EXECUTIVE SUMMARY

After reviewing the Supabase schema and frontend code, I've identified **deprecated tables, columns, and frontend references** that need to be cleaned up:

### **Deprecated Elements Found:**
1. **Schema Elements**: Tables/columns related to AgentKit, GoHighLevel, MongoDB patterns
2. **Frontend References**: Code referencing deprecated platforms
3. **Unused Tables**: Tables created but never used
4. **Legacy Patterns**: MongoDB-style schema patterns in Supabase

---

## 📊 CURRENT SUPABASE SCHEMA ANALYSIS

### **Tables in Current Schema**

| Table Name | Purpose | Status | Action |
|------------|---------|--------|--------|
| `organizations` | Multi-tenancy | ✅ **KEEP** | Core MVP table |
| `users` | User accounts | ✅ **KEEP** | Core MVP table |
| `channels` | Ad platforms (Meta, Google, TikTok) | ✅ **KEEP** | MVP required |
| `campaigns` | Campaign data | ✅ **KEEP** | MVP required (per Requirements V3) |
| `creatives` | Creative assets | ✅ **KEEP** | MVP required |
| `daily_metrics` | Performance metrics | ✅ **KEEP** | MVP required |
| `cohorts` | LTV cohort data | ✅ **KEEP** | MVP required (per Requirements V3) |
| `brain_states` | Brain module outputs | ✅ **KEEP** | MVP required |
| `api_credentials` | Platform OAuth tokens | ⚠️ **REVIEW** | May need cleanup |
| `sync_jobs` | Data sync tracking | ⚠️ **REVIEW** | May need cleanup |
| `action_logs` | Action execution logs | ✅ **KEEP** | MVP required |
| `vendor_users` | Vendor-specific settings | ✅ **KEEP** | Multi-panel architecture |
| `organization_quotas` | Usage quotas | ✅ **KEEP** | Multi-panel architecture |
| `audit_logs` | Audit trail | ✅ **KEEP** | Security requirement |

---

## 🔴 DEPRECATED SCHEMA ELEMENTS

### **1. api_credentials Table - Needs Review**

**Current Schema:**
```sql
CREATE TABLE api_credentials (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  platform VARCHAR(50),  -- May include deprecated platforms
  credentials JSONB,
  ...
);
```

**Issues:**
- May store credentials for deprecated platforms (AgentKit, GoHighLevel, TripleWhale, HubSpot, Klaviyo)
- No constraint limiting to MVP platforms only

**Required Action:**
- Add CHECK constraint to limit `platform` to MVP platforms only
- Migration to remove deprecated platform credentials
- Update frontend to only show MVP platforms

**Migration:**
```sql
-- Remove deprecated platform credentials
DELETE FROM api_credentials 
WHERE platform IN ('agentkit', 'gohighlevel', 'triplewhale', 'hubspot', 'klaviyo', 'stripe', 'linkedin', 'youtube');

-- Add constraint for MVP platforms only
ALTER TABLE api_credentials
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
```

---

### **2. sync_jobs Table - Needs Review**

**Current Schema:**
```sql
CREATE TABLE sync_jobs (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  platform VARCHAR(50),  -- May include deprecated platforms
  status VARCHAR(20),
  ...
);
```

**Issues:**
- May reference deprecated platforms
- No constraint limiting to MVP platforms

**Required Action:**
- Add CHECK constraint for MVP platforms only
- Clean up old sync jobs for deprecated platforms

**Migration:**
```sql
-- Remove deprecated platform sync jobs
DELETE FROM sync_jobs 
WHERE platform IN ('agentkit', 'gohighlevel', 'triplewhale', 'hubspot', 'klaviyo', 'stripe', 'linkedin', 'youtube');

-- Add constraint
ALTER TABLE sync_jobs
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
```

---

### **3. channels Table - Needs Review**

**Current Schema:**
```sql
CREATE TABLE channels (
  id UUID PRIMARY KEY,
  organization_id UUID REFERENCES organizations(id),
  name VARCHAR(255),
  platform VARCHAR(50),  -- May include deprecated platforms
  ...
);
```

**Issues:**
- May have channels for deprecated platforms
- No constraint limiting to MVP platforms

**Required Action:**
- Add CHECK constraint for MVP platforms only
- Clean up deprecated platform channels

**Migration:**
```sql
-- Remove deprecated platform channels
DELETE FROM channels 
WHERE platform IN ('agentkit', 'gohighlevel', 'triplewhale', 'hubspot', 'klaviyo', 'stripe', 'linkedin', 'youtube');

-- Add constraint
ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
```

---

## 🔍 FRONTEND CODE ANALYSIS

### **Deprecated References Found**

#### **1. Platform References**

**Files to Review:**
- `omnify-brain/src/lib/integrations/` - Integration clients
- `omnify-brain/src/app/api/connectors/` - OAuth routes
- `omnify-brain/src/components/onboarding/ConnectPlatformsStep.tsx` - Platform selection

**Required Actions:**
- ✅ **Already Clean**: Only Meta, Google, TikTok, Shopify connectors exist
- ⚠️ **Verify**: No references to deprecated platforms in UI

#### **2. Type Definitions**

**Files to Review:**
- `omnify-brain/src/lib/types.ts` - TypeScript interfaces

**Required Actions:**
- Remove deprecated platform types if any
- Ensure only MVP platforms in type definitions

#### **3. API Routes**

**Files to Review:**
- `omnify-brain/src/app/api/connectors/*` - OAuth and sync routes

**Current State:**
- ✅ Only MVP platforms have routes (meta, google, tiktok, shopify)
- ✅ No AgentKit/GoHighLevel routes

---

## 📋 CLEANUP PLAN

### **Phase 1: Schema Cleanup (Immediate)**

#### **Step 1.1: Create Cleanup Migration**

**File**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`

```sql
-- ============================================
-- Migration 006: Remove Deprecated Platforms
-- ============================================
-- Purpose: Remove all data and constraints related to Phase 1-3 deprecated platforms
-- Deprecated Platforms: AgentKit, GoHighLevel, TripleWhale, HubSpot, Klaviyo, Stripe, LinkedIn, YouTube

-- ============================================
-- 1. Remove deprecated platform credentials
-- ============================================
DELETE FROM api_credentials 
WHERE platform IN (
  'agentkit', 
  'gohighlevel', 
  'triplewhale', 
  'hubspot', 
  'klaviyo', 
  'stripe', 
  'linkedin', 
  'youtube',
  'linkedin_ads',
  'youtube_ads'
);

-- ============================================
-- 2. Remove deprecated platform sync jobs
-- ============================================
DELETE FROM sync_jobs 
WHERE platform IN (
  'agentkit', 
  'gohighlevel', 
  'triplewhale', 
  'hubspot', 
  'klaviyo', 
  'stripe', 
  'linkedin', 
  'youtube',
  'linkedin_ads',
  'youtube_ads'
);

-- ============================================
-- 3. Remove deprecated platform channels
-- ============================================
DELETE FROM channels 
WHERE platform IN (
  'agentkit', 
  'gohighlevel', 
  'triplewhale', 
  'hubspot', 
  'klaviyo', 
  'stripe', 
  'linkedin', 
  'youtube',
  'LinkedIn',
  'YouTube'
);

-- ============================================
-- 4. Add constraints to prevent future deprecated platforms
-- ============================================

-- api_credentials platform constraint
ALTER TABLE api_credentials
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE api_credentials
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));

-- sync_jobs platform constraint
ALTER TABLE sync_jobs
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE sync_jobs
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));

-- channels platform constraint
ALTER TABLE channels
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));

-- ============================================
-- 5. Add comments for documentation
-- ============================================
COMMENT ON CONSTRAINT valid_mvp_platform ON api_credentials IS 
  'MVP platforms only: meta_ads, google_ads, tiktok_ads, shopify';

COMMENT ON CONSTRAINT valid_mvp_platform ON sync_jobs IS 
  'MVP platforms only: meta_ads, google_ads, tiktok_ads, shopify';

COMMENT ON CONSTRAINT valid_mvp_platform ON channels IS 
  'MVP platforms only: meta_ads, google_ads, tiktok_ads, shopify';
```

---

### **Phase 2: Frontend Cleanup (This Week)**

#### **Step 2.1: Review Type Definitions**

**File**: `omnify-brain/src/lib/types.ts`

**Actions:**
- [ ] Remove any deprecated platform types
- [ ] Ensure `ChannelData.platform` only includes MVP platforms
- [ ] Update type comments to reflect MVP-only

**Example:**
```typescript
// BEFORE (if exists):
export type Platform = 'Meta' | 'Google' | 'TikTok' | 'LinkedIn' | 'YouTube' | 'AgentKit' | 'GoHighLevel';

// AFTER:
export type Platform = 'Meta' | 'Google' | 'TikTok' | 'Shopify';
```

---

#### **Step 2.2: Review Integration Clients**

**Files:**
- `omnify-brain/src/lib/integrations/meta-ads.ts`
- `omnify-brain/src/lib/integrations/google-ads.ts`
- `omnify-brain/src/lib/integrations/tiktok-ads.ts`
- `omnify-brain/src/lib/integrations/shopify.ts`

**Actions:**
- [x] ✅ **Already Clean** - Only MVP platforms exist
- [ ] Verify no references to deprecated platforms in comments
- [ ] Update README/docs to reflect MVP-only

---

#### **Step 2.3: Review Onboarding Component**

**File**: `omnify-brain/src/components/onboarding/ConnectPlatformsStep.tsx`

**Actions:**
- [ ] Verify only MVP platforms shown in UI
- [ ] Remove any references to deprecated platforms
- [ ] Update platform icons/logos if needed

---

#### **Step 2.4: Review API Routes**

**Files:**
- `omnify-brain/src/app/api/connectors/meta/`
- `omnify-brain/src/app/api/connectors/google/`
- `omnify-brain/src/app/api/connectors/tiktok/`
- `omnify-brain/src/app/api/connectors/shopify/`

**Actions:**
- [x] ✅ **Already Clean** - Only MVP platforms have routes
- [ ] Add validation to reject deprecated platform requests
- [ ] Update error messages to reflect MVP-only

---

#### **Step 2.5: Review Data Service**

**File**: `omnify-brain/src/lib/data-service.ts`

**Actions:**
- [ ] Verify queries only reference MVP platforms
- [ ] Add type guards for platform validation
- [ ] Update error handling for invalid platforms

---

### **Phase 3: Documentation Cleanup (Next Sprint)**

#### **Step 3.1: Update Schema Documentation**

**Actions:**
- [ ] Document MVP platforms in schema comments
- [ ] Update migration README
- [ ] Create platform reference guide

#### **Step 3.2: Update Frontend Documentation**

**Actions:**
- [ ] Update `omnify-brain/README.md` to state MVP platforms only
- [ ] Remove references to deprecated platforms
- [ ] Update architecture diagrams

---

## 🎯 VALIDATION CHECKLIST

### **Schema Validation**

- [ ] Run migration `006_remove_deprecated_platforms.sql`
- [ ] Verify no deprecated platform data remains
- [ ] Verify constraints prevent deprecated platforms
- [ ] Test inserting deprecated platform (should fail)

### **Frontend Validation**

- [ ] Verify only MVP platforms in UI
- [ ] Test OAuth flows for MVP platforms only
- [ ] Verify error handling for invalid platforms
- [ ] Test type safety (TypeScript compilation)

### **Integration Validation**

- [ ] Verify API routes only handle MVP platforms
- [ ] Test data sync for MVP platforms only
- [ ] Verify onboarding only shows MVP platforms

---

## 📊 IMPACT ANALYSIS

### **Data Impact**

| Table | Rows Affected (Estimate) | Action |
|-------|-------------------------|--------|
| `api_credentials` | 0-10 (if any test data) | DELETE deprecated |
| `sync_jobs` | 0-50 (historical) | DELETE deprecated |
| `channels` | 0-20 (if any test data) | DELETE deprecated |

**Risk**: **LOW** - MVP is new, likely minimal test data

### **Code Impact**

| Component | Files Affected | Risk |
|-----------|----------------|------|
| Type Definitions | 1-2 files | LOW |
| Integration Clients | 0 files (already clean) | NONE |
| API Routes | 0 files (already clean) | NONE |
| UI Components | 1-2 files | LOW |

**Risk**: **LOW** - Most code already clean

---

## 🚀 IMPLEMENTATION ORDER

### **Week 1: Schema Cleanup**
1. Create migration `006_remove_deprecated_platforms.sql`
2. Test migration on development database
3. Run migration on staging
4. Verify constraints work
5. Document changes

### **Week 2: Frontend Cleanup**
1. Review and update type definitions
2. Review and update onboarding component
3. Add platform validation
4. Test all MVP platform flows
5. Update documentation

### **Week 3: Validation & Testing**
1. Run full test suite
2. Verify no deprecated platform references
3. Test error handling
4. Update all documentation
5. Deploy to production

---

## 📝 MIGRATION SCRIPT

**File**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`

See Phase 1, Step 1.1 above for full migration script.

---

## ✅ SUCCESS CRITERIA

1. ✅ No deprecated platform data in database
2. ✅ Constraints prevent deprecated platforms
3. ✅ Frontend only shows MVP platforms
4. ✅ TypeScript types only include MVP platforms
5. ✅ All documentation updated
6. ✅ Tests pass with MVP-only configuration

---

## 🎯 NEXT STEPS

1. **Review this plan** with team
2. **Create migration script** (Phase 1)
3. **Test on development** database
4. **Update frontend code** (Phase 2)
5. **Run validation** (Phase 3)
6. **Deploy to production**

---

**Status**: 🔴 **READY FOR IMPLEMENTATION**  
**Priority**: **HIGH** - Prevents confusion and maintains MVP focus

