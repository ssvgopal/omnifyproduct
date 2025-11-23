-- Multi-Panel Architecture: Add roles and vendor features
-- Migration 002: Roles, Quotas, Usage Tracking, Vendor Management

-- ============================================
-- 1. Add role column to users table
-- ============================================

-- First, add the role column without constraint (allow NULL temporarily)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS role VARCHAR(20);

-- Update existing users to have 'user' role by default
UPDATE users 
SET role = 'user' 
WHERE role IS NULL;

-- Now make it NOT NULL with default
ALTER TABLE users 
ALTER COLUMN role SET DEFAULT 'user';

ALTER TABLE users 
ALTER COLUMN role SET NOT NULL;

-- Add constraint for valid roles (only after all rows have valid values)
ALTER TABLE users
ADD CONSTRAINT valid_user_role 
CHECK (role IN ('user', 'admin', 'vendor'));

-- Create index for role-based queries
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

COMMENT ON COLUMN users.role IS 'User role: user (end user), admin (client admin), vendor (super admin)';

-- ============================================
-- 2. Vendor users table
-- ============================================
CREATE TABLE IF NOT EXISTS vendor_users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  permissions JSONB DEFAULT '{}',
  can_access_all_orgs BOOLEAN DEFAULT true,
  can_manage_billing BOOLEAN DEFAULT true,
  can_manage_quotas BOOLEAN DEFAULT true,
  can_view_security BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vendor_users_user_id ON vendor_users(user_id);

COMMENT ON TABLE vendor_users IS 'Vendor/super admin specific settings and permissions';

-- ============================================
-- 3. Organization quotas
-- ============================================
CREATE TABLE IF NOT EXISTS organization_quotas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
  plan VARCHAR(50) DEFAULT 'free',
  
  -- User limits
  max_users INT DEFAULT 5,
  max_admins INT DEFAULT 2,
  
  -- Channel limits
  max_channels INT DEFAULT 3,
  max_platforms INT DEFAULT 2,
  
  -- API limits
  max_api_calls_per_day INT DEFAULT 10000,
  max_brain_computes_per_day INT DEFAULT 100,
  max_syncs_per_day INT DEFAULT 24,
  
  -- Data limits
  max_data_retention_days INT DEFAULT 90,
  max_exports_per_month INT DEFAULT 10,
  
  -- Feature flags
  features JSONB DEFAULT '{}',
  
  -- Dates
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_org_quotas_org_id ON organization_quotas(organization_id);
CREATE INDEX IF NOT EXISTS idx_org_quotas_plan ON organization_quotas(plan);

COMMENT ON TABLE organization_quotas IS 'Per-organization limits and feature flags';
COMMENT ON COLUMN organization_quotas.plan IS 'Pricing plan: free, starter, growth, enterprise';
COMMENT ON COLUMN organization_quotas.features IS 'Feature flags JSON: {ai_insights: true, advanced_analytics: false}';

-- ============================================
-- 4. Usage logs
-- ============================================
CREATE TABLE IF NOT EXISTS usage_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  resource_type VARCHAR(50) NOT NULL,
  count INT DEFAULT 1,
  date DATE DEFAULT CURRENT_DATE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_logs_org_date ON usage_logs(organization_id, date);
CREATE INDEX IF NOT EXISTS idx_usage_logs_resource ON usage_logs(resource_type);

COMMENT ON TABLE usage_logs IS 'Daily usage tracking per organization';
COMMENT ON COLUMN usage_logs.resource_type IS 'Type: api_call, sync, brain_compute, export';

