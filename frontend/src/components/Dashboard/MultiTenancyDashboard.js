import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Users, 
  Building, 
  UserPlus, 
  Mail, 
  Shield, 
  Settings, 
  CreditCard, 
  BarChart3,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Crown,
  User,
  UserCheck,
  UserX,
  Plus,
  Edit,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  Eye,
  EyeOff,
  Key,
  Lock,
  Globe,
  Server,
  Zap
} from 'lucide-react';
import api from '@/services/api';

const MultiTenancyDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [organization, setOrganization] = useState(null);
  const [users, setUsers] = useState([]);
  const [invitations, setInvitations] = useState([]);
  const [quotas, setQuotas] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('viewer');
  const [currentUser, setCurrentUser] = useState(null);
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, currentUserData] = await Promise.all([
        api.get('/api/organizations/overview'),
        api.get('/api/users/me')
      ]);
      
      setOrganization(overviewData.data.organization);
      setUsers(overviewData.data.users);
      setInvitations(overviewData.data.pending_invitations);
      setQuotas(overviewData.data.quotas);
      setCurrentUser(currentUserData.data);
    } catch (err) {
      console.error("Failed to fetch multi-tenancy data:", err);
      setError("Failed to load organization data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'super_admin': return 'bg-red-500';
      case 'org_admin': return 'bg-purple-500';
      case 'manager': return 'bg-blue-500';
      case 'analyst': return 'bg-green-500';
      case 'viewer': return 'bg-gray-500';
      case 'guest': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'super_admin': return <Crown className="h-4 w-4" />;
      case 'org_admin': return <Shield className="h-4 w-4" />;
      case 'manager': return <UserCheck className="h-4 w-4" />;
      case 'analyst': return <BarChart3 className="h-4 w-4" />;
      case 'viewer': return <Eye className="h-4 w-4" />;
      case 'guest': return <User className="h-4 w-4" />;
      default: return <User className="h-4 w-4" />;
    }
  };

  const getPlanColor = (plan) => {
    switch (plan) {
      case 'enterprise': return 'bg-purple-500';
      case 'professional': return 'bg-blue-500';
      case 'starter': return 'bg-green-500';
      case 'free': return 'bg-gray-500';
      default: return 'bg-gray-500';
    }
  };

  const getQuotaColor = (usage, limit) => {
    const percentage = (usage / limit) * 100;
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-yellow-600';
    return 'text-green-600';
  };

  const handleInviteUser = async () => {
    try {
      await api.post('/api/team/invite', {
        email: inviteEmail,
        role: inviteRole
      });
      
      await fetchData(); // Refresh data
      setShowInviteDialog(false);
      setInviteEmail('');
      setInviteRole('viewer');
    } catch (err) {
      console.error("Failed to invite user:", err);
    }
  };

  const handleCreateUser = async (userData) => {
    try {
      await api.post('/api/users', userData);
      await fetchData(); // Refresh data
      setShowUserDialog(false);
    } catch (err) {
      console.error("Failed to create user:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Multi-Tenancy Dashboard...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-indigo-50 to-purple-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-indigo-800 flex items-center">
              <Building className="mr-2 h-6 w-6 text-indigo-500" /> Multi-Tenancy & User Management
            </CardTitle>
            <CardDescription className="text-gray-700">
              Manage your organization, team members, and subscription
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={fetchData} variant="outline" className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-indigo-600 hover:bg-indigo-700">
                  <UserPlus className="mr-2 h-4 w-4" /> Invite User
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Invite Team Member</DialogTitle>
                  <DialogDescription>
                    Send an invitation to join your organization
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="invite-email">Email Address</Label>
                    <Input
                      id="invite-email"
                      type="email"
                      placeholder="user@example.com"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                    />
                  </div>
                  <div>
                    <Label htmlFor="invite-role">Role</Label>
                    <Select value={inviteRole} onValueChange={setInviteRole}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="viewer">Viewer</SelectItem>
                        <SelectItem value="analyst">Analyst</SelectItem>
                        <SelectItem value="manager">Manager</SelectItem>
                        <SelectItem value="org_admin">Organization Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleInviteUser} className="w-full">
                    <Mail className="mr-2 h-4 w-4" /> Send Invitation
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Organization Overview */}
      {organization && (
        <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
              <Building className="mr-2 h-5 w-5 text-indigo-500" /> Organization Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-600 mb-2">{organization.name}</div>
                <div className="text-lg font-semibold text-gray-800">Organization</div>
                <div className="text-sm text-gray-600">{organization.domain}</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  <Badge className={`${getPlanColor(organization.subscription_plan)} text-white`}>
                    {organization.subscription_plan.toUpperCase()}
                  </Badge>
                </div>
                <div className="text-lg font-semibold text-gray-800">Plan</div>
                <div className="text-sm text-gray-600">{organization.subscription_status}</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{users.length}</div>
                <div className="text-lg font-semibold text-gray-800">Active Users</div>
                <div className="text-sm text-gray-600">of {organization.max_users} max</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">{invitations.length}</div>
                <div className="text-lg font-semibold text-gray-800">Pending Invites</div>
                <div className="text-sm text-gray-600">Awaiting acceptance</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Multi-Tenancy Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-indigo-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="users" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Users</TabsTrigger>
          <TabsTrigger value="invitations" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Invitations</TabsTrigger>
          <TabsTrigger value="quotas" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Quotas</TabsTrigger>
          <TabsTrigger value="subscription" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Subscription</TabsTrigger>
          <TabsTrigger value="settings" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Current User Info */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <User className="mr-2 h-5 w-5 text-blue-500" /> Current User
                </CardTitle>
              </CardHeader>
              <CardContent>
                {currentUser && (
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                        <User className="h-6 w-6 text-indigo-600" />
                      </div>
                      <div>
                        <div className="font-semibold text-lg">{currentUser.first_name} {currentUser.last_name}</div>
                        <div className="text-gray-600">{currentUser.email}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Role:</span>
                      <Badge className={`${getRoleColor(currentUser.role)} text-white`}>
                        {getRoleIcon(currentUser.role)}
                        <span className="ml-1">{currentUser.role.replace('_', ' ').toUpperCase()}</span>
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Status:</span>
                      <Badge className={currentUser.is_active ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}>
                        {currentUser.is_active ? <CheckCircle className="mr-1 h-3 w-3" /> : <XCircle className="mr-1 h-3 w-3" />}
                        {currentUser.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Last Login:</span>
                      <span className="text-sm">{currentUser.last_login ? new Date(currentUser.last_login).toLocaleDateString() : 'Never'}</span>
                    </div>
                    
                    <div className="pt-2 border-t">
                      <div className="text-sm text-gray-600 mb-2">Permissions:</div>
                      <div className="flex flex-wrap gap-1">
                        {currentUser.permissions.slice(0, 5).map((permission, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {permission}
                          </Badge>
                        ))}
                        {currentUser.permissions.length > 5 && (
                          <Badge variant="outline" className="text-xs">
                            +{currentUser.permissions.length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quota Usage Summary */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5 text-green-500" /> Quota Usage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(quotas).map(([quotaType, quota]) => (
                    <div key={quotaType} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium capitalize">{quotaType.replace('_', ' ')}</span>
                        <span className={`font-semibold ${getQuotaColor(quota.current_usage, quota.limit)}`}>
                          {quota.current_usage} / {quota.limit}
                        </span>
                      </div>
                      <Progress value={(quota.current_usage / quota.limit) * 100} className="h-2" />
                      <div className="text-xs text-gray-600">
                        {quota.remaining} remaining • Resets {quota.reset_period}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-indigo-800">Team Members</CardTitle>
                <CardDescription>Manage your organization's users and their roles</CardDescription>
              </div>
              <Dialog open={showUserDialog} onOpenChange={setShowUserDialog}>
                <DialogTrigger asChild>
                  <Button className="flex items-center text-white bg-indigo-600 hover:bg-indigo-700">
                    <Plus className="mr-2 h-4 w-4" /> Add User
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create New User</DialogTitle>
                    <DialogDescription>
                      Add a new user to your organization
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="first-name">First Name</Label>
                        <Input id="first-name" placeholder="John" />
                      </div>
                      <div>
                        <Label htmlFor="last-name">Last Name</Label>
                        <Input id="last-name" placeholder="Doe" />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="email">Email</Label>
                      <Input id="email" type="email" placeholder="john@example.com" />
                    </div>
                    <div>
                      <Label htmlFor="role">Role</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select role" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="viewer">Viewer</SelectItem>
                          <SelectItem value="analyst">Analyst</SelectItem>
                          <SelectItem value="manager">Manager</SelectItem>
                          <SelectItem value="org_admin">Organization Admin</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="password">Password</Label>
                      <Input id="password" type="password" placeholder="Secure password" />
                    </div>
                    <Button className="w-full">
                      <UserPlus className="mr-2 h-4 w-4" /> Create User
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <Card key={user.user_id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                          <User className="h-5 w-5 text-indigo-600" />
                        </div>
                        <div>
                          <div className="font-semibold">{user.first_name} {user.last_name}</div>
                          <div className="text-sm text-gray-600">{user.email}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getRoleColor(user.role)} text-white`}>
                          {getRoleIcon(user.role)}
                          <span className="ml-1">{user.role.replace('_', ' ').toUpperCase()}</span>
                        </Badge>
                        <Badge variant="outline" className={user.is_active ? 'text-green-600 border-green-300' : 'text-red-600 border-red-300'}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      Last login: {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Invitations Tab */}
        <TabsContent value="invitations">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <Mail className="mr-2 h-5 w-5 text-blue-500" /> Pending Invitations
              </CardTitle>
              <CardDescription>Manage team invitations and their status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {invitations.map((invitation) => (
                  <Card key={invitation.invitation_id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Mail className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-semibold">{invitation.email}</div>
                          <div className="text-sm text-gray-600">
                            Invited by: {invitation.invited_by}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getRoleColor(invitation.role)} text-white`}>
                          {getRoleIcon(invitation.role)}
                          <span className="ml-1">{invitation.role.replace('_', ' ').toUpperCase()}</span>
                        </Badge>
                        <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                          <Clock className="mr-1 h-3 w-3" />
                          Pending
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      Expires: {new Date(invitation.expires_at).toLocaleDateString()}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Quotas Tab */}
        <TabsContent value="quotas">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-green-500" /> Usage Quotas
              </CardTitle>
              <CardDescription>Monitor your organization's resource usage and limits</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {Object.entries(quotas).map(([quotaType, quota]) => (
                  <Card key={quotaType} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <BarChart3 className="h-5 w-5 text-indigo-500 mr-2" />
                        <span className="font-semibold capitalize">{quotaType.replace('_', ' ')}</span>
                      </div>
                      <Badge variant="outline" className={quota.is_available ? 'text-green-600 border-green-300' : 'text-red-600 border-red-300'}>
                        {quota.is_available ? 'Available' : 'Exceeded'}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Usage:</span>
                        <span className={`font-semibold ${getQuotaColor(quota.current_usage, quota.limit)}`}>
                          {quota.current_usage} / {quota.limit}
                        </span>
                      </div>
                      <Progress value={(quota.current_usage / quota.limit) * 100} className="h-2" />
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>Remaining: {quota.remaining}</span>
                        <span>Resets {quota.reset_period}</span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Subscription Tab */}
        <TabsContent value="subscription">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <CreditCard className="mr-2 h-5 w-5 text-purple-500" /> Subscription Management
              </CardTitle>
              <CardDescription>Manage your subscription plan and billing</CardDescription>
            </CardHeader>
            <CardContent>
              {organization && (
                <div className="space-y-6">
                  {/* Current Plan */}
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-semibold text-lg">Current Plan</h3>
                      <Badge className={`${getPlanColor(organization.subscription_plan)} text-white`}>
                        {organization.subscription_plan.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span>Status:</span>
                        <span className="font-semibold">{organization.subscription_status}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max Users:</span>
                        <span className="font-semibold">{organization.max_users}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Max Campaigns:</span>
                        <span className="font-semibold">{organization.max_campaigns}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Storage:</span>
                        <span className="font-semibold">{organization.max_storage_gb} GB</span>
                      </div>
                    </div>
                  </div>

                  {/* Available Plans */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Available Plans</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card className="p-4 border-2 border-gray-200">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">Starter</CardTitle>
                          <CardDescription>Perfect for small teams</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold mb-2">$29/month</div>
                          <ul className="text-sm space-y-1">
                            <li>• Up to 5 users</li>
                            <li>• 25 campaigns</li>
                            <li>• 10 GB storage</li>
                            <li>• Priority support</li>
                          </ul>
                        </CardContent>
                        <CardFooter>
                          <Button variant="outline" className="w-full">
                            Upgrade to Starter
                          </Button>
                        </CardFooter>
                      </Card>

                      <Card className="p-4 border-2 border-blue-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">Professional</CardTitle>
                          <CardDescription>For growing businesses</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold mb-2">$99/month</div>
                          <ul className="text-sm space-y-1">
                            <li>• Up to 15 users</li>
                            <li>• 100 campaigns</li>
                            <li>• 50 GB storage</li>
                            <li>• A/B testing</li>
                            <li>• API access</li>
                          </ul>
                        </CardContent>
                        <CardFooter>
                          <Button className="w-full bg-blue-600 hover:bg-blue-700">
                            Upgrade to Professional
                          </Button>
                        </CardFooter>
                      </Card>

                      <Card className="p-4 border-2 border-purple-500">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">Enterprise</CardTitle>
                          <CardDescription>For large organizations</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="text-2xl font-bold mb-2">$299/month</div>
                          <ul className="text-sm space-y-1">
                            <li>• Up to 100 users</li>
                            <li>• 1000 campaigns</li>
                            <li>• 500 GB storage</li>
                            <li>• White label</li>
                            <li>• SSO integration</li>
                            <li>• Dedicated support</li>
                          </ul>
                        </CardContent>
                        <CardFooter>
                          <Button variant="outline" className="w-full">
                            Contact Sales
                          </Button>
                        </CardFooter>
                      </Card>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <Settings className="mr-2 h-5 w-5 text-gray-500" /> Organization Settings
              </CardTitle>
              <CardDescription>Configure your organization preferences and security settings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* General Settings */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">General Settings</h3>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="org-name">Organization Name</Label>
                      <Input id="org-name" defaultValue={organization?.name} />
                    </div>
                    <div>
                      <Label htmlFor="org-domain">Domain</Label>
                      <Input id="org-domain" defaultValue={organization?.domain} placeholder="example.com" />
                    </div>
                    <div>
                      <Label htmlFor="timezone">Timezone</Label>
                      <Select defaultValue="UTC">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="UTC">UTC</SelectItem>
                          <SelectItem value="EST">Eastern Time</SelectItem>
                          <SelectItem value="PST">Pacific Time</SelectItem>
                          <SelectItem value="GMT">Greenwich Mean Time</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {/* Security Settings */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">Security Settings</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <Shield className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Two-Factor Authentication</span>
                      </div>
                      <Badge className="bg-green-500 text-white">Enabled</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center">
                        <Lock className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-medium">Password Policy</span>
                      </div>
                      <Badge className="bg-blue-500 text-white">Enforced</Badge>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center">
                        <Key className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="font-medium">Session Timeout</span>
                      </div>
                      <Badge className="bg-purple-500 text-white">24 hours</Badge>
                    </div>
                  </div>
                </div>

                <Button className="w-full">
                  <Settings className="mr-2 h-4 w-4" /> Save Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MultiTenancyDashboard;
