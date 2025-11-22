import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Input, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Badge } from '@omnify/shared-ui';
import { Search, Filter } from 'lucide-react';

const Logs = () => {
  const [filters, setFilters] = useState({
    level: 'ALL',
    timeRange: '1h',
    search: ''
  });

  const logs = [
    { id: 1, timestamp: '2024-12-22 10:23:45', level: 'INFO', message: 'Workflow execution started', userId: 'user123', workflowId: 'wf456' },
    { id: 2, timestamp: '2024-12-22 10:23:42', level: 'WARN', message: 'High response time detected', userId: 'user789', workflowId: null },
    { id: 3, timestamp: '2024-12-22 10:23:38', level: 'ERROR', message: 'API connection failed', userId: 'user123', workflowId: 'wf456' },
    { id: 4, timestamp: '2024-12-22 10:23:35', level: 'INFO', message: 'User login successful', userId: 'user456', workflowId: null },
    { id: 5, timestamp: '2024-12-22 10:23:30', level: 'INFO', message: 'Data sync completed', userId: null, workflowId: 'wf789' }
  ];

  const getLevelBadge = (level) => {
    const variants = {
      ERROR: 'destructive',
      WARN: 'secondary',
      INFO: 'default',
      DEBUG: 'outline'
    };
    return <Badge variant={variants[level] || 'outline'}>{level}</Badge>;
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Logs</h1>
        <p className="text-gray-600">System logs analysis and triaging</p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Log Level</label>
              <Select value={filters.level} onValueChange={(value) => setFilters({...filters, level: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ALL">All Levels</SelectItem>
                  <SelectItem value="ERROR">Errors</SelectItem>
                  <SelectItem value="WARN">Warnings</SelectItem>
                  <SelectItem value="INFO">Info</SelectItem>
                  <SelectItem value="DEBUG">Debug</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Time Range</label>
              <Select value={filters.timeRange} onValueChange={(value) => setFilters({...filters, timeRange: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5m">Last 5 minutes</SelectItem>
                  <SelectItem value="1h">Last hour</SelectItem>
                  <SelectItem value="24h">Last 24 hours</SelectItem>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input 
                  placeholder="Search logs..." 
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Log Entries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {logs.map((log) => (
              <div key={log.id} className="p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-3">
                    {getLevelBadge(log.level)}
                    <span className="text-sm text-gray-600">{log.timestamp}</span>
                  </div>
                </div>
                <div className="text-sm font-medium mb-1">{log.message}</div>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  {log.userId && <span>User: {log.userId}</span>}
                  {log.workflowId && <span>Workflow: {log.workflowId}</span>}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Logs;
