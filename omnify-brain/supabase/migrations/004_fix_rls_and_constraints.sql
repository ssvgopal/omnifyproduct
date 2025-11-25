-- Omnify Brain - Fix RLS Policies and Constraints
-- Migration: 004_fix_rls_and_constraints.sql
-- Purpose: Fix infinite recursion in RLS policies and add missing constraints

-- ============================================
-- 1. FIX RLS INFINITE RECURSION
-- ============================================
-- The issue: users policy references users table, causing infinite recursion
-- Solution: Use auth.uid() directly without subquery on users table for the users policy

-- Drop problematic policies
DROP POLICY IF EXISTS "Users can view their organization's users" ON users;
DROP POLICY IF EXISTS "Users can view their organization" ON organizations;
DROP POLICY IF EXISTS "Users can view their organization's channels" ON channels;
DROP POLICY IF EXISTS "Users can view their organization's metrics" ON daily_metrics;
DROP POLICY IF EXISTS "Users can view their organization's creatives" ON creatives;
DROP POLICY IF EXISTS "Users can view their organization's brain states" ON brain_states;
DROP POLICY IF EXISTS "Admins can manage channels" ON channels;
DROP POLICY IF EXISTS "Admins can manage credentials" ON api_credentials;

-- Also drop policies from migration 003 if they exist
DROP POLICY IF EXISTS "Users can view their organization's campaigns" ON campaigns;
DROP POLICY IF EXISTS "Users can view their organization's cohorts" ON cohorts;
DROP POLICY IF EXISTS "Users can view their organization's creative daily metrics" ON creative_daily_metrics;

-- Drop any policies we're about to create (in case of re-run)
DROP POLICY IF EXISTS "Users can view own record" ON users;
DROP POLICY IF EXISTS "Service role full access to organizations" ON organizations;
DROP POLICY IF EXISTS "Service role full access to users" ON users;
DROP POLICY IF EXISTS "Service role full access to channels" ON channels;
DROP POLICY IF EXISTS "Service role full access to daily_metrics" ON daily_metrics;
DROP POLICY IF EXISTS "Service role full access to creatives" ON creatives;
DROP POLICY IF EXISTS "Service role full access to brain_states" ON brain_states;
DROP POLICY IF EXISTS "Service role full access to api_credentials" ON api_credentials;
DROP POLICY IF EXISTS "Service role full access to sync_jobs" ON sync_jobs;
DROP POLICY IF EXISTS "Service role full access to campaigns" ON campaigns;
DROP POLICY IF EXISTS "Service role full access to cohorts" ON cohorts;
DROP POLICY IF EXISTS "Service role full access to creative_daily_metrics" ON creative_daily_metrics;
DROP POLICY IF EXISTS "Anon can view demo organization" ON organizations;
DROP POLICY IF EXISTS "Anon can view demo channels" ON channels;
DROP POLICY IF EXISTS "Anon can view demo metrics" ON daily_metrics;
DROP POLICY IF EXISTS "Anon can view demo creatives" ON creatives;
DROP POLICY IF EXISTS "Anon can view demo brain states" ON brain_states;
DROP POLICY IF EXISTS "Anon can view demo campaigns" ON campaigns;
DROP POLICY IF EXISTS "Anon can view demo cohorts" ON cohorts;
DROP POLICY IF EXISTS "Anon can view demo creative daily metrics" ON creative_daily_metrics;

-- Create a security definer function to get user's org_id without RLS
CREATE OR REPLACE FUNCTION get_user_organization_id()
RETURNS UUID
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT organization_id FROM users WHERE id = auth.uid()
$$;

-- Recreate policies using the function (avoids recursion)
CREATE POLICY "Users can view own record" ON users
  FOR SELECT USING (id = auth.uid());

CREATE POLICY "Users can view their organization" ON organizations
  FOR SELECT USING (id = get_user_organization_id());

CREATE POLICY "Users can view their organization's channels" ON channels
  FOR SELECT USING (organization_id = get_user_organization_id());

CREATE POLICY "Users can view their organization's metrics" ON daily_metrics
  FOR SELECT USING (channel_id IN (
    SELECT id FROM channels WHERE organization_id = get_user_organization_id()
  ));

