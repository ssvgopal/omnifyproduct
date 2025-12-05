import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/analytics/summary
 * 
 * Returns aggregated analytics summary for the organization.
 * Query params:
 * - period: '7d' | '30d' | '90d' (default: '30d')
 */
export async function GET(request: NextRequest) {
  try {
    const user = await requireRole('member', request);
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '30d';

    // Calculate date range
    const days = period === '7d' ? 7 : period === '90d' ? 90 : 30;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    const startDateStr = startDate.toISOString().split('T')[0];

    // Get daily metrics for the period
    const { data: metrics, error: metricsError } = await supabaseAdmin
      .from('daily_metrics')
      .select(`
        date,
        spend,
        revenue,
        impressions,
        clicks,
        conversions,
        roas,
        cpa,
        channel:channels(id, name, platform)
      `)
      .eq('organization_id', user.organizationId)
      .gte('date', startDateStr)
      .order('date', { ascending: true });

    if (metricsError) {
      console.error('[ANALYTICS] Metrics fetch error:', metricsError);
      return NextResponse.json(
        { error: 'Failed to fetch metrics' },
        { status: 500 }
      );
    }

    // Calculate totals
    const totals = (metrics || []).reduce(
      (acc, m) => ({
        spend: acc.spend + (m.spend || 0),
        revenue: acc.revenue + (m.revenue || 0),
        impressions: acc.impressions + (m.impressions || 0),
        clicks: acc.clicks + (m.clicks || 0),
        conversions: acc.conversions + (m.conversions || 0),
      }),
      { spend: 0, revenue: 0, impressions: 0, clicks: 0, conversions: 0 }
    );

    // Calculate derived metrics
    const roas = totals.spend > 0 ? totals.revenue / totals.spend : 0;
    const ctr = totals.impressions > 0 ? (totals.clicks / totals.impressions) * 100 : 0;
    const cvr = totals.clicks > 0 ? (totals.conversions / totals.clicks) * 100 : 0;
    const cpa = totals.conversions > 0 ? totals.spend / totals.conversions : 0;
    const cac = cpa; // CAC = CPA for acquisition campaigns

    // Get cohort data for CLV
    const { data: cohorts } = await supabaseAdmin
      .from('cohorts')
      .select('ltv_90d, customer_count')
      .eq('organization_id', user.organizationId)
      .order('cohort_month', { ascending: false })
      .limit(3);

    const clv90d = cohorts && cohorts.length > 0
      ? cohorts.reduce((sum, c) => sum + (c.ltv_90d || 0), 0) / cohorts.length
      : 0;

    // Calculate daily trends for sparklines
    const dailyTrends = (metrics || []).reduce((acc: Record<string, any[]>, m) => {
      const date = m.date;
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(m);
      return acc;
    }, {});

    const sparklineData = Object.entries(dailyTrends).map(([date, dayMetrics]) => {
      const dayTotals = (dayMetrics as any[]).reduce(
        (acc, m) => ({
          spend: acc.spend + (m.spend || 0),
          revenue: acc.revenue + (m.revenue || 0),
        }),
        { spend: 0, revenue: 0 }
      );
      return {
        date,
        spend: dayTotals.spend,
        revenue: dayTotals.revenue,
        roas: dayTotals.spend > 0 ? dayTotals.revenue / dayTotals.spend : 0,
      };
    });

    // Calculate period-over-period change
    const midpoint = Math.floor(sparklineData.length / 2);
    const firstHalf = sparklineData.slice(0, midpoint);
    const secondHalf = sparklineData.slice(midpoint);

    const firstHalfRevenue = firstHalf.reduce((sum, d) => sum + d.revenue, 0);
    const secondHalfRevenue = secondHalf.reduce((sum, d) => sum + d.revenue, 0);
    const revenueChange = firstHalfRevenue > 0
      ? ((secondHalfRevenue - firstHalfRevenue) / firstHalfRevenue) * 100
      : 0;

    return NextResponse.json({
      period,
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
        cac: Math.round(cac * 100) / 100,
        clv90d: Math.round(clv90d * 100) / 100,
      },
      trends: {
        revenueChange: Math.round(revenueChange * 10) / 10,
        sparkline: sparklineData,
      },
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[ANALYTICS] Summary error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
