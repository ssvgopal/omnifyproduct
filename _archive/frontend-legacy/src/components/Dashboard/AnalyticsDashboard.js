import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Zap, 
  Target,
  Activity,
  Clock,
  CheckCircle,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  MousePointer,
  DollarSign,
  Percent
} from 'lucide-react';
import api from '@/services/api';

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('30_days');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.getCrossPlatformAnalytics(timeRange);
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
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-gray-500">Loading analytics...</div>
          </div>
        </div>
      </Card>
    );
  }

  const metrics = analytics?.aggregated_metrics || {};
  const platforms = analytics?.platforms || {};
  const trends = analytics?.trends || {};

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num?.toLocaleString() || 0;
  };

  const getTrendIcon = (trend) => {
    if (trend > 0) return <ArrowUpRight className="w-4 h-4 text-green-500" />;
    if (trend < 0) return <ArrowDownRight className="w-4 h-4 text-red-500" />;
    return <Activity className="w-4 h-4 text-gray-500" />;
  };

  const getTrendColor = (trend) => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-6" data-testid="analytics-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="mr-3 text-blue-500" />
            Analytics Dashboard
          </h2>
          <p className="text-gray-600 mt-1">Comprehensive performance insights across all platforms</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="px-3 py-1">
            <Clock className="w-4 h-4 mr-1" />
            Last updated: 2 min ago
          </Badge>
        </div>
      </div>

      {/* Time Range Selector */}
      <Card className="p-4">
        <Tabs value={timeRange} onValueChange={setTimeRange}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="7_days">Last 7 Days</TabsTrigger>
            <TabsTrigger value="30_days">Last 30 Days</TabsTrigger>
            <TabsTrigger value="90_days">Last 90 Days</TabsTrigger>
            <TabsTrigger value="1_year">Last Year</TabsTrigger>
          </TabsList>
        </Tabs>
      </Card>

      {/* Main Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-800">Total Requests</p>
                  <p className="text-3xl font-bold text-blue-900">{formatNumber(metrics.total_requests)}</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(trends.request_growth)}
                    <span className={`text-sm ml-1 ${getTrendColor(trends.request_growth)}`}>
                      {trends.request_growth > 0 ? '+' : ''}{trends.request_growth}%
                    </span>
                  </div>
                </div>
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-800">Active Users</p>
                  <p className="text-3xl font-bold text-green-900">{formatNumber(metrics.total_users)}</p>
                  <div className="flex items-center mt-1">
                    {getTrendIcon(trends.user_growth)}
                    <span className={`text-sm ml-1 ${getTrendColor(trends.user_growth)}`}>
                      {trends.user_growth > 0 ? '+' : ''}{trends.user_growth}%
                    </span>
                  </div>
                </div>
                <Users className="w-8 h-8 text-green-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-800">Workflows</p>
                  <p className="text-3xl font-bold text-purple-900">{formatNumber(metrics.total_workflows)}</p>
                  <div className="flex items-center mt-1">
                    <Activity className="w-4 h-4 text-purple-500" />
                    <span className="text-sm ml-1 text-purple-600">+8%</span>
                  </div>
                </div>
                <Target className="w-8 h-8 text-purple-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-emerald-800">Success Rate</p>
                  <p className="text-3xl font-bold text-emerald-900">{metrics.success_rate || 0}%</p>
                  <div className="flex items-center mt-1">
                    <CheckCircle className="w-4 h-4 text-emerald-500" />
                    <span className="text-sm ml-1 text-emerald-600">Excellent</span>
                  </div>
                </div>
                <Percent className="w-8 h-8 text-emerald-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-800">Avg Response</p>
                  <p className="text-3xl font-bold text-orange-900">{metrics.average_response_time || 0}ms</p>
                  <div className="flex items-center mt-1">
                    <Clock className="w-4 h-4 text-orange-500" />
                    <span className="text-sm ml-1 text-orange-600">Fast</span>
                  </div>
                </div>
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
            </Card>
          </div>

          {/* Platform Performance */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Target className="mr-2 text-blue-500" />
              Platform Performance
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-500 rounded-lg">
                      <Zap className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-blue-900">AgentKit</h4>
                      <p className="text-sm text-blue-700">AI-Powered Platform</p>
                    </div>
                  </div>
                  <Badge className="bg-blue-100 text-blue-800">Active</Badge>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">Requests:</span>
                    <span className="font-semibold text-blue-900">{formatNumber(platforms.agentkit?.requests)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">Users:</span>
                    <span className="font-semibold text-blue-900">{formatNumber(platforms.agentkit?.users)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">Success Rate:</span>
                    <span className="font-semibold text-blue-900">{platforms.agentkit?.success_rate || 0}%</span>
                  </div>
                  <Progress value={platforms.agentkit?.success_rate || 0} className="h-2" />
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-green-500 rounded-lg">
                      <BarChart3 className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-green-900">GoHighLevel</h4>
                      <p className="text-sm text-green-700">CRM Platform</p>
                    </div>
                  </div>
                  <Badge className="bg-green-100 text-green-800">Active</Badge>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">Requests:</span>
                    <span className="font-semibold text-green-900">{formatNumber(platforms.gohighlevel?.requests)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">Users:</span>
                    <span className="font-semibold text-green-900">{formatNumber(platforms.gohighlevel?.users)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">Success Rate:</span>
                    <span className="font-semibold text-green-900">{platforms.gohighlevel?.success_rate || 0}%</span>
                  </div>
                  <Progress value={platforms.gohighlevel?.success_rate || 0} className="h-2" />
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border border-purple-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-500 rounded-lg">
                      <Settings className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h4 className="font-bold text-purple-900">Custom Platform</h4>
                      <p className="text-sm text-purple-700">Custom Integration</p>
                    </div>
                  </div>
                  <Badge className="bg-purple-100 text-purple-800">Active</Badge>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-purple-700">Requests:</span>
                    <span className="font-semibold text-purple-900">{formatNumber(platforms.custom?.requests)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-purple-700">Users:</span>
                    <span className="font-semibold text-purple-900">{formatNumber(platforms.custom?.users)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-purple-700">Success Rate:</span>
                    <span className="font-semibold text-purple-900">{platforms.custom?.success_rate || 0}%</span>
                  </div>
                  <Progress value={platforms.custom?.success_rate || 0} className="h-2" />
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Platforms Tab */}
        <TabsContent value="platforms" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6">Platform Comparison</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold">Platform</th>
                    <th className="text-left py-3 px-4 font-semibold">Requests</th>
                    <th className="text-left py-3 px-4 font-semibold">Users</th>
                    <th className="text-left py-3 px-4 font-semibold">Success Rate</th>
                    <th className="text-left py-3 px-4 font-semibold">Avg Response</th>
                    <th className="text-left py-3 px-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(platforms).map(([platform, data]) => (
                    <tr key={platform} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium capitalize">{platform}</td>
                      <td className="py-3 px-4">{formatNumber(data.requests)}</td>
                      <td className="py-3 px-4">{formatNumber(data.users)}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <span>{data.success_rate || 0}%</span>
                          <Progress value={data.success_rate || 0} className="w-16 h-2" />
                        </div>
                      </td>
                      <td className="py-3 px-4">{data.avg_response_time || 0}ms</td>
                      <td className="py-3 px-4">
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6">Performance Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Response Time Trends</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <span className="text-sm text-blue-800">Average Response Time</span>
                    <span className="font-bold text-blue-900">{metrics.average_response_time || 0}ms</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-green-800">P95 Response Time</span>
                    <span className="font-bold text-green-900">245ms</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <span className="text-sm text-purple-800">P99 Response Time</span>
                    <span className="font-bold text-purple-900">890ms</span>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Success Metrics</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                    <span className="text-sm text-emerald-800">Overall Success Rate</span>
                    <span className="font-bold text-emerald-900">{metrics.success_rate || 0}%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <span className="text-sm text-yellow-800">Error Rate</span>
                    <span className="font-bold text-yellow-900">0.1%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="text-sm text-red-800">Timeout Rate</span>
                    <span className="font-bold text-red-900">0.05%</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <TrendingUp className="mr-2 text-blue-500" />
              Predictive Analytics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                <h4 className="font-bold text-blue-900 mb-4">Creative Fatigue Prediction</h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">High Risk Creatives:</span>
                    <span className="font-semibold text-blue-900">12</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">Medium Risk:</span>
                    <span className="font-semibold text-blue-900">28</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-blue-700">Low Risk:</span>
                    <span className="font-semibold text-blue-900">156</span>
                  </div>
                </div>
                <div className="mt-4">
                  <Progress value={87} className="h-2" />
                  <p className="text-xs text-blue-600 mt-1">Model Accuracy: 87%</p>
                </div>
              </div>

              <div className="p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-xl border border-green-200">
                <h4 className="font-bold text-green-900 mb-4">LTV Forecasting</h4>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">High Value Segments:</span>
                    <span className="font-semibold text-green-900">8</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">Medium Value:</span>
                    <span className="font-semibold text-green-900">24</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-green-700">Low Value:</span>
                    <span className="font-semibold text-green-900">67</span>
                  </div>
                </div>
                <div className="mt-4">
                  <Progress value={91} className="h-2" />
                  <p className="text-xs text-green-600 mt-1">Model Accuracy: 91%</p>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsDashboard;