import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/integrations
 * 
 * Returns the status of all integrations for the current organization.
 */
export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser(request);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get all credentials for this organization
    const { data: credentials, error } = await supabaseAdmin
      .from('api_credentials')
      .select('platform, is_active, last_synced_at, created_at')
      .eq('organization_id', user.organizationId);

    if (error) {
      console.error('[INTEGRATIONS] Error fetching credentials:', error);
      return NextResponse.json(
        { error: 'Failed to fetch integrations' },
        { status: 500 }
      );
    }

    // Map to integration status
    const PLATFORMS = ['Meta', 'Google', 'TikTok', 'Shopify'];
    const PLATFORM_NAMES: Record<string, string> = {
      Meta: 'Meta Ads',
      Google: 'Google Ads',
      TikTok: 'TikTok Ads',
      Shopify: 'Shopify',
    };
    const PLATFORM_ICONS: Record<string, string> = {
      Meta: '📘',
      Google: '🔍',
      TikTok: '🎵',
      Shopify: '🛍️',
    };

    const integrations = PLATFORMS.map(platform => {
      const cred = credentials?.find(c => c.platform === platform);
      
      return {
        id: platform.toLowerCase(),
        platform,
        name: PLATFORM_NAMES[platform],
        icon: PLATFORM_ICONS[platform],
        status: cred?.is_active ? 'connected' : 'disconnected',
        lastSynced: cred?.last_synced_at || null,
        connectedAt: cred?.created_at || null,
      };
    });

    return NextResponse.json({ integrations });
  } catch (error: any) {
    console.error('[INTEGRATIONS] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}
