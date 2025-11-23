import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../../auth/[...nextauth]/route';
import { BrainService } from '@/lib/services/brain-service';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const organizationId = (session.user as any).organizationId;
    if (!organizationId) {
      return NextResponse.json({ error: 'No organization found' }, { status: 400 });
    }

    const brainService = new BrainService();
    const state = await brainService.getBrainState(organizationId);

    return NextResponse.json(state);
  } catch (error: any) {
    console.error('[API] Brain state error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch brain state' },
      { status: 500 }
    );
  }
}
