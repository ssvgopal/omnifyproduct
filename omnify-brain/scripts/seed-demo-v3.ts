/**
 * Seed Demo Data V3 - Requirements V3 Compliant
 * 
 * Creates demo data matching the $65M Beauty brand scenario:
 * - Meta: Hero channel (ROAS 3.5-3.8)
 * - Google: Solid performer (ROAS 2.2-2.5)
 * - TikTok: Problem child (ROAS 1.9-2.8, declining)
 * - Creative C12: CVR declining from 0.08 to 0.05 over 14 days
 * - Cohorts: LTV drift pattern (128 → 119 → 115 → 112)
 * 
 * Usage: npx tsx scripts/seed-demo-v3.ts
 */

const fs = require('fs');
const path = require('path');

// Type definitions inline to avoid module resolution issues
interface ChannelData {
  id: string;
  name: string;
  platform: string;
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  cpa: number;
  ctr: number;
}

interface CampaignData {
  id: string;
  channelId: string;
  campaignId: string;
  campaignName: string;
  campaignType: string;
  status: string;
  dailyBudget: number;
}

interface CreativeData {
  id: string;
  name: string;
  channelId: string;
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  ctr: number;
  roas: number;
  status: string;
  launchDate: string;
}

interface DailyMetricExtended {
  date: string;
  channelId: string;
  spend: number;
  revenue: number;
  roas: number;
  status: string;
  impressions: number;
  clicks: number;
  conversions: number;
  frequency: number;
  cvr: number;
  cpa: number;
}

interface CreativeDailyMetric {
  id: string;
  creativeId: string;
  date: string;
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  ctr: number;
  cvr: number;
  cpa: number;
  frequency: number;
}

interface CohortData {
  id: string;
  cohortMonth: string;
  acquisitionChannel: string;
  customerCount: number;
  totalRevenue: number;
  ltv30d: number;
  ltv60d: number;
  ltv90d: number;
  ltv180d?: number;
  avgOrderValue: number;
  repeatPurchaseRate: number;
}

// Configuration
const DATA_DIR = path.join(process.cwd(), 'src', 'data', 'seeds');
const DAYS_TO_GENERATE = 30;
const ORG_ID = 'org_demo_beauty_65m';

// Ensure directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Helper functions
const noise = (val: number, percent: number) => val * (1 + (Math.random() * percent * 2 - percent));
const round = (val: number, decimals: number) => Number(val.toFixed(decimals));

// ============================================
// 1. CHANNELS - $65M Beauty Brand Scenario
// ============================================
const channels: ChannelData[] = [
  {
    id: 'ch_meta',
    name: 'Meta Ads',
    platform: 'Meta',
    spend: 0,
    revenue: 0,
    impressions: 0,
    clicks: 0,
    conversions: 0,
    roas: 3.65, // Hero channel
    cpa: 28,
    ctr: 0.018
  },
  {
    id: 'ch_google',
    name: 'Google Ads',
    platform: 'Google',
    spend: 0,
    revenue: 0,
    impressions: 0,
    clicks: 0,
    conversions: 0,
    roas: 2.35, // Solid performer
    cpa: 42,
    ctr: 0.032
  },
  {
    id: 'ch_tiktok',
    name: 'TikTok Ads',
    platform: 'TikTok',
    spend: 0,
    revenue: 0,
    impressions: 0,
    clicks: 0,
    conversions: 0,
    roas: 2.1, // Problem child (declining)
    cpa: 48,
    ctr: 0.012
  }
];

// ============================================
// 2. CAMPAIGNS
// ============================================
const campaigns: CampaignData[] = [
  // Meta campaigns
  {
    id: 'camp_meta_prospecting',
    channelId: 'ch_meta',
    campaignId: 'meta_23851234567890',
    campaignName: 'Meta - Prospecting - LAL',
    campaignType: 'prospecting',
    status: 'active',
    dailyBudget: 2500,
  },
  {
    id: 'camp_meta_retargeting',
    channelId: 'ch_meta',
    campaignId: 'meta_23851234567891',
    campaignName: 'Meta - Retargeting - Website Visitors',
    campaignType: 'retargeting',
    status: 'active',
    dailyBudget: 1500,
  },
  // Google campaigns
  {
    id: 'camp_google_search',
    channelId: 'ch_google',
    campaignId: 'google_12345678901',
    campaignName: 'Google - Search - Brand',
    campaignType: 'brand',
    status: 'active',
    dailyBudget: 800,
  },
  {
    id: 'camp_google_pmax',
    channelId: 'ch_google',
    campaignId: 'google_12345678902',
    campaignName: 'Google - PMax - All Products',
    campaignType: 'conversion',
    status: 'active',
    dailyBudget: 1200,
  },
  // TikTok campaigns
  {
    id: 'camp_tiktok_spark',
    channelId: 'ch_tiktok',
    campaignId: 'tiktok_7891234567890',
    campaignName: 'TikTok - Spark Ads - UGC',
    campaignType: 'prospecting',
    status: 'active',
    dailyBudget: 1800,
  },
];

