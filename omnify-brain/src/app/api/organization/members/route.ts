import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * GET /api/organization/members
 * 
 * Returns all members of the current user's organization.
 */
export async function GET(request: NextRequest) {
  try {
    const user = await requireRole('member', request);

    const { data: members, error } = await supabaseAdmin
      .from('users')
      .select('id, email, name, role, created_at, onboarding_completed')
      .eq('organization_id', user.organizationId)
      .order('created_at', { ascending: true });

    if (error) {
      console.error('[MEMBERS] Fetch error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch members' },
        { status: 500 }
      );
    }

    // Transform to expected format
    const formattedMembers = (members || []).map(m => ({
      id: m.id,
      email: m.email,
      name: m.name,
      role: m.role,
      status: m.onboarding_completed ? 'active' : 'pending',
      createdAt: m.created_at,
    }));

    return NextResponse.json({ members: formattedMembers });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[MEMBERS] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
