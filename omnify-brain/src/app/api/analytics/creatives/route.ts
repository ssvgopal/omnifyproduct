import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/analytics/creatives
 * 
 * Returns per-creative analytics with fatigue indicators.
 * Query params:
 * - period: '7d' | '30d' | '90d' (default: '30d')
 * - channelId: optional filter by channel
 * - status: 'active' | 'paused' | 'all' (default: 'all')
 */
export async function GET(request: NextRequest) {
  try {
    const user = await requireRole('member', request);
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '30d';
    const channelId = searchParams.get('channelId');
    const status = searchParams.get('status') || 'all';

    const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    const startDateStr = startDate.toISOString().split('T')[0];

    // Build creatives query
    let creativesQuery = supabaseAdmin
      .from('creatives')
      .select(`
        id,
        name,
        status,
        launch_date,
        thumbnail_url,
        channel:channels(id, name, platform)
      `)
      .eq('organization_id', user.organizationId);

    if (channelId) {
      creativesQuery = creativesQuery.eq('channel_id', channelId);
    }
    if (status !== 'all') {
      creativesQuery = creativesQuery.eq('status', status);
    }

    const { data: creatives, error: creativesError } = await creativesQuery;

    if (creativesError) {
      console.error('[ANALYTICS] Creatives fetch error:', creativesError);
      return NextResponse.json({ error: 'Failed to fetch creatives' }, { status: 500 });
    }

    // Get creative daily metrics
    const { data: metrics, error: metricsError } = await supabaseAdmin
      .from('creative_daily_metrics')
      .select('creative_id, date, spend, revenue, impressions, clicks, conversions, cvr, cpa, frequency')
      .in('creative_id', (creatives || []).map(c => c.id))
      .gte('date', startDateStr)
      .order('date', { ascending: false });

    if (metricsError) {
      console.error('[ANALYTICS] Creative metrics fetch error:', metricsError);
      return NextResponse.json({ error: 'Failed to fetch creative metrics' }, { status: 500 });
    }

    // Process each creative
    const creativeAnalytics = (creatives || []).map(creative => {
      const creativeMetrics = (metrics || []).filter(m => m.creative_id === creative.id);

      // Calculate totals
      const totals = creativeMetrics.reduce(
        (acc, m) => ({
          spend: acc.spend + (m.spend || 0),
          revenue: acc.revenue + (m.revenue || 0),
          impressions: acc.impressions + (m.impressions || 0),
          clicks: acc.clicks + (m.clicks || 0),
          conversions: acc.conversions + (m.conversions || 0),
        }),
        { spend: 0, revenue: 0, impressions: 0, clicks: 0, conversions: 0 }
      );

      const roas = totals.spend > 0 ? totals.revenue / totals.spend : 0;
      const ctr = totals.impressions > 0 ? (totals.clicks / totals.impressions) * 100 : 0;
      const cvr = totals.clicks > 0 ? (totals.conversions / totals.clicks) * 100 : 0;
      const cpa = totals.conversions > 0 ? totals.spend / totals.conversions : 0;

      // Calculate fatigue indicators
      const recent7 = creativeMetrics.slice(0, 7);
      const baseline14 = creativeMetrics.slice(7, 21);

      const recentCvr = recent7.length > 0
        ? recent7.reduce((sum, m) => sum + (m.cvr || 0), 0) / recent7.length
        : 0;
      const baselineCvr = baseline14.length > 0
        ? baseline14.reduce((sum, m) => sum + (m.cvr || 0), 0) / baseline14.length
        : 0;
      const recentFreq = recent7.length > 0
        ? recent7.reduce((sum, m) => sum + (m.frequency || 0), 0) / recent7.length
        : 0;

      const cvrDrop = baselineCvr > 0 ? ((baselineCvr - recentCvr) / baselineCvr) * 100 : 0;
      const isFatiguing = cvrDrop > 20 || recentFreq > 3.5;

      // Calculate days since launch
      const launchDate = creative.launch_date ? new Date(creative.launch_date) : null;
      const daysSinceLaunch = launchDate
        ? Math.floor((Date.now() - launchDate.getTime()) / (1000 * 60 * 60 * 24))
        : null;

      // Sparkline data
      const sparkline = creativeMetrics
        .slice(0, 14)
        .reverse()
        .map(m => ({
          date: m.date,
          revenue: m.revenue || 0,
          cvr: m.cvr || 0,
        }));

      return {
        id: creative.id,
        name: creative.name,
        status: creative.status,
        thumbnailUrl: creative.thumbnail_url,
        channel: creative.channel,
        daysSinceLaunch,
        totals: {
          spend: Math.round(totals.spend * 100) / 100,
          revenue: Math.round(totals.revenue * 100) / 100,
          impressions: totals.impressions,
          clicks: totals.clicks,
          conversions: totals.conversions,
        },
        metrics: {
          roas: Math.round(roas * 100) / 100,
          ctr: Math.round(ctr * 100) / 100,
          cvr: Math.round(cvr * 100) / 100,
          cpa: Math.round(cpa * 100) / 100,
        },
        fatigue: {
          isFatiguing,
          cvrDrop: Math.round(cvrDrop * 10) / 10,
          frequency: Math.round(recentFreq * 100) / 100,
          recentCvr: Math.round(recentCvr * 10000) / 100,
          baselineCvr: Math.round(baselineCvr * 10000) / 100,
        },
        sparkline,
      };
    });

    // Sort by revenue descending
    creativeAnalytics.sort((a, b) => b.totals.revenue - a.totals.revenue);

    return NextResponse.json({
      period,
      creatives: creativeAnalytics,
      summary: {
        total: creativeAnalytics.length,
        active: creativeAnalytics.filter(c => c.status === 'active').length,
        fatiguing: creativeAnalytics.filter(c => c.fatigue.isFatiguing).length,
      },
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[ANALYTICS] Creatives error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
