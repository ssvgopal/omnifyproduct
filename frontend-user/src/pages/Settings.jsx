import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabsContent, TabsList, TabsTrigger, Button, Input, Label } from '@omnify/shared-ui';
import { Settings as SettingsIcon, Key, Bell, CreditCard } from 'lucide-react';

const Settings = () => {
  const [apiKeys, setApiKeys] = useState([
    { id: 1, name: 'Meta Ads API', key: '••••••••••••1234', status: 'active' },
    { id: 2, name: 'Google Ads API', key: '••••••••••••5678', status: 'active' }
  ]);

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
                  <div className="p-4 border rounded-lg flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">Meta Ads</h4>
                      <p className="text-sm text-gray-600">Connected</p>
                    </div>
                    <Button variant="outline" size="sm">Disconnect</Button>
                  </div>
                  <div className="p-4 border rounded-lg flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">Google Ads</h4>
                      <p className="text-sm text-gray-600">Connected</p>
                    </div>
                    <Button variant="outline" size="sm">Disconnect</Button>
                  </div>
                  <div className="p-4 border rounded-lg flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold">LinkedIn Ads</h4>
                      <p className="text-sm text-gray-600">Not connected</p>
                    </div>
                    <Button size="sm">Connect</Button>
                  </div>
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
                    <input type="checkbox" defaultChecked className="h-5 w-5" />
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-semibold">Predictive Alerts</h4>
                      <p className="text-sm text-gray-600">Get notified of performance risks</p>
                    </div>
                    <input type="checkbox" defaultChecked className="h-5 w-5" />
                  </div>
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-semibold">Weekly Reports</h4>
                      <p className="text-sm text-gray-600">Receive weekly performance summaries</p>
                    </div>
                    <input type="checkbox" defaultChecked className="h-5 w-5" />
                  </div>
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
