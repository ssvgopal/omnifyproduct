import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { validatePlatform } from '@/lib/validation';

export async function POST(request: NextRequest) {
  // Platform validation
  const validation = validatePlatform('tiktok_ads');
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

    // Get TikTok credentials
    const { data: credentials } = await supabaseAdmin
      .from('api_credentials')
      .select('credentials')
      .eq('organization_id', user.organizationId)
      .eq('platform', 'TikTok')
      .eq('is_active', true)
      .single();

    if (!credentials) {
      return NextResponse.json(
        { error: 'TikTok Ads not connected' },
        { status: 400 }
      );
    }

    // Create sync job
    const { data: syncJob } = await supabaseAdmin
      .from('sync_jobs')
      .insert({
        organization_id: user.organizationId,
        platform: 'TikTok',
        status: 'running',
        started_at: new Date().toISOString(),
        records_synced: 0,
      })
      .select()
      .single();

    // TODO: Implement TikTok Ads API sync
    // For now, return placeholder

    await supabaseAdmin
      .from('sync_jobs')
      .update({
        status: 'completed',
        completed_at: new Date().toISOString(),
        records_synced: 0,
      })
      .eq('id', syncJob?.id);

    return NextResponse.json({
      success: true,
      recordsSynced: 0,
      message: 'TikTok Ads sync not yet implemented',
    });
  } catch (error: any) {
    console.error('[TIKTOK SYNC] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Sync failed' },
      { status: 500 }
    );
  }
}

