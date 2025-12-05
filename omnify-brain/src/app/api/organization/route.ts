import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/organization
 * 
 * Returns the current user's organization details.
 */
export async function GET(request: NextRequest) {
  try {
    const user = await requireRole('member', request);

    const { data: organization, error } = await supabaseAdmin
      .from('organizations')
      .select('*')
      .eq('id', user.organizationId)
      .single();

    if (error || !organization) {
      console.error('[ORGANIZATION] Fetch error:', error);
      return NextResponse.json(
        { error: 'Organization not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ organization });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[ORGANIZATION] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/**
 * PATCH /api/organization
 * 
 * Updates the current user's organization.
 */
export async function PATCH(request: NextRequest) {
  try {
    const user = await requireRole('admin', request);
    const body = await request.json();

    const { name, website, metadata } = body;

    const updatePayload: Record<string, any> = {};
    if (name) updatePayload.name = name;
    if (website !== undefined) updatePayload.website = website;
    if (metadata) updatePayload.metadata = metadata;

    const { data: organization, error } = await supabaseAdmin
      .from('organizations')
      .update(updatePayload)
      .eq('id', user.organizationId)
      .select('*')
      .single();

    if (error) {
      console.error('[ORGANIZATION] Update error:', error);
      return NextResponse.json(
        { error: 'Failed to update organization' },
        { status: 500 }
      );
    }

    return NextResponse.json({ organization });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[ORGANIZATION] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
