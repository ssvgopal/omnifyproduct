import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabsContent, TabsList, TabsTrigger, Button, Input, Label } from '@omnify/shared-ui';
import { Settings as SettingsIcon, Key, Bell, CreditCard, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';

const Settings = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  
  const [integrations, setIntegrations] = useState([]);
  const [apiKeys, setApiKeys] = useState([]);
  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    predictiveAlerts: true,
    weeklyReports: true,
  });

  useEffect(() => {
    const loadSettings = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        // Load integrations
        const integrationsData = await api.getIntegrations().catch(() => []);
        setIntegrations(integrationsData);

        // Load user preferences for notifications
        const profileData = await api.getUserProfile(user.user_id || user.sub).catch(() => null);
        if (profileData?.preferences) {
          setNotifications({
            emailNotifications: profileData.preferences.emailNotifications !== false,
            predictiveAlerts: profileData.preferences.predictiveAlerts !== false,
            weeklyReports: profileData.preferences.weeklyReports !== false,
          });
        }
      } catch (error) {
        console.error('Error loading settings:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [user]);

  const handleConnectIntegration = async (platform) => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      // In a real app, this would open an OAuth flow or credential form
      await api.connectIntegration(platform, {});
      setMessage({ type: 'success', text: `${platform} connected successfully!` });
      
      // Reload integrations
      const integrationsData = await api.getIntegrations();
      setIntegrations(integrationsData);
      
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to connect integration' });
    } finally {
      setSaving(false);
    }
  };

  const handleDisconnectIntegration = async (platform) => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      await api.disconnectIntegration(platform);
      setMessage({ type: 'success', text: `${platform} disconnected successfully!` });
      
      // Reload integrations
      const integrationsData = await api.getIntegrations();
      setIntegrations(integrationsData);
      
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to disconnect integration' });
    } finally {
      setSaving(false);
    }
  };

  const handleSaveNotifications = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const profileData = {
        preferences: {
          ...notifications,
        },
      };

      await api.updateUserProfile(user.user_id || user.sub, profileData);
      setMessage({ type: 'success', text: 'Notification preferences saved!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: error.message || 'Failed to save preferences' });
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Manage your account settings and integrations</p>
        </div>

        <Tabs defaultValue="integrations" className="space-y-6">
          <TabsList>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            <TabsTrigger value="api-keys">API Keys</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="billing">Billing</TabsTrigger>
          </TabsList>

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

          <TabsContent value="integrations">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <SettingsIcon className="h-5 w-5 mr-2" />
                  Platform Integrations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {['Meta Ads', 'Google Ads', 'LinkedIn Ads', 'Shopify', 'HubSpot'].map((platform) => {
                    const integration = integrations.find(i => i.platform === platform);
                    const isConnected = !!integration;
                    
                    return (
                      <div key={platform} className="p-4 border rounded-lg flex items-center justify-between">
                        <div>
                          <h4 className="font-semibold">{platform}</h4>
                          <p className="text-sm text-gray-600">
                            {isConnected ? 'Connected' : 'Not connected'}
                          </p>
                        </div>
                        {isConnected ? (
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handleDisconnectIntegration(platform)}
                            disabled={saving}
                          >
                            Disconnect
                          </Button>
                        ) : (
                          <Button 
                            size="sm" 
                            onClick={() => handleConnectIntegration(platform)}
                            disabled={saving}
                          >
                            {saving ? 'Connecting...' : 'Connect'}
                          </Button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="api-keys">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Key className="h-5 w-5 mr-2" />
                  API Key Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {apiKeys.map((key) => (
                    <div key={key.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-semibold">{key.name}</h4>
                          <p className="text-sm text-gray-600 font-mono">{key.key}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            {key.status}
                          </span>
                          <Button variant="outline" size="sm">Regenerate</Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full">Add New API Key</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Bell className="h-5 w-5 mr-2" />
                  Notification Preferences
                </CardTitle>
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
                      checked={notifications.emailNotifications}
                      onChange={(e) => setNotifications({...notifications, emailNotifications: e.target.checked})}
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
                      checked={notifications.predictiveAlerts}
                      onChange={(e) => setNotifications({...notifications, predictiveAlerts: e.target.checked})}
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
                      checked={notifications.weeklyReports}
                      onChange={(e) => setNotifications({...notifications, weeklyReports: e.target.checked})}
                      className="h-5 w-5"
                    />
                  </div>
                  <Button onClick={handleSaveNotifications} disabled={saving} className="mt-4">
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      'Save Preferences'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="billing">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CreditCard className="h-5 w-5 mr-2" />
                  Subscription Management
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold">Current Plan</h4>
                      <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-semibold">
                        Professional
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">$799/month</p>
                    <Button variant="outline" className="mr-2">Upgrade Plan</Button>
                    <Button variant="outline">Cancel Subscription</Button>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">Billing History</h4>
                    <p className="text-sm text-gray-600">No billing history available</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Settings;
