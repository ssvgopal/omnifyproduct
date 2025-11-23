import { supabaseAdmin } from '../supabase';
import { MetaAdsClient } from '../integrations/meta-ads';
import { GoogleAdsClient } from '../integrations/google-ads';
import { TikTokAdsClient } from '../integrations/tiktok-ads';
import { ShopifyClient } from '../integrations/shopify';
import { subDays } from 'date-fns';

export interface SyncConfig {
    organizationId: string;
    platform: 'Meta' | 'Google' | 'TikTok' | 'Shopify';
    credentials: any;
    dateRange?: { start: Date; end: Date };
}

export class DataSyncService {
    /**
     * Sync data from a specific platform
     */
    async syncPlatform(config: SyncConfig): Promise<{
        success: boolean;
        recordsSynced: number;
        error?: string;
    }> {
        // Create sync job record
        const { data: job, error: jobError } = await supabaseAdmin
            .from('sync_jobs')
            .insert({
                organization_id: config.organizationId,
                platform: config.platform,
                status: 'running',
                started_at: new Date().toISOString()
            })
            .select()
            .single();

        if (jobError || !job) {
            console.error('[SYNC] Error creating job:', jobError);
            return { success: false, recordsSynced: 0, error: 'Failed to create sync job' };
        }

        try {
            let recordsSynced = 0;

            switch (config.platform) {
                case 'Meta':
                    recordsSynced = await this.syncMetaAds(config);
                    break;
                case 'Google':
                    recordsSynced = await this.syncGoogleAds(config);
                    break;
                case 'TikTok':
                    recordsSynced = await this.syncTikTokAds(config);
                    break;
                case 'Shopify':
                    recordsSynced = await this.syncShopify(config);
                    break;
            }

            // Update job as completed
            await supabaseAdmin
                .from('sync_jobs')
                .update({
                    status: 'completed',
                    completed_at: new Date().toISOString(),
                    records_synced: recordsSynced
                })
                .eq('id', job.id);

            return { success: true, recordsSynced };
        } catch (error: any) {
            console.error(`[SYNC] Error syncing ${config.platform}:`, error.message);

            // Update job as failed
            await supabaseAdmin
                .from('sync_jobs')
                .update({
                    status: 'failed',
                    completed_at: new Date().toISOString(),
                    error_message: error.message
                })
                .eq('id', job.id);

            return { success: false, recordsSynced: 0, error: error.message };
        }
    }

    /**
     * Sync Meta Ads data
     */
    private async syncMetaAds(config: SyncConfig): Promise<number> {
        const client = new MetaAdsClient(
            config.credentials.accessToken,
            config.credentials.accountId
        );

        const dateRange = config.dateRange || {
            start: subDays(new Date(), 30),
            end: new Date()
        };

        // Get or create channel
        const { data: channel } = await supabaseAdmin
            .from('channels')
            .upsert({
                organization_id: config.organizationId,
                name: 'Meta Ads',
                platform: 'Meta',
                external_id: config.credentials.accountId,
                is_active: true
            }, { onConflict: 'organization_id,platform,external_id' })
            .select()
            .single();

        if (!channel) throw new Error('Failed to create channel');

        // Fetch insights
        const insights = await client.fetchAccountInsights(dateRange);

        // Insert daily metrics
        const metrics = insights.map(insight => ({
            channel_id: channel.id,
            date: insight.date_start,
            spend: parseFloat(insight.spend),
            impressions: parseInt(insight.impressions),
            clicks: parseInt(insight.clicks),
            revenue: client.extractPurchaseValue(insight),
            roas: client.calculateROAS(insight, client.extractPurchaseValue(insight))
        }));

        const { error } = await supabaseAdmin
            .from('daily_metrics')
            .upsert(metrics, { onConflict: 'channel_id,date' });

        if (error) throw error;

        // Fetch and sync creatives
        const creatives = await client.fetchAdsWithInsights(dateRange);
        // ... (creative sync logic)

        return metrics.length;
    }

