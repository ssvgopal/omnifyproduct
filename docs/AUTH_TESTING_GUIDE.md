# Auth Testing Guide - Supabase Auth Direct

**Date**: January 2025  
**Purpose**: Step-by-step guide to test the Supabase Auth migration

---

## ✅ COMMIT CREATED

**Commit**: `refactor: Migrate API routes from NextAuth.js to Supabase Auth direct`

**Files Changed:**
- `omnify-brain/src/lib/auth.ts` - Now uses Supabase Auth directly
- All API routes (14 files) - Updated to pass `request` parameter
- Documentation added

---

## 🧪 TESTING STEPS

### **Step 1: Verify Build**

```bash
cd omnify-brain
npm run build
```

**Expected:** Build succeeds with no TypeScript errors

---

### **Step 2: Get Supabase Auth Token**

**Option A: Browser Console (After Login)**

1. Start dev server: `npm run dev`
2. Navigate to `http://localhost:3000/login`
3. Login with your credentials
4. Open browser console (F12)
5. Run:

```javascript
// Get Supabase Auth token
const storageKey = Object.keys(localStorage).find(key => key.includes('auth-token'));
if (storageKey) {
  const tokenData = JSON.parse(localStorage.getItem(storageKey));
  console.log('Access Token:', tokenData?.access_token);
  // Copy this token
}
```

**Option B: Direct Login (Programmatic)**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

const { data, error } = await supabase.auth.signInWithPassword({
  email: 'your-email@example.com',
  password: 'your-password',
});

if (error) {
  console.error('Login error:', error);
} else {
  console.log('Access Token:', data.session?.access_token);
}
```

---

### **Step 3: Test API Endpoint**

**Test Upload Endpoint:**

```bash
# Replace YOUR_ACCESS_TOKEN with token from Step 2
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123" \
  -v
```

**Expected Response:**
```json
{
  "success": true,
  "path": "org-id/creatives/test-123.jpg",
  "url": "https://...signed-url...",
  "size": 12345,
  "type": "image/jpeg"
}
```

**Error Cases to Test:**

1. **No Token:**
   ```bash
   curl -X POST http://localhost:3000/api/upload/creative \
     -F "file=@test.jpg"
   ```
   **Expected:** `401 Unauthorized`

2. **Invalid Token:**
   ```bash
   curl -X POST http://localhost:3000/api/upload/creative \
     -H "Authorization: Bearer invalid-token" \
     -F "file=@test.jpg"
   ```
   **Expected:** `401 Unauthorized`

3. **Expired Token:**
   - Wait 1 hour (or use expired token)
   **Expected:** `401 Unauthorized`

---

### **Step 4: Test Other Endpoints**

**Test Brain Cycle:**
```bash
curl -X POST http://localhost:3000/api/brain-cycle \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -v
```

**Test Action Execution:**
```bash
curl -X POST http://localhost:3000/api/actions/execute \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actionType": "pause_creative",
    "targetId": "creative-123",
    "targetType": "creative"
  }' \
  -v
```

---

## 🔍 VERIFICATION CHECKLIST

- [ ] Build succeeds (`npm run build`)
- [ ] No TypeScript errors
- [ ] Can get access token from browser/localStorage
- [ ] API accepts `Authorization: Bearer <token>` header
- [ ] API returns `401` for missing token
- [ ] API returns `401` for invalid token
- [ ] API returns `200` for valid token
- [ ] User data fetched correctly from database

---

## 🐛 TROUBLESHOOTING

### **Error: "Unauthorized" even with valid token**

**Check:**
1. Token is not expired (Supabase tokens expire after 1 hour)
2. User exists in `users` table with `auth_id` matching Supabase Auth user ID
3. `auth_id` column exists in `users` table (run migration `003_add_auth_id.sql`)

### **Error: "User not found in database"**

**Solution:**
- Ensure user record exists in `users` table
- Ensure `auth_id` column is populated with Supabase Auth user ID
- Check that `users.auth_id = auth.users.id`

### **Error: TypeScript compilation errors**

**Solution:**
- Check that all API routes pass `request` parameter to `getCurrentUser(request)`
- Verify `auth.ts` exports are correct

---

## ✅ SUCCESS CRITERIA

1. ✅ Build succeeds
2. ✅ Can authenticate with Supabase Auth token
3. ✅ API routes accept `Authorization: Bearer <token>` header
4. ✅ User data fetched correctly
5. ✅ All API routes work with new auth system

---

**Status**: ✅ **READY FOR TESTING**




