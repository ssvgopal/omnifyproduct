-- Migration: 008_onboarding_flags.sql
-- Purpose: Track onboarding completion status for organizations and users
-- Safe to run multiple times due to IF NOT EXISTS guards.

ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;

ALTER TABLE users
ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN DEFAULT false;





