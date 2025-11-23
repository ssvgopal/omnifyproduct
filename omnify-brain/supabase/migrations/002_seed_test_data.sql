-- Seed Test Data
-- Creates test organizations, users, and sample data

-- ============================================
-- 1. Create Test Organizations
-- ============================================

-- Demo Beauty Co (main test org)
INSERT INTO organizations (id, name)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'Demo Beauty Co'),
  ('22222222-2222-2222-2222-222222222222', 'Acme Fashion'),
  ('33333333-3333-3333-3333-333333333333', 'TechStart Inc')
ON CONFLICT DO NOTHING;

-- ============================================
-- 2. Create Test Users (all three roles)
-- ============================================

-- USERS (end users at Demo Beauty Co)
INSERT INTO users (id, email, organization_id, role)
VALUES 
  ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'sarah@demo.com', '11111111-1111-1111-1111-111111111111', 'user'),
  ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'jason@demo.com', '11111111-1111-1111-1111-111111111111', 'user'),
  ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'emily@demo.com', '11111111-1111-1111-1111-111111111111', 'user')
ON CONFLICT (email) DO NOTHING;

-- ADMIN (admin at Demo Beauty Co)
INSERT INTO users (id, email, organization_id, role)
VALUES 
  ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'admin@demo.com', '11111111-1111-1111-1111-111111111111', 'admin')
ON CONFLICT (email) DO NOTHING;

-- VENDOR (your team - super admins)
INSERT INTO users (id, email, organization_id, role)
VALUES 
  ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'vendor@omnify.ai', NULL, 'vendor'),
  ('ffffffff-ffff-ffff-ffff-ffffffffffff', 'support@omnify.ai', NULL, 'vendor')
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- 3. Create Vendor User Records
-- ============================================

INSERT INTO vendor_users (user_id, can_access_all_orgs, can_manage_billing, can_manage_quotas, can_view_security)
VALUES 
  ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', true, true, true, true),
  ('ffffffff-ffff-ffff-ffff-ffffffffffff', true, false, false, true)
ON CONFLICT (user_id) DO NOTHING;

-- ============================================
-- 4. Create Organization Quotas
-- ============================================

INSERT INTO organization_quotas (organization_id, plan, max_users, max_channels, features)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'growth', 20, 10, '{"ai_insights": true, "advanced_analytics": true}'),
  ('22222222-2222-2222-2222-222222222222', 'enterprise', 100, 50, '{"ai_insights": true, "advanced_analytics": true, "white_label": true}'),
  ('33333333-3333-3333-3333-333333333333', 'free', 5, 3, '{"ai_insights": false}')
ON CONFLICT (organization_id) DO NOTHING;

-- ============================================
-- 5. Create Subscriptions
-- ============================================

INSERT INTO subscriptions (organization_id, plan, status, amount_cents, billing_cycle)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'growth', 'active', 29900, 'monthly'),
  ('22222222-2222-2222-2222-222222222222', 'enterprise', 'active', 99900, 'monthly'),
  ('33333333-3333-3333-3333-333333333333', 'free', 'trialing', 0, 'monthly')
ON CONFLICT (organization_id) DO NOTHING;

-- ============================================
-- 6. Create Sample Channels
-- ============================================

INSERT INTO channels (id, organization_id, name, platform, is_active)
VALUES 
  ('c1111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'Meta Ads', 'meta', true),
  ('c2222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 'Google Ads', 'google', true),
  ('c3333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'TikTok Ads', 'tiktok', true)
ON CONFLICT DO NOTHING;

-- ============================================
-- 7. Create Sample Daily Metrics (last 7 days)
-- ============================================

INSERT INTO daily_metrics (channel_id, date, spend, revenue, impressions, clicks, conversions, roas)
VALUES 
  -- Meta Ads - last 7 days
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 6, 1200.00, 4800.00, 45000, 1200, 96, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 5, 1350.00, 5400.00, 48000, 1350, 108, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 4, 1500.00, 6000.00, 52000, 1500, 120, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 3, 1400.00, 5600.00, 50000, 1400, 112, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 2, 1600.00, 6400.00, 55000, 1600, 128, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE - 1, 1800.00, 7200.00, 60000, 1800, 144, 4.0),
  ('c1111111-1111-1111-1111-111111111111', CURRENT_DATE, 2000.00, 8000.00, 65000, 2000, 160, 4.0),
  
  -- Google Ads - last 7 days
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 6, 800.00, 2400.00, 30000, 800, 48, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 5, 900.00, 2700.00, 33000, 900, 54, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 4, 1000.00, 3000.00, 35000, 1000, 60, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 3, 950.00, 2850.00, 34000, 950, 57, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 2, 1100.00, 3300.00, 38000, 1100, 66, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE - 1, 1200.00, 3600.00, 40000, 1200, 72, 3.0),
  ('c2222222-2222-2222-2222-222222222222', CURRENT_DATE, 1300.00, 3900.00, 42000, 1300, 78, 3.0)
ON CONFLICT (channel_id, date) DO NOTHING;

-- ============================================
-- 8. Create Sample Brain State
-- ============================================

INSERT INTO brain_states (organization_id, memory_output, oracle_output, curiosity_output)
VALUES (
  '11111111-1111-1111-1111-111111111111',
  '{
    "totalSpend": 10800,
    "totalRevenue": 43200,
    "blendedRoas": 4.0,
    "channelPerformance": [
      {"name": "Meta Ads", "spend": 7200, "revenue": 28800, "roas": 4.0},
      {"name": "Google Ads", "spend": 3600, "revenue": 10800, "roas": 3.0}
    ]
  }',
  '{
    "riskScore": 0.35,
    "riskFactors": [
      {"type": "creative_fatigue", "severity": "medium", "description": "Creative #123 showing 25% decline"}
    ]
  }',
  '{
    "recommendations": [
      {
        "action": "Scale Meta Ads by 20%",
        "rationale": "Consistent 4.0 ROAS with room to grow",
        "impact": "+$5,760 revenue",
        "confidence": 0.85
      }
    ]
  }'
)
ON CONFLICT DO NOTHING;

-- ============================================
-- 9. Create Sample Usage Logs
-- ============================================

INSERT INTO usage_logs (organization_id, resource_type, count, date)
VALUES 
  ('11111111-1111-1111-1111-111111111111', 'api_call', 245, CURRENT_DATE),
  ('11111111-1111-1111-1111-111111111111', 'brain_compute', 12, CURRENT_DATE),
  ('11111111-1111-1111-1111-111111111111', 'sync', 3, CURRENT_DATE),
  ('22222222-2222-2222-2222-222222222222', 'api_call', 890, CURRENT_DATE),
  ('33333333-3333-3333-3333-333333333333', 'api_call', 45, CURRENT_DATE)
ON CONFLICT DO NOTHING;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify organizations
SELECT 'Organizations:', COUNT(*) FROM organizations;

-- Verify users by role
SELECT 'Users by role:' as label, role, COUNT(*) 
FROM users 
GROUP BY role;

-- Verify quotas
SELECT 'Organization quotas:', COUNT(*) FROM organization_quotas;

-- Verify channels
SELECT 'Channels:', COUNT(*) FROM channels;

-- Verify metrics
SELECT 'Daily metrics:', COUNT(*) FROM daily_metrics;

SELECT '✅ Test data seeded successfully!' as status;
