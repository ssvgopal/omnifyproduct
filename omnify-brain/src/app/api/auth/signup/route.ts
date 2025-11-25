import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/db/supabase';

// Ensure this route runs in the Node.js runtime so that secure environment
// variables like SUPABASE_SERVICE_ROLE_KEY are available via process.env.
export const runtime = 'nodejs';

export async function POST(request: NextRequest) {
  try {
    const { email, name, companyName, authId } = await request.json();

    if (!email || !name || !companyName || !authId) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Step 1: Create organization
    const { data: organization, error: orgError } = await supabaseAdmin
      .from('organizations')
      .insert({
        name: companyName,
      })
      .select()
      .single();

    if (orgError || !organization) {
      console.error('[SIGNUP] Organization creation error:', orgError);
      return NextResponse.json(
        { error: 'Failed to create organization' },
        { status: 500 }
      );
    }

    // Step 2: Create user linked to organization
    // Note: The current Supabase `users` table does not have an `auth_id` column
    // applied yet (see migration `003_add_auth_id.sql`), so we insert without it
    // to avoid schema cache errors (PGRST204). Authentication currently links
    // by email in `[...nextauth]/route.ts`, so this is safe for now.
    const { data: user, error: userError } = await supabaseAdmin
      .from('users')
      .insert({
        email,
        organization_id: organization.id,
        role: 'admin', // First user is admin
      })
      .select()
      .single();

    if (userError || !user) {
      console.error('[SIGNUP] User creation error:', userError);
      // Cleanup: delete organization if user creation fails
      await supabaseAdmin
        .from('organizations')
        .delete()
        .eq('id', organization.id);
      
      return NextResponse.json(
        { error: 'Failed to create user' },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        organizationId: user.organization_id,
        role: user.role,
      },
      organization: {
        id: organization.id,
        name: organization.name,
      },
    });
  } catch (error: any) {
    console.error('[SIGNUP] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

