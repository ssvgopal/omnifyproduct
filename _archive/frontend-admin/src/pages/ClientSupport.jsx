import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Input, Textarea, Button, Badge } from '@omnify/shared-ui';
import { Search, AlertCircle, CheckCircle2 } from 'lucide-react';

const ClientSupport = () => {
  const [clientId, setClientId] = useState('');
  const [issueDescription, setIssueDescription] = useState('');

  const clients = [
    { id: 'user123', name: 'Sarah Johnson', errors: 3, lastActivity: '2 hours ago', status: 'active' },
    { id: 'user456', name: 'Marcus Chen', errors: 0, lastActivity: '5 minutes ago', status: 'active' },
    { id: 'user789', name: 'Jennifer Smith', errors: 12, lastActivity: '1 day ago', status: 'needs_attention' }
  ];

  const handleAnalyze = () => {
    // TODO: Implement client issue analysis
    alert(`Analyzing issue for client ${clientId}...`);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Client Support</h1>
        <p className="text-gray-600">Analyze client issues and provide support</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Client Issue Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Client ID</label>
                <Input 
                  placeholder="Enter client ID..."
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Issue Description</label>
                <Textarea 
                  placeholder="Describe the client's issue..."
                  value={issueDescription}
                  onChange={(e) => setIssueDescription(e.target.value)}
                  rows={4}
                />
              </div>
              <Button onClick={handleAnalyze} className="w-full">
                Analyze Issue
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Client Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {clients.map((client) => (
                <div key={client.id} className="p-3 border rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <div className="font-semibold">{client.name}</div>
                      <div className="text-sm text-gray-600">{client.id}</div>
                    </div>
                    {client.errors > 0 ? (
                      <Badge variant="destructive">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        {client.errors} errors
                      </Badge>
                    ) : (
                      <Badge variant="default">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        No issues
                      </Badge>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">Last activity: {client.lastActivity}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ClientSupport;
