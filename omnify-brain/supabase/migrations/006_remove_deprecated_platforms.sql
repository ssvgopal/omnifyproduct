-- ============================================
-- Migration 006: Remove Deprecated Platforms
-- ============================================
-- Purpose: Remove all data and constraints related to Phase 1-3 deprecated platforms
-- Deprecated Platforms: AgentKit, GoHighLevel, TripleWhale, HubSpot, Klaviyo, Stripe, LinkedIn, YouTube
-- MVP Platforms Only: meta_ads, google_ads, tiktok_ads, shopify

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
CHECK (platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify', 'Meta', 'Google', 'TikTok', 'Shopify'));

-- Note: We allow both lowercase with _ads suffix and capitalized names for channels
-- This is because channels.platform may use display names (Meta, Google, TikTok, Shopify)
-- while api_credentials and sync_jobs use technical names (meta_ads, google_ads, etc.)

-- ============================================
-- 5. Update action_logs platform constraint (if exists)
-- ============================================
-- action_logs may have platform column, add constraint if it exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'action_logs' AND column_name = 'platform'
  ) THEN
    ALTER TABLE action_logs
    DROP CONSTRAINT IF EXISTS valid_mvp_platform;
    
    ALTER TABLE action_logs
    ADD CONSTRAINT valid_mvp_platform 
    CHECK (platform IS NULL OR platform IN ('meta_ads', 'google_ads', 'tiktok_ads', 'shopify'));
  END IF;
END $$;

-- ============================================
-- 6. Add comments for documentation
-- ============================================
COMMENT ON CONSTRAINT valid_mvp_platform ON api_credentials IS 
  'MVP platforms only: meta_ads, google_ads, tiktok_ads, shopify';

COMMENT ON CONSTRAINT valid_mvp_platform ON sync_jobs IS 
  'MVP platforms only: meta_ads, google_ads, tiktok_ads, shopify';

COMMENT ON CONSTRAINT valid_mvp_platform ON channels IS 
  'MVP platforms only: Meta, Google, TikTok, Shopify (display names) or meta_ads, google_ads, tiktok_ads, shopify (technical names)';

-- ============================================
-- 7. Update cohorts acquisition_channel constraint (if needed)
-- ============================================
-- Cohorts table has acquisition_channel which may reference deprecated platforms
DO $$
BEGIN
  -- Check if cohorts table exists and has acquisition_channel column
  IF EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'cohorts' AND column_name = 'acquisition_channel'
  ) THEN
    -- Update any deprecated channel references to 'All' or remove
    UPDATE cohorts
    SET acquisition_channel = 'All'
    WHERE acquisition_channel IN (
      'agentkit', 'gohighlevel', 'triplewhale', 'hubspot', 
      'klaviyo', 'stripe', 'linkedin', 'youtube'
    );
    
    -- Add constraint if not exists
    ALTER TABLE cohorts
    DROP CONSTRAINT IF EXISTS valid_acquisition_channel;
    
    ALTER TABLE cohorts
    ADD CONSTRAINT valid_acquisition_channel 
    CHECK (
      acquisition_channel IS NULL OR 
      acquisition_channel IN ('Meta', 'Google', 'TikTok', 'Shopify', 'Organic', 'All')
    );
  END IF;
END $$;

-- ============================================
-- 8. Summary
-- ============================================
DO $$
DECLARE
  credentials_count INT;
  sync_jobs_count INT;
  channels_count INT;
BEGIN
  SELECT COUNT(*) INTO credentials_count FROM api_credentials;
  SELECT COUNT(*) INTO sync_jobs_count FROM sync_jobs;
  SELECT COUNT(*) INTO channels_count FROM channels;
  
  RAISE NOTICE 'Migration 006 Complete:';
  RAISE NOTICE '  - api_credentials: % rows remaining', credentials_count;
  RAISE NOTICE '  - sync_jobs: % rows remaining', sync_jobs_count;
  RAISE NOTICE '  - channels: % rows remaining', channels_count;
  RAISE NOTICE '  - Constraints added to prevent deprecated platforms';
END $$;

