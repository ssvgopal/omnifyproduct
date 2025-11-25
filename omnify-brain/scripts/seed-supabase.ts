/**
 * Seed Supabase with Demo Data
 * 
 * Populates Supabase with the $65M Beauty brand demo scenario.
 * 
 * Usage: npx tsx scripts/seed-supabase.ts
 * 
 * Prerequisites:
 * - NEXT_PUBLIC_SUPABASE_URL in .env
 * - SUPABASE_SERVICE_ROLE_KEY in .env
 * - Migration 003 applied
 */

const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('❌ Missing Supabase credentials in .env.local');
  console.error('   Required: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

const SEED_DIR = path.join(process.cwd(), 'src', 'data', 'seeds');

async function seedSupabase() {
  console.log('');
  console.log('🌱 ═══════════════════════════════════════════════════════');
  console.log('   SEEDING SUPABASE WITH DEMO DATA');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('');

  try {
    // 1. Create or get demo organization
    console.log('📦 Step 1: Creating demo organization...');
    const { data: org, error: orgError } = await supabase
      .from('organizations')
      .upsert({
        id: 'org_demo_beauty_65m',
        name: 'Demo Beauty Brand ($65M)',
      }, { onConflict: 'id' })
      .select()
      .single();

    if (orgError) {
      // Try insert if upsert fails
      const { data: existingOrg } = await supabase
        .from('organizations')
        .select()
        .eq('name', 'Demo Beauty Brand ($65M)')
        .single();
      
      if (existingOrg) {
        console.log(`   ✓ Using existing org: ${existingOrg.id}`);
        var organizationId = existingOrg.id;
      } else {
        const { data: newOrg, error: insertError } = await supabase
          .from('organizations')
          .insert({ name: 'Demo Beauty Brand ($65M)' })
          .select()
          .single();
        
        if (insertError) throw insertError;
        console.log(`   ✓ Created org: ${newOrg.id}`);
        var organizationId = newOrg.id;
      }
    } else {
      console.log(`   ✓ Org ready: ${org.id}`);
      var organizationId = org.id;
    }

    // 2. Load seed data from JSON files
    console.log('');
    console.log('📂 Step 2: Loading seed data from JSON files...');
    
    const channels = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'channels.json'), 'utf-8'));
    const campaigns = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'campaigns.json'), 'utf-8'));
    const creatives = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'creatives.json'), 'utf-8'));
    const dailyMetrics = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'daily_metrics.json'), 'utf-8'));
    const creativeDailyMetrics = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'creative_daily_metrics.json'), 'utf-8'));
    const cohorts = JSON.parse(fs.readFileSync(path.join(SEED_DIR, 'cohorts.json'), 'utf-8'));

    console.log(`   ✓ Loaded ${channels.length} channels`);
    console.log(`   ✓ Loaded ${campaigns.length} campaigns`);
    console.log(`   ✓ Loaded ${creatives.length} creatives`);
    console.log(`   ✓ Loaded ${dailyMetrics.length} daily metrics`);
    console.log(`   ✓ Loaded ${creativeDailyMetrics.length} creative daily metrics`);
    console.log(`   ✓ Loaded ${cohorts.length} cohorts`);

    // 3. Insert channels
    console.log('');
    console.log('📊 Step 3: Inserting channels...');
    
    const channelIdMap: Record<string, string> = {};
    
    for (const ch of channels) {
      const { data, error } = await supabase
        .from('channels')
        .upsert({
          organization_id: organizationId,
          name: ch.name,
          platform: ch.platform,
          external_id: ch.id,
          is_active: true,
        }, { onConflict: 'organization_id,name' })
        .select()
        .single();

      if (error) {
        // Try to get existing
        const { data: existing } = await supabase
          .from('channels')
          .select()
          .eq('organization_id', organizationId)
          .eq('name', ch.name)
          .single();
        
        if (existing) {
          channelIdMap[ch.id] = existing.id;
          console.log(`   ✓ ${ch.name}: ${existing.id} (existing)`);
        } else {
          console.error(`   ✗ Failed to insert ${ch.name}:`, error.message);
        }
      } else {
        channelIdMap[ch.id] = data.id;
        console.log(`   ✓ ${ch.name}: ${data.id}`);
      }
    }

    // 4. Insert campaigns
    console.log('');
    console.log('📊 Step 4: Inserting campaigns...');
    
    for (const camp of campaigns) {
      const channelId = channelIdMap[camp.channelId];
      if (!channelId) {
        console.log(`   ⚠ Skipping campaign ${camp.campaignName} - channel not found`);
        continue;
      }

      const { error } = await supabase
        .from('campaigns')
        .upsert({
          organization_id: organizationId,
          channel_id: channelId,
          campaign_id: camp.campaignId,
          campaign_name: camp.campaignName,
          campaign_type: camp.campaignType,
          status: camp.status,
          daily_budget: camp.dailyBudget,
        }, { onConflict: 'organization_id,channel_id,campaign_id' });

      if (error) {
        console.log(`   ⚠ ${camp.campaignName}: ${error.message}`);
      } else {
        console.log(`   ✓ ${camp.campaignName}`);
      }
    }

    // 5. Insert creatives
    console.log('');
    console.log('📊 Step 5: Inserting creatives...');
    
    const creativeIdMap: Record<string, string> = {};
    
    for (const cr of creatives) {
      const channelId = channelIdMap[cr.channelId];
      if (!channelId) {
        console.log(`   ⚠ Skipping creative ${cr.name} - channel not found`);
        continue;
      }

      const { data, error } = await supabase
        .from('creatives')
        .upsert({
          channel_id: channelId,
          name: cr.name,
          external_id: cr.id,
          status: cr.status,
          launch_date: cr.launchDate,
          spend: cr.spend,
          revenue: cr.revenue,
          impressions: cr.impressions,
          clicks: cr.clicks,
          roas: cr.roas,
          ctr: cr.ctr,
        }, { onConflict: 'channel_id,name' })
        .select()
        .single();

      if (error) {
        const { data: existing } = await supabase
          .from('creatives')
          .select()
          .eq('channel_id', channelId)
          .eq('name', cr.name)
          .single();
        
        if (existing) {
          creativeIdMap[cr.id] = existing.id;
          console.log(`   ✓ ${cr.name}: ${existing.id} (existing)`);
        } else {
          console.log(`   ⚠ ${cr.name}: ${error.message}`);
        }
      } else {
        creativeIdMap[cr.id] = data.id;
        console.log(`   ✓ ${cr.name}: ${data.id}`);
      }
    }

    // 6. Insert daily metrics
    console.log('');
    console.log('📊 Step 6: Inserting daily metrics...');
    
    let metricsInserted = 0;
    const metricsToInsert = dailyMetrics.map((dm: any) => ({
      channel_id: channelIdMap[dm.channelId],
      date: dm.date,
      spend: dm.spend,
      revenue: dm.revenue,
      impressions: dm.impressions,
      clicks: dm.clicks,
      conversions: dm.conversions,
      roas: dm.roas,
      cpa: dm.cpa,
      ctr: dm.clicks / dm.impressions,
      frequency: dm.frequency,
      cvr: dm.cvr,
    })).filter((dm: any) => dm.channel_id);

    // Insert in batches
    const batchSize = 50;
    for (let i = 0; i < metricsToInsert.length; i += batchSize) {
      const batch = metricsToInsert.slice(i, i + batchSize);
      const { error } = await supabase
        .from('daily_metrics')
        .upsert(batch, { onConflict: 'channel_id,date' });
      
      if (error) {
        console.log(`   ⚠ Batch ${i}-${i + batchSize}: ${error.message}`);
      } else {
        metricsInserted += batch.length;
      }
    }
    console.log(`   ✓ Inserted ${metricsInserted} daily metrics`);

    // 7. Insert creative daily metrics
    console.log('');
    console.log('📊 Step 7: Inserting creative daily metrics...');
    
    let creativeMetricsInserted = 0;
    const creativeMetricsToInsert = creativeDailyMetrics.map((cdm: any) => ({
      creative_id: creativeIdMap[cdm.creativeId],
      date: cdm.date,
      spend: cdm.spend,
      revenue: cdm.revenue,
      impressions: cdm.impressions,
      clicks: cdm.clicks,
      conversions: cdm.conversions,
      roas: cdm.roas,
      ctr: cdm.ctr,
      cvr: cdm.cvr,
      cpa: cdm.cpa,
      frequency: cdm.frequency,
    })).filter((cdm: any) => cdm.creative_id);

    for (let i = 0; i < creativeMetricsToInsert.length; i += batchSize) {
      const batch = creativeMetricsToInsert.slice(i, i + batchSize);
      const { error } = await supabase
        .from('creative_daily_metrics')
        .upsert(batch, { onConflict: 'creative_id,date' });
      
      if (error) {
        console.log(`   ⚠ Batch ${i}-${i + batchSize}: ${error.message}`);
      } else {
        creativeMetricsInserted += batch.length;
      }
    }
    console.log(`   ✓ Inserted ${creativeMetricsInserted} creative daily metrics`);

    // 8. Insert cohorts
    console.log('');
    console.log('📊 Step 8: Inserting cohorts...');
    
    for (const c of cohorts) {
      const { error } = await supabase
        .from('cohorts')
        .upsert({
          organization_id: organizationId,
          cohort_month: c.cohortMonth,
          acquisition_channel: c.acquisitionChannel,
          customer_count: c.customerCount,
          total_revenue: c.totalRevenue,
          ltv_30d: c.ltv30d,
          ltv_60d: c.ltv60d,
          ltv_90d: c.ltv90d,
          ltv_180d: c.ltv180d,
          avg_order_value: c.avgOrderValue,
          repeat_purchase_rate: c.repeatPurchaseRate,
        }, { onConflict: 'organization_id,cohort_month,acquisition_channel' });

      if (error) {
        console.log(`   ⚠ ${c.cohortMonth} (${c.acquisitionChannel}): ${error.message}`);
      } else {
        console.log(`   ✓ ${c.cohortMonth} (${c.acquisitionChannel})`);
      }
    }

    // Done
    console.log('');
    console.log('═══════════════════════════════════════════════════════════');
    console.log('✅ SUPABASE SEEDING COMPLETE');
    console.log('═══════════════════════════════════════════════════════════');
    console.log(`   Organization ID: ${organizationId}`);
    console.log(`   Channels: ${Object.keys(channelIdMap).length}`);
    console.log(`   Creatives: ${Object.keys(creativeIdMap).length}`);
    console.log(`   Daily Metrics: ${metricsInserted}`);
    console.log(`   Creative Daily Metrics: ${creativeMetricsInserted}`);
    console.log(`   Cohorts: ${cohorts.length}`);
    console.log('');
    console.log('🚀 Next: Run brain cycle with:');
    console.log(`   curl -X POST http://localhost:3000/api/brain-cycle \\`);
    console.log(`     -H "Content-Type: application/json" \\`);
    console.log(`     -d '{"organizationId": "${organizationId}"}'`);
    console.log('');

  } catch (error) {
    console.error('❌ Seeding failed:', error);
    process.exit(1);
  }
}

seedSupabase();
