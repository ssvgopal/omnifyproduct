# Omnify Brain - Deployment Guide

## Prerequisites

- Node.js 18+
- Supabase project (with migrations applied)
- Vercel account (or other hosting)
- OAuth credentials (Google, Meta)

---

## Environment Variables

### Required

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# NextAuth
NEXTAUTH_URL=https://your-domain.vercel.app
NEXTAUTH_SECRET=your-random-secret-32-chars-min

# Google OAuth (for login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Optional (for full functionality)

```bash
# Meta Ads Connector
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret

# Google Ads Connector (separate from OAuth)
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token

# Cron Security
CRON_SECRET=your-cron-secret
```

---

## Deployment Steps

### 1. Prepare Supabase

```bash
# Apply all migrations
cd supabase
supabase db push

# Or apply individually
supabase migration up
```

### 2. Deploy to Vercel

#### Option A: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add NEXTAUTH_URL
vercel env add NEXTAUTH_SECRET
vercel env add GOOGLE_CLIENT_ID
vercel env add GOOGLE_CLIENT_SECRET

# Deploy to production
vercel --prod
```

#### Option B: Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Import Git Repository
3. Select `omnify-brain` repo
4. Add environment variables in Settings
5. Deploy

### 3. Configure OAuth Redirect URLs

#### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to APIs & Services > Credentials
3. Edit your OAuth 2.0 Client
4. Add authorized redirect URI:
   ```
   https://your-domain.vercel.app/api/auth/callback/google
   ```

#### Meta OAuth
1. Go to [Meta for Developers](https://developers.facebook.com)
2. Select your app
3. Add OAuth redirect URI:
   ```
   https://your-domain.vercel.app/api/connectors/meta/callback
   ```

### 4. Verify Deployment

```bash
# Run E2E tests
npx tsx scripts/e2e-test.ts

# Or manually test
curl https://your-domain.vercel.app/api/brain-state
```

---

## Cron Job Setup

The daily sync cron is configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/daily-sync",
      "schedule": "0 6 * * *"
    }
  ]
}
```

This runs at 6 AM UTC daily. The cron endpoint requires a `CRON_SECRET` for security.

---

## Post-Deployment Checklist

- [ ] Verify login works (email + Google)
- [ ] Test signup flow
- [ ] Complete onboarding wizard
- [ ] Connect at least one ad platform
- [ ] Verify brain cycle runs
- [ ] Check dashboard displays data
- [ ] Test action execution
- [ ] Verify cron job runs (check Vercel logs)

---

## Troubleshooting

### "Unauthorized" errors
- Check `SUPABASE_SERVICE_ROLE_KEY` is set correctly
- Verify `NEXTAUTH_SECRET` matches across environments

### OAuth redirect errors
- Ensure redirect URIs match exactly (including trailing slashes)
- Check OAuth credentials are for correct environment

### Brain cycle fails
- Check Supabase connection
- Verify migrations are applied
- Check for RLS policy issues

### Cron not running
- Verify `CRON_SECRET` is set
- Check Vercel cron logs in dashboard
- Ensure cron is enabled for your Vercel plan

---

## Monitoring

### Vercel Logs
```bash
vercel logs --follow
```

### Supabase Logs
Check Supabase dashboard > Logs

### Error Tracking
Consider adding:
- Sentry for error tracking
- Vercel Analytics for performance

---

## Rollback

```bash
# List deployments
vercel ls

# Rollback to previous
vercel rollback
```

---

## Local Development

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Run development server
npm run dev

# Run tests
npx tsx scripts/e2e-test.ts
```

---

## Security Notes

1. **Never commit `.env` files** - Use Vercel environment variables
2. **Rotate secrets regularly** - Especially `NEXTAUTH_SECRET`
3. **Use HTTPS only** - Vercel provides this by default
4. **Enable RLS** - All Supabase tables have RLS policies
5. **Audit OAuth scopes** - Only request necessary permissions
