import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge, Button, Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@omnify/shared-ui';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

const IntegrationManagement = () => {
  const integrations = [
    { name: 'Meta Ads', status: 'active', users: 45, lastSync: '2 minutes ago', health: 'healthy' },
    { name: 'Google Ads', status: 'active', users: 38, lastSync: '5 minutes ago', health: 'healthy' },
    { name: 'LinkedIn Ads', status: 'active', users: 12, lastSync: '10 minutes ago', health: 'warning' },
    { name: 'HubSpot', status: 'active', users: 28, lastSync: '1 hour ago', health: 'healthy' },
    { name: 'Shopify', status: 'inactive', users: 0, lastSync: 'Never', health: 'unknown' }
  ];

  const getHealthIcon = (health) => {
    switch (health) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <XCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Integration Management</h1>
        <p className="text-gray-600">Configure and monitor platform integrations</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Platform Integrations</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Platform</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Active Users</TableHead>
                <TableHead>Last Sync</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {integrations.map((integration) => (
                <TableRow key={integration.name}>
                  <TableCell className="font-medium">{integration.name}</TableCell>
                  <TableCell>
                    <Badge variant={integration.status === 'active' ? 'default' : 'secondary'}>
                      {integration.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{integration.users}</TableCell>
                  <TableCell className="text-gray-600">{integration.lastSync}</TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      {getHealthIcon(integration.health)}
                      <span className="ml-2 capitalize">{integration.health}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm">Configure</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default IntegrationManagement;


