# Auth Migration: NextAuth.js → Supabase Auth Direct

**Date**: January 2025  
**Status**: ✅ **COMPLETE** - All API routes now use Supabase Auth directly

---

## 🔄 CHANGES MADE

### **1. Updated `omnify-brain/src/lib/auth.ts`**

**Before:** Used NextAuth.js `getServerSession()`  
**After:** Uses Supabase Auth token verification from `Authorization` header

**Key Changes:**
- `getCurrentUser()` now accepts `NextRequest` parameter
- Verifies Supabase Auth access token from `Authorization: Bearer <token>` header
- Fetches user from database using `auth_id` (Supabase Auth user ID)

### **2. Updated All API Routes**

All API routes now pass `request` parameter to auth functions:

```typescript
// Before
const user = await getCurrentUser();

// After
const user = await getCurrentUser(request);
```

**Updated Routes:**
- ✅ `/api/upload/creative`
- ✅ `/api/upload/avatar`
- ✅ `/api/upload/logo`
- ✅ `/api/actions/execute`
- ✅ `/api/brain-cycle`
- ✅ `/api/connectors/*/auth`
- ✅ `/api/connectors/*/sync`

---

## 🔑 HOW IT WORKS NOW

### **Authentication Flow:**

1. **Client logs in via Supabase Auth:**
   ```typescript
   const { data } = await supabase.auth.signInWithPassword({
     email: 'user@example.com',
     password: 'password',
   });
   
   const accessToken = data.session?.access_token;
   ```

2. **Client sends token in API requests:**
   ```typescript
   fetch('/api/upload/creative', {
     headers: {
       'Authorization': `Bearer ${accessToken}`,
     },
     // ...
   });
   ```

3. **Server verifies token:**
   ```typescript
   // In API route
   const user = await getCurrentUser(request);
   // Verifies token with Supabase, fetches user from database
   ```

---

## 📋 TESTING

### **Get Access Token:**

**Method 1: Browser Console**
```javascript
// After login, run in browser console
const storageKey = Object.keys(localStorage).find(key => key.includes('auth-token'));
const tokenData = JSON.parse(localStorage.getItem(storageKey));
console.log('Access Token:', tokenData?.access_token);
```

**Method 2: Direct Login**
```typescript
const { data } = await supabase.auth.signInWithPassword({
  email: 'your-email@example.com',
  password: 'your-password',
});
const accessToken = data.session?.access_token;
```

### **Test API:**

```bash
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123"
```

---

## ⚠️ NOTES

1. **NextAuth.js Still Present:** The NextAuth.js setup is still in the codebase for frontend session management, but API routes now use Supabase Auth directly.

2. **Token Expiration:** Supabase Auth access tokens expire after 1 hour. Use refresh tokens to get new access tokens.

3. **Frontend:** Frontend can still use NextAuth.js for session management, but API calls should use Supabase Auth tokens.

---

## ✅ BENEFITS

1. **No Indirection** - Direct Supabase Auth, no NextAuth.js layer
2. **Standard Bearer Tokens** - Uses `Authorization: Bearer <token>` header
3. **Simpler** - One less dependency to manage
4. **Better for API** - Standard REST API authentication pattern

---

**Status**: ✅ **COMPLETE** - All API routes now use Supabase Auth directly

