import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { getLatestBrainState } from '@/lib/data-service';

/**
 * GET /api/brain-state
 * GET /api/brain-state?organizationId=xxx
 * 
 * Returns the latest brain state.
 * Priority:
 * 1. Supabase (if organizationId provided)
 * 2. Local JSON file (for demo)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const organizationId = searchParams.get('organizationId');

    // Try Supabase first if organizationId provided
    if (organizationId) {
      const supabaseState = await getLatestBrainState(organizationId);
      if (supabaseState) {
        return NextResponse.json(supabaseState);
      }
    }

    // Fall back to local file (demo mode)
    const outputPath = path.join(
      process.cwd(), 
      'src', 
      'data', 
      'outputs', 
      'brain-state-org_demo_beauty_65m.json'
    );

    if (fs.existsSync(outputPath)) {
      const data = fs.readFileSync(outputPath, 'utf-8');
      return NextResponse.json(JSON.parse(data));
    }

    // Return 404 if no brain state exists
    return NextResponse.json(
      { error: 'Brain state not found. Run brain cycle first.' },
      { status: 404 }
    );
  } catch (error) {
    console.error('Error loading brain state:', error);
    return NextResponse.json(
      { error: 'Failed to load brain state' },
      { status: 500 }
    );
  }
}
