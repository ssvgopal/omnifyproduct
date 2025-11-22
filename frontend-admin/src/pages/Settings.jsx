import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Input, Label, Button, Switch } from '@omnify/shared-ui';
import { Settings as SettingsIcon, Bell, Shield, Database } from 'lucide-react';

const Settings = () => {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">System Settings</h1>
        <p className="text-gray-600">Configure system-wide settings</p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Notifications
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Email Alerts</Label>
                  <p className="text-sm text-gray-600">Receive email notifications for system events</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Critical Alerts</Label>
                  <p className="text-sm text-gray-600">Immediate notifications for critical issues</p>
                </div>
                <Switch defaultChecked />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2" />
              Security
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label>Session Timeout (minutes)</Label>
                <Input type="number" defaultValue={30} className="mt-2" />
              </div>
              <div>
                <Label>Max Login Attempts</Label>
                <Input type="number" defaultValue={5} className="mt-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Data Retention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label>Log Retention (days)</Label>
                <Input type="number" defaultValue={90} className="mt-2" />
              </div>
              <div>
                <Label>Workflow History (days)</Label>
                <Input type="number" defaultValue={180} className="mt-2" />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end">
          <Button>Save Settings</Button>
        </div>
      </div>
    </div>
  );
};

export default Settings;


