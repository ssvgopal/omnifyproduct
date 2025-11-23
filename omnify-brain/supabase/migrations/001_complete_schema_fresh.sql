-- Complete Schema - Fresh Start
-- Creates all tables from scratch with proper dependencies

-- ============================================
-- 1. Organizations (top-level entity)
-- ============================================
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_organizations_created ON organizations(created_at DESC);

-- ============================================
-- 2. Users (with roles)
-- ============================================
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'vendor')),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_role ON users(role);

COMMENT ON COLUMN users.role IS 'User role: user (end user), admin (client admin), vendor (super admin)';
COMMENT ON COLUMN users.organization_id IS 'NULL for vendor users, required for user/admin';

-- ============================================
-- 3. Vendor Users (super admin details)
-- ============================================
CREATE TABLE vendor_users (
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

CREATE INDEX idx_vendor_users_user_id ON vendor_users(user_id);

-- ============================================
-- 4. Channels (marketing platforms)
-- ============================================
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  platform VARCHAR(50) NOT NULL,
  external_id VARCHAR(255),
  is_active BOOLEAN DEFAULT true,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_channels_org ON channels(organization_id);
CREATE INDEX idx_channels_platform ON channels(platform);

-- ============================================
-- 5. Daily Metrics
-- ============================================
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  spend DECIMAL(10, 2) DEFAULT 0,
  revenue DECIMAL(10, 2) DEFAULT 0,
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  conversions INT DEFAULT 0,
  roas DECIMAL(10, 2) DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_daily_metrics_channel ON daily_metrics(channel_id);
CREATE INDEX idx_daily_metrics_date ON daily_metrics(date DESC);
CREATE UNIQUE INDEX idx_daily_metrics_channel_date ON daily_metrics(channel_id, date);

-- ============================================
-- 6. Creatives
-- ============================================
CREATE TABLE creatives (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  external_id VARCHAR(255),
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50),
  status VARCHAR(50) DEFAULT 'active',
  spend DECIMAL(10, 2) DEFAULT 0,
  revenue DECIMAL(10, 2) DEFAULT 0,
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  conversions INT DEFAULT 0,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_creatives_channel ON creatives(channel_id);
CREATE INDEX idx_creatives_status ON creatives(status);

-- ============================================
-- 7. Brain States (cached brain computations)
-- ============================================
CREATE TABLE brain_states (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  memory_output JSONB NOT NULL,
  oracle_output JSONB NOT NULL,
  curiosity_output JSONB NOT NULL,
  computed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_brain_states_org ON brain_states(organization_id);
CREATE INDEX idx_brain_states_computed ON brain_states(computed_at DESC);

-- ============================================
-- 8. API Credentials
-- ============================================
CREATE TABLE api_credentials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  platform VARCHAR(50) NOT NULL,
  credentials JSONB NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_credentials_org ON api_credentials(organization_id);
CREATE INDEX idx_api_credentials_platform ON api_credentials(platform);

-- ============================================
-- 9. Sync Jobs
-- ============================================
CREATE TABLE sync_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  platform VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'pending',
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  error_message TEXT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sync_jobs_org ON sync_jobs(organization_id);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(status);
CREATE INDEX idx_sync_jobs_created ON sync_jobs(created_at DESC);

-- ============================================
-- 10. Organization Quotas
-- ============================================
CREATE TABLE organization_quotas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
  plan VARCHAR(50) DEFAULT 'free',
  max_users INT DEFAULT 5,
  max_admins INT DEFAULT 2,
  max_channels INT DEFAULT 3,
  max_platforms INT DEFAULT 2,
  max_api_calls_per_day INT DEFAULT 10000,
  max_brain_computes_per_day INT DEFAULT 100,
  max_syncs_per_day INT DEFAULT 24,
  max_data_retention_days INT DEFAULT 90,
  max_exports_per_month INT DEFAULT 10,
  features JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_org_quotas_org_id ON organization_quotas(organization_id);
CREATE INDEX idx_org_quotas_plan ON organization_quotas(plan);

-- ============================================
-- 11. Usage Logs
-- ============================================
CREATE TABLE usage_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  resource_type VARCHAR(50) NOT NULL,
  count INT DEFAULT 1,
  date DATE DEFAULT CURRENT_DATE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_logs_org_date ON usage_logs(organization_id, date);
CREATE INDEX idx_usage_logs_resource ON usage_logs(resource_type);

-- ============================================
-- 12. Audit Logs
-- ============================================
CREATE TABLE audit_logs (
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

CREATE INDEX idx_audit_logs_vendor ON audit_logs(vendor_user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================
-- 13. Subscriptions
-- ============================================
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE UNIQUE,
  plan VARCHAR(50) DEFAULT 'free',
  status VARCHAR(20) DEFAULT 'active',
  amount_cents INT DEFAULT 0,
  currency VARCHAR(3) DEFAULT 'USD',
  billing_cycle VARCHAR(20) DEFAULT 'monthly',
  stripe_subscription_id VARCHAR(255),
  stripe_customer_id VARCHAR(255),
  trial_ends_at TIMESTAMP,
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  canceled_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_org ON subscriptions(organization_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- ============================================
-- 14. Invoices
-- ============================================
CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  subscription_id UUID REFERENCES subscriptions(id),
  invoice_number VARCHAR(50) UNIQUE,
  amount_cents INT NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20) DEFAULT 'draft',
  stripe_invoice_id VARCHAR(255),
  stripe_invoice_url TEXT,
  due_date DATE,
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_invoices_org ON invoices(organization_id);
CREATE INDEX idx_invoices_status ON invoices(status);

-- ============================================
-- 15. Security Events
-- ============================================
CREATE TABLE security_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  event_type VARCHAR(50) NOT NULL,
  severity VARCHAR(20) DEFAULT 'low',
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL,
  description TEXT,
  metadata JSONB DEFAULT '{}',
  ip_address VARCHAR(45),
  user_agent TEXT,
  resolved BOOLEAN DEFAULT false,
  resolved_by UUID REFERENCES vendor_users(id) ON DELETE SET NULL,
  resolved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_severity ON security_events(severity);

-- ============================================
-- 16. System Metrics
-- ============================================
CREATE TABLE system_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  metric_name VARCHAR(100) NOT NULL,
  metric_value NUMERIC NOT NULL,
  metric_unit VARCHAR(20),
  tags JSONB DEFAULT '{}',
  timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp DESC);

-- ============================================
-- 17. Feature Flags
-- ============================================
CREATE TABLE feature_flags (
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

CREATE INDEX idx_feature_flags_enabled ON feature_flags(enabled);

-- ============================================
-- 18. Row Level Security Policies
-- ============================================

-- Users: Can view users in their org
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view users in their org"
  ON users FOR SELECT
  USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ) OR auth.uid() IN (
    SELECT user_id FROM vendor_users
  ));

-- Channels: Org members and vendors
ALTER TABLE channels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org channels"
  ON channels FOR SELECT
  USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ) OR auth.uid() IN (
    SELECT user_id FROM vendor_users
  ));

-- Daily Metrics: Org members and vendors
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org metrics"
  ON daily_metrics FOR SELECT
  USING (channel_id IN (
    SELECT id FROM channels WHERE organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  ) OR auth.uid() IN (
    SELECT user_id FROM vendor_users
  ));

-- Organization Quotas: Org members and vendors
ALTER TABLE organization_quotas ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org quotas"
  ON organization_quotas FOR SELECT
  USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ) OR auth.uid() IN (
    SELECT user_id FROM vendor_users
  ));

-- ============================================
-- 19. Helper Functions
-- ============================================

CREATE OR REPLACE FUNCTION is_vendor(user_uuid UUID)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM users 
    WHERE id = user_uuid AND role = 'vendor'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

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

CREATE OR REPLACE FUNCTION get_daily_usage(org_uuid UUID, resource VARCHAR, date_param DATE DEFAULT CURRENT_DATE)
RETURNS INT AS $$
  SELECT COALESCE(SUM(count), 0)::INT
  FROM usage_logs
  WHERE organization_id = org_uuid
    AND resource_type = resource
    AND date = date_param;
$$ LANGUAGE SQL STABLE;

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
-- SCHEMA COMPLETE
-- ============================================

SELECT 'Schema created successfully!' as status;
