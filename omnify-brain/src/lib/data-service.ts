/**
 * Data Service - Supabase Data Fetching
 * 
 * Fetches data from Supabase for brain module processing.
 * Supports both live Supabase data and local seed files.
 */

import { supabaseAdmin } from './supabase';

// Use admin client to bypass RLS for server-side operations
const supabase = supabaseAdmin;
import { 
  ChannelData, 
  CreativeData, 
  DailyMetricExtended,
  CohortData,
  CreativeDailyMetric,
  CampaignData
} from './types';

export interface BrainDataInput {
  channels: ChannelData[];
  creatives: CreativeData[];
  dailyMetrics: DailyMetricExtended[];
  cohorts: CohortData[];
  creativeDailyMetrics: CreativeDailyMetric[];
  campaigns: CampaignData[];
}

/**
 * Fetch all data needed for brain processing from Supabase
 */
export async function fetchBrainData(organizationId: string): Promise<BrainDataInput> {
  const [
    channelsResult,
    creativesResult,
    dailyMetricsResult,
    cohortsResult,
    creativeDailyMetricsResult,
    campaignsResult
  ] = await Promise.all([
    fetchChannels(organizationId),
    fetchCreatives(organizationId),
    fetchDailyMetrics(organizationId),
    fetchCohorts(organizationId),
    fetchCreativeDailyMetrics(organizationId),
    fetchCampaigns(organizationId)
  ]);

  return {
    channels: channelsResult,
    creatives: creativesResult,
    dailyMetrics: dailyMetricsResult,
    cohorts: cohortsResult,
    creativeDailyMetrics: creativeDailyMetricsResult,
    campaigns: campaignsResult
  };
}

/**
 * Fetch channels for an organization
 */
async function fetchChannels(organizationId: string): Promise<ChannelData[]> {
  const { data, error } = await supabase
    .from('channels')
    .select('*')
    .eq('organization_id', organizationId)
    .eq('is_active', true);

  if (error) {
    console.error('Error fetching channels:', error);
    return [];
  }

  return (data || []).map(ch => ({
    id: ch.id,
    name: ch.name,
    platform: ch.platform,
    spend: 0, // Will be aggregated from daily_metrics
    revenue: 0,
    impressions: 0,
    clicks: 0,
    conversions: 0,
    roas: 0,
    cpa: 0,
    ctr: 0
  }));
}

/**
 * Fetch creatives for an organization
 */
async function fetchCreatives(organizationId: string): Promise<CreativeData[]> {
  const { data, error } = await supabase
    .from('creatives')
    .select(`
      *,
      channels!inner(organization_id)
    `)
    .eq('channels.organization_id', organizationId);

  if (error) {
    console.error('Error fetching creatives:', error);
    return [];
  }

  return (data || []).map(cr => ({
    id: cr.id,
    name: cr.name,
    channelId: cr.channel_id,
    spend: cr.spend || 0,
    revenue: cr.revenue || 0,
    impressions: cr.impressions || 0,
    clicks: cr.clicks || 0,
    ctr: cr.ctr || 0,
    roas: cr.roas || 0,
    status: cr.status,
    launchDate: cr.launch_date
  }));
}

/**
 * Fetch daily metrics for the last 30 days
 */
async function fetchDailyMetrics(organizationId: string): Promise<DailyMetricExtended[]> {
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const dateStr = thirtyDaysAgo.toISOString().split('T')[0];

  const { data, error } = await supabase
    .from('daily_metrics')
    .select(`
      *,
      channels!inner(organization_id, name, platform)
    `)
    .eq('channels.organization_id', organizationId)
    .gte('date', dateStr)
    .order('date', { ascending: true });

  if (error) {
    console.error('Error fetching daily metrics:', error);
    return [];
  }

  return (data || []).map(dm => ({
    date: dm.date,
    channelId: dm.channel_id,
    spend: dm.spend || 0,
    revenue: dm.revenue || 0,
    roas: dm.roas || 0,
    status: 'neutral',
    impressions: dm.impressions || 0,
    clicks: dm.clicks || 0,
    conversions: dm.conversions || 0,
    frequency: dm.frequency || 0,
    cvr: dm.cvr || (dm.conversions && dm.clicks ? dm.conversions / dm.clicks : 0),
    cpa: dm.cpa || (dm.conversions && dm.spend ? dm.spend / dm.conversions : 0)
  }));
}

