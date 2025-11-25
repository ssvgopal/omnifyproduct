import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser, requireAdmin } from '@/lib/auth';
import { inviteUserToOrganization } from '@/lib/organization';

export async function POST(request: NextRequest) {
  try {
    const user = await requireAdmin();
    const { email, role = 'member' } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    const result = await inviteUserToOrganization(
      user.organizationId,
      email,
      role as 'admin' | 'member' | 'viewer'
    );

    if (result.error) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      message: result.message,
    });
  } catch (error: any) {
    if (error.message === 'Unauthorized' || error.message === 'Insufficient permissions') {
      return NextResponse.json(
        { error: error.message },
        { status: 403 }
      );
    }
    
    console.error('[INVITE] Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

