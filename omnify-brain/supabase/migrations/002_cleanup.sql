-- Cleanup script for migration 002
-- Run this FIRST if you had a failed migration attempt

-- Remove the constraint if it exists
ALTER TABLE users DROP CONSTRAINT IF EXISTS valid_user_role;

-- Drop the role column if it exists (we'll recreate it properly)
ALTER TABLE users DROP COLUMN IF EXISTS role;

-- Verify the column is gone
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'role';

-- Should return 0 rows if cleanup was successful
