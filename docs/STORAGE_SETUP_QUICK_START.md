# Storage Setup Quick Start

**Problem**: "must be owner of relation objects" error when running migration

**Solution**: Create buckets and policies through Supabase Dashboard

---

## ⚡ QUICK FIX (5 Minutes)

### **Step 1: Create Buckets**

1. Go to **Supabase Dashboard** → **Storage**
2. Click **"New Bucket"** for each:

   | Bucket | Public? |
   |--------|---------|
   | `creatives` | ❌ No (Private) |
   | `avatars` | ❌ No (Private) |
   | `logos` | ❌ No (Private) |
   | `exports` | ❌ No (Private) |

### **Step 2: Set Up Policies (Simplified)**

**Option A: Use Simple Policies (Recommended for MVP)**

Run `007a_storage_policies_simple.sql` in Supabase SQL Editor.

**Option B: Use Dashboard UI**

1. Go to **Storage** → Select bucket → **"Policies"** tab
2. Click **"New Policy"**
3. Use templates from `docs/STORAGE_SETUP_GUIDE.md`

### **Step 3: Add Organization Checks in Code**

Since simplified policies don't enforce organization scoping, add checks in your upload routes:

```typescript
// In upload routes, verify organizationId matches user's org
if (organizationId !== user.organizationId) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 403 });
}
```

---

## ✅ VERIFICATION

Test upload:
```bash
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123"
```

---

**Status**: ✅ **READY** - All buckets are private. Use signed URLs for access.

**Security Note:** All buckets are private for better security. Use `getSignedUrl()` to generate temporary access URLs for authenticated users.

