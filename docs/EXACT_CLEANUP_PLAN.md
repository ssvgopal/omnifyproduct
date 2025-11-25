# Exact Cleanup Plan - Next Steps

**Date**: January 2025  
**Status**: 📋 **READY FOR EXECUTION**  
**Last Updated**: After Supabase migration completion

---

## ✅ COMPLETED

1. ✅ **Supabase Migration Script Created**
   - `006_remove_deprecated_platforms.sql` - Ready to run
   - `006_cleanup_channels_standalone.sql` - Standalone fix script
   - `006a_fix_channels_constraint.sql` - Constraint fix script

2. ✅ **Type Definitions Fixed**
   - `omnify-brain/src/lib/types.ts` - Only MVP platforms (`Meta`, `Google`, `TikTok`, `Shopify`)

3. ✅ **Frontend Code Verified Clean**
   - `ConnectPlatformsStep.tsx` - Only MVP platforms shown
   - `SyncDataStep.tsx` - Only MVP platforms referenced
   - API routes - Only MVP platforms have connectors
   - No deprecated platform references found in `omnify-brain/src/`

---

## 🎯 EXACT PLAN - NEXT STEPS

### **PHASE 1: Archive Legacy Frontend** (Priority: HIGH)

#### **Step 1.1: Archive `frontend/` Directory**

**Action:**
```bash
# Move frontend to archive
git mv frontend _archive/frontend-legacy
```

**Files to Move:**
- `frontend/` → `_archive/frontend-legacy/`

**Validation:**
- [ ] `frontend/` no longer exists in root
- [ ] `_archive/frontend-legacy/` exists
- [ ] No broken imports/references in codebase

**Why:**
- `frontend/` contains React 19 (CRA) with AgentKit/GoHighLevel references
- Not aligned with MVP (Next.js 15, Supabase, MVP platforms only)
- Already archived: `frontend-admin/`, `frontend-user/`

---

### **PHASE 2: Add Platform Validation** (Priority: MEDIUM)

#### **Step 2.1: Add Validation to API Routes**

**Files to Update:**
1. `omnify-brain/src/app/api/connectors/meta/auth/route.ts`
2. `omnify-brain/src/app/api/connectors/google/auth/route.ts`
3. `omnify-brain/src/app/api/connectors/tiktok/auth/route.ts`
4. `omnify-brain/src/app/api/connectors/shopify/auth/route.ts`
5. `omnify-brain/src/app/api/connectors/*/sync/route.ts` (all sync routes)
6. `omnify-brain/src/app/api/actions/execute/route.ts`

**Action:**
Add platform validation at the start of each route handler:

```typescript
const MVP_PLATFORMS = ['meta_ads', 'google_ads', 'tiktok_ads', 'shopify'];
const MVP_PLATFORMS_DISPLAY = ['Meta', 'Google', 'TikTok', 'Shopify'];

// Validate platform
if (!MVP_PLATFORMS.includes(platform) && !MVP_PLATFORMS_DISPLAY.includes(platform)) {
  return NextResponse.json(
    { error: 'Invalid platform. MVP supports: Meta Ads, Google Ads, TikTok Ads, Shopify only.' },
    { status: 400 }
  );
}
```

**Why:**
- Prevents deprecated platform requests from being processed
- Clear error messages for users
- Defense in depth (even though frontend only shows MVP)

---

#### **Step 2.2: Add Validation to Data Service**

**File:** `omnify-brain/src/lib/data-service.ts`

**Action:**
Add platform type guard function:

```typescript
const MVP_PLATFORMS = ['Meta', 'Google', 'TikTok', 'Shopify'] as const;
type MVPPlatform = typeof MVP_PLATFORMS[number];

export function isValidMVPPlatform(platform: string): platform is MVPPlatform {
  return MVP_PLATFORMS.includes(platform as MVPPlatform);
}
```

Use in queries to filter out any invalid platforms.

---

### **PHASE 3: Documentation Updates** (Priority: MEDIUM)

#### **Step 3.1: Update Root README**

**File:** `README.md`

**Actions:**
- [ ] State `omnify-brain/` is the ONLY active frontend
- [ ] Remove references to `frontend/`, `frontend-admin/`, `frontend-user/`
- [ ] Add MVP platforms list
- [ ] Update architecture diagram if exists

