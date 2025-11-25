# Cleanup Implementation Roadmap

**Date**: January 2025  
**Status**: 📋 **READY FOR IMPLEMENTATION**  
**Purpose**: Step-by-step guide to execute Supabase and frontend cleanup

---

## 🎯 OVERVIEW

This roadmap consolidates all cleanup tasks identified in:
- `docs/FRONTEND_ARCHITECTURE_ANALYSIS.md` - Frontend structure issues
- `docs/SUPABASE_AND_FRONTEND_CLEANUP_PLAN.md` - Schema cleanup plan

---

## 📋 PHASE 1: SUPABASE SCHEMA CLEANUP (Week 1)

### **Step 1.1: Test Migration on Development**

**File**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`

**Actions:**
1. [ ] Backup development database
2. [ ] Run migration in Supabase SQL Editor (development)
3. [ ] Verify deprecated data removed
4. [ ] Verify constraints prevent deprecated platforms
5. [ ] Test inserting deprecated platform (should fail)

**Validation:**
```sql
-- Should return 0 rows
SELECT * FROM api_credentials WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify');

-- Should fail
INSERT INTO api_credentials (organization_id, platform, credentials) 
VALUES ('test-uuid', 'agentkit', '{}');
```

---

### **Step 1.2: Update Schema Documentation**

**Files to Update:**
- `omnify-brain/supabase/migrations/README.md` (create if missing)
- `docs/DATABASE_ARCHITECTURE_EXPLAINED.md`

**Actions:**
- [ ] Document MVP platforms only
- [ ] Remove references to deprecated platforms
- [ ] Add constraint documentation

---

## 📋 PHASE 2: FRONTEND CODE CLEANUP (Week 1-2)

### **Step 2.1: Archive Legacy Frontend**

**Action:**
```bash
git mv frontend _archive/frontend-legacy
git commit -m "archive: Move legacy frontend to archive"
```

**Validation:**
- [ ] `frontend/` no longer in root
- [ ] `_archive/frontend-legacy/` exists
- [ ] No broken references in codebase

---

### **Step 2.2: Review Type Definitions**

**File**: `omnify-brain/src/lib/types.ts`

**Actions:**
- [ ] Review `ChannelData.platform` type
- [ ] Ensure only MVP platforms in type union
- [ ] Remove any deprecated platform types
- [ ] Add JSDoc comments for MVP-only

**Example Fix:**
```typescript
// BEFORE (if exists):
export type Platform = 'Meta' | 'Google' | 'TikTok' | 'LinkedIn' | 'YouTube' | 'Email';

// AFTER:
export type Platform = 'Meta' | 'Google' | 'TikTok' | 'Shopify';
```

---

### **Step 2.3: Review Onboarding Component**

**File**: `omnify-brain/src/components/onboarding/ConnectPlatformsStep.tsx`

**Actions:**
- [ ] Verify only MVP platforms shown
- [ ] Remove any deprecated platform buttons/options
- [ ] Update platform icons/logos if needed
- [ ] Add tooltip explaining MVP platforms only

---

### **Step 2.4: Review Integration Clients**

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

### **Step 2.5: Review API Routes**

**Files:**
- `omnify-brain/src/app/api/connectors/meta/`
- `omnify-brain/src/app/api/connectors/google/`
- `omnify-brain/src/app/api/connectors/tiktok/`
- `omnify-brain/src/app/api/connectors/shopify/`

**Actions:**
- [x] ✅ **Already Clean** - Only MVP platforms have routes
- [ ] Add validation to reject deprecated platform requests
- [ ] Update error messages to reflect MVP-only

**Example:**
```typescript
// Add to each connector route
if (!['meta_ads', 'google_ads', 'tiktok_ads', 'shopify'].includes(platform)) {
  return NextResponse.json(
    { error: 'Invalid platform. MVP supports: Meta Ads, Google Ads, TikTok Ads, Shopify only.' },
    { status: 400 }
  );
}
```

---

### **Step 2.6: Review Data Service**

**File**: `omnify-brain/src/lib/data-service.ts`

**Actions:**
- [ ] Verify queries only reference MVP platforms
- [ ] Add type guards for platform validation
- [ ] Update error handling for invalid platforms

---

### **Step 2.7: Clarify Roles vs Personas**

**Files:**
- `omnify-brain/src/components/shared/PersonaToggle.tsx`
- `omnify-brain/src/lib/persona-context.tsx`
- `omnify-brain/src/middleware.ts`

**Actions:**
- [ ] Add tooltip to PersonaToggle explaining personas are UI views, not roles
- [ ] Update middleware comments to clarify roles vs personas
- [ ] Create `docs/ROLES_VS_PERSONAS.md` explaining distinction

---

### **Step 2.8: Consolidate Dashboard Routes**

**Files:**
- `omnify-brain/src/app/(dashboard)/`
- `omnify-brain/src/app/dashboard-v3/`

**Actions:**
- [ ] Review if `dashboard-v3` is duplicate
- [ ] Remove duplicate if exists
- [ ] Clarify `(dashboard)` route group purpose
- [ ] Ensure single dashboard per role

---

## 📋 PHASE 3: DOCUMENTATION CLEANUP (Week 2)

### **Step 3.1: Update Root README**

**File**: `README.md`

**Actions:**
- [ ] State `omnify-brain/` is the ONLY frontend
- [ ] Remove references to multiple frontends
- [ ] Update architecture diagrams
- [ ] Add MVP platforms list

---

### **Step 3.2: Update Frontend Documentation**

**Files:**
- `omnify-brain/README.md`
- `docs/FRONTEND_SPLIT_SETUP_GUIDE.md` (archive or update)

**Actions:**
- [ ] Update to reflect single frontend architecture
- [ ] Remove references to legacy frontends
- [ ] Document role-based routing
- [ ] Document persona views

---

### **Step 3.3: Create Roles vs Personas Guide**

**File**: `docs/ROLES_VS_PERSONAS.md` (new)

**Content:**
- Roles (authentication): USER, ADMIN, VENDOR
- Personas (UI views): Sarah (CMO), Jason (VP), Emily (Director)
- How they work together
- Examples

---

## 📋 PHASE 4: VALIDATION & TESTING (Week 2-3)

### **Step 4.1: Schema Validation**

**Tests:**
- [ ] Run migration on staging
- [ ] Verify no deprecated platform data
- [ ] Test constraints prevent deprecated platforms
- [ ] Verify MVP platforms work correctly

---

### **Step 4.2: Frontend Validation**

**Tests:**
- [ ] Verify only MVP platforms in UI
- [ ] Test OAuth flows for MVP platforms
- [ ] Test error handling for invalid platforms
- [ ] Verify TypeScript compilation

---

### **Step 4.3: Integration Validation**

**Tests:**
- [ ] Test data sync for MVP platforms
- [ ] Verify onboarding only shows MVP platforms
- [ ] Test action execution
- [ ] Verify brain cycle works

---

## 📊 IMPLEMENTATION CHECKLIST

### **Immediate (Today)**
- [ ] Create migration `006_remove_deprecated_platforms.sql` ✅ **DONE**
- [ ] Archive `frontend/` to `_archive/frontend-legacy`
- [ ] Update root README to state single frontend

### **This Week**
- [ ] Test migration on development database
- [ ] Review and update type definitions
- [ ] Review onboarding component
- [ ] Add platform validation to API routes
- [ ] Create `docs/ROLES_VS_PERSONAS.md`

### **Next Week**
- [ ] Run migration on staging
- [ ] Update all documentation
- [ ] Run full test suite
- [ ] Deploy to production

---

## 🎯 SUCCESS CRITERIA

1. ✅ No deprecated platform data in database
2. ✅ Constraints prevent deprecated platforms
3. ✅ Frontend only shows MVP platforms
4. ✅ TypeScript types only include MVP platforms
5. ✅ Single frontend (`omnify-brain/` only)
6. ✅ Roles vs personas clearly documented
7. ✅ All documentation updated
8. ✅ Tests pass with MVP-only configuration

---

## 📝 NOTES

### **Platform Naming Convention**

**Technical Names** (for `api_credentials`, `sync_jobs`):
- `meta_ads`
- `google_ads`
- `tiktok_ads`
- `shopify`

**Display Names** (for `channels.platform`):
- `Meta`
- `Google`
- `TikTok`
- `Shopify`

**Why Both?**
- Technical names are consistent with API integrations
- Display names are user-friendly in UI
- Constraints allow both for flexibility

---

## 🚀 NEXT STEPS

1. **Review this roadmap** with team
2. **Execute Phase 1** (Supabase migration)
3. **Execute Phase 2** (Frontend cleanup)
4. **Execute Phase 3** (Documentation)
5. **Execute Phase 4** (Validation)

---

**Status**: 📋 **READY FOR EXECUTION**  
**Priority**: **HIGH** - Maintains MVP focus and prevents confusion

