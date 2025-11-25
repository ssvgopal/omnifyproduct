# How to Get Bearer Token for API Testing

**Date**: January 2025  
**Purpose**: Guide for getting Supabase Auth tokens to test API endpoints

---

## 🔑 OVERVIEW

We're using **Supabase Auth** directly. The bearer token is the **Supabase Auth access token**.

---

## 📋 METHOD 1: Get Token from Browser (Easiest)

### **Step 1: Login via Browser**

1. Start dev server:
   ```bash
   cd omnify-brain
   npm run dev
   ```

2. Navigate to: `http://localhost:3000/login`

3. Login with your credentials (uses Supabase Auth)

### **Step 2: Get Token from Browser**

**Option A: Chrome DevTools - Local Storage**

1. Open Chrome DevTools (F12)
2. Go to **Application** tab → **Local Storage** → `http://localhost:3000`
3. Find key: `sb-<project-ref>-auth-token`
4. Copy the **Value** (it's a JSON string)
5. Parse it and extract `access_token`:

```javascript
// Run in browser console
const tokenData = JSON.parse(localStorage.getItem('sb-<project-ref>-auth-token'));
const accessToken = tokenData?.access_token;
console.log(accessToken);
```

**Option B: Browser Console (Quick Script)**

```javascript
// Run in browser console (on any page after login)
// Replace <project-ref> with your Supabase project reference
const storageKey = Object.keys(localStorage).find(key => key.includes('auth-token'));
if (storageKey) {
  const tokenData = JSON.parse(localStorage.getItem(storageKey));
  console.log('Access Token:', tokenData?.access_token);
  console.log('Refresh Token:', tokenData?.refresh_token);
}
```

**Option C: Network Tab**

1. Open DevTools → **Network** tab
2. Make any API request (e.g., navigate to dashboard)
3. Find the request → **Headers** → Look for `Authorization` header
4. Extract the token after `Bearer `

---

## 📋 METHOD 2: Get Token Programmatically (Client-Side)

### **Create a Test Page or Use Browser Console**

**Option A: Browser Console Script**

```javascript
// Run in browser console after login
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
);

// Get current session
const { data: { session } } = await supabase.auth.getSession();
console.log('Access Token:', session?.access_token);
console.log('Refresh Token:', session?.refresh_token);
```

**Option B: Create Test API Route**

Create `omnify-brain/src/app/api/test-token/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  
  if (!authHeader?.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Missing or invalid authorization header' }, { status: 401 });
  }

  const token = authHeader.substring(7);
  
  // Verify token with Supabase
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) {
    return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
  }

  return NextResponse.json({
    user: user,
    message: 'Token is valid',
  });
}
```

Then call: `GET http://localhost:3000/api/test-token` with `Authorization: Bearer YOUR_TOKEN`

---

## 📋 METHOD 3: Login via Supabase Auth (Direct)

### **Step 1: Login and Get Token**

**Using Supabase Client (JavaScript/TypeScript):**

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'your-email@example.com',
  password: 'your-password',
});

if (error) {
  console.error('Login error:', error);
} else {
  // Get access token
  const accessToken = data.session?.access_token;
  console.log('Access Token:', accessToken);
  
  // Use this token in API requests
}
```

**Using cURL (Direct API Call):**

```bash
# Login and get token
curl -X POST 'https://<project-ref>.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: YOUR_SUPABASE_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# Response will contain: { "access_token": "...", "refresh_token": "..." }
```

### **Step 2: Use Token in API Requests**

```bash
# Use the access_token from above
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123"
```

---

## 🧪 TESTING WITH CURL

### **Step 1: Get Token**

Use Method 1 (Browser) or Method 3 (Direct Login) to get the Supabase Auth access token.

### **Step 2: Use Token in Request**

**Use Authorization Header:**

```bash
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123"
```

**Note:** Your API routes should verify the Supabase Auth token from the `Authorization` header.

---

## 🔧 UPDATE API ROUTES TO USE SUPABASE AUTH

Your API routes should verify Supabase Auth tokens. Update them like this:

```typescript
// In your API route
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST(request: NextRequest) {
  // Get token from Authorization header
  const authHeader = request.headers.get('authorization');
  
  if (!authHeader?.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = authHeader.substring(7);
  
  // Verify token with Supabase
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const { data: { user }, error } = await supabase.auth.getUser(token);

  if (error || !user) {
    return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
  }

  // Get user from your users table
  const { data: dbUser } = await supabase
    .from('users')
    .select('*, organization:organizations(*)')
    .eq('auth_id', user.id)
    .single();

  if (!dbUser) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  // Use dbUser for the rest of your logic
  // ...
}
```

---

## ✅ RECOMMENDED APPROACH

**For Testing:**

1. **Login via Browser** (Method 1) - Easiest
2. **Get access token from Local Storage** (browser console)
3. **Use it in curl with Authorization header:**

```bash
# Get token from browser (run in console)
# const tokenData = JSON.parse(localStorage.getItem('sb-<project-ref>-auth-token'));
# const accessToken = tokenData?.access_token;

# Test upload
TOKEN="your-supabase-access-token-here"

curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123"
```

---

## 🎯 QUICK TEST SCRIPT

Create `test-upload.sh`:

```bash
#!/bin/bash

# Get token from environment or prompt
TOKEN=${SUPABASE_ACCESS_TOKEN:-""}

if [ -z "$TOKEN" ]; then
  echo "Please set SUPABASE_ACCESS_TOKEN environment variable"
  echo "Get it from browser: Application → Local Storage → sb-<project-ref>-auth-token → access_token"
  echo "Or login via: supabase.auth.signInWithPassword() and get data.session.access_token"
  exit 1
fi

# Test upload
curl -X POST http://localhost:3000/api/upload/creative \
  -H "Authorization: Bearer ${TOKEN}" \
  -F "file=@test.jpg" \
  -F "creativeId=test-123" \
  -v
```

Run:
```bash
export SUPABASE_ACCESS_TOKEN="your-access-token-here"
bash test-upload.sh
```

---

## 📝 NOTES

1. **Supabase Auth tokens expire** - Access tokens expire after 1 hour, refresh tokens last longer
2. **Tokens are JWT** - They contain user info (id, email, etc.)
3. **Authorization header** - Use `Authorization: Bearer <token>` for API requests
4. **Refresh tokens** - Use refresh token to get new access token when it expires

## 🔄 REFRESHING TOKENS

If your access token expires:

```typescript
const { data, error } = await supabase.auth.refreshSession({
  refresh_token: refreshToken
});

const newAccessToken = data.session?.access_token;
```

---

**Status**: ✅ **READY** - Use browser DevTools to get Supabase Auth access token, then use in curl with Authorization header

