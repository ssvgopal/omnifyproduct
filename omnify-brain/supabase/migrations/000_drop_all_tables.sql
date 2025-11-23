-- DROP ALL TABLES - Fresh Start
-- WARNING: This will delete ALL data. Only use in development!

-- Drop all tables in reverse dependency order
DROP TABLE IF EXISTS feature_flags CASCADE;
DROP TABLE IF EXISTS system_metrics CASCADE;
DROP TABLE IF EXISTS security_events CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS usage_logs CASCADE;
DROP TABLE IF EXISTS organization_quotas CASCADE;
DROP TABLE IF EXISTS vendor_users CASCADE;
DROP TABLE IF EXISTS brain_states CASCADE;
DROP TABLE IF EXISTS sync_jobs CASCADE;
DROP TABLE IF EXISTS api_credentials CASCADE;
DROP TABLE IF EXISTS creatives CASCADE;
DROP TABLE IF EXISTS daily_metrics CASCADE;
DROP TABLE IF EXISTS channels CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Drop custom functions if they exist
DROP FUNCTION IF EXISTS is_vendor(UUID);
DROP FUNCTION IF EXISTS is_org_admin(UUID, UUID);
DROP FUNCTION IF EXISTS get_daily_usage(UUID, VARCHAR, DATE);
DROP FUNCTION IF EXISTS is_within_quota(UUID, VARCHAR);

-- Verify all tables are dropped
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- Should return empty or only system tables
