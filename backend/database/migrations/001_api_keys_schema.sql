-- API Keys and Integrations Schema for OmniFy Cloud Connect
-- This migration creates tables for secure API key storage and platform integrations

-- ========== ORGANIZATIONS TABLE ==========
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- ========== API KEYS TABLE ==========
CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'openai', 'anthropic', 'gemini', 'grok', 'openrouter', 'meta_ads', 'google_ads', 'tiktok', 'shopify'
    key_name VARCHAR(100) NOT NULL, -- 'api_key', 'access_token', 'client_id', etc.
    key_value_encrypted TEXT NOT NULL, -- Encrypted using Fernet
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(organization_id, platform, key_name)
);

-- ========== INTEGRATIONS TABLE ==========
CREATE TABLE IF NOT EXISTS integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL, -- 'meta_ads', 'google_ads', 'tiktok', 'shopify'
    platform_account_id VARCHAR(255), -- External account ID (e.g., Meta Ad Account ID)
    platform_account_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'connected', 'error', 'disconnected'
    last_sync_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    config JSONB DEFAULT '{}', -- Additional configuration
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, platform, platform_account_id)
);

-- ========== DAILY METRICS TABLE ==========
CREATE TABLE IF NOT EXISTS daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES integrations(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    spend DECIMAL(12, 2) DEFAULT 0,
    revenue DECIMAL(12, 2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    roas DECIMAL(10, 2) DEFAULT 0,
    ctr DECIMAL(5, 2) DEFAULT 0,
    cpc DECIMAL(10, 2) DEFAULT 0,
    cpm DECIMAL(10, 2) DEFAULT 0,
    raw_data JSONB DEFAULT '{}', -- Store raw platform response
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, platform, metric_date)
);

-- ========== CAMPAIGNS TABLE ==========
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    integration_id UUID REFERENCES integrations(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_campaign_id VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'ended'
    objective VARCHAR(100),
    budget DECIMAL(12, 2),
    spend DECIMAL(12, 2) DEFAULT 0,
    revenue DECIMAL(12, 2) DEFAULT 0,
    roas DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, platform, platform_campaign_id)
);

-- ========== CREATIVES TABLE ==========
CREATE TABLE IF NOT EXISTS creatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    platform_creative_id VARCHAR(255) NOT NULL,
    creative_name VARCHAR(255),
    creative_type VARCHAR(50), -- 'image', 'video', 'carousel', 'text'
    status VARCHAR(20) DEFAULT 'active',
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend DECIMAL(12, 2) DEFAULT 0,
    fatigue_score DECIMAL(5, 2) DEFAULT 0, -- 0-100 score
    fatigue_prediction_date DATE, -- Predicted fatigue date
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(organization_id, platform, platform_creative_id)
);

-- ========== PREDICTIONS TABLE ==========
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    prediction_type VARCHAR(50) NOT NULL, -- 'creative_fatigue', 'roi_decay', 'ltv_forecast', 'audience_saturation'
    entity_type VARCHAR(50), -- 'campaign', 'creative', 'audience'
    entity_id UUID,
    prediction_date DATE NOT NULL,
    prediction_value DECIMAL(12, 2),
    confidence_score DECIMAL(5, 2), -- 0-100
    prediction_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ========== INDEXES ==========
CREATE INDEX IF NOT EXISTS idx_api_keys_org ON api_keys(organization_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_platform ON api_keys(platform);
CREATE INDEX IF NOT EXISTS idx_integrations_org ON integrations(organization_id);
CREATE INDEX IF NOT EXISTS idx_integrations_status ON integrations(status);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_org_date ON daily_metrics(organization_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_platform ON daily_metrics(platform);
CREATE INDEX IF NOT EXISTS idx_campaigns_org ON campaigns(organization_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_platform ON campaigns(platform);
CREATE INDEX IF NOT EXISTS idx_creatives_campaign ON creatives(campaign_id);
CREATE INDEX IF NOT EXISTS idx_predictions_org_type ON predictions(organization_id, prediction_type);

-- ========== UPDATED_AT TRIGGER ==========
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_keys_updated_at BEFORE UPDATE ON api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_metrics_updated_at BEFORE UPDATE ON daily_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_creatives_updated_at BEFORE UPDATE ON creatives
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========== ROW LEVEL SECURITY ==========
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE creatives ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their organization's data)
CREATE POLICY organizations_policy ON organizations
    FOR ALL USING (id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY api_keys_policy ON api_keys
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY integrations_policy ON integrations
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY daily_metrics_policy ON daily_metrics
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY campaigns_policy ON campaigns
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY creatives_policy ON creatives
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

CREATE POLICY predictions_policy ON predictions
    FOR ALL USING (organization_id IN (
        SELECT organization_id FROM auth.users WHERE id = auth.uid()
    ));

-- Insert default organization for testing
INSERT INTO organizations (name, slug) VALUES ('Default Organization', 'default')
ON CONFLICT (slug) DO NOTHING;
