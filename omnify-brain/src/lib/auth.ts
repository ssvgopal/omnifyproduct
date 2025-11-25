import { getServerSession } from 'next-auth';
import { authOptions } from '@/app/api/auth/[...nextauth]/route';
import { supabaseAdmin } from '@/lib/db/supabase';

export interface SessionUser {
  id: string;
  email: string;
  name?: string;
  organizationId: string;
  role: 'admin' | 'member' | 'viewer';
}

/**
 * Get the current user session
 */
export async function getCurrentUser(): Promise<SessionUser | null> {
  const session = await getServerSession(authOptions);
  
  if (!session?.user) {
    return null;
  }

  return {
    id: (session.user as any).id,
    email: session.user.email!,
    name: session.user.name || undefined,
    organizationId: (session.user as any).organizationId,
    role: (session.user as any).role || 'member',
  };
}

/**
 * Check if user has required role
 */
export async function requireRole(requiredRole: 'admin' | 'member' | 'viewer'): Promise<SessionUser> {
  const user = await getCurrentUser();
  
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
export async function requireAdmin(): Promise<SessionUser> {
  return requireRole('admin');
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