**Example Update:**
```markdown
## Frontend

**Active Frontend:**
- `omnify-brain/` - Next.js 15, Supabase, NextAuth.js
  - Port: 3000 (production)
  - Port: 3001 (demo)

**Archived Frontends:**
- `_archive/frontend-legacy/` - Legacy React 19 (CRA)
- `_archive/frontend-admin/` - Legacy admin panel
- `_archive/frontend-user/` - Legacy user panel

## MVP Platforms

- Meta Ads
- Google Ads
- TikTok Ads
- Shopify
```

---

#### **Step 3.2: Update omnify-brain README**

**File:** `omnify-brain/README.md`

**Actions:**
- [ ] Verify it states MVP platforms only
- [ ] Remove any references to deprecated platforms
- [ ] Add note about platform constraints in database

---

#### **Step 3.3: Create Roles vs Personas Guide**

**File:** `docs/ROLES_VS_PERSONAS.md` (new)

**Content:**
```markdown
# Roles vs Personas - Clarification

## Roles (Authentication & Authorization)

- **USER** - End user/team member (can view dashboard)
- **ADMIN** - Organization admin (can manage team, integrations, billing)
- **VENDOR** - Super admin/Omnify team (can access all organizations)

## Personas (UI Views - FACE Module)

- **Sarah (CMO)** - Strategic view, explains to CEO/board
- **Jason (VP Growth)** - Revenue-focused, growth targets
- **Emily (Director)** - Daily campaign execution

## Key Distinction

- **Roles** = Who you are (authentication/authorization)
- **Personas** = How you view data (UI customization)

## Implementation

- Roles are enforced in `middleware.ts` (route protection)
- Personas are selected in `PersonaToggle.tsx` (UI view)
- A USER can switch between personas (Sarah/Jason/Emily)
- An ADMIN can switch between personas
- A VENDOR can switch between personas
```

---

### **PHASE 4: Verify & Test** (Priority: LOW)

#### **Step 4.1: Verify No Broken References**

**Action:**
Search codebase for references to `frontend/`:

```bash
# Search for imports/references to frontend/
grep -r "frontend/" --exclude-dir=node_modules --exclude-dir=_archive
```

**Expected:** No results (or only in documentation)

---

#### **Step 4.2: TypeScript Compilation Check**

**Action:**
```bash
cd omnify-brain
npm run build
```

**Expected:** No errors related to deprecated platforms

---

#### **Step 4.3: Test Onboarding Flow**

**Action:**
1. Start dev server: `npm run dev`
2. Navigate to `/onboarding`
3. Verify only MVP platforms shown
4. Test connecting a platform
5. Verify no errors

---

## 📊 IMPLEMENTATION ORDER

### **Immediate (Today)**
1. ✅ Archive `frontend/` directory
2. ⏳ Add platform validation to API routes
3. ⏳ Update root README

### **This Week**
4. ⏳ Add validation to data service
5. ⏳ Create roles vs personas guide
6. ⏳ Update omnify-brain README

### **Next Week**
7. ⏳ Verify no broken references
8. ⏳ Run TypeScript compilation check
9. ⏳ Test onboarding flow

---

## ✅ SUCCESS CRITERIA

1. ✅ `frontend/` archived to `_archive/frontend-legacy/`
2. ✅ All API routes validate MVP platforms only
3. ✅ Data service has platform validation
4. ✅ Root README states single frontend
5. ✅ Roles vs personas clearly documented
6. ✅ TypeScript compiles without errors
7. ✅ Onboarding only shows MVP platforms
8. ✅ No broken references in codebase

---

## 📝 NOTES

### **Why Archive Instead of Delete?**
- Preserves history for reference
- Can be restored if needed
- Clear separation from active code

### **Platform Naming Convention**
- **Technical Names** (API routes, database): `meta_ads`, `google_ads`, `tiktok_ads`, `shopify`
- **Display Names** (UI, types): `Meta`, `Google`, `TikTok`, `Shopify`

### **Risk Assessment**
- **Archive frontend/**: LOW - No active references found
- **Add validation**: LOW - Only adds safety checks
- **Update docs**: LOW - No code changes

---

**Status**: 📋 **READY FOR EXECUTION**  
**Priority**: **HIGH** - Maintains MVP focus and prevents confusion

