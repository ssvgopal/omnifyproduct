-- Migration: Add auth_id to users table for Supabase Auth integration
-- Run this in Supabase SQL Editor

-- Add auth_id column to link users table with auth.users
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_id UUID;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_auth_id ON users(auth_id);

-- Add comment
COMMENT ON COLUMN users.auth_id IS 'References auth.users(id) from Supabase Auth';

