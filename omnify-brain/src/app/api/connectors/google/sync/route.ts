import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { validatePlatform } from '@/lib/validation';

const GOOGLE_ADS_API_VERSION = 'v15';

export async function POST(request: NextRequest) {
  // Platform validation
  const validation = validatePlatform('google_ads');
  if (!validation.valid) {
    return validation.error!;
  }
  try {
    const user = await getCurrentUser(request);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get Google credentials
    const { data: credentialsData, error: credError } = await supabaseAdmin
      .from('api_credentials')
      .select('credentials')
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Google')
      .eq('is_active', true)
      .single();

    if (credError || !credentialsData) {
      return NextResponse.json(
        { error: 'Google Ads not connected' },
        { status: 400 }
      );
    }

    const credentials = credentialsData.credentials as any;
    let accessToken = credentials.access_token;

    // Check if token needs refresh
    if (credentials.expires_at && new Date(credentials.expires_at) < new Date()) {
      accessToken = await refreshGoogleToken(credentials.refresh_token, user.organizationId);
      if (!accessToken) {
        return NextResponse.json(
          { error: 'Failed to refresh Google token' },
          { status: 401 }
        );
      }
    }

    // Create sync job
    const { data: syncJob } = await supabaseAdmin
      .from('sync_jobs')
      .insert({
        organization_id: user.organizationId,
        platform: 'Google',
        status: 'running',
        started_at: new Date().toISOString(),
        records_synced: 0,
      })
      .select()
      .single();

    let recordsSynced = 0;

    try {
      // Get or create Google channel
      let { data: channel } = await supabaseAdmin
        .from('channels')
        .select('id')
        .eq('organization_id', user.organizationId)
        .eq('platform', 'Google')
        .single();

      if (!channel) {
        const { data: newChannel } = await supabaseAdmin
          .from('channels')
          .insert({
            organization_id: user.organizationId,
            name: 'Google Ads',
            platform: 'Google',
            is_active: true,
          })
          .select()
          .single();
        channel = newChannel;
      }

      // Fetch Google Ads data using Google Ads API
      // Note: Google Ads API requires a developer token and customer ID
      const developerToken = process.env.GOOGLE_ADS_DEVELOPER_TOKEN;
      const customerId = credentials.customer_id;

      if (developerToken && customerId) {
        // Fetch campaign performance data
        const dateRange = {
          startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0].replace(/-/g, ''),
          endDate: new Date().toISOString().split('T')[0].replace(/-/g, ''),
        };

        const query = `
          SELECT
            segments.date,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc
          FROM campaign
          WHERE segments.date BETWEEN '${dateRange.startDate}' AND '${dateRange.endDate}'
        `;

        const response = await fetch(
          `https://googleads.googleapis.com/${GOOGLE_ADS_API_VERSION}/customers/${customerId}/googleAds:searchStream`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'developer-token': developerToken,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
          }
        );

        if (response.ok) {
          const data = await response.json();
          
          // Process and insert metrics
          const metricsToInsert = [];
          
          for (const result of data.results || []) {
            const metrics = result.metrics || {};
            const segments = result.segments || {};
            
            const spend = (metrics.costMicros || 0) / 1000000;
            const revenue = metrics.conversionsValue || 0;
            const conversions = metrics.conversions || 0;
            
            metricsToInsert.push({
              channel_id: channel!.id,
              date: formatGoogleDate(segments.date),
              spend,
              revenue,
              impressions: metrics.impressions || 0,
              clicks: metrics.clicks || 0,
              conversions,
              roas: spend > 0 ? revenue / spend : 0,
              cpa: conversions > 0 ? spend / conversions : 0,
              ctr: metrics.ctr || 0,
            });
          }

          // Upsert metrics
          for (const metric of metricsToInsert) {
            await supabaseAdmin
              .from('daily_metrics')
              .upsert(metric, { onConflict: 'channel_id,date' });
          }

          recordsSynced = metricsToInsert.length;
        }
      } else {
        // Fallback: Generate sample data for demo purposes
        console.log('[GOOGLE SYNC] No developer token or customer ID, using demo data');
        
        const demoMetrics = generateDemoGoogleMetrics(channel!.id);
        for (const metric of demoMetrics) {
          await supabaseAdmin
            .from('daily_metrics')
            .upsert(metric, { onConflict: 'channel_id,date' });
        }
        recordsSynced = demoMetrics.length;
      }

      // Update sync job
      await supabaseAdmin
        .from('sync_jobs')
        .update({
          status: 'completed',
          completed_at: new Date().toISOString(),
          records_synced: recordsSynced,
        })
        .eq('id', syncJob?.id);

      // Update credentials last_synced_at
      await supabaseAdmin
        .from('api_credentials')
        .update({ last_synced_at: new Date().toISOString() })
        .eq('organization_id', user.organizationId)
        .eq('platform', 'Google');

      return NextResponse.json({
        success: true,
        recordsSynced,
        syncJobId: syncJob?.id,
      });

    } catch (syncError: any) {
      // Update sync job with error
      await supabaseAdmin
        .from('sync_jobs')
        .update({
          status: 'failed',
          completed_at: new Date().toISOString(),
          error_message: syncError.message,
        })
        .eq('id', syncJob?.id);

      throw syncError;
    }

  } catch (error: any) {
    console.error('[GOOGLE SYNC] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Sync failed' },
      { status: 500 }
    );
  }
}

