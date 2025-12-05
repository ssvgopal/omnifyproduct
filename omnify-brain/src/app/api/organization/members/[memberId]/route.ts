import { NextRequest, NextResponse } from 'next/server';
import { requireRole } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';

/**
 * PATCH /api/organization/members/[memberId]
 * 
 * Updates a team member's role.
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ memberId: string }> }
) {
  try {
    const user = await requireRole('admin', request);
    const { memberId } = await params;
    const body = await request.json();

    const { role } = body;

    if (!role || !['member', 'viewer'].includes(role)) {
      return NextResponse.json(
        { error: 'Invalid role. Must be "member" or "viewer".' },
        { status: 400 }
      );
    }

    // Verify member belongs to same organization
    const { data: member, error: fetchError } = await supabaseAdmin
      .from('users')
      .select('id, organization_id, role')
      .eq('id', memberId)
      .single();

    if (fetchError || !member) {
      return NextResponse.json(
        { error: 'Member not found' },
        { status: 404 }
      );
    }

    if (member.organization_id !== user.organizationId) {
      return NextResponse.json(
        { error: 'Member not in your organization' },
        { status: 403 }
      );
    }

    // Cannot change admin role
    if (member.role === 'admin') {
      return NextResponse.json(
        { error: 'Cannot change admin role' },
        { status: 400 }
      );
    }

    // Update role
    const { error: updateError } = await supabaseAdmin
      .from('users')
      .update({ role })
      .eq('id', memberId);

    if (updateError) {
      console.error('[MEMBERS] Update error:', updateError);
      return NextResponse.json(
        { error: 'Failed to update member' },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[MEMBERS] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

/**
 * DELETE /api/organization/members/[memberId]
 * 
 * Removes a team member from the organization.
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ memberId: string }> }
) {
  try {
    const user = await requireRole('admin', request);
    const { memberId } = await params;

    // Cannot delete yourself
    if (memberId === user.id) {
      return NextResponse.json(
        { error: 'Cannot remove yourself' },
        { status: 400 }
      );
    }

    // Verify member belongs to same organization
    const { data: member, error: fetchError } = await supabaseAdmin
      .from('users')
      .select('id, organization_id, role')
      .eq('id', memberId)
      .single();

    if (fetchError || !member) {
      return NextResponse.json(
        { error: 'Member not found' },
        { status: 404 }
      );
    }

    if (member.organization_id !== user.organizationId) {
      return NextResponse.json(
        { error: 'Member not in your organization' },
        { status: 403 }
      );
    }

    // Cannot remove admin
    if (member.role === 'admin') {
      return NextResponse.json(
        { error: 'Cannot remove admin' },
        { status: 400 }
      );
    }

    // Remove member (soft delete - set organization_id to null)
    const { error: deleteError } = await supabaseAdmin
      .from('users')
      .update({ organization_id: null })
      .eq('id', memberId);

    if (deleteError) {
      console.error('[MEMBERS] Delete error:', deleteError);
      return NextResponse.json(
        { error: 'Failed to remove member' },
        { status: 500 }
      );
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json({ error: error.message }, { status: 403 });
    }
    console.error('[MEMBERS] Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
