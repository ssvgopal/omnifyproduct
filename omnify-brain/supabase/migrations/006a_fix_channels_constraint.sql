-- ============================================
-- Migration 006a: Fix Channels Constraint (If 006 Failed)
-- ============================================
-- Purpose: Fix channels table if constraint addition failed due to existing invalid data
-- Run this if migration 006 failed with constraint violation error

-- ============================================
-- Step 1: Check what invalid platform values exist
-- ============================================
-- First, let's see what platform values are in the table
DO $$
DECLARE
  invalid_platforms TEXT[];
BEGIN
  SELECT ARRAY_AGG(DISTINCT platform) INTO invalid_platforms
  FROM channels
  WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');
  
  IF invalid_platforms IS NOT NULL AND array_length(invalid_platforms, 1) > 0 THEN
    RAISE NOTICE 'Found invalid platform values: %', array_to_string(invalid_platforms, ', ');
    RAISE NOTICE 'These will be deleted or you can update them manually';
  ELSE
    RAISE NOTICE 'No invalid platform values found';
  END IF;
END $$;

-- ============================================
-- Step 2: Delete all non-MVP channels
-- ============================================
-- Delete channels that are NOT MVP platforms
DELETE FROM channels 
WHERE platform NOT IN (
  'meta_ads', 'google_ads', 'tiktok_ads', 'shopify',  -- Technical names
  'Meta', 'Google', 'TikTok', 'Shopify'              -- Display names
);

-- ============================================
-- Step 3: Verify all channels are now valid
-- ============================================
DO $$
DECLARE
  invalid_count INT;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM channels
  WHERE platform NOT IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify');
  
  IF invalid_count > 0 THEN
    RAISE EXCEPTION 'Still have % invalid platform values. Please review and fix manually.', invalid_count;
  ELSE
    RAISE NOTICE 'All channels now have valid MVP platform values';
  END IF;
END $$;

-- ============================================
-- Step 4: Add constraint (should work now)
-- ============================================
ALTER TABLE channels
DROP CONSTRAINT IF EXISTS valid_mvp_platform;

ALTER TABLE channels
ADD CONSTRAINT valid_mvp_platform 
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify'));

COMMENT ON CONSTRAINT valid_mvp_platform ON channels IS 
  'MVP platforms only: Meta, Google, TikTok, Shopify (display names) or meta_ads, google_ads, tiktok_ads, shopify (technical names)';

RAISE NOTICE 'Migration 006a Complete: Channels constraint added successfully';

