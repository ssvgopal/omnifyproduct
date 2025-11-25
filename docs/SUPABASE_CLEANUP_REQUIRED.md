# Supabase Tables Cleanup Required

**Date**: January 2025  
**Status**: 🔴 **ACTION REQUIRED**  
**Purpose**: Clear summary of Supabase schema cleanup needed

---

## 🎯 EXECUTIVE SUMMARY

Three Supabase tables need cleanup to remove deprecated platform data and add constraints to prevent future deprecated platforms:

1. **`api_credentials`** - Stores OAuth tokens for platforms
2. **`sync_jobs`** - Tracks data synchronization jobs
3. **`channels`** - Stores marketing channel/platform information

**Additional cleanup:**
4. **`cohorts`** - May have deprecated acquisition channels

---

## 📊 DETAILED CLEANUP REQUIREMENTS

### **1. api_credentials Table**

**Current State:**
- Stores OAuth credentials for all platforms
- No constraint limiting to MVP platforms
- May contain deprecated platform data

**Cleanup Required:**

#### **Step 1.1: Remove Deprecated Data**
```sql
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
  'youtube_ads',
  'LinkedIn',
  'YouTube',
  'AgentKit',
  'GoHighLevel',
  'TripleWhale',
  'HubSpot',
  'Klaviyo',
  'Stripe'
);
```

#### **Step 1.2: Add Constraint**
```sql
ALTER TABLE api_credentials
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE api_credentials
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
```

**Impact:**
- Removes any deprecated platform credentials
- Prevents future deprecated platforms from being added
- Ensures only MVP platforms can store credentials

---

### **2. sync_jobs Table**

**Current State:**
- Tracks data sync jobs for all platforms
- No constraint limiting to MVP platforms
- May contain historical sync jobs for deprecated platforms

**Cleanup Required:**

#### **Step 2.1: Remove Deprecated Data**
```sql
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
  'youtube_ads',
  'LinkedIn',
  'YouTube',
  'AgentKit',
  'GoHighLevel',
  'TripleWhale',
  'HubSpot',
  'Klaviyo',
  'Stripe'
);
```

#### **Step 2.2: Add Constraint**
```sql
ALTER TABLE sync_jobs
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE sync_jobs
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
```

**Impact:**
- Removes historical sync jobs for deprecated platforms
- Prevents future deprecated platform sync jobs
- Ensures only MVP platforms can create sync jobs

---

### **3. channels Table**

**Current State:**
- Stores marketing channels/platforms
- May allow deprecated platforms in `platform` column
- No constraint limiting to MVP platforms

**Cleanup Required:**

#### **Step 3.1: Remove Deprecated Data**
```sql
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
  'linkedin_ads',
  'youtube_ads',
  'LinkedIn',
  'YouTube',
  'AgentKit',
  'GoHighLevel',
  'TripleWhale',
  'HubSpot',
  'Klaviyo',
  'Stripe',
  'Email'  -- Email is not an ad platform, remove if not needed
);
```

#### **Step 3.2: Add Constraint**
```sql
ALTER TABLE channels
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify'));
```

**Note:** We allow both technical names (`meta_ads`) and display names (`Meta`) because:
- `channels.platform` may use display names in UI
- `api_credentials.platform` uses technical names
- This provides flexibility while maintaining MVP focus

**Impact:**
- Removes deprecated platform channels
- Prevents future deprecated platform channels
- Ensures only MVP platforms can be created

---

### **4. cohorts Table (Optional)**

**Current State:**
- Has `acquisition_channel` column
- May reference deprecated platforms
- No constraint limiting to MVP platforms

**Cleanup Required:**

#### **Step 4.1: Update Deprecated References**
```sql
UPDATE cohorts
SET acquisition_channel = 'All'
WHERE acquisition_channel IN (
  'agentkit', 'gohighlevel', 'triplewhale', 'hubspot', 
  'klaviyo', 'stripe', 'linkedin', 'youtube'
);
```

#### **Step 4.2: Add Constraint (Optional)**
```sql
ALTER TABLE cohorts
DROP CONSTRAINT IF EXISTS valid_acquisition_channel;

ALTER TABLE cohorts
ADD CONSTRAINT valid_acquisition_channel 
CHECK (
  acquisition_channel IS NULL OR 
  acquisition_channel IN ('Meta', 'Google', 'TikTok', 'Shopify', 'Organic', 'All')
);
```

