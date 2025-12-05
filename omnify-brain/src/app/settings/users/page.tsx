'use client';

import { useState, useEffect } from 'react';
import { Users, UserPlus, Mail, Shield, Trash2, Loader2, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface TeamMember {
  id: string;
  email: string;
  name?: string;
  role: 'admin' | 'member' | 'viewer';
  status: 'active' | 'pending';
  createdAt: string;
}

const ROLE_LABELS: Record<string, { label: string; color: string }> = {
  admin: { label: 'Admin', color: 'bg-purple-100 text-purple-700' },
  member: { label: 'Member', color: 'bg-blue-100 text-blue-700' },
  viewer: { label: 'Viewer', color: 'bg-gray-100 text-gray-700' },
};

export default function UsersSettingsPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [inviting, setInviting] = useState(false);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'member' | 'viewer'>('member');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMembers();
  }, []);

  async function fetchMembers() {
    try {
      const response = await fetch('/api/organization/members');
      if (response.ok) {
        const data = await response.json();
        setMembers(data.members || []);
      }
    } catch (err) {
      console.error('Failed to fetch members:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setInviting(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/invite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: inviteEmail,
          role: inviteRole,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to send invite');
      }

      setInviteEmail('');
      setShowInviteForm(false);
      fetchMembers();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setInviting(false);
    }
  }

  async function handleRemoveMember(memberId: string) {
    if (!confirm('Are you sure you want to remove this team member?')) return;

    try {
      const response = await fetch(`/api/organization/members/${memberId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        fetchMembers();
      }
    } catch (err) {
      console.error('Failed to remove member:', err);
    }
  }

  async function handleUpdateRole(memberId: string, newRole: string) {
    try {
      const response = await fetch(`/api/organization/members/${memberId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole }),
      });
      if (response.ok) {
        fetchMembers();
      }
    } catch (err) {
      console.error('Failed to update role:', err);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="p-6 border-b flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="h-6 w-6 text-purple-600" />
            <div>
              <h2 className="text-lg font-semibold">Team Members</h2>
              <p className="text-sm text-gray-500">
                Manage who has access to your organization
              </p>
            </div>
          </div>
          <Button onClick={() => setShowInviteForm(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Invite Member
          </Button>
        </div>

        {/* Invite Form */}
        {showInviteForm && (
          <div className="p-6 bg-gray-50 border-b">
            <form onSubmit={handleInvite} className="space-y-4">
              <h3 className="font-medium">Invite a new team member</h3>
              
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
                  {error}
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-3">
                <div className="md:col-span-2 space-y-2">
                  <Label htmlFor="email">Email address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={inviteEmail}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInviteEmail(e.target.value)}
                    placeholder="colleague@company.com"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <select
                    id="role"
                    value={inviteRole}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setInviteRole(e.target.value as 'member' | 'viewer')}
                    className="w-full h-10 px-3 rounded-md border border-input bg-background text-sm"
                  >
                    <option value="member">Member</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-2">
                <Button type="submit" disabled={inviting}>
                  {inviting ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="h-4 w-4 mr-2" />
                      Send Invite
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowInviteForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Members List */}
        <div className="divide-y">
          {members.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No team members yet</p>
              <p className="text-sm">Invite your first team member to get started</p>
            </div>
          ) : (
            members.map((member) => (
              <div
                key={member.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                    <span className="text-purple-700 font-medium">
                      {(member.name || member.email).charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {member.name || member.email.split('@')[0]}
                      </span>
                      <Badge className={ROLE_LABELS[member.role]?.color || ''}>
                        <Shield className="h-3 w-3 mr-1" />
                        {ROLE_LABELS[member.role]?.label || member.role}
                      </Badge>
                      {member.status === 'pending' && (
                        <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                          Pending
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{member.email}</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {member.role !== 'admin' && (
                    <>
                      <select
                        value={member.role}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleUpdateRole(member.id, e.target.value)}
                        className="h-8 px-2 text-sm rounded border border-gray-200"
                      >
                        <option value="member">Member</option>
                        <option value="viewer">Viewer</option>
                      </select>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveMember(member.id)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Role Permissions Info */}
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <h3 className="font-medium mb-4">Role Permissions</h3>
        <div className="grid gap-4 md:grid-cols-3">
          <div className="p-4 bg-purple-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-purple-100 text-purple-700">Admin</Badge>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Full access to all features</li>
              <li>• Manage team members</li>
              <li>• Configure integrations</li>
              <li>• Execute actions</li>
            </ul>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-blue-100 text-blue-700">Member</Badge>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• View dashboard & analytics</li>
              <li>• Execute recommended actions</li>
              <li>• Cannot manage team</li>
              <li>• Cannot configure integrations</li>
            </ul>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-gray-100 text-gray-700">Viewer</Badge>
            </div>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• View dashboard only</li>
              <li>• Cannot execute actions</li>
              <li>• Read-only access</li>
              <li>• Ideal for stakeholders</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
