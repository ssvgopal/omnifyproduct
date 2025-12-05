import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * POST /api/onboarding/brain-init
 *
 * Triggers the first brain cycle for the current organization and
 * marks onboarding as completed.
 */
export async function POST(request: NextRequest) {
  try {
    const user = await requireRole('member', request); // any onboarded member/admin

    // Call the existing brain-cycle route internally so we reuse the logic.
    const baseUrl =
      process.env.NEXTAUTH_URL || process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';

    const brainResponse = await fetch(`${baseUrl}/api/brain-cycle`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // The brain-cycle route uses Supabase Auth token from Authorization header;
        // in onboarding we rely on bearer token from client, so this endpoint is
        // typically called from the browser with Authorization attached.
        // For internal/server-side calls we could add a service token here later.
      },
    });

    if (!brainResponse.ok) {
      const text = await brainResponse.text();
      console.error('[ONBOARDING] Brain init failed:', text);
      return NextResponse.json(
        { error: 'Brain cycle failed during onboarding' },
        { status: 500 }
      );
    }

    const brainData = await brainResponse.json();

    // Mark onboarding as completed for org and user
    await supabaseAdmin
      .from('organizations')
      .update({ onboarding_completed: true })
      .eq('id', user.organizationId);

    await supabaseAdmin
      .from('users')
      .update({ onboarding_completed: true })
      .eq('id', user.id);

    return NextResponse.json({
      success: true,
      brainState: {
        memory: brainData.memory,
        oracle: brainData.oracle,
        curiosity: brainData.curiosity,
      },
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json(
        { error: error.message },
        { status: 403 }
      );
    }

    console.error('[ONBOARDING] Brain-init endpoint error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}






