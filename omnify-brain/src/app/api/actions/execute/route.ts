import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser, requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { validatePlatform } from '@/lib/validation';

export async function POST(request: NextRequest) {
  try {
    const user = await requireRole('member', request); // Member or admin can execute actions
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

    // Platform validation
    const validation = validatePlatform(platform);
    if (!validation.valid) {
      return validation.error!;
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
  // Get channel details
  const { data: fromChannel } = await supabaseAdmin
    .from('channels')
    .select('external_id, name')
    .eq('id', fromChannelId)
    .single();

  const { data: toChannel } = await supabaseAdmin
    .from('channels')
    .select('external_id, name')
    .eq('id', toChannelId)
    .single();

  if (!fromChannel || !toChannel) {
    return { success: false, error: 'Channel not found' };
  }

  if (platform === 'Meta') {
    try {
      // Get campaigns for the source channel and reduce budget
      const campaignsResponse = await fetch(
        `https://graph.facebook.com/v18.0/${fromChannel.external_id}/campaigns?` +
        `fields=id,name,daily_budget&access_token=${credentials.access_token}`
      );
      const campaignsData = await campaignsResponse.json();

      if (campaignsData.data && campaignsData.data.length > 0) {
        // Reduce budget from first active campaign
        const campaign = campaignsData.data[0];
        const currentBudget = parseInt(campaign.daily_budget) / 100; // Meta uses cents
        const newBudget = Math.max(0, currentBudget - amount);

        await fetch(
          `https://graph.facebook.com/v18.0/${campaign.id}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              daily_budget: Math.round(newBudget * 100),
              access_token: credentials.access_token,
            }),
          }
        );
      }

      // Get campaigns for destination channel and increase budget
      const toCampaignsResponse = await fetch(
        `https://graph.facebook.com/v18.0/${toChannel.external_id}/campaigns?` +
        `fields=id,name,daily_budget&access_token=${credentials.access_token}`
      );
      const toCampaignsData = await toCampaignsResponse.json();

      if (toCampaignsData.data && toCampaignsData.data.length > 0) {
        const campaign = toCampaignsData.data[0];
        const currentBudget = parseInt(campaign.daily_budget) / 100;
        const newBudget = currentBudget + amount;

        await fetch(
          `https://graph.facebook.com/v18.0/${campaign.id}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              daily_budget: Math.round(newBudget * 100),
              access_token: credentials.access_token,
            }),
          }
        );
      }

      return {
        success: true,
        actionId: `shift_${fromChannelId}_to_${toChannelId}`,
        message: `Shifted $${amount} from ${fromChannel.name} to ${toChannel.name}`,
      };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // For other platforms or demo mode, simulate success
  return {
    success: true,
    actionId: `shift_${fromChannelId}_to_${toChannelId}`,
    message: `[Simulated] Shifted $${amount} from ${fromChannel.name} to ${toChannel.name}`,
  };
}

async function executeIncreaseBudget(
  platform: string,
  credentials: any,
  targetId: string,
  amount: number
) {
  // Get channel/campaign details
  const { data: channel } = await supabaseAdmin
    .from('channels')
    .select('external_id, name')
    .eq('id', targetId)
    .single();

  if (!channel) {
    return { success: false, error: 'Channel not found' };
  }

  if (platform === 'Meta') {
    try {
      // Get campaigns for this channel
      const campaignsResponse = await fetch(
        `https://graph.facebook.com/v18.0/${channel.external_id}/campaigns?` +
        `fields=id,name,daily_budget&access_token=${credentials.access_token}`
      );
      const campaignsData = await campaignsResponse.json();

      if (campaignsData.data && campaignsData.data.length > 0) {
        const campaign = campaignsData.data[0];
        const currentBudget = parseInt(campaign.daily_budget) / 100;
        const newBudget = currentBudget + amount;

        const updateResponse = await fetch(
          `https://graph.facebook.com/v18.0/${campaign.id}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              daily_budget: Math.round(newBudget * 100),
              access_token: credentials.access_token,
            }),
          }
        );

        if (!updateResponse.ok) {
          const error = await updateResponse.json();
          return { success: false, error: error.error?.message || 'Failed to update budget' };
        }

        return {
          success: true,
          actionId: `increase_${targetId}`,
          message: `Increased ${channel.name} budget by $${amount}`,
        };
      }

      return { success: false, error: 'No campaigns found' };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // For other platforms or demo mode, simulate success
  return {
    success: true,
    actionId: `increase_${targetId}`,
    message: `[Simulated] Increased ${channel.name} budget by $${amount}`,
  };
}

