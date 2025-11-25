import { NextRequest } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { supabaseAdmin } from '@/lib/db/supabase';

export interface SessionUser {
  id: string;
  email: string;
  name?: string;
  organizationId: string;
  role: 'admin' | 'member' | 'viewer';
}

/**
 * Get the current user from Supabase Auth token
 * Supports Authorization header: Bearer <token>
 */
export async function getCurrentUser(request?: NextRequest): Promise<SessionUser | null> {
  let accessToken: string | null = null;

  // Get token from Authorization header
  if (request) {
    const authHeader = request.headers.get('authorization');
    if (authHeader?.startsWith('Bearer ')) {
      accessToken = authHeader.substring(7);
    }
  }

  if (!accessToken) {
    return null;
  }

  // Verify token with Supabase
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  );

  const { data: { user: authUser }, error: authError } = await supabase.auth.getUser(accessToken);

  if (authError || !authUser) {
    console.error('[AUTH] Token verification failed:', authError);
    return null;
  }

  // Get user from our users table using auth_id
  const { data: dbUser, error: dbError } = await supabaseAdmin
    .from('users')
    .select('*, organization:organizations(*)')
    .eq('auth_id', authUser.id)
    .single();

  if (dbError || !dbUser) {
    console.error('[AUTH] User not found in database:', dbError);
    return null;
  }

  return {
    id: dbUser.id,
    email: dbUser.email,
    name: dbUser.email.split('@')[0], // Fallback to email prefix
    organizationId: dbUser.organization_id,
    role: (dbUser.role as 'admin' | 'member' | 'viewer') || 'member',
  };
}

/**
 * Check if user has required role
 */
export async function requireRole(
  requiredRole: 'admin' | 'member' | 'viewer',
  request?: NextRequest
): Promise<SessionUser> {
  const user = await getCurrentUser(request);
  
  if (!user) {
    throw new Error('Unauthorized');
  }

  const roleHierarchy = { admin: 3, member: 2, viewer: 1 };
  const userLevel = roleHierarchy[user.role];
  const requiredLevel = roleHierarchy[requiredRole];

  if (userLevel < requiredLevel) {
    throw new Error('Insufficient permissions');
  }

  return user;
}

/**
 * Check if user is admin
 */
export async function requireAdmin(request?: NextRequest): Promise<SessionUser> {
  return requireRole('admin', request);
}

/**
 * Get user's organization data
 */
export async function getUserOrganization(userId: string) {
  const { data: user, error } = await supabaseAdmin
    .from('users')
    .select('organization:organizations(*)')
    .eq('id', userId)
    .single();

  if (error || !user) {
    return null;
  }

  return (user as any).organization;
}

