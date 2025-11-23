import axios from 'axios';
import { format } from 'date-fns';

export interface TikTokMetric {
    stat_time_day: string;
    spend: string;
    impressions: string;
    clicks: string;
    conversion: string;
    conversion_value: string;
}

export class TikTokAdsClient {
    private accessToken: string;
    private advertiserId: string;
    private baseUrl = 'https://business-api.tiktok.com/open_api/v1.3';

    constructor(accessToken: string, advertiserId: string) {
        this.accessToken = accessToken;
        this.advertiserId = advertiserId;
    }

    /**
     * Fetch campaign metrics
     */
    async fetchCampaignMetrics(dateRange: { start: Date; end: Date }) {
        const url = `${this.baseUrl}/reports/integrated/get/`;

        try {
            const response = await axios.get(url, {
                headers: {
                    'Access-Token': this.accessToken
                },
                params: {
                    advertiser_id: this.advertiserId,
                    report_type: 'BASIC',
                    data_level: 'AUCTION_CAMPAIGN',
                    dimensions: JSON.stringify(['stat_time_day']),
                    metrics: JSON.stringify([
                        'spend',
                        'impressions',
                        'clicks',
                        'conversion',
                        'conversion_value'
                    ]),
                    start_date: format(dateRange.start, 'yyyy-MM-dd'),
                    end_date: format(dateRange.end, 'yyyy-MM-dd'),
                    page_size: 1000
                }
            });

            if (response.data.code !== 0) {
                throw new Error(response.data.message);
            }

            return response.data.data.list as TikTokMetric[];
        } catch (error: any) {
            console.error('[TIKTOK_ADS] Error fetching metrics:', error.response?.data || error.message);
            throw new Error(`TikTok Ads API Error: ${error.response?.data?.message || error.message}`);
        }
    }

    /**
     * Fetch ad creative data
     */
    async fetchAdCreatives() {
        const url = `${this.baseUrl}/ad/get/`;

        try {
            const response = await axios.get(url, {
                headers: {
                    'Access-Token': this.accessToken
                },
                params: {
                    advertiser_id: this.advertiserId,
                    filtering: JSON.stringify({
                        primary_status: 'STATUS_ENABLE'
                    }),
                    page_size: 100
                }
            });

            if (response.data.code !== 0) {
                throw new Error(response.data.message);
            }

            return response.data.data.list;
        } catch (error: any) {
            console.error('[TIKTOK_ADS] Error fetching creatives:', error.response?.data || error.message);
            throw new Error(`TikTok Ads API Error: ${error.response?.data?.message || error.message}`);
        }
    }

    /**
     * Calculate ROAS
     */
    calculateROAS(metric: TikTokMetric): number {
        const spend = parseFloat(metric.spend);
        const revenue = parseFloat(metric.conversion_value);
        return spend > 0 ? revenue / spend : 0;
    }
}
