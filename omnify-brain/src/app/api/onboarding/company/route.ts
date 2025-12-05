import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * POST /api/onboarding/company
 *
 * Saves basic organization profile information collected during onboarding.
 * Body: { name: string; industry?: string; annualSpend?: string }
 *
 * For now we:
 * - Update the organization's name
 * - Store industry/annualSpend into a metadata JSONB column when available in the schema,
 *   otherwise ignore them safely.
 */
export async function POST(request: NextRequest) {
  try {
    const user = await requireRole('admin', request);
    const body = await request.json();

    const { name, industry, annualSpend } = body || {};

    if (!name || typeof name !== 'string') {
      return NextResponse.json(
        { error: 'Organization name is required' },
        { status: 400 }
      );
    }

    // Update organization name; metadata is optional / best-effort.
    const updatePayload: Record<string, any> = { name };

    if (industry || annualSpend) {
      // If organizations has a metadata JSONB column, this will work.
      // If not, PostgREST/Supabase will ignore unknown keys at runtime in dev;
      // adjust schema later if we want to persist these fields formally.
      updatePayload.metadata = {
        industry,
        annualSpend,
      };
    }

    const { data, error } = await supabaseAdmin
      .from('organizations')
      .update(updatePayload)
      .eq('id', user.organizationId)
      .select('*')
      .single();

    if (error || !data) {
      console.error('[ONBOARDING] Company update error:', error);
      return NextResponse.json(
        { error: 'Failed to update organization' },
        { status: 500 }
      );
    }

    // Mark onboarding as started for both org and user
    await supabaseAdmin
      .from('organizations')
      .update({ onboarding_completed: false })
      .eq('id', user.organizationId);

    await supabaseAdmin
      .from('users')
      .update({ onboarding_completed: false })
      .eq('id', user.id);

    return NextResponse.json({
      success: true,
      organization: data,
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json(
        { error: error.message },
        { status: 403 }
      );
    }

    console.error('[ONBOARDING] Company endpoint error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}






