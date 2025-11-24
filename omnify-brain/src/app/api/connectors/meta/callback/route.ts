import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

const META_APP_ID = process.env.META_APP_ID;
const META_APP_SECRET = process.env.META_APP_SECRET;
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

    // Decode state to get user info
    const stateData = JSON.parse(Buffer.from(state, 'base64').toString());
    const { userId, organizationId } = stateData;

    // Exchange code for access token
    const redirectUri = `${BASE_URL}/api/connectors/meta/callback`;
    const tokenResponse = await fetch(
      `https://graph.facebook.com/v18.0/oauth/access_token?` +
      `client_id=${META_APP_ID}&` +
      `client_secret=${META_APP_SECRET}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `code=${code}`,
      { method: 'GET' }
    );

    const tokenData = await tokenResponse.json();

    if (!tokenData.access_token) {
      return NextResponse.redirect(
        new URL('/onboarding?error=token_exchange_failed', request.url)
      );
    }

    // Get long-lived token (60 days)
    const longLivedResponse = await fetch(
      `https://graph.facebook.com/v18.0/oauth/access_token?` +
      `grant_type=fb_exchange_token&` +
      `client_id=${META_APP_ID}&` +
      `client_secret=${META_APP_SECRET}&` +
      `fb_exchange_token=${tokenData.access_token}`,
      { method: 'GET' }
    );

    const longLivedData = await longLivedResponse.json();
    const accessToken = longLivedData.access_token || tokenData.access_token;

    // Get user's ad accounts
    const accountsResponse = await fetch(
      `https://graph.facebook.com/v18.0/me/adaccounts?access_token=${accessToken}&fields=id,name,account_id`
    );
    const accountsData = await accountsResponse.json();

    // Store credentials securely (encrypted in production)
    const { error: credError } = await supabaseAdmin
      .from('api_credentials')
      .upsert({
        organization_id: organizationId,
        platform: 'Meta',
        credentials: {
          access_token: accessToken,
          expires_at: longLivedData.expires_in 
            ? new Date(Date.now() + longLivedData.expires_in * 1000).toISOString()
            : null,
          ad_accounts: accountsData.data || [],
        },
        is_active: true,
        last_synced_at: null,
      }, {
        onConflict: 'organization_id,platform',
      });

    if (credError) {
      console.error('[META CALLBACK] Error storing credentials:', credError);
      return NextResponse.redirect(
        new URL('/onboarding?error=storage_failed', request.url)
      );
    }

    // Redirect back to onboarding
    return NextResponse.redirect(
      new URL('/onboarding?platform=meta&connected=true', request.url)
    );
  } catch (error: any) {
    console.error('[META CALLBACK] Error:', error);
    return NextResponse.redirect(
      new URL(`/onboarding?error=${encodeURIComponent(error.message)}`, request.url)
    );
  }
}

