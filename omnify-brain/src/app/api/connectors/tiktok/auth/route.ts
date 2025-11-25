import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { validatePlatform } from '@/lib/validation';

const TIKTOK_APP_ID = process.env.TIKTOK_APP_ID;
const TIKTOK_APP_SECRET = process.env.TIKTOK_APP_SECRET;
const BASE_URL = process.env.NEXTAUTH_URL || 'http://localhost:3000';

export async function GET(request: NextRequest) {
  try {
    // Platform validation
    const validation = validatePlatform('tiktok_ads');
    if (!validation.valid) {
      return validation.error!;
    }

    const user = await getCurrentUser(request);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Generate OAuth URL for TikTok Ads
    const redirectUri = `${BASE_URL}/api/connectors/tiktok/callback`;
    const state = Buffer.from(JSON.stringify({ userId: user.id, organizationId: user.organizationId })).toString('base64');

    const authUrl = `https://www.tiktok.com/v2/auth/authorize?` +
      `client_key=${TIKTOK_APP_ID}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=ads.read&` +
      `state=${state}`;

    return NextResponse.json({ authUrl });
  } catch (error: any) {
    console.error('[TIKTOK AUTH] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to generate auth URL' },
      { status: 500 }
    );
  }
}

