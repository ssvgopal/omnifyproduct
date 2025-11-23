-- Diagnostic queries to understand the current state
-- Run these to see what's causing the issue

-- 1. Check if role column exists
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'role';

-- 2. Check existing users and their role values (if column exists)
-- Comment out if role column doesn't exist yet
-- SELECT id, email, role, organization_id FROM users LIMIT 10;

-- 3. Check for any constraints on users table
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'users';

-- 4. Count users
SELECT COUNT(*) as total_users FROM users;

-- 5. Check if there are any NULL organization_ids (could be vendors)
SELECT COUNT(*) as users_without_org 
FROM users 
WHERE organization_id IS NULL;
