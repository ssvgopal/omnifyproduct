import axios from 'axios';
import { format } from 'date-fns';

export interface GoogleAdsMetric {
    date: string;
    cost_micros: string;
    impressions: string;
    clicks: string;
    conversions: string;
    conversions_value: string;
}

export class GoogleAdsClient {
    private clientId: string;
    private clientSecret: string;
    private refreshToken: string;
    private customerId: string;
    private accessToken?: string;
    private baseUrl = 'https://googleads.googleapis.com/v14';

    constructor(config: {
        clientId: string;
        clientSecret: string;
        refreshToken: string;
        customerId: string;
    }) {
        this.clientId = config.clientId;
        this.clientSecret = config.clientSecret;
        this.refreshToken = config.refreshToken;
        this.customerId = config.customerId.replace(/-/g, ''); // Remove dashes
    }

    /**
     * Get OAuth access token
     */
    private async getAccessToken(): Promise<string> {
        if (this.accessToken) return this.accessToken;

        try {
            const response = await axios.post('https://oauth2.googleapis.com/token', {
                client_id: this.clientId,
                client_secret: this.clientSecret,
                refresh_token: this.refreshToken,
                grant_type: 'refresh_token'
            });

            this.accessToken = response.data.access_token as string;
            return this.accessToken;
        } catch (error: any) {
            console.error('[GOOGLE_ADS] Error getting access token:', error.response?.data || error.message);
            throw new Error('Failed to authenticate with Google Ads API');
        }
    }

    /**
     * Fetch campaign metrics using Google Ads Query Language (GAQL)
     */
    async fetchCampaignMetrics(dateRange: { start: Date; end: Date }) {
        const accessToken = await this.getAccessToken();
        const url = `${this.baseUrl}/customers/${this.customerId}/googleAds:searchStream`;

        const query = `
      SELECT
        segments.date,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.conversions,
        metrics.conversions_value
      FROM campaign
      WHERE segments.date BETWEEN '${format(dateRange.start, 'yyyy-MM-dd')}' 
        AND '${format(dateRange.end, 'yyyy-MM-dd')}'
      ORDER BY segments.date DESC
    `;

        try {
            const response = await axios.post(
                url,
                { query },
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                        'developer-token': process.env.GOOGLE_ADS_DEVELOPER_TOKEN!,
                        'login-customer-id': this.customerId
                    }
                }
            );

            // Parse streaming response
            const results: GoogleAdsMetric[] = [];
            for (const batch of response.data) {
                if (batch.results) {
                    results.push(...batch.results.map((r: any) => ({
                        date: r.segments.date,
                        cost_micros: r.metrics.costMicros,
                        impressions: r.metrics.impressions,
                        clicks: r.metrics.clicks,
                        conversions: r.metrics.conversions,
                        conversions_value: r.metrics.conversionsValue
                    })));
                }
            }

            return results;
        } catch (error: any) {
            console.error('[GOOGLE_ADS] Error fetching metrics:', error.response?.data || error.message);
            throw new Error(`Google Ads API Error: ${error.response?.data?.error?.message || error.message}`);
        }
    }

    /**
     * Convert micros to dollars
     */
    microsToDollars(micros: string): number {
        return parseFloat(micros) / 1_000_000;
    }

    /**
     * Calculate ROAS
     */
    calculateROAS(metric: GoogleAdsMetric): number {
        const spend = this.microsToDollars(metric.cost_micros);
        const revenue = parseFloat(metric.conversions_value);
        return spend > 0 ? revenue / spend : 0;
    }
}