// ============================================
// 3. CREATIVES (Including C12 with fatigue pattern)
// ============================================
const creatives: CreativeData[] = [
  // Meta creatives
  {
    id: 'cr_c12',
    name: 'Creative C12 - UGC Testimonial',
    channelId: 'ch_meta',
    spend: 15000,
    revenue: 28500,
    impressions: 450000,
    clicks: 8100,
    ctr: 0.018,
    roas: 1.9, // Current (fatigued)
    status: 'active',
    launchDate: '2024-10-15'
  },
  {
    id: 'cr_c13',
    name: 'Creative C13 - Product Demo',
    channelId: 'ch_meta',
    spend: 12000,
    revenue: 45600,
    impressions: 380000,
    clicks: 7220,
    ctr: 0.019,
    roas: 3.8,
    status: 'active',
    launchDate: '2024-11-01'
  },
  {
    id: 'cr_c14',
    name: 'Creative C14 - Before/After',
    channelId: 'ch_meta',
    spend: 8000,
    revenue: 30400,
    impressions: 250000,
    clicks: 4750,
    ctr: 0.019,
    roas: 3.8,
    status: 'active',
    launchDate: '2024-11-15'
  },
  // Google creatives
  {
    id: 'cr_g01',
    name: 'Google - RSA - Brand Terms',
    channelId: 'ch_google',
    spend: 6000,
    revenue: 15000,
    impressions: 120000,
    clicks: 3840,
    ctr: 0.032,
    roas: 2.5,
    status: 'active',
    launchDate: '2024-09-01'
  },
  // TikTok creatives
  {
    id: 'cr_t01',
    name: 'TikTok - Trend Dance #1',
    channelId: 'ch_tiktok',
    spend: 9000,
    revenue: 16200,
    impressions: 800000,
    clicks: 9600,
    ctr: 0.012,
    roas: 1.8,
    status: 'active',
    launchDate: '2024-10-01'
  },
  {
    id: 'cr_t02',
    name: 'TikTok - GRWM Routine',
    channelId: 'ch_tiktok',
    spend: 7500,
    revenue: 15750,
    impressions: 650000,
    clicks: 7800,
    ctr: 0.012,
    roas: 2.1,
    status: 'active',
    launchDate: '2024-10-20'
  },
];

// ============================================
// 4. DAILY METRICS (30 days with patterns)
// ============================================
const dailyMetrics: DailyMetricExtended[] = [];
const today = new Date();

