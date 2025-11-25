import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser, requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

export async function POST(request: NextRequest) {
  try {
    const user = await requireRole('member'); // Member or admin can execute actions
    const { actionType, targetId, targetType, amount, fromChannelId, toChannelId } = await request.json();

    if (!actionType || !targetId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Get platform credentials based on action
    let platform = '';
    if (targetType === 'creative' || targetType === 'campaign') {
      // Determine platform from creative/campaign
      const { data: creative } = await supabaseAdmin
        .from('creatives')
        .select('channel:channels(platform)')
        .eq('id', targetId)
        .single();
      
      if (creative) {
        platform = (creative.channel as any)?.platform || '';
      }
    } else if (fromChannelId || toChannelId) {
      const channelId = fromChannelId || toChannelId;
      const { data: channel } = await supabaseAdmin
        .from('channels')
        .select('platform')
        .eq('id', channelId)
        .single();
      
      if (channel) {
        platform = channel.platform;
      }
    }

    if (!platform) {
      return NextResponse.json(
        { error: 'Could not determine platform' },
        { status: 400 }
      );
    }

    // Get credentials
    const { data: credentials } = await supabaseAdmin
      .from('api_credentials')
      .select('credentials')
      .eq('organization_id', user.organizationId)
      .eq('platform', platform)
      .eq('is_active', true)
      .single();

    if (!credentials) {
      return NextResponse.json(
        { error: `${platform} not connected` },
        { status: 400 }
      );
    }

    let result;

    // Execute action based on type
    switch (actionType) {
      case 'pause_creative':
        result = await executePauseCreative(
          platform,
          credentials.credentials as any,
          targetId
        );
        break;

      case 'shift_budget':
        result = await executeShiftBudget(
          platform,
          credentials.credentials as any,
          fromChannelId!,
          toChannelId!,
          amount
        );
        break;

      case 'increase_budget':
        result = await executeIncreaseBudget(
          platform,
          credentials.credentials as any,
          targetId,
          amount
        );
        break;

      default:
        return NextResponse.json(
          { error: 'Unknown action type' },
          { status: 400 }
        );
    }

    // Log action
    await supabaseAdmin
      .from('action_logs')
      .insert({
        organization_id: user.organizationId,
        user_id: user.id,
        action_type: actionType,
        target_id: targetId,
        platform,
        status: result.success ? 'completed' : 'failed',
        error_message: result.error || null,
        executed_at: new Date().toISOString(),
      });

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || 'Action execution failed' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      actionId: result.actionId,
      message: result.message,
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json(
        { error: error.message },
        { status: 403 }
      );
    }

    console.error('[ACTION EXECUTE] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Action execution failed' },
      { status: 500 }
    );
  }
}

// Action execution helpers
async function executePauseCreative(
  platform: string,
  credentials: any,
  creativeId: string
) {
  if (platform === 'Meta') {
    // Get creative external ID
    const { data: creative } = await supabaseAdmin
      .from('creatives')
      .select('external_id')
      .eq('id', creativeId)
      .single();

    if (!creative?.external_id) {
      return { success: false, error: 'Creative external ID not found' };
    }

    // Pause ad in Meta
    const response = await fetch(
      `https://graph.facebook.com/v18.0/${creative.external_id}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'PAUSED',
          access_token: credentials.access_token,
        }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      return { success: false, error: error.error?.message || 'Failed to pause creative' };
    }

    // Update creative status in our DB
    await supabaseAdmin
      .from('creatives')
      .update({ status: 'paused' })
      .eq('id', creativeId);

    return { success: true, actionId: `pause_${creativeId}`, message: 'Creative paused successfully' };
  }

  return { success: false, error: `Platform ${platform} not yet implemented` };
}

async function executeShiftBudget(
  platform: string,
  credentials: any,
  fromChannelId: string,
  toChannelId: string,
  amount: number
) {
  // TODO: Implement budget shift for each platform
  // This requires platform-specific API calls to adjust campaign/ad set budgets
  return { success: false, error: 'Budget shift not yet implemented' };
}

async function executeIncreaseBudget(
  platform: string,
  credentials: any,
  targetId: string,
  amount: number
) {
  // TODO: Implement budget increase for each platform
  return { success: false, error: 'Budget increase not yet implemented' };
}

