# Testing Guide - Three-Panel Interface

**Quick start guide to test the three-role system**

---

## 🚀 Step 1: Run Seed Script

In Supabase SQL Editor, run:
```sql
-- File: 002_seed_test_data.sql
-- Copy and paste entire file
```

This creates:
- 3 test organizations
- 6 test users (3 roles)
- Sample data (channels, metrics, brain state)

---

## 👥 Step 2: Test Accounts

### Test Users Created

| Email | Password | Role | Organization | Purpose |
|-------|----------|------|--------------|---------|
| `sarah@demo.com` | `demo` | **user** | Demo Beauty Co | End user - View only |
| `jason@demo.com` | `demo` | **user** | Demo Beauty Co | End user - View only |
| `admin@demo.com` | `demo` | **admin** | Demo Beauty Co | Admin - Manage org |
| `vendor@omnify.ai` | `demo` | **vendor** | None | Super admin - View all |

---

## 🧪 Step 3: Test Each Role

### Start the App
```bash
cd omnify-brain
npm run dev
```

Open: http://localhost:3000

---

### Test 1: USER Role (End User)

**Login**: `sarah@demo.com` / `demo`

**Should See**:
- ✅ Redirected to `/dashboard`
- ✅ Blue-themed Brain dashboard
- ✅ MEMORY, ORACLE, CURIOSITY cards
- ✅ Their company's data only

**Should NOT See**:
- ❌ Cannot access `/admin/*` routes
- ❌ Cannot access `/vendor/*` routes
- ❌ No team management
- ❌ No billing access

**Try accessing**:
- `/dashboard` → ✅ Works
- `/admin/team` → ❌ Redirects to `/dashboard`
- `/vendor/clients` → ❌ Redirects to `/dashboard`

---

### Test 2: ADMIN Role (Organization Admin)

**Login**: `admin@demo.com` / `demo`

**Should See**:
- ✅ Redirected to `/admin` (or `/dashboard`)
- ✅ Purple-themed admin panel
- ✅ Can access user dashboard
- ✅ Team management page
- ✅ Integrations page
- ✅ Billing page
- ✅ Settings page

**Should NOT See**:
- ❌ Cannot access `/vendor/*` routes
- ❌ Cannot see other organizations

**Try accessing**:
- `/dashboard` → ✅ Works (can view dashboard)
- `/admin/team` → ✅ Works (manage team)
- `/admin/integrations` → ✅ Works (connect platforms)
- `/vendor/clients` → ❌ Redirects to `/dashboard`

---

### Test 3: VENDOR Role (Super Admin)

**Login**: `vendor@omnify.ai` / `demo`

**Should See**:
- ✅ Redirected to `/vendor/clients`
- ✅ Dark-themed vendor panel
- ✅ **ALL** organizations listed
- ✅ System monitoring dashboard
- ✅ Can access any route

**Try accessing**:
- `/vendor/clients` → ✅ Works (see all clients)
- `/vendor/monitoring` → ✅ Works (system health)
- `/dashboard` → ✅ Works (can view any org's dashboard)
- `/admin/team` → ✅ Works (can manage any org)

---

## 📋 Verification Checklist

### Route Protection Working?
- [ ] User cannot access `/admin/*`
- [ ] User cannot access `/vendor/*`
- [ ] Admin cannot access `/vendor/*`
- [ ] Vendor can access everything

### Data Isolation Working?
- [ ] User sees only their org's data
- [ ] Admin sees only their org's data
- [ ] Vendor sees all orgs' data

### UI Themes Correct?
- [ ] User dashboard has **blue** accents
- [ ] Admin panel has **purple** accents
- [ ] Vendor panel has **dark** theme

### Session Includes Role?
In browser console:
```javascript
// After login, check session
fetch('/api/auth/session')
  .then(r => r.json())
  .then(console.log)

// Should show: { user: { email, role, organizationId } }
```

---

## 🐛 Troubleshooting

### "Cannot read property 'role'"
**Fix**: Make sure you ran `002_seed_test_data.sql` and users have roles

### "Redirecting to /dashboard in a loop"
**Fix**: Check middleware.ts is correctly checking roles

### "No data displayed"
**Fix**: Make sure seed script created channels and metrics

### "Login fails"
**Fix**: Verify `.env.local` has:
```
NEXT_PUBLIC_SUPABASE_URL=your-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000
```

---

## 🎯 What to Verify

### For Each Role:

1. **Login Success**
   - User can login with test credentials
   - Redirected to appropriate page

2. **Navigation**
   - Sidebar shows correct menu items
   - Links work correctly
   - Active state highlights current page

3. **Data Display**
   - Dashboard shows correct data
   - Numbers make sense
   - No console errors

4. **Route Protection**
   - Unauthorized routes redirect
   - No errors on redirect
   - User stays authenticated

5. **Theme**
   - Correct colors for role
   - Layout looks professional
   - Mobile responsive

---

## ✅ Success Criteria

All these should work:

- [x] Database seeded successfully
- [x] 6 test users created (3 roles)
- [ ] USER can login and view dashboard
- [ ] USER cannot access admin panel
- [ ] ADMIN can login and manage team
- [ ] ADMIN cannot access vendor panel
- [ ] VENDOR can login and see all clients
- [ ] VENDOR can access monitoring page
- [ ] Role-based routing works
- [ ] Data isolation works
- [ ] Themes display correctly

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. **Build remaining pages**:
   - Admin: Team, Integrations, Billing
   - Vendor: Billing, Security, Quotas
   - User: Analytics, Campaigns

2. **Implement OAuth flows**:
   - Meta Ads OAuth
   - Google Ads OAuth
   - TikTok OAuth

3. **Add real password hashing**:
   - Replace `demo` password with bcrypt
   - Implement password reset

4. **Deploy to production**:
   - Vercel deployment
   - Production Supabase
   - Environment variables

---

**Ready to test? Start with Step 1 (run seed script)!** 🎯