    /**
     * Sync Google Ads data
     */
    private async syncGoogleAds(config: SyncConfig): Promise<number> {
        const client = new GoogleAdsClient({
            clientId: config.credentials.clientId,
            clientSecret: config.credentials.clientSecret,
            refreshToken: config.credentials.refreshToken,
            customerId: config.credentials.customerId
        });

        const dateRange = config.dateRange || {
            start: subDays(new Date(), 30),
            end: new Date()
        };

        // Get or create channel
        const { data: channel } = await supabaseAdmin
            .from('channels')
            .upsert({
                organization_id: config.organizationId,
                name: 'Google Ads',
                platform: 'Google',
                external_id: config.credentials.customerId,
                is_active: true
            }, { onConflict: 'organization_id,platform,external_id' })
            .select()
            .single();

        if (!channel) throw new Error('Failed to create channel');

        // Fetch metrics
        const metrics = await client.fetchCampaignMetrics(dateRange);

        // Insert daily metrics
        const dailyMetrics = metrics.map(metric => ({
            channel_id: channel.id,
            date: metric.date,
            spend: client.microsToDollars(metric.cost_micros),
            impressions: parseInt(metric.impressions),
            clicks: parseInt(metric.clicks),
            conversions: parseInt(metric.conversions),
            revenue: parseFloat(metric.conversions_value),
            roas: client.calculateROAS(metric)
        }));

        const { error } = await supabaseAdmin
            .from('daily_metrics')
            .upsert(dailyMetrics, { onConflict: 'channel_id,date' });

        if (error) throw error;

        return dailyMetrics.length;
    }

    /**
     * Sync TikTok Ads data
     */
    private async syncTikTokAds(config: SyncConfig): Promise<number> {
        const client = new TikTokAdsClient(
            config.credentials.accessToken,
            config.credentials.advertiserId
        );

        const dateRange = config.dateRange || {
            start: subDays(new Date(), 30),
            end: new Date()
        };

        // Get or create channel
        const { data: channel } = await supabaseAdmin
            .from('channels')
            .upsert({
                organization_id: config.organizationId,
                name: 'TikTok Ads',
                platform: 'TikTok',
                external_id: config.credentials.advertiserId,
                is_active: true
            }, { onConflict: 'organization_id,platform,external_id' })
            .select()
            .single();

        if (!channel) throw new Error('Failed to create channel');

        // Fetch metrics
        const metrics = await client.fetchCampaignMetrics(dateRange);

        // Insert daily metrics
        const dailyMetrics = metrics.map(metric => ({
            channel_id: channel.id,
            date: metric.stat_time_day,
            spend: parseFloat(metric.spend),
            impressions: parseInt(metric.impressions),
            clicks: parseInt(metric.clicks),
            conversions: parseInt(metric.conversion),
            revenue: parseFloat(metric.conversion_value),
            roas: client.calculateROAS(metric)
        }));

        const { error } = await supabaseAdmin
            .from('daily_metrics')
            .upsert(dailyMetrics, { onConflict: 'channel_id,date' });

        if (error) throw error;

        return dailyMetrics.length;
    }

    /**
     * Sync Shopify data
     */
    private async syncShopify(config: SyncConfig): Promise<number> {
        const client = new ShopifyClient(
            config.credentials.storeUrl,
            config.credentials.accessToken
        );

        const dateRange = config.dateRange || {
            start: subDays(new Date(), 30),
            end: new Date()
        };

        // Fetch orders
        const orders = await client.fetchOrders(dateRange);
        const dailyRevenue = client.calculateDailyRevenue(orders);

        // Get or create channel
        const { data: channel } = await supabaseAdmin
            .from('channels')
            .upsert({
                organization_id: config.organizationId,
                name: 'Shopify',
                platform: 'Shopify',
                external_id: config.credentials.storeUrl,
                is_active: true
            }, { onConflict: 'organization_id,platform,external_id' })
            .select()
            .single();

        if (!channel) throw new Error('Failed to create channel');

        // Insert daily metrics (revenue only, no spend for Shopify)
        const dailyMetrics = Array.from(dailyRevenue.entries()).map(([date, revenue]) => ({
            channel_id: channel.id,
            date,
            revenue,
            spend: 0
        }));

        const { error } = await supabaseAdmin
            .from('daily_metrics')
            .upsert(dailyMetrics, { onConflict: 'channel_id,date' });

        if (error) throw error;

        return dailyMetrics.length;
    }

    /**
     * Sync all platforms for an organization
     */
    async syncAllPlatforms(organizationId: string): Promise<{
        success: boolean;
        results: Record<string, { success: boolean; recordsSynced: number }>;
    }> {
        // Get all active credentials
        const { data: credentials } = await supabaseAdmin
            .from('api_credentials')
            .select('*')
            .eq('organization_id', organizationId)
            .eq('is_active', true);

        if (!credentials || credentials.length === 0) {
            return { success: false, results: {} };
        }

        const results: Record<string, { success: boolean; recordsSynced: number }> = {};

        for (const cred of credentials) {
            const result = await this.syncPlatform({
                organizationId,
                platform: cred.platform as any,
                credentials: cred.credentials
            });

            results[cred.platform] = {
                success: result.success,
                recordsSynced: result.recordsSynced
            };
        }

        return {
            success: Object.values(results).every(r => r.success),
            results
        };
    }
}