/**
 * Fetch cohorts for LTV analysis
 */
async function fetchCohorts(organizationId: string): Promise<CohortData[]> {
  const { data, error } = await supabase
    .from('cohorts')
    .select('*')
    .eq('organization_id', organizationId)
    .order('cohort_month', { ascending: false });

  if (error) {
    console.error('Error fetching cohorts:', error);
    return [];
  }

  return (data || []).map(c => ({
    id: c.id,
    cohortMonth: c.cohort_month,
    acquisitionChannel: c.acquisition_channel || 'All',
    customerCount: c.customer_count || 0,
    totalRevenue: c.total_revenue || 0,
    ltv30d: c.ltv_30d || 0,
    ltv60d: c.ltv_60d || 0,
    ltv90d: c.ltv_90d || 0,
    ltv180d: c.ltv_180d,
    avgOrderValue: c.avg_order_value || 0,
    repeatPurchaseRate: c.repeat_purchase_rate || 0
  }));
}

/**
 * Fetch creative daily metrics for fatigue detection
 */
async function fetchCreativeDailyMetrics(organizationId: string): Promise<CreativeDailyMetric[]> {
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const dateStr = thirtyDaysAgo.toISOString().split('T')[0];

  const { data, error } = await supabase
    .from('creative_daily_metrics')
    .select(`
      *,
      creatives!inner(
        channel_id,
        channels!inner(organization_id)
      )
    `)
    .eq('creatives.channels.organization_id', organizationId)
    .gte('date', dateStr)
    .order('date', { ascending: true });

  if (error) {
    console.error('Error fetching creative daily metrics:', error);
    return [];
  }

  return (data || []).map(cdm => ({
    id: cdm.id,
    creativeId: cdm.creative_id,
    date: cdm.date,
    spend: cdm.spend || 0,
    revenue: cdm.revenue || 0,
    impressions: cdm.impressions || 0,
    clicks: cdm.clicks || 0,
    conversions: cdm.conversions || 0,
    roas: cdm.roas || 0,
    ctr: cdm.ctr || 0,
    cvr: cdm.cvr || 0,
    cpa: cdm.cpa || 0,
    frequency: cdm.frequency || 0
  }));
}

/**
 * Fetch campaigns
 */
async function fetchCampaigns(organizationId: string): Promise<CampaignData[]> {
  const { data, error } = await supabase
    .from('campaigns')
    .select('*')
    .eq('organization_id', organizationId)
    .eq('status', 'active');

  if (error) {
    console.error('Error fetching campaigns:', error);
    return [];
  }

  return (data || []).map(c => ({
    id: c.id,
    channelId: c.channel_id,
    campaignId: c.campaign_id,
    campaignName: c.campaign_name,
    campaignType: c.campaign_type || 'conversion',
    status: c.status,
    dailyBudget: c.daily_budget || 0
  }));
}

/**
 * Save brain state to Supabase
 */
export async function saveBrainState(
  organizationId: string,
  memoryOutput: any,
  oracleOutput: any,
  curiosityOutput: any
): Promise<{ id: string } | null> {
  const { data, error } = await supabaseAdmin
    .from('brain_states')
    .insert({
      organization_id: organizationId,
      memory_output: memoryOutput,
      oracle_output: oracleOutput,
      curiosity_output: curiosityOutput,
      computed_at: new Date().toISOString()
    })
    .select('id')
    .single();

  if (error) {
    console.error('Error saving brain state:', error);
    return null;
  }

  return data;
}

/**
 * Get latest brain state from Supabase
 */
export async function getLatestBrainState(organizationId: string): Promise<any | null> {
  const { data, error } = await supabase
    .from('brain_states')
    .select('*')
    .eq('organization_id', organizationId)
    .order('computed_at', { ascending: false })
    .limit(1)
    .single();

  if (error) {
    console.error('Error fetching brain state:', error);
    return null;
  }

  return {
    timestamp: data.computed_at,
    organizationId: data.organization_id,
    memory: data.memory_output,
    oracle: data.oracle_output,
    curiosity: data.curiosity_output
  };
}
