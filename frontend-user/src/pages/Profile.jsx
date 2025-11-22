import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Label } from '@omnify/shared-ui';
import { User, Mail, Building, Save, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
    adSpend: '',
  });

  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    predictiveAlerts: true,
    weeklyReports: true,
    dashboardTheme: 'light',
  });

  useEffect(() => {
    const loadProfile = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        // Load user profile data
        const profileData = await api.getUserProfile(user.user_id || user.sub);
        
        setProfile({
          name: profileData.demographics?.name || user.name || '',
          email: user.email || '',
          company: profileData.demographics?.company || '',
          role: profileData.demographics?.role || '',
          adSpend: profileData.demographics?.adSpend || '',
        });

        // Load preferences
        if (profileData.preferences) {
          setPreferences({
            emailNotifications: profileData.preferences.emailNotifications !== false,
            predictiveAlerts: profileData.preferences.predictiveAlerts !== false,
            weeklyReports: profileData.preferences.weeklyReports !== false,
            dashboardTheme: profileData.preferences.dashboardTheme || 'light',
          });
        }
      } catch (error) {
        console.error('Error loading profile:', error);
        // Fallback to user data from auth context
        setProfile({
          name: user.name || '',
          email: user.email || '',
          company: '',
          role: '',
          adSpend: '',
        });
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [user]);

  const handleSave = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const profileData = {
        demographics: {
          name: profile.name,
          company: profile.company,
          role: profile.role,
          adSpend: profile.adSpend,
        },
        preferences: preferences,
      };

      await api.updateUserProfile(user.user_id || user.sub, profileData);
      
      // Update auth context
      updateUser({ ...user, ...profileData.demographics });
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      
      // Clear message after 3 seconds
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.message || 'Failed to update profile. Please try again.' 
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile</h1>
          <p className="text-gray-600">Manage your account information</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="h-5 w-5 mr-2" />
              Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Full Name</Label>
                <Input id="name" value={profile.name} onChange={(e) => setProfile({...profile, name: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="email">Email</Label>
                <Input id="email" type="email" value={profile.email} onChange={(e) => setProfile({...profile, email: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="company">Company</Label>
                <Input id="company" value={profile.company} onChange={(e) => setProfile({...profile, company: e.target.value})} />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <Input id="role" value={profile.role} onChange={(e) => setProfile({...profile, role: e.target.value})} />
              </div>
              
              {message.text && (
                <div className={`p-3 rounded-lg flex items-center ${
                  message.type === 'success' 
                    ? 'bg-green-50 text-green-700 border border-green-200' 
                    : 'bg-red-50 text-red-700 border border-red-200'
                }`}>
                  {message.type === 'success' ? (
                    <CheckCircle2 className="h-5 w-5 mr-2" />
                  ) : (
                    <AlertCircle className="h-5 w-5 mr-2" />
                  )}
                  <span className="text-sm">{message.text}</span>
                </div>
              )}
              
              <Button onClick={handleSave} disabled={saving}>
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Building className="h-5 w-5 mr-2" />
              Account Details
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">User ID:</span>
                <span className="font-semibold font-mono text-sm">{user?.user_id || user?.sub || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Organization ID:</span>
                <span className="font-semibold font-mono text-sm">{user?.organization_id || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Roles:</span>
                <span className="font-semibold">{user?.roles?.join(', ') || 'User'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Notification Preferences</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">Email Notifications</h4>
                  <p className="text-sm text-gray-600">Receive alerts via email</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.emailNotifications}
                  onChange={(e) => setPreferences({...preferences, emailNotifications: e.target.checked})}
                  className="h-5 w-5"
                />
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">Predictive Alerts</h4>
                  <p className="text-sm text-gray-600">Get notified of performance risks</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.predictiveAlerts}
                  onChange={(e) => setPreferences({...preferences, predictiveAlerts: e.target.checked})}
                  className="h-5 w-5"
                />
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <h4 className="font-semibold">Weekly Reports</h4>
                  <p className="text-sm text-gray-600">Receive weekly performance summaries</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.weeklyReports}
                  onChange={(e) => setPreferences({...preferences, weeklyReports: e.target.checked})}
                  className="h-5 w-5"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;


