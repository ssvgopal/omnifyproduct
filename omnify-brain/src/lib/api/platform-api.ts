/**
 * Platform API Client
 * Handles communication with backend platform integration APIs
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface DateRange {
  start: string;
  end: string;
}

export interface MetricsRequest {
  organization_id: string;
  date_range?: DateRange;
}

export interface SyncRequest {
  organization_id: string;
  days?: number;
}

export interface PlatformMetrics {
  spend: number;
  revenue: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  ctr: number;
  cpc: number;
  cpm?: number;
}

export interface UnifiedMetrics {
  blended_metrics: PlatformMetrics;
  platform_breakdown: Record<string, PlatformMetrics>;
  date_range: DateRange;
}

class PlatformAPIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  // ========== META ADS ==========

  async getMetaAccount(organizationId: string) {
    const response = await fetch(`${this.baseUrl}/platforms/meta-ads/account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Meta account: ${response.statusText}`);
    }

    return response.json();
  }

  async getMetaCampaigns(organizationId: string) {
    const response = await fetch(`${this.baseUrl}/platforms/meta-ads/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Meta campaigns: ${response.statusText}`);
    }

    return response.json();
  }

  async getMetaInsights(organizationId: string, dateRange?: DateRange) {
    const response = await fetch(`${this.baseUrl}/platforms/meta-ads/insights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        organization_id: organizationId,
        date_range: dateRange 
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Meta insights: ${response.statusText}`);
    }

    return response.json();
  }

  async getMetaSummary(organizationId: string) {
    const response = await fetch(`${this.baseUrl}/platforms/meta-ads/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Meta summary: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== GOOGLE ADS ==========

  async getGoogleCampaigns(organizationId: string) {
    const response = await fetch(`${this.baseUrl}/platforms/google-ads/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Google campaigns: ${response.statusText}`);
    }

    return response.json();
  }

  async getGoogleMetrics(organizationId: string, dateRange?: DateRange) {
    const response = await fetch(`${this.baseUrl}/platforms/google-ads/metrics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        organization_id: organizationId,
        date_range: dateRange 
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Google metrics: ${response.statusText}`);
    }

    return response.json();
  }

  async getGoogleSummary(organizationId: string) {
    const response = await fetch(`${this.baseUrl}/platforms/google-ads/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ organization_id: organizationId })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch Google summary: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== DATA SYNC ==========

  async syncPlatform(organizationId: string, platform: string, days: number = 7) {
    const response = await fetch(`${this.baseUrl}/platforms/sync/${platform}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        organization_id: organizationId,
        days 
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to sync ${platform}: ${response.statusText}`);
    }

    return response.json();
  }

  async syncAllPlatforms(organizationId: string, days: number = 7) {
    const response = await fetch(`${this.baseUrl}/platforms/sync/all`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        organization_id: organizationId,
        days 
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to sync all platforms: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== UNIFIED METRICS ==========

  async getUnifiedMetrics(organizationId: string, dateRange?: DateRange): Promise<UnifiedMetrics> {
    const response = await fetch(`${this.baseUrl}/platforms/unified-metrics`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        organization_id: organizationId,
        date_range: dateRange 
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch unified metrics: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  }

  // ========== HEALTH CHECK ==========

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/platforms/health`);
    return response.json();
  }
}

// Singleton instance
export const platformAPI = new PlatformAPIClient();
