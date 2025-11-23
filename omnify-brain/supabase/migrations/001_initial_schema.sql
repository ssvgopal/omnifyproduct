-- Omnify Brain - Database Schema
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Organizations (Multi-tenant)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('admin', 'member', 'viewer')) DEFAULT 'member',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Marketing Channels
CREATE TABLE channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  platform TEXT CHECK (platform IN ('Meta', 'Google', 'TikTok', 'Shopify', 'Email', 'LinkedIn')) NOT NULL,
  external_id TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(organization_id, platform, external_id)
);

-- Daily Metrics (Time-series data)
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  spend NUMERIC(12,2) DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  roas NUMERIC(10,2) DEFAULT 0,
  cpa NUMERIC(10,2) DEFAULT 0,
  ctr NUMERIC(5,4) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(channel_id, date)
);

-- Create index for time-series queries
CREATE INDEX idx_daily_metrics_date ON daily_metrics(date DESC);
CREATE INDEX idx_daily_metrics_channel_date ON daily_metrics(channel_id, date DESC);

-- Creatives
CREATE TABLE creatives (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  external_id TEXT,
  status TEXT CHECK (status IN ('active', 'paused', 'archived')) DEFAULT 'active',
  launch_date DATE,
  spend NUMERIC(12,2) DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  roas NUMERIC(10,2) DEFAULT 0,
  ctr NUMERIC(5,4) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Brain States (Cached outputs)
CREATE TABLE brain_states (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  memory_output JSONB,
  oracle_output JSONB,
  curiosity_output JSONB,
  computed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for latest brain state
CREATE INDEX idx_brain_states_org_computed ON brain_states(organization_id, computed_at DESC);

-- API Credentials (Encrypted)
CREATE TABLE api_credentials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  credentials JSONB NOT NULL, -- Store encrypted credentials
  is_active BOOLEAN DEFAULT TRUE,
  last_synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(organization_id, platform)
);

-- Sync Jobs (Track data ingestion)
CREATE TABLE sync_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')) DEFAULT 'pending',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  error_message TEXT,
  records_synced INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sync_jobs_org_created ON sync_jobs(organization_id, created_at DESC);

-- Row Level Security (RLS) Policies
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE creatives ENABLE ROW LEVEL SECURITY;
ALTER TABLE brain_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE sync_jobs ENABLE ROW LEVEL SECURITY;

-- Users can only see their own organization's data
CREATE POLICY "Users can view their organization" ON organizations
  FOR SELECT USING (id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

CREATE POLICY "Users can view their organization's users" ON users
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

CREATE POLICY "Users can view their organization's channels" ON channels
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

CREATE POLICY "Users can view their organization's metrics" ON daily_metrics
  FOR SELECT USING (channel_id IN (
    SELECT id FROM channels WHERE organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  ));

CREATE POLICY "Users can view their organization's creatives" ON creatives
  FOR SELECT USING (channel_id IN (
    SELECT id FROM channels WHERE organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  ));

CREATE POLICY "Users can view their organization's brain states" ON brain_states
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

-- Admin policies for insert/update/delete
CREATE POLICY "Admins can manage channels" ON channels
  FOR ALL USING (
    organization_id IN (
      SELECT organization_id FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Admins can manage credentials" ON api_credentials
  FOR ALL USING (
    organization_id IN (
      SELECT organization_id FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Functions
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_channels_updated_at BEFORE UPDATE ON channels
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_creatives_updated_at BEFORE UPDATE ON creatives
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_api_credentials_updated_at BEFORE UPDATE ON api_credentials
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