**Impact:**
- Updates deprecated channel references to 'All'
- Prevents future deprecated channel references
- Maintains data integrity

---

## 🔧 COMPLETE MIGRATION SCRIPT

**File**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`

**Status**: ✅ **CREATED AND READY**

The migration script includes:
1. ✅ Delete deprecated data from `api_credentials`
2. ✅ Delete deprecated data from `sync_jobs`
3. ✅ Delete deprecated data from `channels`
4. ✅ Add constraints to all three tables
5. ✅ Update `cohorts` acquisition_channel
6. ✅ Add constraint to `cohorts` (optional)
7. ✅ Add documentation comments

---

## 📋 EXECUTION STEPS

### **Step 1: Backup Database**
```sql
-- In Supabase Dashboard, create a backup before running migration
```

### **Step 2: Test on Development**
```sql
-- Run migration in Supabase SQL Editor (development environment)
-- File: omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql
```

### **Step 3: Verify Results**
```sql
-- Should return 0 rows
SELECT * FROM api_credentials WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify');
SELECT * FROM sync_jobs WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify');
SELECT * FROM channels WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');

-- Should fail (constraint violation)
INSERT INTO api_credentials (organization_id, platform, credentials) 
VALUES ('test-uuid', 'agentkit', '{}');
```

### **Step 4: Run on Staging**
- After successful development test
- Run same migration on staging

### **Step 5: Run on Production**
- After successful staging test
- Run same migration on production

---

## 🎯 MVP PLATFORMS ALLOWED

### **Technical Names** (for `api_credentials`, `sync_jobs`):
- `meta_ads`
- `google_ads`
- `tiktok_ads`
- `shopify`

### **Display Names** (for `channels.platform`):
- `Meta`
- `Google`
- `TikTok`
- `Shopify`

### **Acquisition Channels** (for `cohorts.acquisition_channel`):
- `Meta`
- `Google`
- `TikTok`
- `Shopify`
- `Organic`
- `All`

---

## 📊 EXPECTED IMPACT

### **Data Deletion**
| Table | Estimated Rows Affected | Risk |
|-------|------------------------|------|
| `api_credentials` | 0-10 | LOW (MVP is new) |
| `sync_jobs` | 0-50 | LOW (historical data) |
| `channels` | 0-20 | LOW (test data) |
| `cohorts` | 0-10 | LOW (updates, not deletes) |

**Total Risk**: **LOW** - MVP is new, minimal production data

### **Constraint Addition**
- **No Breaking Changes**: Constraints only prevent new deprecated platforms
- **Existing MVP Data**: Unaffected
- **Future Protection**: Prevents accidental deprecated platform additions

---

## ✅ VALIDATION CHECKLIST

After running migration:

- [ ] No deprecated platform data in `api_credentials`
- [ ] No deprecated platform data in `sync_jobs`
- [ ] No deprecated platform data in `channels`
- [ ] Constraints prevent deprecated platforms
- [ ] MVP platforms still work correctly
- [ ] Can insert MVP platforms
- [ ] Cannot insert deprecated platforms (constraint violation)

---

## 🚨 IMPORTANT NOTES

### **Before Running Migration:**
1. ✅ **Backup database** (Supabase Dashboard)
2. ✅ **Test on development** first
3. ✅ **Verify no production data** will be affected
4. ✅ **Check for any dependencies** on deprecated platforms

### **After Running Migration:**
1. ✅ **Verify constraints work** (try inserting deprecated platform)
2. ✅ **Test MVP platforms** still work
3. ✅ **Update frontend** if needed (already mostly clean)
4. ✅ **Document changes** in migration comments

---

## 📝 SUMMARY

**Tables Requiring Cleanup:**
1. ✅ `api_credentials` - Remove deprecated, add constraint
2. ✅ `sync_jobs` - Remove deprecated, add constraint
3. ✅ `channels` - Remove deprecated, add constraint
4. ⚠️ `cohorts` - Update deprecated references (optional)

**Migration Script:**
- ✅ **Created**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`
- ✅ **Ready**: Can be run in Supabase SQL Editor
- ✅ **Safe**: Only removes deprecated data, adds constraints

**Next Steps:**
1. Review migration script
2. Test on development database
3. Run on staging
4. Run on production

---

**Status**: ✅ **MIGRATION SCRIPT READY**  
**Risk**: **LOW** - Only removes deprecated data, adds constraints  
**Priority**: **HIGH** - Maintains MVP focus

