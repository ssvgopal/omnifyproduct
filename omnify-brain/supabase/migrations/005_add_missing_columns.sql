-- Omnify Brain - Add Missing Columns
-- Migration: 005_add_missing_columns.sql
-- Purpose: Add columns that may be missing from initial schema

-- ============================================
-- 1. DAILY_METRICS - Add missing columns
-- ============================================
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS cpa NUMERIC(10,2) DEFAULT 0;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS ctr NUMERIC(5,4) DEFAULT 0;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS frequency NUMERIC(5,2) DEFAULT 0;
ALTER TABLE daily_metrics ADD COLUMN IF NOT EXISTS cvr NUMERIC(5,4) DEFAULT 0;

-- ============================================
-- 2. CREATIVES - Add missing columns
-- ============================================
ALTER TABLE creatives ADD COLUMN IF NOT EXISTS ctr NUMERIC(5,4) DEFAULT 0;
ALTER TABLE creatives ADD COLUMN IF NOT EXISTS cpa NUMERIC(10,2) DEFAULT 0;

-- ============================================
-- 3. Verify columns exist
-- ============================================
-- This will fail if columns don't exist, confirming they were added
DO $$
BEGIN
  PERFORM cpa, ctr, frequency, cvr FROM daily_metrics LIMIT 0;
  PERFORM ctr FROM creatives LIMIT 0;
  RAISE NOTICE 'All columns verified successfully';
END $$;
