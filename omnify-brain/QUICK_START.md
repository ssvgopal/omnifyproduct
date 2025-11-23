# Quick Start Guide

## 🎯 You Have Two Apps Now!

### 1. **Demo** (MVP - Fully Working)
- **Location**: `demo/` directory
- **Port**: 3001
- **Data**: Static JSON (no database)
- **Status**: ✅ Ready to run

### 2. **Production** (Full SaaS - Needs Setup)
- **Location**: `src/` directory
- **Port**: 3000
- **Data**: Supabase database
- **Status**: ⚙️ Needs configuration

---

## 🚀 Run the Demo (5 minutes)

```bash
# Navigate to demo
cd demo

# Install dependencies
npm install

# Run everything (seed + brain + server)
npm run demo

# Or run steps individually:
npm run seed    # Generate demo data
npm run brain   # Process brain cycle
npm run dev     # Start server
```

**Open**: http://localhost:3001

✅ **Works immediately** - no setup needed!

---

## 🔧 Set Up Production (15 minutes)

### Step 1: Install Dependencies
```bash
# From root directory
npm install
```

### Step 2: Create Supabase Project

1. Go to https://app.supabase.com/
2. Click "New Project"
3. Choose project name (e.g., "omnify-brain")
4. Set password
5. Select region
6. Click "Create"

**Wait 2-3 minutes for provisioning**

### Step 3: Deploy Database Schema

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy contents of: `supabase/migrations/001_initial_schema.sql`
4. Paste and click "Run"

✅ **Schema deployed!**

### Step 4: Get Credentials

In Supabase dashboard, go to **Settings** > **API**:

- Copy **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
- Copy **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Copy **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`

### Step 5: Configure Environment

```bash
# Create environment file
copy .env.example .env.local
# or on Git Bash: cp .env.example .env.local
```

Edit `.env.local`:
```bash
# Supabase (paste from Step 4)
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# NextAuth (generate secret)
NEXTAUTH_SECRET=run_this_in_terminal_to_generate
NEXTAUTH_URL=http://localhost:3000
```

**Generate NextAuth secret**:
```bash
# Git Bash / Linux / Mac
openssl rand -base64 32

# Windows PowerShell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

Paste the result into `NEXTAUTH_SECRET`

### Step 6: Seed Production Data

Create `scripts/seed-production.ts`:
```typescript
import { supabaseAdmin } from '../src/lib/db/supabase';

async function seedProduction() {
  console.log('🌱 Seeding production data...');

  // 1. Create organization
  const { data: org } = await supabaseAdmin
    .from('organizations')
    .insert({ name: 'Demo Beauty Co' })
    .select()
    .single();

  console.log('✅ Organization created:', org.name);

  // 2. Create users
  const users = [
    { email: 'sarah@demo.com', role: 'admin' },
    { email: 'jason@demo.com', role: 'member' },
    { email: 'emily@demo.com', role: 'member' },
  ];

  for (const user of users) {
    await supabaseAdmin.from('users').insert({
      ...user,
      organization_id: org.id,
    });
  }
  console.log('✅ Users created');

  // 3. Create channels
  const channels = [
    { name: 'Meta Ads', platform: 'Meta', external_id: 'act_123' },
    { name: 'Google Ads', platform: 'Google', external_id: 'cust_456' },
    { name: 'TikTok Ads', platform: 'TikTok', external_id: 'adv_789' },
  ];

  const channelRecords = [];
  for (const channel of channels) {
    const { data } = await supabaseAdmin
      .from('channels')
      .insert({ ...channel, organization_id: org.id })
      .select()
      .single();
    channelRecords.push(data);
  }
  console.log('✅ Channels created');

  // 4. Generate metrics (90 days)
  const metrics = [];
  for (let i = 90; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    
    for (const channel of channelRecords) {
      const spend = Math.random() * 2000 + 500;
      const roas = Math.random() * 2 + 1.5;
      
      metrics.push({
        channel_id: channel.id,
        date: date.toISOString().split('T')[0],
        spend: Math.round(spend),
        revenue: Math.round(spend * roas),
        impressions: Math.floor(Math.random() * 100000),
        clicks: Math.floor(Math.random() * 5000),
        conversions: Math.floor(Math.random() * 100),
        roas: parseFloat(roas.toFixed(2)),
      });
    }
  }

  await supabaseAdmin.from('daily_metrics').insert(metrics);
  console.log('✅ Metrics seeded (90 days)');

  console.log('🎉 Production data seeded successfully!');
}

seedProduction().catch(console.error);
```