-- ============================================
-- 5. Audit logs (vendor actions)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  vendor_user_id UUID REFERENCES vendor_users(id),
  action VARCHAR(100) NOT NULL,
  target_type VARCHAR(50),
  target_id UUID,
  details JSONB DEFAULT '{}',
  ip_address VARCHAR(45),
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_vendor ON audit_logs(vendor_user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Audit trail for all vendor actions';
COMMENT ON COLUMN audit_logs.target_type IS 'Type: organization, user, quota, etc.';

-- ============================================
-- 6. Billing subscriptions
-- ============================================
CREATE TABLE IF NOT EXISTS subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
  plan VARCHAR(50) DEFAULT 'free',
  status VARCHAR(20) DEFAULT 'active',
  
  -- Pricing
  amount_cents INT DEFAULT 0,
  currency VARCHAR(3) DEFAULT 'USD',
  billing_cycle VARCHAR(20) DEFAULT 'monthly',
  
  -- Stripe (or other payment provider)
  stripe_subscription_id VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  
  -- Dates
  trial_ends_at TIMESTAMP,
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  canceled_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_org ON subscriptions(organization_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_sub ON subscriptions(stripe_subscription_id);

COMMENT ON TABLE subscriptions IS 'Billing and subscription management';
COMMENT ON COLUMN subscriptions.status IS 'Status: active, trialing, past_due, canceled, incomplete';

-- ============================================
-- 7. Invoices
-- ============================================
CREATE TABLE IF NOT EXISTS invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES subscriptions(id),
  
  -- Invoice details
  invoice_number VARCHAR(50) UNIQUE,
  amount_cents INT NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) DEFAULT 'draft',
  
  -- Stripe
  stripe_invoice_id VARCHAR(255),
  stripe_invoice_url TEXT,
  
  -- Dates
  due_date DATE,
  paid_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_org ON invoices(organization_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_created ON invoices(created_at DESC);

COMMENT ON TABLE invoices IS 'Invoice records for billing';
COMMENT ON COLUMN invoices.status IS 'Status: draft, open, paid, void, uncollectible';

-- ============================================
-- 8. Security events
-- ============================================
CREATE TABLE IF NOT EXISTS security_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) DEFAULT 'low',
  
  -- Related entities
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  
  -- Event details
  description TEXT,
  metadata JSONB DEFAULT '{}',
  
  -- Connection info
  ip_address VARCHAR(45),
  user_agent TEXT,
  
  -- Resolution
  resolved BOOLEAN DEFAULT false,
  resolved_by UUID REFERENCES vendor_users(id) ON DELETE SET NULL,
  resolved_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_resolved ON security_events(resolved);
CREATE INDEX IF NOT EXISTS idx_security_events_created ON security_events(created_at DESC);

COMMENT ON TABLE security_events IS 'Security incidents and suspicious activity';
COMMENT ON COLUMN security_events.event_type IS 'Type: failed_login, suspicious_activity, rate_limit_exceeded, etc.';
COMMENT ON COLUMN security_events.severity IS 'Severity: low, medium, high, critical';

-- ============================================
-- 9. System health metrics
-- ============================================
CREATE TABLE IF NOT EXISTS system_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  metric_name VARCHAR(100) NOT NULL,
  metric_value NUMERIC NOT NULL,
  metric_unit VARCHAR(20),
  tags JSONB DEFAULT '{}',
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

COMMENT ON TABLE system_metrics IS 'System health and performance metrics for vendor monitoring';

-- ============================================
-- 10. Feature flags
-- ============================================
CREATE TABLE IF NOT EXISTS feature_flags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  flag_name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT,
  enabled BOOLEAN DEFAULT false,
  rollout_percentage INT DEFAULT 0,
  target_organizations UUID[],
  target_users UUID[],
  metadata JSONB DEFAULT '{}',
  created_by UUID REFERENCES vendor_users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feature_flags_enabled ON feature_flags(enabled);

COMMENT ON TABLE feature_flags IS 'Global feature flags for gradual rollouts';

-- ============================================
-- 11. Update RLS policies for new tables
-- ============================================

-- Organization quotas: only visible to org admins and vendors
ALTER TABLE organization_quotas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org quotas"
  ON organization_quotas FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  );

CREATE POLICY "Vendors can view all quotas"
  ON organization_quotas FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM vendor_users WHERE user_id = auth.uid()
    )
  );

-- Usage logs: visible to org members
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org usage"
  ON usage_logs FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  );

-- Subscriptions: visible to org members
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org subscription"
  ON subscriptions FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  );

-- Invoices: visible to org admins
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view their org invoices"
  ON invoices FOR SELECT
  USING (
    organization_id IN (
      SELECT organization_id FROM users 
      WHERE id = auth.uid() AND role IN ('admin', 'vendor')
    )
  );

-- Audit logs: vendor only
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only vendors can view audit logs"
  ON audit_logs FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM vendor_users WHERE user_id = auth.uid()
    )
  );

-- Security events: vendor only
ALTER TABLE security_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only vendors can view security events"
  ON security_events FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM vendor_users WHERE user_id = auth.uid()
    )
  );

-- ============================================
-- 12. Helper functions
-- ============================================

-- Check if user is vendor
CREATE OR REPLACE FUNCTION is_vendor(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users 
    WHERE id = user_uuid AND role = 'vendor'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user is admin of an organization
CREATE OR REPLACE FUNCTION is_org_admin(user_uuid UUID, org_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users 
    WHERE id = user_uuid 
      AND organization_id = org_uuid 
      AND role IN ('admin', 'vendor')
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get organization usage for a specific resource type
CREATE OR REPLACE FUNCTION get_daily_usage(org_uuid UUID, resource VARCHAR, date_param DATE DEFAULT CURRENT_DATE)
RETURNS INT AS $$
  SELECT COALESCE(SUM(count), 0)::INT
  FROM usage_logs
  WHERE organization_id = org_uuid
    AND resource_type = resource
    AND date = date_param;
$$ LANGUAGE SQL STABLE;

-- Check if organization is within quota
CREATE OR REPLACE FUNCTION is_within_quota(org_uuid UUID, resource VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
  current_usage INT;
  quota_limit INT;
BEGIN
  current_usage := get_daily_usage(org_uuid, resource);
  
  SELECT 
    CASE resource
      WHEN 'api_call' THEN max_api_calls_per_day
      WHEN 'brain_compute' THEN max_brain_computes_per_day
      WHEN 'sync' THEN max_syncs_per_day
      ELSE 999999
    END INTO quota_limit
  FROM organization_quotas
  WHERE organization_id = org_uuid;
  
  RETURN current_usage < COALESCE(quota_limit, 999999);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- 13. Seed default data
-- ============================================

-- Create default quotas for existing organizations
INSERT INTO organization_quotas (organization_id, plan)
SELECT id, 'free'
FROM organizations
WHERE id NOT IN (SELECT organization_id FROM organization_quotas);

-- Create default subscription for existing organizations
INSERT INTO subscriptions (organization_id, plan, status)
SELECT id, 'free', 'active'
FROM organizations
WHERE id NOT IN (SELECT organization_id FROM subscriptions);

-- ============================================
-- MIGRATION COMPLETE
-- ============================================
COMMENT ON SCHEMA public IS 'Multi-panel architecture: User, Admin, Vendor roles with quotas and billing';
