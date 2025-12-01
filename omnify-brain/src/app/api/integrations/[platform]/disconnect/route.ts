import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * POST /api/integrations/[platform]/disconnect
 * 
 * Disconnects an integration by deactivating the credentials.
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { platform: string } }
) {
  try {
    const user = await getCurrentUser(request);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const platform = params.platform;
    const platformMap: Record<string, string> = {
      meta: 'Meta',
      google: 'Google',
      tiktok: 'TikTok',
      shopify: 'Shopify',
    };

    const platformName = platformMap[platform.toLowerCase()];
    if (!platformName) {
      return NextResponse.json(
        { error: 'Invalid platform' },
        { status: 400 }
      );
    }

    // Deactivate credentials (soft delete)
    const { error } = await supabaseAdmin
      .from('api_credentials')
      .update({
        is_active: false,
        updated_at: new Date().toISOString(),
      })
      .eq('organization_id', user.organizationId)
      .eq('platform', platformName);

    if (error) {
      console.error('[DISCONNECT] Error:', error);
      return NextResponse.json(
        { error: 'Failed to disconnect integration' },
        { status: 500 }
      );
    }

    // Log the disconnection
    await supabaseAdmin
      .from('action_logs')
      .insert({
        organization_id: user.organizationId,
        user_id: user.id,
        action_type: 'disconnect_integration',
        target_id: platformName,
        target_type: 'integration',
        status: 'completed',
        result: { platform: platformName },
        created_at: new Date().toISOString(),
      });

    return NextResponse.json({
      success: true,
      message: `${platformName} disconnected successfully`,
    });
  } catch (error: any) {
    console.error('[DISCONNECT] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to disconnect' },
      { status: 500 }
    );
  }
}
