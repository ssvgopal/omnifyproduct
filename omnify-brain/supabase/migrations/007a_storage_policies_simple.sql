-- ============================================
-- Migration 007a: Simple Storage Policies (Fallback)
-- ============================================
-- Purpose: Simplified storage policies if complex organization-scoped policies fail
-- Use this if you get permission errors with 007_create_storage_buckets.sql
--
-- IMPORTANT: These are less secure - they allow all authenticated users
-- to access all files in each bucket. You should add organization checks
-- in your application code.

-- ============================================
-- Prerequisites
-- ============================================
-- 1. Create buckets in Supabase Dashboard first (ALL PRIVATE):
--    - creatives (Private)
--    - avatars (Private)
--    - logos (Private)
--    - exports (Private)
--
-- 2. Then run this migration

-- ============================================
-- Creatives Bucket (Simplified)
-- ============================================
-- Allow all authenticated users to access creatives
-- NOTE: Add organization checks in application code!

DROP POLICY IF EXISTS "Authenticated users can upload creatives" ON storage.objects;
CREATE POLICY "Authenticated users can upload creatives"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'creatives');

DROP POLICY IF EXISTS "Authenticated users can view creatives" ON storage.objects;
CREATE POLICY "Authenticated users can view creatives"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'creatives');

DROP POLICY IF EXISTS "Authenticated users can update creatives" ON storage.objects;
CREATE POLICY "Authenticated users can update creatives"
ON storage.objects FOR UPDATE
TO authenticated
USING (bucket_id = 'creatives');

DROP POLICY IF EXISTS "Authenticated users can delete creatives" ON storage.objects;
CREATE POLICY "Authenticated users can delete creatives"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'creatives');

-- ============================================
-- Avatars Bucket (Simplified)
-- ============================================
-- Allow users to upload their own avatar
DROP POLICY IF EXISTS "Users can upload their own avatar" ON storage.objects;
CREATE POLICY "Users can upload their own avatar"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'avatars' AND
  name = auth.uid()::text || '.%'
);

-- Authenticated users can view avatars (private bucket)
DROP POLICY IF EXISTS "Users can view avatars" ON storage.objects;
CREATE POLICY "Users can view avatars"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'avatars');

-- Users can update/delete their own avatar
DROP POLICY IF EXISTS "Users can manage their own avatar" ON storage.objects;
CREATE POLICY "Users can manage their own avatar"
ON storage.objects FOR ALL
TO authenticated
USING (
  bucket_id = 'avatars' AND
  name = auth.uid()::text || '.%'
);

-- ============================================
-- Logos Bucket (Simplified)
-- ============================================
-- Allow authenticated users to upload logos
-- NOTE: Add admin check in application code!
DROP POLICY IF EXISTS "Authenticated users can upload logos" ON storage.objects;
CREATE POLICY "Authenticated users can upload logos"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'logos');

-- Authenticated users can view logos (private bucket)
DROP POLICY IF EXISTS "Users can view logos" ON storage.objects;
CREATE POLICY "Users can view logos"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'logos');

-- Authenticated users can update/delete logos
-- NOTE: Add admin check in application code!
DROP POLICY IF EXISTS "Authenticated users can manage logos" ON storage.objects;
CREATE POLICY "Authenticated users can manage logos"
ON storage.objects FOR ALL
TO authenticated
USING (bucket_id = 'logos');

-- ============================================
-- Exports Bucket (Simplified)
-- ============================================
-- Allow all authenticated users to access exports
-- NOTE: Add organization checks in application code!
DROP POLICY IF EXISTS "Authenticated users can upload exports" ON storage.objects;
CREATE POLICY "Authenticated users can upload exports"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'exports');

DROP POLICY IF EXISTS "Authenticated users can view exports" ON storage.objects;
CREATE POLICY "Authenticated users can view exports"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'exports');

DROP POLICY IF EXISTS "Authenticated users can delete exports" ON storage.objects;
CREATE POLICY "Authenticated users can delete exports"
ON storage.objects FOR DELETE
TO authenticated
USING (bucket_id = 'exports');

-- ============================================
-- Summary
-- ============================================
DO $$
BEGIN
  RAISE NOTICE 'Migration 007a Complete: Simple Storage Policies';
  RAISE NOTICE '';
  RAISE NOTICE 'WARNING: These policies are simplified and less secure.';
  RAISE NOTICE 'They allow all authenticated users to access all files in each bucket.';
  RAISE NOTICE '';
  RAISE NOTICE 'You MUST add organization checks in your application code:';
  RAISE NOTICE '- Check user.organizationId before upload';
  RAISE NOTICE '- Filter files by organizationId when listing';
  RAISE NOTICE '- Verify organizationId matches before delete';
  RAISE NOTICE '';
  RAISE NOTICE 'For better security, use 007_create_storage_buckets.sql';
  RAISE NOTICE 'after setting up proper storage admin access.';
END $$;