Run it:
```bash
npx tsx scripts/seed-production.ts
```

### Step 7: Run Production

```bash
npm run dev
```

**Open**: http://localhost:3000

#### Test Login
1. Click "Get Started"
2. Login with:
   - Email: `sarah@demo.com`
   - Password: `demo`
3. See your production dashboard! 🎉

---

## 📊 Verify Everything Works

### Demo Checklist
- [ ] Opens at http://localhost:3001
- [ ] Shows 3-column dashboard
- [ ] Displays MEMORY, ORACLE, CURIOSITY
- [ ] Persona toggle works
- [ ] All cards show data

### Production Checklist
- [ ] Opens at http://localhost:3000
- [ ] Landing page loads
- [ ] Can navigate to login
- [ ] Can log in with sarah@demo.com / demo
- [ ] Dashboard shows real data from Supabase
- [ ] Can click refresh button
- [ ] Loading states work

---

## 🐛 Troubleshooting

### "Cannot find module 'swr'"
**Fix**: Run `npm install` in root directory

### "Invalid credentials"
**Fix**: Check `.env.local` has correct Supabase keys

### "Failed to fetch brain state"
**Fix**: Ensure seed script ran successfully, check Supabase dashboard for data

### "Middleware error"
**Fix**: Ensure `NEXTAUTH_SECRET` is set in `.env.local`

### Demo won't start
**Fix**: 
```bash
cd demo
rm -rf node_modules .next
npm install
npm run demo
```

---

## 📂 Project Structure

```
omnify-brain/
├── demo/                    # MVP Demo (Port 3001)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── scripts/
│   └── package.json
│
├── src/                     # Production (Port 3000)
│   ├── app/
│   │   ├── (auth)/         # Login
│   │   ├── (dashboard)/    # Dashboard
│   │   └── api/            # API routes
│   ├── components/
│   ├── lib/
│   └── middleware.ts
│
├── supabase/               # Database
│   └── migrations/
│
├── package.json            # Production deps
├── .env.local             # Your config (create this)
└── .env.example           # Template
```

---

## 🎯 What's Next?

After you have both running, see:
- **PRODUCTION_PLAN.md** - Full 6-week roadmap
- **GAP_CLOSURE_CHECKLIST.md** - Remaining features
- **IMPLEMENTATION_COMPLETE.md** - What's been built

### Phase 2: Platform Integrations
- OAuth flows for Meta/Google/TikTok
- Manual sync UI
- Scheduled syncs

### Phase 3: AI Integration
- OpenAI-powered creative fatigue
- Anthropic-powered recommendations

### Phase 4: Polish
- Historical charts
- Mobile responsive
- Export functionality

---

## 💡 Tips

- **Demo** is always safe to experiment with
- **Production** connects to real database
- Both can run simultaneously (different ports)
- Changes to demo don't affect production

---

## 🚨 Important Notes

### Security
- Current password is hardcoded (`demo`)
- **MUST** implement proper hashing before production
- See line 30 in `src/app/api/auth/[...nextauth]/route.ts`

### Costs
- Supabase: Free tier (500 MB database)
- Vercel: Free tier (hobby projects)
- No API costs until you add Meta/Google/TikTok

---

## 📞 Need Help?

Check the documentation:
1. **IMPLEMENTATION_COMPLETE.md** - What's been built
2. **PRODUCTION_PLAN.md** - Full roadmap
3. **GAP_CLOSURE_CHECKLIST.md** - Remaining work

**Ready to start?** Run the demo first, then set up production! 🚀