for (let i = DAYS_TO_GENERATE; i >= 0; i--) {
  const date = new Date(today);
  date.setDate(today.getDate() - i);
  const dateStr = date.toISOString().split('T')[0];

  // Meta (Hero - stable high performance)
  const metaSpend = noise(4000, 0.08);
  const metaRoas = noise(3.65, 0.05); // 3.5-3.8 range
  const metaRev = metaSpend * metaRoas;
  const metaClicks = Math.round(noise(280, 0.1));
  const metaConversions = Math.round(noise(45, 0.1));
  const metaCvr = metaConversions / metaClicks;

  dailyMetrics.push({
    date: dateStr,
    channelId: 'ch_meta',
    spend: round(metaSpend, 2),
    revenue: round(metaRev, 2),
    roas: round(metaRoas, 2),
    status: 'winner',
    impressions: Math.round(noise(150000, 0.1)),
    clicks: metaClicks,
    conversions: metaConversions,
    frequency: round(noise(2.1, 0.1), 2),
    cvr: round(metaCvr, 4),
    cpa: round(metaSpend / metaConversions, 2),
  });

  // Google (Solid - stable medium performance)
  const googleSpend = noise(2000, 0.05);
  const googleRoas = noise(2.35, 0.06); // 2.2-2.5 range
  const googleRev = googleSpend * googleRoas;
  const googleClicks = Math.round(noise(180, 0.08));
  const googleConversions = Math.round(noise(28, 0.08));
  const googleCvr = googleConversions / googleClicks;

  dailyMetrics.push({
    date: dateStr,
    channelId: 'ch_google',
    spend: round(googleSpend, 2),
    revenue: round(googleRev, 2),
    roas: round(googleRoas, 2),
    status: 'neutral',
    impressions: Math.round(noise(60000, 0.08)),
    clicks: googleClicks,
    conversions: googleConversions,
    frequency: round(noise(1.8, 0.1), 2),
    cvr: round(googleCvr, 4),
    cpa: round(googleSpend / googleConversions, 2),
  });

  // TikTok (Problem child - declining ROAS)
  let tiktokSpend = noise(1800, 0.1);
  let tiktokBaseRoas = 2.8; // Started at 2.8

  // Decay pattern: ROAS declining from 2.8 to 1.9 over 14 days
  if (i < 14) {
    const decayFactor = (14 - i) / 14; // 0 to 1 over 14 days
    tiktokBaseRoas = 2.8 - (decayFactor * 0.9); // 2.8 → 1.9
  }
  
  const tiktokRoas = noise(tiktokBaseRoas, 0.08);
  const tiktokRev = tiktokSpend * tiktokRoas;
  const tiktokClicks = Math.round(noise(220, 0.12));
  const tiktokConversions = Math.round(noise(22, 0.15));
  const tiktokCvr = tiktokConversions / tiktokClicks;

  dailyMetrics.push({
    date: dateStr,
    channelId: 'ch_tiktok',
    spend: round(tiktokSpend, 2),
    revenue: round(tiktokRev, 2),
    roas: round(tiktokRoas, 2),
    status: tiktokRoas < 2.0 ? 'loser' : 'neutral',
    impressions: Math.round(noise(280000, 0.12)),
    clicks: tiktokClicks,
    conversions: tiktokConversions,
    frequency: round(noise(3.2, 0.15), 2), // Higher frequency
    cvr: round(tiktokCvr, 4),
    cpa: round(tiktokSpend / tiktokConversions, 2),
  });
}

// ============================================
// 5. CREATIVE DAILY METRICS (C12 fatigue pattern)
// ============================================
const creativeDailyMetrics: CreativeDailyMetric[] = [];

