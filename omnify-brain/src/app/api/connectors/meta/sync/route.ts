import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { validatePlatform } from '@/lib/validation';

export async function POST(request: NextRequest) {
  // Platform validation
  const validation = validatePlatform('meta_ads');
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

    // Get Meta credentials
    const { data: credentials, error: credError } = await supabaseAdmin
      .from('api_credentials')
      .select('credentials')
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Meta')
      .eq('is_active', true)
      .single();

    if (credError || !credentials) {
      return NextResponse.json(
        { error: 'Meta Ads not connected' },
        { status: 400 }
      );
    }

    const { access_token, ad_accounts } = credentials.credentials as any;
    if (!access_token || !ad_accounts || ad_accounts.length === 0) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 400 }
      );
    }

    // Create sync job
    const { data: syncJob, error: jobError } = await supabaseAdmin
      .from('sync_jobs')
      .insert({
        organization_id: user.organizationId,
        platform: 'Meta',
        status: 'running',
        started_at: new Date().toISOString(),
        records_synced: 0,
      })
      .select()
      .single();

    if (jobError || !syncJob) {
      return NextResponse.json(
        { error: 'Failed to create sync job' },
        { status: 500 }
      );
    }

    // Fetch data from Meta Ads API (simplified - in production, fetch campaigns, ads, insights)
    const adAccountId = ad_accounts[0].id;
    const dateRange = {
      since: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      until: new Date().toISOString().split('T')[0],
    };

    // Fetch insights for the ad account
    const insightsUrl = `https://graph.facebook.com/v18.0/${adAccountId}/insights?` +
      `access_token=${access_token}&` +
      `time_range={'since':'${dateRange.since}','until':'${dateRange.until}'}&` +
      `fields=spend,impressions,clicks,actions,date_start,date_stop&` +
      `level=account`;

    const insightsResponse = await fetch(insightsUrl);
    const insightsData = await insightsResponse.json();

    // Get or create Meta channel
    let { data: channel } = await supabaseAdmin
      .from('channels')
      .select('id')
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Meta')
      .single();

    if (!channel) {
      const { data: newChannel } = await supabaseAdmin
        .from('channels')
        .insert({
          organization_id: user.organizationId,
          name: 'Meta Ads',
          platform: 'Meta',
          external_id: adAccountId,
          is_active: true,
        })
        .select()
        .single();
      channel = newChannel;
    }

    // Map insights to daily_metrics
    const recordsToInsert = [];
    if (insightsData.data && Array.isArray(insightsData.data)) {
      for (const insight of insightsData.data) {
        const revenue = insight.actions?.find((a: any) => a.action_type === 'purchase')?.value || 0;
        const conversions = insight.actions?.find((a: any) => a.action_type === 'purchase')?.value || 0;
        
        recordsToInsert.push({
          channel_id: channel!.id,
          date: insight.date_start,
          spend: parseFloat(insight.spend || 0),
          revenue: parseFloat(revenue),
          impressions: parseInt(insight.impressions || 0),
          clicks: parseInt(insight.clicks || 0),
          conversions: parseInt(conversions),
          roas: revenue > 0 && parseFloat(insight.spend) > 0 
            ? parseFloat(revenue) / parseFloat(insight.spend) 
            : 0,
          cpa: conversions > 0 && parseFloat(insight.spend) > 0
            ? parseFloat(insight.spend) / parseInt(conversions)
            : 0,
          ctr: parseInt(insight.impressions) > 0
            ? parseInt(insight.clicks) / parseInt(insight.impressions)
            : 0,
        });
      }
    }

    // Insert daily metrics (upsert to avoid duplicates)
    if (recordsToInsert.length > 0) {
      for (const record of recordsToInsert) {
        await supabaseAdmin
          .from('daily_metrics')
          .upsert(record, {
            onConflict: 'channel_id,date',
          });
      }
    }

    // Update sync job
    await supabaseAdmin
      .from('sync_jobs')
      .update({
        status: 'completed',
        completed_at: new Date().toISOString(),
        records_synced: recordsToInsert.length,
      })
      .eq('id', syncJob.id);

    // Update credentials last_synced_at
    await supabaseAdmin
      .from('api_credentials')
      .update({
        last_synced_at: new Date().toISOString(),
      })
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Meta');

    return NextResponse.json({
      success: true,
      recordsSynced: recordsToInsert.length,
      syncJobId: syncJob.id,
    });
  } catch (error: any) {
    console.error('[META SYNC] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Sync failed' },
      { status: 500 }
    );
  }
}

