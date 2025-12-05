import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/analytics/channels
 * 
 * Returns per-channel analytics breakdown.
 * Query params:
 * - period: '7d' | '30d' | '90d' (default: '30d')
 */
export async function GET(request: NextRequest) {
  try {
    const user = await requireRole('member', request);
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '30d';

    const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    const startDateStr = startDate.toISOString().split('T')[0];

    // Get channels for this organization
    const { data: channels, error: channelsError } = await supabaseAdmin
      .from('channels')
      .select('id, name, platform')
      .eq('organization_id', user.organizationId);

    if (channelsError) {
      console.error('[ANALYTICS] Channels fetch error:', channelsError);
      return NextResponse.json({ error: 'Failed to fetch channels' }, { status: 500 });
    }

    // Get metrics per channel
    const { data: metrics, error: metricsError } = await supabaseAdmin
      .from('daily_metrics')
      .select('channel_id, date, spend, revenue, impressions, clicks, conversions')
      .eq('organization_id', user.organizationId)
      .gte('date', startDateStr);

    if (metricsError) {
      console.error('[ANALYTICS] Metrics fetch error:', metricsError);
      return NextResponse.json({ error: 'Failed to fetch metrics' }, { status: 500 });
    }

    // Aggregate by channel
    const channelMetrics = (channels || []).map(channel => {
      const channelData = (metrics || []).filter(m => m.channel_id === channel.id);
      
      const totals = channelData.reduce(
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

      // Calculate trend (last 7 days vs prior 7 days)
      const sortedData = channelData.sort((a, b) => 
        new Date(b.date).getTime() - new Date(a.date).getTime()
      );
      const recent7 = sortedData.slice(0, 7);
      const prior7 = sortedData.slice(7, 14);

      const recentRevenue = recent7.reduce((sum, m) => sum + (m.revenue || 0), 0);
      const priorRevenue = prior7.reduce((sum, m) => sum + (m.revenue || 0), 0);
      const trend = priorRevenue > 0 
        ? ((recentRevenue - priorRevenue) / priorRevenue) * 100 
        : 0;

      // Sparkline data (daily revenue for the period)
      const dailyData = channelData.reduce((acc: Record<string, number>, m) => {
        acc[m.date] = (acc[m.date] || 0) + (m.revenue || 0);
        return acc;
      }, {});

      const sparkline = Object.entries(dailyData)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, revenue]) => ({ date, revenue }));

      return {
        id: channel.id,
        name: channel.name,
        platform: channel.platform,
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
        trend: Math.round(trend * 10) / 10,
        sparkline,
      };
    });

    // Sort by revenue descending
    channelMetrics.sort((a, b) => b.totals.revenue - a.totals.revenue);

    return NextResponse.json({
      period,
      channels: channelMetrics,
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[ANALYTICS] Channels error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
