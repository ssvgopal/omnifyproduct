import axios from 'axios';
import { format, subDays } from 'date-fns';

export interface MetaInsight {
    date_start: string;
    date_stop: string;
    spend: string;
    impressions: string;
    clicks: string;
    conversions?: string;
    actions?: Array<{ action_type: string; value: string }>;
}

export interface MetaCreative {
    id: string;
    name: string;
    status: string;
    insights?: {
        data: MetaInsight[];
    };
}

export class MetaAdsClient {
    private accessToken: string;
    private accountId: string;
    private baseUrl = 'https://graph.facebook.com/v18.0';

    constructor(accessToken: string, accountId: string) {
        this.accessToken = accessToken;
        this.accountId = accountId;
    }

    /**
     * Fetch account insights for a date range
     */
    async fetchAccountInsights(dateRange: { start: Date; end: Date }) {
        const url = `${this.baseUrl}/${this.accountId}/insights`;

        try {
            const response = await axios.get(url, {
                params: {
                    access_token: this.accessToken,
                    time_range: JSON.stringify({
                        since: format(dateRange.start, 'yyyy-MM-dd'),
                        until: format(dateRange.end, 'yyyy-MM-dd')
                    }),
                    time_increment: 1, // Daily breakdown
                    fields: 'spend,impressions,clicks,actions,action_values',
                    level: 'account'
                }
            });

            return response.data.data as MetaInsight[];
        } catch (error: any) {
            console.error('[META_ADS] Error fetching insights:', error.response?.data || error.message);
            throw new Error(`Meta Ads API Error: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    /**
     * Fetch all active campaigns
     */
    async fetchCampaigns() {
        const url = `${this.baseUrl}/${this.accountId}/campaigns`;

        try {
            const response = await axios.get(url, {
                params: {
                    access_token: this.accessToken,
                    fields: 'id,name,status,objective',
                    limit: 100
                }
            });

            return response.data.data;
        } catch (error: any) {
            console.error('[META_ADS] Error fetching campaigns:', error.response?.data || error.message);
            throw new Error(`Meta Ads API Error: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    /**
     * Fetch ads with creative data and insights
     */
    async fetchAdsWithInsights(dateRange: { start: Date; end: Date }) {
        const url = `${this.baseUrl}/${this.accountId}/ads`;

        try {
            const response = await axios.get(url, {
                params: {
                    access_token: this.accessToken,
                    fields: 'id,name,status,creative{id,name},insights{spend,impressions,clicks,actions}',
                    time_range: JSON.stringify({
                        since: format(dateRange.start, 'yyyy-MM-dd'),
                        until: format(dateRange.end, 'yyyy-MM-dd')
                    }),
                    limit: 100,
                    filtering: JSON.stringify([
                        { field: 'status', operator: 'IN', value: ['ACTIVE', 'PAUSED'] }
                    ])
                }
            });

            return response.data.data as MetaCreative[];
        } catch (error: any) {
            console.error('[META_ADS] Error fetching ads:', error.response?.data || error.message);
            throw new Error(`Meta Ads API Error: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    /**
     * Calculate ROAS from Meta insights
     */
    calculateROAS(insight: MetaInsight, revenue: number): number {
        const spend = parseFloat(insight.spend || '0');
        return spend > 0 ? revenue / spend : 0;
    }

    /**
     * Extract purchase conversion value from actions
     */
    extractPurchaseValue(insight: MetaInsight): number {
        if (!insight.actions) return 0;

        const purchaseAction = insight.actions.find(
            a => a.action_type === 'offsite_conversion.fb_pixel_purchase'
        );

        return purchaseAction ? parseFloat(purchaseAction.value) : 0;
    }
}
