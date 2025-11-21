import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Settings as SettingsIcon,
  User,
  Shield,
  Bell,
  Globe,
  Key,
  Smartphone,
  Mail,
  CheckCircle2,
  XCircle,
  Loader2
} from 'lucide-react';
import api from '@/services/api';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Profile state
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    organization: '',
    role: ''
  });
  
  // MFA state
  const [mfaStatus, setMfaStatus] = useState({
    enabled: false,
    method: null,
    devices: []
  });
  
  // Sessions state
  const [sessions, setSessions] = useState([]);
  
  // Preferences state
  const [preferences, setPreferences] = useState({
    notifications: true,
    email_alerts: true,
    theme: 'light',
    language: 'en'
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // Load profile
      const profileRes = await api.get('/api/auth/profile');
      if (profileRes.data.success) {
        setProfile(profileRes.data.data);
      }
      
      // Load MFA status
      const mfaRes = await api.get('/api/mfa/status');
      if (mfaRes.data.success) {
        setMfaStatus(mfaRes.data.data);
      }
      
      // Load sessions
      const sessionsRes = await api.get('/api/sessions');
      if (sessionsRes.data.success) {
        setSessions(sessionsRes.data.data);
      }
      
    } catch (err) {
      console.error('Error loading settings:', err);
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await api.put('/api/auth/profile', profile);
      setSuccess('Profile updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleEnableMFA = async (method) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.post(`/api/mfa/${method}/setup`);
      if (response.data.success) {
        if (method === 'totp' && response.data.data.qr_code) {
          // Show QR code modal
          alert('Scan QR code with authenticator app');
        }
        await loadSettings();
        setSuccess('MFA enabled successfully');
      }
    } catch (err) {
      setError('Failed to enable MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await api.post('/api/mfa/disable');
      await loadSettings();
      setSuccess('MFA disabled successfully');
    } catch (err) {
      setError('Failed to disable MFA');
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId) => {
    try {
      await api.delete(`/api/sessions/${sessionId}`);
      await loadSettings();
      setSuccess('Session revoked');
    } catch (err) {
      setError('Failed to revoke session');
    }
  };

  const handleSavePreferences = async () => {
    try {
      setLoading(true);
      await api.put('/api/settings/preferences', preferences);
      setSuccess('Preferences saved');
    } catch (err) {
      setError('Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-4 bg-green-50 border-green-200">
            <CheckCircle2 className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="security">
              <Shield className="h-4 w-4 mr-2" />
              Security
            </TabsTrigger>
            <TabsTrigger value="sessions">
              <Smartphone className="h-4 w-4 mr-2" />
              Sessions
            </TabsTrigger>
            <TabsTrigger value="preferences">
              <SettingsIcon className="h-4 w-4 mr-2" />
              Preferences
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your personal information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input
                    id="name"
                    value={profile.name}
                    onChange={(e) => setProfile({...profile, name: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({...profile, email: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="organization">Organization</Label>
                  <Input
                    id="organization"
                    value={profile.organization}
                    disabled
                  />
                </div>
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Input
                    id="role"
                    value={profile.role}
                    disabled
                  />
                </div>
                <Button onClick={handleSaveProfile} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Save Changes
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Multi-Factor Authentication</CardTitle>
                <CardDescription>Add an extra layer of security to your account</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">MFA Status</h3>
                    <p className="text-sm text-gray-600">
                      {mfaStatus.enabled ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <Badge variant={mfaStatus.enabled ? "default" : "secondary"}>
                    {mfaStatus.enabled ? 'Active' : 'Inactive'}
                  </Badge>
                </div>

                {!mfaStatus.enabled ? (
                  <div className="space-y-3">
                    <Button onClick={() => handleEnableMFA('totp')} variant="outline" className="w-full">
                      <Key className="h-4 w-4 mr-2" />
                      Enable TOTP (Authenticator App)
                    </Button>
                    <Button onClick={() => handleEnableMFA('sms')} variant="outline" className="w-full">
                      <Smartphone className="h-4 w-4 mr-2" />
                      Enable SMS Verification
                    </Button>
                    <Button onClick={() => handleEnableMFA('email')} variant="outline" className="w-full">
                      <Mail className="h-4 w-4 mr-2" />
                      Enable Email Verification
                    </Button>
                  </div>
                ) : (
                  <Button onClick={handleDisableMFA} variant="destructive">
                    Disable MFA
                  </Button>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Sessions Tab */}
          <TabsContent value="sessions" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Active Sessions</CardTitle>
                <CardDescription>Manage your active device sessions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {sessions.map((session) => (
                    <div key={session.session_id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-semibold">{session.device_name || 'Unknown Device'}</p>
                        <p className="text-sm text-gray-600">{session.ip_address}</p>
                        <p className="text-xs text-gray-500">
                          Last active: {new Date(session.last_activity).toLocaleString()}
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRevokeSession(session.session_id)}
                      >
                        Revoke
                      </Button>
                    </div>
                  ))}
                  {sessions.length === 0 && (
                    <p className="text-gray-600 text-center py-4">No active sessions</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Preferences Tab */}
          <TabsContent value="preferences" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Preferences</CardTitle>
                <CardDescription>Customize your experience</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Email Notifications</Label>
                    <p className="text-sm text-gray-600">Receive email alerts</p>
                  </div>
                  <Switch
                    checked={preferences.email_alerts}
                    onCheckedChange={(checked) => setPreferences({...preferences, email_alerts: checked})}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>In-App Notifications</Label>
                    <p className="text-sm text-gray-600">Show notifications in app</p>
                  </div>
                  <Switch
                    checked={preferences.notifications}
                    onCheckedChange={(checked) => setPreferences({...preferences, notifications: checked})}
                  />
                </div>
                <div>
                  <Label>Theme</Label>
                  <Select
                    value={preferences.theme}
                    onValueChange={(value) => setPreferences({...preferences, theme: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Language</Label>
                  <Select
                    value={preferences.language}
                    onValueChange={(value) => setPreferences({...preferences, language: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleSavePreferences} disabled={loading}>
                  {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Save Preferences
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Settings;

