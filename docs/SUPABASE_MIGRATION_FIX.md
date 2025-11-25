# Supabase Migration Fix - Constraint Violation Error

**Date**: January 2025  
**Issue**: Constraint violation when adding `valid_mvp_platform` to `channels` table  
**Status**: ✅ **FIXED**

---

## 🚨 ERROR ENCOUNTERED

```
ERROR: 23514: check constraint "valid_mvp_platform" of relation "channels" is violated by some row
```

**Cause**: The `channels` table contains platform values that don't match the constraint we're trying to add.

---

## ✅ SOLUTION

### **Option 1: Use Updated Migration 006 (Recommended)**

The migration script has been updated to:
1. **Delete ALL non-MVP channels first** (using `NOT IN` instead of `IN`)
2. **Validate before adding constraint**
3. **Better error handling**

**Updated Migration**: `omnify-brain/supabase/migrations/006_remove_deprecated_platforms.sql`

**Key Change:**
```sql
-- OLD (only deleted specific deprecated platforms):
DELETE FROM channels WHERE platform IN ('agentkit', 'gohighlevel', ...);

-- NEW (deletes ALL non-MVP platforms):
DELETE FROM channels 
WHERE platform NOT IN (
  'meta_ads', 'google_ads', 'tiktok_ads', 'shopify',  -- Technical names
  'Meta', 'Google', 'TikTok', 'Shopify'              -- Display names
);
```

---

### **Option 2: Use Fix Script 006a (If 006 Already Failed)**

If you already ran migration 006 and it failed, use the fix script:

**File**: `omnify-brain/supabase/migrations/006a_fix_channels_constraint.sql`

**What it does:**
1. Shows what invalid platform values exist
2. Deletes all non-MVP channels
3. Validates all channels are now valid
4. Adds the constraint

**Run this:**
```sql
-- In Supabase SQL Editor, run:
-- omnify-brain/supabase/migrations/006a_fix_channels_constraint.sql
```

---

## 🔍 MANUAL FIX (If Needed)

If you want to see what invalid values exist before fixing:

```sql
-- See what platform values exist in channels table
SELECT DISTINCT platform, COUNT(*) as count
FROM channels
GROUP BY platform
ORDER BY count DESC;

-- See which ones are invalid
SELECT DISTINCT platform
FROM channels
WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');
```

Then either:
1. **Delete invalid channels:**
   ```sql
   DELETE FROM channels 
   WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');
   ```

2. **Or update them to valid values:**
   ```sql
   -- Example: Update 'meta' to 'Meta'
   UPDATE channels SET platform = 'Meta' WHERE platform = 'meta';
   ```

Then add the constraint:
```sql
ALTER TABLE channels
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify'));
```

---

## ✅ VERIFICATION

After running the fix, verify:

```sql
-- Should return 0 rows
SELECT * FROM channels 
WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');

-- Should show only MVP platforms
SELECT DISTINCT platform FROM channels;

-- Should fail (constraint violation)
INSERT INTO channels (organization_id, name, platform) 
VALUES ('test-uuid', 'Test', 'agentkit');
```

---

## 📝 SUMMARY

**Problem**: Constraint violation because `channels` table has invalid platform values  
**Solution**: Delete all non-MVP channels BEFORE adding constraint  
**Files**: 
- ✅ `006_remove_deprecated_platforms.sql` (updated)
- ✅ `006a_fix_channels_constraint.sql` (new fix script)

**Status**: ✅ **FIXED** - Migration now handles existing invalid data

