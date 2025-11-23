import { supabase, supabaseAdmin } from './supabase';

/**
 * Get all active channels for an organization
 */
export async function getOrganizationChannels(organizationId: string) {
  const { data, error } = await supabaseAdmin
    .from('channels')
    .select('*')
    .eq('organization_id', organizationId)
    .eq('is_active', true)
    .order('created_at', { ascending: true });

  if (error) {
    console.error('[DB] Error fetching channels:', error);
    throw new Error('Failed to fetch channels');
  }

  return data || [];
}

/**
 * Get daily metrics for channels within a date range
 */
export async function getDailyMetrics(
  channelIds: string[],
  dateRange: { start: Date; end: Date }
) {
  if (channelIds.length === 0) {
    return [];
  }

  const { data, error } = await supabaseAdmin
    .from('daily_metrics')
    .select('*')
    .in('channel_id', channelIds)
    .gte('date', dateRange.start.toISOString().split('T')[0])
    .lte('date', dateRange.end.toISOString().split('T')[0])
    .order('date', { ascending: false });

  if (error) {
    console.error('[DB] Error fetching metrics:', error);
    throw new Error('Failed to fetch metrics');
  }

  return data || [];
}

/**
 * Get creatives for channels
 */
export async function getCreatives(channelIds: string[]) {
  if (channelIds.length === 0) {
    return [];
  }

  const { data, error } = await supabaseAdmin
    .from('creatives')
    .select('*')
    .in('channel_id', channelIds)
    .eq('status', 'active')
    .order('spend', { ascending: false });

  if (error) {
    console.error('[DB] Error fetching creatives:', error);
    throw new Error('Failed to fetch creatives');
  }

  return data || [];
}

/**
 * Get latest brain state for an organization
 */
export async function getLatestBrainState(organizationId: string) {
  const { data, error } = await supabaseAdmin
    .from('brain_states')
    .select('*')
    .eq('organization_id', organizationId)
    .order('computed_at', { ascending: false })
    .limit(1)
    .single();

  if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
    console.error('[DB] Error fetching brain state:', error);
    throw new Error('Failed to fetch brain state');
  }

  return data;
}

/**
 * Get API credentials for an organization
 */
export async function getOrganizationCredentials(
  organizationId: string,
  platform?: string
) {
  let query = supabaseAdmin
    .from('api_credentials')
    .select('*')
    .eq('organization_id', organizationId)
    .eq('is_active', true);

  if (platform) {
    query = query.eq('platform', platform);
  }

  const { data, error } = await query;

  if (error) {
    console.error('[DB] Error fetching credentials:', error);
    throw new Error('Failed to fetch credentials');
  }

  return data || [];
}

/**
 * Get sync job history for an organization
 */
export async function getSyncJobs(organizationId: string, limit = 10) {
  const { data, error } = await supabaseAdmin
    .from('sync_jobs')
    .select('*')
    .eq('organization_id', organizationId)
    .order('created_at', { ascending: false })
    .limit(limit);

  if (error) {
    console.error('[DB] Error fetching sync jobs:', error);
    throw new Error('Failed to fetch sync jobs');
  }

  return data || [];
}