for (let i = DAYS_TO_GENERATE; i >= 0; i--) {
  const date = new Date(today);
  date.setDate(today.getDate() - i);
  const dateStr = date.toISOString().split('T')[0];

  // Creative C12 - Fatigue pattern: CVR declining 0.08 → 0.05 over 14 days
  let c12BaseCvr = 0.08;
  let c12BaseCpa = 25;
  let c12Frequency = 2.5;

  if (i < 14) {
    const fatigueFactor = (14 - i) / 14; // 0 to 1 over 14 days
    c12BaseCvr = 0.08 - (fatigueFactor * 0.03); // 0.08 → 0.05
    c12BaseCpa = 25 + (fatigueFactor * 15); // 25 → 40
    c12Frequency = 2.5 + (fatigueFactor * 1.5); // 2.5 → 4.0
  }

  const c12Spend = noise(500, 0.1);
  const c12Impressions = Math.round(noise(15000, 0.1));
  const c12Clicks = Math.round(c12Impressions * noise(0.018, 0.1));
  const c12Cvr = noise(c12BaseCvr, 0.1);
  const c12Conversions = Math.round(c12Clicks * c12Cvr);
  const c12Revenue = c12Conversions * noise(95, 0.1); // AOV ~$95
  const c12Roas = c12Spend > 0 ? c12Revenue / c12Spend : 0;

  creativeDailyMetrics.push({
    id: `cdm_c12_${dateStr}`,
    creativeId: 'cr_c12',
    date: dateStr,
    spend: round(c12Spend, 2),
    revenue: round(c12Revenue, 2),
    impressions: c12Impressions,
    clicks: c12Clicks,
    conversions: c12Conversions,
    roas: round(c12Roas, 4),
    ctr: round(c12Clicks / c12Impressions, 6),
    cvr: round(c12Cvr, 6),
    cpa: round(c12Spend / Math.max(c12Conversions, 1), 2),
    frequency: round(noise(c12Frequency, 0.1), 2),
  });

  // Creative C13 - Stable performer
  const c13Spend = noise(400, 0.1);
  const c13Impressions = Math.round(noise(12000, 0.1));
  const c13Clicks = Math.round(c13Impressions * noise(0.019, 0.1));
  const c13Cvr = noise(0.065, 0.08);
  const c13Conversions = Math.round(c13Clicks * c13Cvr);
  const c13Revenue = c13Conversions * noise(95, 0.1);
  const c13Roas = c13Spend > 0 ? c13Revenue / c13Spend : 0;

  creativeDailyMetrics.push({
    id: `cdm_c13_${dateStr}`,
    creativeId: 'cr_c13',
    date: dateStr,
    spend: round(c13Spend, 2),
    revenue: round(c13Revenue, 2),
    impressions: c13Impressions,
    clicks: c13Clicks,
    conversions: c13Conversions,
    roas: round(c13Roas, 4),
    ctr: round(c13Clicks / c13Impressions, 6),
    cvr: round(c13Cvr, 6),
    cpa: round(c13Spend / Math.max(c13Conversions, 1), 2),
    frequency: round(noise(2.2, 0.1), 2),
  });

  // TikTok T01 - Also showing fatigue
  let t01BaseCvr = 0.055;
  let t01Frequency = 3.0;

  if (i < 10) {
    const fatigueFactor = (10 - i) / 10;
    t01BaseCvr = 0.055 - (fatigueFactor * 0.015); // 0.055 → 0.04
    t01Frequency = 3.0 + (fatigueFactor * 1.0); // 3.0 → 4.0
  }

  const t01Spend = noise(300, 0.12);
  const t01Impressions = Math.round(noise(25000, 0.12));
  const t01Clicks = Math.round(t01Impressions * noise(0.012, 0.1));
  const t01Cvr = noise(t01BaseCvr, 0.1);
  const t01Conversions = Math.round(t01Clicks * t01Cvr);
  const t01Revenue = t01Conversions * noise(85, 0.1);
  const t01Roas = t01Spend > 0 ? t01Revenue / t01Spend : 0;

  creativeDailyMetrics.push({
    id: `cdm_t01_${dateStr}`,
    creativeId: 'cr_t01',
    date: dateStr,
    spend: round(t01Spend, 2),
    revenue: round(t01Revenue, 2),
    impressions: t01Impressions,
    clicks: t01Clicks,
    conversions: t01Conversions,
    roas: round(t01Roas, 4),
    ctr: round(t01Clicks / t01Impressions, 6),
    cvr: round(t01Cvr, 6),
    cpa: round(t01Spend / Math.max(t01Conversions, 1), 2),
    frequency: round(noise(t01Frequency, 0.1), 2),
  });
}

