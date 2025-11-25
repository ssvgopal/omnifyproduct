-- Migration: Add action_logs table for tracking executed actions
-- Run this in Supabase SQL Editor

CREATE TABLE IF NOT EXISTS action_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  action_type VARCHAR(50) NOT NULL,
  target_id VARCHAR(255),
  platform VARCHAR(50),
  status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'failed', 'reverted')) DEFAULT 'pending',
  error_message TEXT,
  executed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_action_logs_org ON action_logs(organization_id);
CREATE INDEX idx_action_logs_user ON action_logs(user_id);
CREATE INDEX idx_action_logs_executed ON action_logs(executed_at DESC);

COMMENT ON TABLE action_logs IS 'Audit log of all actions executed by users';

