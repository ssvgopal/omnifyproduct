import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@omnify/shared-ui';
import { Activity, Workflow, Gauge, FileText } from 'lucide-react';

const AdminDashboard = () => {
  const [stats] = useState({
    systemHealth: { status: 'healthy', responseTime: 45, errorRate: 0.02 },
    workflows: { total: 1247, completed: 1189, successRate: 95.3 },
    performance: { avgResponse: 125, totalRequests: 45231, slowRequests: 12 },
    logs: { total: 12543, errors: 23, warnings: 156 }
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
        <p className="text-gray-600">System monitoring and management overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">System Health</span>
              <Activity className="h-5 w-5 text-green-500" />
            </div>
            <div className="text-2xl font-bold mb-1 capitalize">{stats.systemHealth.status}</div>
            <div className="text-sm text-gray-600">
              {stats.systemHealth.responseTime}ms avg • {stats.systemHealth.errorRate}% errors
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Workflows</span>
              <Workflow className="h-5 w-5 text-blue-500" />
            </div>
            <div className="text-2xl font-bold mb-1">{stats.workflows.total}</div>
            <div className="text-sm text-gray-600">
              {stats.workflows.completed} completed • {stats.workflows.successRate}% success
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Performance</span>
              <Gauge className="h-5 w-5 text-purple-500" />
            </div>
            <div className="text-2xl font-bold mb-1">{stats.performance.avgResponse}ms</div>
            <div className="text-sm text-gray-600">
              {stats.performance.totalRequests} requests • {stats.performance.slowRequests} slow
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">Logs (24h)</span>
              <FileText className="h-5 w-5 text-orange-500" />
            </div>
            <div className="text-2xl font-bold mb-1">{stats.logs.total.toLocaleString()}</div>
            <div className="text-sm text-gray-600">
              {stats.logs.errors} errors • {stats.logs.warnings} warnings
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="p-3 bg-gray-50 rounded text-sm">
                <div className="font-medium">Workflow execution completed</div>
                <div className="text-gray-600 text-xs">2 minutes ago</div>
              </div>
              <div className="p-3 bg-gray-50 rounded text-sm">
                <div className="font-medium">System health check passed</div>
                <div className="text-gray-600 text-xs">5 minutes ago</div>
              </div>
              <div className="p-3 bg-gray-50 rounded text-sm">
                <div className="font-medium">New user registered</div>
                <div className="text-gray-600 text-xs">12 minutes ago</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <button className="w-full text-left p-3 border rounded hover:bg-gray-50">
                View System Health
              </button>
              <button className="w-full text-left p-3 border rounded hover:bg-gray-50">
                Analyze Logs
              </button>
              <button className="w-full text-left p-3 border rounded hover:bg-gray-50">
                Manage Users
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
