-- ============================================
-- Migration 007: Storage Bucket Setup Guide
-- ============================================
-- Purpose: Instructions for setting up Supabase Storage buckets
-- 
-- IMPORTANT: Storage buckets and policies must be created through:
-- 1. Supabase Dashboard (Storage section)
-- 2. Supabase Management API
-- 3. Supabase CLI
--
-- This file provides the SQL for RLS policies, but buckets must be created first.

-- ============================================
-- STEP 1: Create Buckets in Supabase Dashboard
-- ============================================
-- Go to: Supabase Dashboard → Storage → New Bucket
--
-- Create these buckets (ALL PRIVATE for security):
-- 1. Name: "creatives" | Public: No (Private)
-- 2. Name: "avatars" | Public: No (Private)
-- 3. Name: "logos" | Public: No (Private)
-- 4. Name: "exports" | Public: No (Private)
--
-- Note: All buckets are private. Use signed URLs for access.
--
-- After creating buckets, run the policies below.

-- ============================================
-- STEP 2: Storage Policies (RLS)
-- ============================================
-- Note: These policies use Supabase's storage schema
-- You may need to run these as a Supabase admin or through the Dashboard

-- Create helper function to get user's organization_id (avoids RLS recursion)
-- This function uses SECURITY DEFINER to bypass RLS when checking users table
-- Uses id = auth.uid() pattern consistent with other migrations
CREATE OR REPLACE FUNCTION get_user_organization_id_for_storage()
RETURNS UUID
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT organization_id FROM users 
  WHERE id = auth.uid()
  LIMIT 1;
$$;

-- ============================================
-- Creatives Bucket Policies
-- ============================================

-- Allow authenticated users to upload creatives for their organization
DROP POLICY IF EXISTS "Users can upload creatives for their organization" ON storage.objects;
CREATE POLICY "Users can upload creatives for their organization"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'creatives' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- Allow authenticated users to view creatives in their organization
DROP POLICY IF EXISTS "Users can view creatives in their organization" ON storage.objects;
CREATE POLICY "Users can view creatives in their organization"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'creatives' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- Allow authenticated users to update creatives in their organization
DROP POLICY IF EXISTS "Users can update creatives for their organization" ON storage.objects;
CREATE POLICY "Users can update creatives for their organization"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'creatives' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- Allow authenticated users to delete creatives in their organization
DROP POLICY IF EXISTS "Users can delete creatives for their organization" ON storage.objects;
CREATE POLICY "Users can delete creatives for their organization"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'creatives' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- ============================================
-- Avatars Bucket Policies
-- ============================================

-- Allow authenticated users to upload their own avatar
DROP POLICY IF EXISTS "Users can upload their own avatar" ON storage.objects;
CREATE POLICY "Users can upload their own avatar"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'avatars' AND
  name = auth.uid()::text || '.%'
);

-- Allow authenticated users to view avatars (private bucket)
DROP POLICY IF EXISTS "Users can view avatars" ON storage.objects;
CREATE POLICY "Users can view avatars"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'avatars');

-- Allow authenticated users to update their own avatar
DROP POLICY IF EXISTS "Users can update their own avatar" ON storage.objects;
CREATE POLICY "Users can update their own avatar"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'avatars' AND
  name = auth.uid()::text || '.%'
);

-- Allow authenticated users to delete their own avatar
DROP POLICY IF EXISTS "Users can delete their own avatar" ON storage.objects;
CREATE POLICY "Users can delete their own avatar"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'avatars' AND
  name = auth.uid()::text || '.%'
);

-- ============================================
-- Logos Bucket Policies
-- ============================================

-- Allow admins/vendors to upload logos for their organization
DROP POLICY IF EXISTS "Admins can upload logos for their organization" ON storage.objects;
CREATE POLICY "Admins can upload logos for their organization"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'logos' AND
  name = get_user_organization_id_for_storage()::text || '.%' AND
  (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'vendor')
);

-- Allow authenticated users to view logos (private bucket)
DROP POLICY IF EXISTS "Users can view logos" ON storage.objects;
CREATE POLICY "Users can view logos"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'logos');

-- Allow admins/vendors to update logos for their organization
DROP POLICY IF EXISTS "Admins can update logos for their organization" ON storage.objects;
CREATE POLICY "Admins can update logos for their organization"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'logos' AND
  name = get_user_organization_id_for_storage()::text || '.%' AND
  (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'vendor')
);

-- Allow admins/vendors to delete logos for their organization
DROP POLICY IF EXISTS "Admins can delete logos for their organization" ON storage.objects;
CREATE POLICY "Admins can delete logos for their organization"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'logos' AND
  name = get_user_organization_id_for_storage()::text || '.%' AND
  (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'vendor')
);

-- ============================================
-- Exports Bucket Policies
-- ============================================

-- Allow authenticated users to upload exports for their organization
DROP POLICY IF EXISTS "Users can upload exports for their organization" ON storage.objects;
CREATE POLICY "Users can upload exports for their organization"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'exports' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- Allow authenticated users to view exports in their organization
DROP POLICY IF EXISTS "Users can view exports in their organization" ON storage.objects;
CREATE POLICY "Users can view exports in their organization"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'exports' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- Allow authenticated users to delete exports in their organization
DROP POLICY IF EXISTS "Users can delete exports for their organization" ON storage.objects;
CREATE POLICY "Users can delete exports for their organization"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'exports' AND
  (storage.foldername(name))[1] = get_user_organization_id_for_storage()::text
);

-- ============================================
-- Alternative: Use Service Role (if policies fail)
-- ============================================
-- If you get permission errors, you can:
-- 1. Use Supabase Dashboard → Storage → Policies (UI)
-- 2. Use Supabase Management API
-- 3. Contact Supabase support for storage policy setup
--
-- The policies above use auth.uid() which requires:
-- - Users table linked to auth.users via auth_id
-- - Proper RLS on users table
-- - Authenticated requests

-- ============================================
-- Summary
-- ============================================
DO $$
BEGIN
  RAISE NOTICE 'Migration 007: Storage Setup Instructions';
  RAISE NOTICE '';
  RAISE NOTICE 'IMPORTANT: Storage buckets must be created in Supabase Dashboard first!';
  RAISE NOTICE '';
  RAISE NOTICE 'Steps:';
  RAISE NOTICE '1. Go to Supabase Dashboard → Storage';
  RAISE NOTICE '2. Create buckets: creatives, avatars, logos, exports';
  RAISE NOTICE '3. Set public access: ALL PRIVATE (unchecked for all buckets)';
  RAISE NOTICE '4. Use signed URLs for file access (getSignedUrl function)';
  RAISE NOTICE '4. Then run this migration to create policies';
  RAISE NOTICE '';
  RAISE NOTICE 'If you get permission errors:';
  RAISE NOTICE '- Use Supabase Dashboard → Storage → Policies (UI)';
  RAISE NOTICE '- Or use Supabase Management API';
  RAISE NOTICE '- Policies use auth.uid() which requires proper auth setup';
END $$;
