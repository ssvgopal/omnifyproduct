# Supabase Storage Setup Guide

**Date**: January 2025  
**Status**: 📋 **SETUP REQUIRED**

---

## 🚨 IMPORTANT: Storage Setup Process

Supabase Storage buckets and policies **cannot be created via SQL migrations alone**. You must use the Supabase Dashboard or Management API.

---

## 📋 STEP-BY-STEP SETUP

### **Step 1: Create Storage Buckets**

**Go to:** Supabase Dashboard → Storage → New Bucket

**Create these 4 buckets:**

| Bucket Name | Public Access | Purpose |
|-------------|---------------|---------|
| `creatives` | ❌ No (Private) | Ad creative assets (images/videos) |
| `avatars` | ✅ Yes (Public) | User profile pictures |
| `logos` | ✅ Yes (Public) | Organization logos |
| `exports` | ❌ No (Private) | Generated reports/exports |

**For each bucket:**
1. Click "New Bucket"
2. Enter bucket name
3. Set public access (as shown above)
4. Click "Create bucket"

---

### **Step 2: Create Storage Policies**

**Option A: Via Supabase Dashboard (Recommended)**

1. Go to **Storage** → Select a bucket (e.g., `creatives`)
2. Click **"Policies"** tab
3. Click **"New Policy"**
4. Use the policy templates below

**Option B: Via SQL (If you have admin access)**

Run the policies from `007_create_storage_buckets.sql` in Supabase SQL Editor.

**Note:** If you get "must be owner" errors, use Option A (Dashboard).

---

## 🔒 POLICY TEMPLATES

### **Creatives Bucket (Private)**

**Policy 1: Upload**
- Policy Name: `Users can upload creatives for their organization`
- Allowed Operation: `INSERT`
- Target Roles: `authenticated`
- USING Expression: `bucket_id = 'creatives'`
- WITH CHECK Expression: `(storage.foldername(name))[1] = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)`

**Policy 2: View**
- Policy Name: `Users can view creatives in their organization`
- Allowed Operation: `SELECT`
- Target Roles: `authenticated`
- USING Expression: `bucket_id = 'creatives' AND (storage.foldername(name))[1] = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)`

**Policy 3: Update**
- Policy Name: `Users can update creatives for their organization`
- Allowed Operation: `UPDATE`
- Target Roles: `authenticated`
- USING Expression: Same as View policy

**Policy 4: Delete**
- Policy Name: `Users can delete creatives for their organization`
- Allowed Operation: `DELETE`
- Target Roles: `authenticated`
- USING Expression: Same as View policy

---

### **Avatars Bucket (Public)**

**Policy 1: Upload**
- Policy Name: `Users can upload their own avatar`
- Allowed Operation: `INSERT`
- Target Roles: `authenticated`
- WITH CHECK Expression: `bucket_id = 'avatars' AND name = auth.uid()::text || '.%'`

**Policy 2: View (Public)**
- Policy Name: `Avatars are publicly viewable`
- Allowed Operation: `SELECT`
- Target Roles: `public`
- USING Expression: `bucket_id = 'avatars'`

**Policy 3: Update**
- Policy Name: `Users can update their own avatar`
- Allowed Operation: `UPDATE`
- Target Roles: `authenticated`
- USING Expression: `bucket_id = 'avatars' AND name = auth.uid()::text || '.%'`

**Policy 4: Delete**
- Policy Name: `Users can delete their own avatar`
- Allowed Operation: `DELETE`
- Target Roles: `authenticated`
- USING Expression: Same as Update policy

---

### **Logos Bucket (Public)**

**Policy 1: Upload (Admin Only)**
- Policy Name: `Admins can upload logos for their organization`
- Allowed Operation: `INSERT`
- Target Roles: `authenticated`
- WITH CHECK Expression: `bucket_id = 'logos' AND name = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)::text || '.%' AND (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'vendor')`

**Policy 2: View (Public)**
- Policy Name: `Logos are publicly viewable`
- Allowed Operation: `SELECT`
- Target Roles: `public`
- USING Expression: `bucket_id = 'logos'`

**Policy 3: Update (Admin Only)**
- Policy Name: `Admins can update logos for their organization`
- Allowed Operation: `UPDATE`
- Target Roles: `authenticated`
- USING Expression: Same as Upload policy

**Policy 4: Delete (Admin Only)**
- Policy Name: `Admins can delete logos for their organization`
- Allowed Operation: `DELETE`
- Target Roles: `authenticated`
- USING Expression: Same as Upload policy

---

### **Exports Bucket (Private)**

**Policy 1: Upload**
- Policy Name: `Users can upload exports for their organization`
- Allowed Operation: `INSERT`
- Target Roles: `authenticated`
- WITH CHECK Expression: `bucket_id = 'exports' AND (storage.foldername(name))[1] = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)`

**Policy 2: View**
- Policy Name: `Users can view exports in their organization`
- Allowed Operation: `SELECT`
- Target Roles: `authenticated`
- USING Expression: Same as Upload policy

**Policy 3: Delete**
- Policy Name: `Users can delete exports for their organization`
- Allowed Operation: `DELETE`
- Target Roles: `authenticated`
- USING Expression: Same as Upload policy

---

## 🔧 ALTERNATIVE: Simplified Policies (If Complex Policies Fail)

If the organization-scoped policies don't work, you can use simpler policies:

### **Simplified Creatives Policy**
```sql
-- Allow all authenticated users to access creatives
CREATE POLICY "Authenticated users can access creatives"
ON storage.objects
FOR ALL
TO authenticated
USING (bucket_id = 'creatives');
```

**Note:** This is less secure but will work. You'll need to add organization checks in your application code.

---

## ✅ VERIFICATION

After setting up buckets and policies:

1. **Test Upload:**
   ```bash
   curl -X POST http://localhost:3000/api/upload/creative \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test.jpg" \
     -F "creativeId=test-123"
   ```

2. **Check Storage:**
   - Go to Supabase Dashboard → Storage
   - Verify files appear in correct buckets
   - Verify organization-scoped paths

3. **Test Access:**
   - Try accessing files from different organizations
   - Should only see files from your organization

---

## 🐛 TROUBLESHOOTING

### **Error: "must be owner of relation objects"**

**Solution:**
- Use Supabase Dashboard → Storage → Policies (UI) instead of SQL
- Or contact Supabase support for storage admin access

### **Error: "auth.uid() returns null"**

**Solution:**
- Ensure users are authenticated via Supabase Auth
- Check that `users` table has `auth_id` column linked to `auth.users`
- Verify RLS is enabled on `users` table

### **Error: "organization_id not found"**

**Solution:**
- Ensure user has `organization_id` set in `users` table
- Check that user is properly linked to organization
- Verify organization exists

---

## 📝 NOTES

1. **Storage policies use `auth.uid()`** which requires:
   - Users authenticated via Supabase Auth
   - `users` table linked to `auth.users` via `auth_id`
   - Proper RLS on `users` table

2. **Organization-scoped access** requires:
   - `users.organization_id` to be set
   - Policies that check organization_id in path or metadata

3. **Public buckets** (avatars, logos) can be accessed without authentication for viewing, but upload/update/delete still require authentication.

---

**Status**: 📋 **SETUP REQUIRED**  
**Next**: Create buckets in Dashboard, then set up policies

