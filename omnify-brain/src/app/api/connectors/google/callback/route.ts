import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;
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

    // Decode state
    const stateData = JSON.parse(Buffer.from(state, 'base64').toString());
    const { userId, organizationId } = stateData;

    // Exchange code for tokens
    const redirectUri = `${BASE_URL}/api/connectors/google/callback`;
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        code,
        client_id: GOOGLE_CLIENT_ID!,
        client_secret: GOOGLE_CLIENT_SECRET!,
        redirect_uri: redirectUri,
        grant_type: 'authorization_code',
      }),
    });

    const tokenData = await tokenResponse.json();

    if (!tokenData.access_token) {
      return NextResponse.redirect(
        new URL('/onboarding?error=token_exchange_failed', request.url)
      );
    }

    // Store credentials
    const { error: credError } = await supabaseAdmin
      .from('api_credentials')
      .upsert({
        organization_id: organizationId,
        platform: 'Google',
        credentials: {
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token,
          expires_at: tokenData.expires_in
            ? new Date(Date.now() + tokenData.expires_in * 1000).toISOString()
            : null,
        },
        is_active: true,
        last_synced_at: null,
      }, {
        onConflict: 'organization_id,platform',
      });

    if (credError) {
      console.error('[GOOGLE CALLBACK] Error storing credentials:', credError);
      return NextResponse.redirect(
        new URL('/onboarding?error=storage_failed', request.url)
      );
    }

    return NextResponse.redirect(
      new URL('/onboarding?platform=google&connected=true', request.url)
    );
  } catch (error: any) {
    console.error('[GOOGLE CALLBACK] Error:', error);
    return NextResponse.redirect(
      new URL(`/onboarding?error=${encodeURIComponent(error.message)}`, request.url)
    );
  }
}

