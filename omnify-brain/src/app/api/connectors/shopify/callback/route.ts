import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/db/supabase';
import crypto from 'crypto';

const SHOPIFY_API_KEY = process.env.SHOPIFY_API_KEY;
const SHOPIFY_API_SECRET = process.env.SHOPIFY_API_SECRET;
const BASE_URL = process.env.NEXTAUTH_URL || 'http://localhost:3000';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const code = searchParams.get('code');
    const shop = searchParams.get('shop');
    const state = searchParams.get('state');
    const hmac = searchParams.get('hmac');

    if (!code || !shop || !state || !hmac) {
      return NextResponse.redirect(
        new URL('/onboarding?error=missing_params', request.url)
      );
    }

    // Verify HMAC
    const params = new URLSearchParams(searchParams);
    params.delete('hmac');
    params.delete('signature');
    const message = Array.from(params.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, value]) => `${key}=${value}`)
      .join('&');
    
    const calculatedHmac = crypto
      .createHmac('sha256', SHOPIFY_API_SECRET!)
      .update(message)
      .digest('hex');

    if (calculatedHmac !== hmac) {
      return NextResponse.redirect(
        new URL('/onboarding?error=invalid_hmac', request.url)
      );
    }

    const stateData = JSON.parse(Buffer.from(state, 'base64').toString());
    const { organizationId } = stateData;

    // Exchange code for access token
    const tokenResponse = await fetch(`https://${shop}/admin/oauth/access_token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: SHOPIFY_API_KEY,
        client_secret: SHOPIFY_API_SECRET,
        code,
      }),
    });

    const tokenData = await tokenResponse.json();

    if (!tokenData.access_token) {
      return NextResponse.redirect(
        new URL('/onboarding?error=token_exchange_failed', request.url)
      );
    }

    // Store credentials
    await supabaseAdmin
      .from('api_credentials')
      .upsert({
        organization_id: organizationId,
        platform: 'Shopify',
        credentials: {
          access_token: tokenData.access_token,
          shop_domain: shop,
        },
        is_active: true,
        last_synced_at: null,
      }, {
        onConflict: 'organization_id,platform',
      });

    return NextResponse.redirect(
      new URL('/onboarding?platform=shopify&connected=true', request.url)
    );
  } catch (error: any) {
    console.error('[SHOPIFY CALLBACK] Error:', error);
    return NextResponse.redirect(
      new URL(`/onboarding?error=${encodeURIComponent(error.message)}`, request.url)
    );
  }
}

