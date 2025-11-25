-- ============================================
-- Standalone Script: Clean Channels Table
-- ============================================
-- Purpose: Remove all non-MVP platform channels and add constraint
-- Run this in Supabase SQL Editor if migration 006 has issues
-- This is a simplified, standalone version

-- Step 1: Delete all channels that are NOT MVP platforms
DELETE FROM channels 
WHERE platform NOT IN (
  'meta_ads', 
  'google_ads', 
  'tiktok_ads', 
  'shopify',
  'Meta', 
  'Google', 
  'TikTok', 
  'Shopify'
);

-- Step 2: Also delete any deprecated platforms (case-insensitive check)
DELETE FROM channels 
WHERE LOWER(platform) IN (
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
  'email'
);

-- Step 3: Verify all channels are now valid (optional check)
-- This will show you if there are any remaining invalid values
SELECT DISTINCT platform 
FROM channels 
WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');

-- Step 4: Drop existing constraint if it exists
ALTER TABLE channels
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

-- Step 5: Add the constraint
ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify'));

-- Done! The constraint is now added.

