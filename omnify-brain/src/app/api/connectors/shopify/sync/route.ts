import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { validatePlatform } from '@/lib/validation';

export async function POST(request: NextRequest) {
  // Platform validation
  const validation = validatePlatform('shopify');
  if (!validation.valid) {
    return validation.error!;
  }
  try {
    const user = await getCurrentUser();
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get Shopify credentials
    const { data: credentials } = await supabaseAdmin
      .from('api_credentials')
      .select('credentials')
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Shopify')
      .eq('is_active', true)
      .single();

    if (!credentials) {
      return NextResponse.json(
        { error: 'Shopify not connected' },
        { status: 400 }
      );
    }

    const { access_token, shop_domain } = credentials.credentials as any;

    // Create sync job
    const { data: syncJob } = await supabaseAdmin
      .from('sync_jobs')
      .insert({
        organization_id: user.organizationId,
        platform: 'Shopify',
        status: 'running',
        started_at: new Date().toISOString(),
        records_synced: 0,
      })
      .select()
      .single();

    // Fetch orders from Shopify
    const ordersResponse = await fetch(
      `https://${shop_domain}/admin/api/2024-01/orders.json?limit=250&status=any`,
      {
        headers: {
          'X-Shopify-Access-Token': access_token,
        },
      }
    );

    const ordersData = await ordersResponse.json();
    const orders = ordersData.orders || [];

    // Calculate cohorts from orders
    const cohortsMap = new Map<string, { customer_count: number; revenue_30d: number; revenue_60d: number; revenue_90d: number }>();

    for (const order of orders) {
      const orderDate = new Date(order.created_at);
      const cohortMonth = `${orderDate.getFullYear()}-${String(orderDate.getMonth() + 1).padStart(2, '0')}`;
      
      if (!cohortsMap.has(cohortMonth)) {
        cohortsMap.set(cohortMonth, {
          customer_count: 0,
          revenue_30d: 0,
          revenue_60d: 0,
          revenue_90d: 0,
        });
      }

      const cohort = cohortsMap.get(cohortMonth)!;
      cohort.customer_count += 1;
      
      const daysSinceOrder = Math.floor((Date.now() - orderDate.getTime()) / (1000 * 60 * 60 * 24));
      const orderTotal = parseFloat(order.total_price || 0);

      if (daysSinceOrder <= 30) cohort.revenue_30d += orderTotal;
      if (daysSinceOrder <= 60) cohort.revenue_60d += orderTotal;
      if (daysSinceOrder <= 90) cohort.revenue_90d += orderTotal;
    }

    // Insert/update cohorts
    for (const [cohortMonth, data] of cohortsMap.entries()) {
      await supabaseAdmin
        .from('cohorts')
        .upsert({
          cohort_month: cohortMonth,
          customer_count: data.customer_count,
          ltv_30d: data.revenue_30d / data.customer_count,
          ltv_60d: data.revenue_60d / data.customer_count,
          ltv_90d: data.revenue_90d / data.customer_count,
        }, {
          onConflict: 'cohort_month',
        });
    }

    // Update sync job
    await supabaseAdmin
      .from('sync_jobs')
      .update({
        status: 'completed',
        completed_at: new Date().toISOString(),
        records_synced: orders.length,
      })
      .eq('id', syncJob?.id);

    // Update credentials
    await supabaseAdmin
      .from('api_credentials')
      .update({
        last_synced_at: new Date().toISOString(),
      })
      .eq('organization_id', user.organizationId)
      .eq('platform', 'Shopify');

    return NextResponse.json({
      success: true,
      recordsSynced: orders.length,
      cohortsCreated: cohortsMap.size,
      syncJobId: syncJob?.id,
    });
  } catch (error: any) {
    console.error('[SHOPIFY SYNC] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Sync failed' },
      { status: 500 }
    );
  }
}