CREATE POLICY "Users can view their organization's creatives" ON creatives
  FOR SELECT USING (channel_id IN (
    SELECT id FROM channels WHERE organization_id = get_user_organization_id()
  ));

CREATE POLICY "Users can view their organization's brain states" ON brain_states
  FOR SELECT USING (organization_id = get_user_organization_id());

CREATE POLICY "Users can view their organization's campaigns" ON campaigns
  FOR SELECT USING (organization_id = get_user_organization_id());

CREATE POLICY "Users can view their organization's cohorts" ON cohorts
  FOR SELECT USING (organization_id = get_user_organization_id());

CREATE POLICY "Users can view their organization's creative daily metrics" ON creative_daily_metrics
  FOR SELECT USING (creative_id IN (
    SELECT cr.id FROM creatives cr
    JOIN channels ch ON cr.channel_id = ch.id
    WHERE ch.organization_id = get_user_organization_id()
  ));

-- Admin policies
CREATE POLICY "Admins can manage channels" ON channels
  FOR ALL USING (
    organization_id = get_user_organization_id() AND
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
  );

CREATE POLICY "Admins can manage credentials" ON api_credentials
  FOR ALL USING (
    organization_id = get_user_organization_id() AND
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
  );

-- ============================================
-- 2. ADD SERVICE ROLE BYPASS POLICIES
-- ============================================
-- Allow service role (used by backend) to access all data

CREATE POLICY "Service role full access to organizations" ON organizations
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to users" ON users
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to channels" ON channels
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to daily_metrics" ON daily_metrics
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to creatives" ON creatives
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to brain_states" ON brain_states
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to api_credentials" ON api_credentials
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to sync_jobs" ON sync_jobs
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to campaigns" ON campaigns
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to cohorts" ON cohorts
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access to creative_daily_metrics" ON creative_daily_metrics
  FOR ALL USING (auth.role() = 'service_role');

-- ============================================
-- 3. ADD MISSING UNIQUE CONSTRAINTS
-- ============================================

-- Add unique constraint on channels (organization_id, name) for upsert
ALTER TABLE channels DROP CONSTRAINT IF EXISTS channels_organization_id_name_key;
ALTER TABLE channels ADD CONSTRAINT channels_organization_id_name_key UNIQUE (organization_id, name);

-- Add unique constraint on creatives (channel_id, name) for upsert
ALTER TABLE creatives DROP CONSTRAINT IF EXISTS creatives_channel_id_name_key;
ALTER TABLE creatives ADD CONSTRAINT creatives_channel_id_name_key UNIQUE (channel_id, name);

-- ============================================
-- 4. ADD ANON ROLE POLICIES (for public API access if needed)
-- ============================================
-- These allow the anon key to read data (useful for demo/public dashboards)

CREATE POLICY "Anon can view demo organization" ON organizations
  FOR SELECT USING (name LIKE 'Demo%');

CREATE POLICY "Anon can view demo channels" ON channels
  FOR SELECT USING (organization_id IN (
    SELECT id FROM organizations WHERE name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo metrics" ON daily_metrics
  FOR SELECT USING (channel_id IN (
    SELECT ch.id FROM channels ch
    JOIN organizations o ON ch.organization_id = o.id
    WHERE o.name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo creatives" ON creatives
  FOR SELECT USING (channel_id IN (
    SELECT ch.id FROM channels ch
    JOIN organizations o ON ch.organization_id = o.id
    WHERE o.name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo brain states" ON brain_states
  FOR SELECT USING (organization_id IN (
    SELECT id FROM organizations WHERE name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo campaigns" ON campaigns
  FOR SELECT USING (organization_id IN (
    SELECT id FROM organizations WHERE name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo cohorts" ON cohorts
  FOR SELECT USING (organization_id IN (
    SELECT id FROM organizations WHERE name LIKE 'Demo%'
  ));

CREATE POLICY "Anon can view demo creative daily metrics" ON creative_daily_metrics
  FOR SELECT USING (creative_id IN (
    SELECT cr.id FROM creatives cr
    JOIN channels ch ON cr.channel_id = ch.id
    JOIN organizations o ON ch.organization_id = o.id
    WHERE o.name LIKE 'Demo%'
  ));

-- ============================================
-- DONE
-- ============================================
COMMENT ON FUNCTION get_user_organization_id IS 'Security definer function to get current user organization ID without RLS recursion';