// ============================================
// 6. COHORTS (LTV drift pattern: 128 → 119 → 115 → 112)
// ============================================
const cohorts: CohortData[] = [
  // Historical baseline cohorts (6+ months ago)
  {
    id: 'cohort_2024_04',
    cohortMonth: '2024-04',
    acquisitionChannel: 'All',
    customerCount: 2850,
    totalRevenue: 364800,
    ltv30d: 58,
    ltv60d: 98,
    ltv90d: 128, // Baseline
    ltv180d: 165,
    avgOrderValue: 95,
    repeatPurchaseRate: 0.42,
  },
  {
    id: 'cohort_2024_05',
    cohortMonth: '2024-05',
    acquisitionChannel: 'All',
    customerCount: 3100,
    totalRevenue: 390600,
    ltv30d: 56,
    ltv60d: 96,
    ltv90d: 126,
    ltv180d: 162,
    avgOrderValue: 94,
    repeatPurchaseRate: 0.41,
  },
  {
    id: 'cohort_2024_06',
    cohortMonth: '2024-06',
    acquisitionChannel: 'All',
    customerCount: 3250,
    totalRevenue: 403000,
    ltv30d: 55,
    ltv60d: 94,
    ltv90d: 124,
    ltv180d: 158,
    avgOrderValue: 93,
    repeatPurchaseRate: 0.40,
  },
  // Transition cohorts
  {
    id: 'cohort_2024_07',
    cohortMonth: '2024-07',
    acquisitionChannel: 'All',
    customerCount: 3400,
    totalRevenue: 408000,
    ltv30d: 54,
    ltv60d: 92,
    ltv90d: 120,
    avgOrderValue: 92,
    repeatPurchaseRate: 0.38,
  },
  {
    id: 'cohort_2024_08',
    cohortMonth: '2024-08',
    acquisitionChannel: 'All',
    customerCount: 3550,
    totalRevenue: 412300,
    ltv30d: 52,
    ltv60d: 90,
    ltv90d: 119, // Starting to drift
    avgOrderValue: 91,
    repeatPurchaseRate: 0.37,
  },
  // Recent cohorts (showing drift)
  {
    id: 'cohort_2024_09',
    cohortMonth: '2024-09',
    acquisitionChannel: 'All',
    customerCount: 3700,
    totalRevenue: 418100,
    ltv30d: 50,
    ltv60d: 86,
    ltv90d: 115, // Drifting
    avgOrderValue: 89,
    repeatPurchaseRate: 0.35,
  },
  {
    id: 'cohort_2024_10',
    cohortMonth: '2024-10',
    acquisitionChannel: 'All',
    customerCount: 3850,
    totalRevenue: 423500,
    ltv30d: 48,
    ltv60d: 82,
    ltv90d: 112, // Continued drift
    avgOrderValue: 88,
    repeatPurchaseRate: 0.33,
  },
  {
    id: 'cohort_2024_11',
    cohortMonth: '2024-11',
    acquisitionChannel: 'All',
    customerCount: 4000,
    totalRevenue: 428000,
    ltv30d: 46,
    ltv60d: 78,
    ltv90d: 110, // Most recent
    avgOrderValue: 87,
    repeatPurchaseRate: 0.32,
  },
  // Channel-specific cohorts for deeper analysis
  {
    id: 'cohort_2024_10_meta',
    cohortMonth: '2024-10',
    acquisitionChannel: 'Meta',
    customerCount: 2100,
    totalRevenue: 243600,
    ltv30d: 52,
    ltv60d: 88,
    ltv90d: 116,
    avgOrderValue: 92,
    repeatPurchaseRate: 0.36,
  },
  {
    id: 'cohort_2024_10_tiktok',
    cohortMonth: '2024-10',
    acquisitionChannel: 'TikTok',
    customerCount: 950,
    totalRevenue: 95000,
    ltv30d: 42,
    ltv60d: 72,
    ltv90d: 100, // TikTok cohorts lower LTV
    avgOrderValue: 82,
    repeatPurchaseRate: 0.28,
  },
];

// ============================================
// 7. WRITE ALL DATA FILES
// ============================================
fs.writeFileSync(
  path.join(DATA_DIR, 'channels.json'), 
  JSON.stringify(channels, null, 2)
);
fs.writeFileSync(
  path.join(DATA_DIR, 'campaigns.json'), 
  JSON.stringify(campaigns, null, 2)
);
fs.writeFileSync(
  path.join(DATA_DIR, 'creatives.json'), 
  JSON.stringify(creatives, null, 2)
);
fs.writeFileSync(
  path.join(DATA_DIR, 'daily_metrics.json'), 
  JSON.stringify(dailyMetrics, null, 2)
);
fs.writeFileSync(
  path.join(DATA_DIR, 'creative_daily_metrics.json'), 
  JSON.stringify(creativeDailyMetrics, null, 2)
);
fs.writeFileSync(
  path.join(DATA_DIR, 'cohorts.json'), 
  JSON.stringify(cohorts, null, 2)
);

console.log('✅ Seed data V3 generated successfully!');
console.log(`   📁 Location: ${DATA_DIR}`);
console.log('   📊 Files created:');
console.log(`      - channels.json (${channels.length} channels)`);
console.log(`      - campaigns.json (${campaigns.length} campaigns)`);
console.log(`      - creatives.json (${creatives.length} creatives)`);
console.log(`      - daily_metrics.json (${dailyMetrics.length} records)`);
console.log(`      - creative_daily_metrics.json (${creativeDailyMetrics.length} records)`);
console.log(`      - cohorts.json (${cohorts.length} cohorts)`);
console.log('');
console.log('🎯 Demo Scenario: $65M Beauty Brand');
console.log('   - Meta: Hero (ROAS 3.5-3.8)');
console.log('   - Google: Solid (ROAS 2.2-2.5)');
console.log('   - TikTok: Problem child (ROAS declining 2.8→1.9)');
console.log('   - Creative C12: Fatiguing (CVR 0.08→0.05)');
console.log('   - LTV Drift: 128→112 (-12.5%)');