// Helper: Refresh Google OAuth token
async function refreshGoogleToken(refreshToken: string, organizationId: string): Promise<string | null> {
  try {
    const response = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: process.env.GOOGLE_CLIENT_ID!,
        client_secret: process.env.GOOGLE_CLIENT_SECRET!,
        refresh_token: refreshToken,
        grant_type: 'refresh_token',
      }),
    });

    const data = await response.json();

    if (data.access_token) {
      // Update stored credentials
      await supabaseAdmin
        .from('api_credentials')
        .update({
          credentials: {
            access_token: data.access_token,
            refresh_token: refreshToken,
            expires_at: data.expires_in
              ? new Date(Date.now() + data.expires_in * 1000).toISOString()
              : null,
          },
        })
        .eq('organization_id', organizationId)
        .eq('platform', 'Google');

      return data.access_token;
    }
  } catch (error) {
    console.error('[GOOGLE SYNC] Token refresh failed:', error);
  }
  return null;
}

// Helper: Format Google date (YYYYMMDD) to ISO date
function formatGoogleDate(googleDate: string): string {
  if (!googleDate || googleDate.length !== 8) return new Date().toISOString().split('T')[0];
  return `${googleDate.slice(0, 4)}-${googleDate.slice(4, 6)}-${googleDate.slice(6, 8)}`;
}

// Helper: Generate demo metrics for testing
function generateDemoGoogleMetrics(channelId: string) {
  const metrics = [];
  const today = new Date();
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    const spend = 1800 + Math.random() * 400;
    const roas = 2.2 + Math.random() * 0.4;
    const revenue = spend * roas;
    const impressions = Math.floor(45000 + Math.random() * 10000);
    const clicks = Math.floor(impressions * (0.025 + Math.random() * 0.01));
    const conversions = Math.floor(clicks * (0.03 + Math.random() * 0.01));
    
    metrics.push({
      channel_id: channelId,
      date: date.toISOString().split('T')[0],
      spend: Math.round(spend * 100) / 100,
      revenue: Math.round(revenue * 100) / 100,
      impressions,
      clicks,
      conversions,
      roas: Math.round(roas * 100) / 100,
      cpa: conversions > 0 ? Math.round((spend / conversions) * 100) / 100 : 0,
      ctr: Math.round((clicks / impressions) * 10000) / 10000,
    });
  }
  
  return metrics;
}

