import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/db/supabase';

const TIKTOK_APP_ID = process.env.TIKTOK_APP_ID;
const TIKTOK_APP_SECRET = process.env.TIKTOK_APP_SECRET;
const BASE_URL = process.env.NEXTAUTH_URL || 'http://localhost:3000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');

    if (error) {
      return NextResponse.redirect(
        new URL(`/onboarding?error=${encodeURIComponent(error)}`, request.url)
      );
    }

    if (!code || !state) {
      return NextResponse.redirect(
        new URL('/onboarding?error=missing_params', request.url)
      );
    }

    const stateData = JSON.parse(Buffer.from(state, 'base64').toString());
    const { organizationId } = stateData;

    // Exchange code for access token
    const redirectUri = `${BASE_URL}/api/connectors/tiktok/callback`;
    const tokenResponse = await fetch('https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_id: TIKTOK_APP_ID,
        secret: TIKTOK_APP_SECRET,
        auth_code: code,
        grant_type: 'authorization_code',
      }),
    });

    const tokenData = await tokenResponse.json();

    if (!tokenData.data?.access_token) {
      return NextResponse.redirect(
        new URL('/onboarding?error=token_exchange_failed', request.url)
      );
    }

    // Store credentials
    await supabaseAdmin
      .from('api_credentials')
      .upsert({
        organization_id: organizationId,
        platform: 'TikTok',
        credentials: {
          access_token: tokenData.data.access_token,
          refresh_token: tokenData.data.refresh_token,
          expires_at: tokenData.data.expires_in
            ? new Date(Date.now() + tokenData.data.expires_in * 1000).toISOString()
            : null,
        },
        is_active: true,
        last_synced_at: null,
      }, {
        onConflict: 'organization_id,platform',
      });

    return NextResponse.redirect(
      new URL('/onboarding?platform=tiktok&connected=true', request.url)
    );
  } catch (error: any) {
    console.error('[TIKTOK CALLBACK] Error:', error);
    return NextResponse.redirect(
      new URL(`/onboarding?error=${encodeURIComponent(error.message)}`, request.url)
    );
  }
}

