// Load environment variables from .env.local FIRST
// Using require to ensure synchronous execution before any imports
const { config } = require('dotenv');
const { resolve } = require('path');

// Load .env.local from root directory
const result = config({ path: resolve(process.cwd(), '.env.local') });

if (result.error) {
  console.error('❌ Error loading .env.local:', result.error);
  process.exit(1);
}

// Verify required environment variables are loaded
if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
  console.error('❌ NEXT_PUBLIC_SUPABASE_URL is required but not found in .env.local');
  process.exit(1);
}

if (!process.env.SUPABASE_SERVICE_ROLE_KEY) {
  console.error('❌ SUPABASE_SERVICE_ROLE_KEY is required but not found in .env.local');
  process.exit(1);
}

// Create Supabase client directly here to avoid module load-time env var access
// Use the package from omnify-brain's node_modules
const supabasePath = resolve(process.cwd(), 'omnify-brain/node_modules/@supabase/supabase-js');
const { createClient } = require(supabasePath);

const supabaseAdmin = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!,
  {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  }
);

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
  // Valid roles: 'user', 'admin', 'vendor' (from migration 002)
  const users = [
    { email: 'sarah@demo.com', role: 'admin' },
    { email: 'jason@demo.com', role: 'user' },
    { email: 'emily@demo.com', role: 'user' },
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
