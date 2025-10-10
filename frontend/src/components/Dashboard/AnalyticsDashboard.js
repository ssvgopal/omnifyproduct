import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import api from '@/services/api';

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.getCrossPlatformAnalytics('30_days');
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading analytics...</div>
        </div>
      </Card>
    );
  }

  const metrics = analytics?.aggregated_metrics || {};
  const platforms = analytics?.platforms || {};

  return (
    <div className="space-y-6" data-testid="analytics-dashboard">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">📊 Cross-Platform Analytics</h2>
        
        {/* Aggregated Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="text-center" data-testid="metric-requests">
            <p className="text-3xl font-bold text-blue-600">{metrics.total_requests?.toLocaleString() || 0}</p>
            <p className="text-sm text-gray-600 mt-1">Total Requests</p>
          </div>
          <div className="text-center" data-testid="metric-users">
            <p className="text-3xl font-bold text-green-600">{metrics.total_users?.toLocaleString() || 0}</p>
            <p className="text-sm text-gray-600 mt-1">Total Users</p>
          </div>
          <div className="text-center" data-testid="metric-workflows">
            <p className="text-3xl font-bold text-purple-600">{metrics.total_workflows?.toLocaleString() || 0}</p>
            <p className="text-sm text-gray-600 mt-1">Total Workflows</p>
          </div>
          <div className="text-center" data-testid="metric-success-rate">
            <p className="text-3xl font-bold text-emerald-600">{metrics.success_rate || 0}%</p>
            <p className="text-sm text-gray-600 mt-1">Success Rate</p>
          </div>
          <div className="text-center" data-testid="metric-response-time">
            <p className="text-3xl font-bold text-orange-600">{metrics.average_response_time || 0}ms</p>
            <p className="text-sm text-gray-600 mt-1">Avg Response</p>
          </div>
        </div>

        {/* Platform Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 bg-blue-50">
            <h3 className="font-semibold mb-3 flex items-center">
              <span className="mr-2">🤖</span> AgentKit
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Requests:</span>
                <span className="font-medium">{platforms.agentkit?.requests?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Users:</span>
                <span className="font-medium">{platforms.agentkit?.users?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-medium">{platforms.agentkit?.success_rate || 0}%</span>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-green-50">
            <h3 className="font-semibold mb-3 flex items-center">
              <span className="mr-2">📊</span> GoHighLevel
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Requests:</span>
                <span className="font-medium">{platforms.gohighlevel?.requests?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Users:</span>
                <span className="font-medium">{platforms.gohighlevel?.users?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-medium">{platforms.gohighlevel?.success_rate || 0}%</span>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-purple-50">
            <h3 className="font-semibold mb-3 flex items-center">
              <span className="mr-2">⚙️</span> Custom Platform
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Requests:</span>
                <span className="font-medium">{platforms.custom?.requests?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Users:</span>
                <span className="font-medium">{platforms.custom?.users?.toLocaleString() || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Success Rate:</span>
                <span className="font-medium">{platforms.custom?.success_rate || 0}%</span>
              </div>
            </div>
          </Card>
        </div>
      </Card>

      {/* Trends */}
      {analytics?.trends && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">📈 Trends</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <span>User Growth</span>
              <span className="font-bold text-blue-600">{analytics.trends.user_growth}</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <span>Request Growth</span>
              <span className="font-bold text-green-600">{analytics.trends.request_growth}</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
              <span>Performance</span>
              <span className="font-bold text-purple-600 capitalize">{analytics.trends.performance_trend}</span>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AnalyticsDashboard;
