import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';

const SHOPIFY_API_KEY = process.env.SHOPIFY_API_KEY;
const SHOPIFY_API_SECRET = process.env.SHOPIFY_API_SECRET;
const BASE_URL = process.env.NEXTAUTH_URL || 'http://localhost:3000';

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser();
    const searchParams = request.nextUrl.searchParams;
    const shop = searchParams.get('shop'); // Shopify store domain

    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    if (!shop) {
      return NextResponse.json(
        { error: 'Shop parameter required (e.g., yourstore.myshopify.com)' },
        { status: 400 }
      );
    }

    // Generate OAuth URL for Shopify
    const redirectUri = `${BASE_URL}/api/connectors/shopify/callback`;
    const scope = 'read_orders,read_customers,read_products';
    const state = Buffer.from(JSON.stringify({ userId: user.id, organizationId: user.organizationId })).toString('base64');

    const authUrl = `https://${shop}/admin/oauth/authorize?` +
      `client_id=${SHOPIFY_API_KEY}&` +
      `scope=${encodeURIComponent(scope)}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `state=${state}`;

    return NextResponse.json({ authUrl });
  } catch (error: any) {
    console.error('[SHOPIFY AUTH] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to generate auth URL' },
      { status: 500 }
    );
  }
}

