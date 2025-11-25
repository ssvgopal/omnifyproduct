-- Omnify Brain - Schema Update: Campaigns & Cohorts Tables
-- Migration: 003_campaigns_cohorts_schema.sql
-- Purpose: Add missing tables per Requirements V3 (B.3.2.1, C.1.2, B.4.2.3, C.1.5)

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. CAMPAIGNS TABLE (Missing per B.3.2.1, C.1.2)
-- ============================================
-- Tracks individual campaigns within channels
CREATE TABLE IF NOT EXISTS campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  channel_id UUID REFERENCES channels(id) ON DELETE CASCADE,
  campaign_id VARCHAR(100) NOT NULL, -- External platform campaign ID
  campaign_name VARCHAR(255) NOT NULL,
  campaign_type VARCHAR(50), -- e.g., 'prospecting', 'retargeting', 'brand', 'conversion'
  status VARCHAR(20) CHECK (status IN ('active', 'paused', 'archived')) DEFAULT 'active',
  daily_budget NUMERIC(12,2),
  lifetime_budget NUMERIC(12,2),
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(organization_id, channel_id, campaign_id)
);

-- Indexes for campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_org ON campaigns(organization_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_channel ON campaigns(channel_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);

-- ============================================
-- 2. COHORTS TABLE (Missing per B.4.2.3, C.1.5)
-- ============================================
-- Tracks customer cohort LTV data for drift detection
CREATE TABLE IF NOT EXISTS cohorts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  cohort_month VARCHAR(7) NOT NULL, -- Format: 'YYYY-MM'
  acquisition_channel VARCHAR(50), -- 'Meta', 'Google', 'TikTok', 'Organic', 'All'
  customer_count INTEGER NOT NULL DEFAULT 0,
  total_revenue NUMERIC(14,2) DEFAULT 0,
  ltv_30d NUMERIC(10,2), -- 30-day LTV
  ltv_60d NUMERIC(10,2), -- 60-day LTV
  ltv_90d NUMERIC(10,2), -- 90-day LTV
  ltv_180d NUMERIC(10,2), -- 180-day LTV (optional)
  avg_order_value NUMERIC(10,2),
  repeat_purchase_rate NUMERIC(5,4), -- e.g., 0.35 = 35%
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(organization_id, cohort_month, acquisition_channel)
);

-- Indexes for cohorts
CREATE INDEX IF NOT EXISTS idx_cohorts_org ON cohorts(organization_id);
CREATE INDEX IF NOT EXISTS idx_cohorts_month ON cohorts(cohort_month DESC);
CREATE INDEX IF NOT EXISTS idx_cohorts_channel ON cohorts(acquisition_channel);

-- ============================================
-- 3. UPDATE DAILY_METRICS TABLE (Partial per C.1.4)
-- ============================================
-- Add missing columns: creative_id, campaign_id, frequency, cvr, cpa

-- Add creative_id column (links to specific creative)
ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS creative_id UUID REFERENCES creatives(id) ON DELETE SET NULL;

-- Add campaign_id column (links to specific campaign)
ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL;

-- Add frequency column (avg times user sees ad)
ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS frequency NUMERIC(6,2) DEFAULT 0;

-- Add cvr column (conversion rate)
ALTER TABLE daily_metrics 
ADD COLUMN IF NOT EXISTS cvr NUMERIC(8,6) DEFAULT 0;

-- Note: cpa column already exists in original schema

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_daily_metrics_creative ON daily_metrics(creative_id);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_campaign ON daily_metrics(campaign_id);

-- ============================================
-- 4. CREATIVE_DAILY_METRICS TABLE (New - for time-series creative data)
-- ============================================
-- Tracks daily performance per creative for fatigue detection
CREATE TABLE IF NOT EXISTS creative_daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  creative_id UUID REFERENCES creatives(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  spend NUMERIC(12,2) DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  roas NUMERIC(10,4) DEFAULT 0,
  ctr NUMERIC(8,6) DEFAULT 0,
  cvr NUMERIC(8,6) DEFAULT 0, -- Conversion rate
  cpa NUMERIC(10,2) DEFAULT 0,
  frequency NUMERIC(6,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(creative_id, date)
);

-- Indexes for creative_daily_metrics
CREATE INDEX IF NOT EXISTS idx_creative_daily_metrics_date ON creative_daily_metrics(date DESC);
CREATE INDEX IF NOT EXISTS idx_creative_daily_metrics_creative_date ON creative_daily_metrics(creative_id, date DESC);

-- ============================================
-- 5. ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on new tables
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE cohorts ENABLE ROW LEVEL SECURITY;
ALTER TABLE creative_daily_metrics ENABLE ROW LEVEL SECURITY;

-- Campaigns policies
CREATE POLICY "Users can view their organization's campaigns" ON campaigns
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

CREATE POLICY "Admins can manage campaigns" ON campaigns
  FOR ALL USING (
    organization_id IN (
      SELECT organization_id FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Cohorts policies
CREATE POLICY "Users can view their organization's cohorts" ON cohorts
  FOR SELECT USING (organization_id IN (
    SELECT organization_id FROM users WHERE id = auth.uid()
  ));

CREATE POLICY "Admins can manage cohorts" ON cohorts
  FOR ALL USING (
    organization_id IN (
      SELECT organization_id FROM users 
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Creative daily metrics policies
CREATE POLICY "Users can view their organization's creative metrics" ON creative_daily_metrics
  FOR SELECT USING (creative_id IN (
    SELECT c.id FROM creatives c
    JOIN channels ch ON c.channel_id = ch.id
    WHERE ch.organization_id IN (
      SELECT organization_id FROM users WHERE id = auth.uid()
    )
  ));

-- ============================================
-- 6. UPDATE TRIGGERS
-- ============================================

-- Trigger for campaigns updated_at
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Trigger for cohorts updated_at
CREATE TRIGGER update_cohorts_updated_at BEFORE UPDATE ON cohorts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- 7. COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE campaigns IS 'Individual marketing campaigns within channels (per Requirements V3 B.3.2.1)';
COMMENT ON TABLE cohorts IS 'Customer cohort LTV data for drift detection (per Requirements V3 B.4.2.3)';
COMMENT ON TABLE creative_daily_metrics IS 'Time-series creative performance for fatigue detection (per Requirements V3 B.4.2.1)';

COMMENT ON COLUMN cohorts.ltv_30d IS '30-day customer lifetime value for this cohort';
COMMENT ON COLUMN cohorts.ltv_60d IS '60-day customer lifetime value for this cohort';
COMMENT ON COLUMN cohorts.ltv_90d IS '90-day customer lifetime value for this cohort';
COMMENT ON COLUMN daily_metrics.frequency IS 'Average number of times users see the ad';
COMMENT ON COLUMN daily_metrics.cvr IS 'Conversion rate (conversions / clicks)';
