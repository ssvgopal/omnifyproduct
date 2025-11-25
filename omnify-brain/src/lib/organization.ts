import { supabaseAdmin } from '@/lib/db/supabase';

export interface OrganizationMember {
  id: string;
  email: string;
  role: 'admin' | 'member' | 'viewer';
  created_at: string;
}

/**
 * Get all members of an organization
 */
export async function getOrganizationMembers(organizationId: string): Promise<OrganizationMember[]> {
  const { data, error } = await supabaseAdmin
    .from('users')
    .select('id, email, role, created_at')
    .eq('organization_id', organizationId)
    .order('created_at', { ascending: false });

  if (error) {
    console.error('[ORG] Error fetching members:', error);
    return [];
  }

  return data || [];
}

/**
 * Invite a user to the organization
 */
export async function inviteUserToOrganization(
  organizationId: string,
  email: string,
  role: 'admin' | 'member' | 'viewer' = 'member'
) {
  // Check if user already exists
  const { data: existingUser } = await supabaseAdmin
    .from('users')
    .select('id, organization_id')
    .eq('email', email)
    .single();

  if (existingUser) {
    if (existingUser.organization_id === organizationId) {
      return { error: 'User is already a member of this organization' };
    }
    return { error: 'User already exists in another organization' };
  }

  // Create invitation (in a real app, you'd send an email)
  // For now, we'll create a placeholder user that needs to accept
  // In production, use a user_invitations table
  
  return { success: true, message: 'Invitation sent (placeholder)' };
}

/**
 * Update user role in organization
 */
export async function updateUserRole(
  organizationId: string,
  userId: string,
  newRole: 'admin' | 'member' | 'viewer'
) {
  const { error } = await supabaseAdmin
    .from('users')
    .update({ role: newRole })
    .eq('id', userId)
    .eq('organization_id', organizationId);

  if (error) {
    return { error: error.message };
  }

  return { success: true };
}

/**
 * Remove user from organization
 */
export async function removeUserFromOrganization(
  organizationId: string,
  userId: string
) {
  const { error } = await supabaseAdmin
    .from('users')
    .delete()
    .eq('id', userId)
    .eq('organization_id', organizationId);

  if (error) {
    return { error: error.message };
  }

  return { success: true };
}

