import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import IntegrationSetup from '@/components/Integrations/IntegrationSetup';
import CampaignManagementInterface from '@/components/Dashboard/CampaignManagementInterface';
import AnalyticsDashboard from '@/components/Dashboard/AnalyticsDashboard';
import { 
  LayoutDashboard,
  Target,
  BarChart3,
  Settings,
  Zap,
  TrendingUp,
  Users,
  DollarSign
} from 'lucide-react';
import api from '@/services/api';

const DemoDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState({
    totalCampaigns: 0,
    activeCampaigns: 0,
    totalSpend: 0,
    totalRevenue: 0,
    roas: 0,
    activeUsers: 0,
    totalImpressions: 0,
    totalClicks: 0,
    totalConversions: 0,
    avgCtr: 0,
    avgCpa: 0,
    platformBreakdown: {},
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setLoading(true);
      // Load aggregated stats from backend
      const response = await api.get('/api/analytics/dashboard/stats?days=30');
      if (response.data) {
        // Map backend response to frontend state
        setStats({
          totalCampaigns: response.data.total_campaigns || 0,
          activeCampaigns: response.data.active_campaigns || 0,
          totalSpend: response.data.total_spend || 0,
          totalRevenue: response.data.total_revenue || 0,
          roas: response.data.roas || 0,
          activeUsers: response.data.active_users || 0,
          totalImpressions: response.data.total_impressions || 0,
          totalClicks: response.data.total_clicks || 0,
          totalConversions: response.data.total_conversions || 0,
          avgCtr: response.data.avg_ctr || 0,
          avgCpa: response.data.avg_cpa || 0,
          platformBreakdown: response.data.platform_breakdown || {},
          recentActivity: response.data.recent_activity || []
        });
      }
    } catch (err) {
      console.error('Error loading dashboard stats:', err);
      // Use mock data as fallback only if API fails
      setStats({
        totalCampaigns: 12,
        activeCampaigns: 8,
        totalSpend: 45230,
        totalRevenue: 125000,
        roas: 2.76,
        activeUsers: 1245,
        totalImpressions: 0,
        totalClicks: 0,
        totalConversions: 0,
        avgCtr: 0,
        avgCpa: 0,
        platformBreakdown: {},
        recentActivity: []
      });
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, trend, color = 'blue' }) => (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-2xl font-bold mt-2">{value}</p>
            {trend && (
              <div className={`flex items-center mt-2 text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
                <TrendingUp className="h-4 w-4 mr-1" />
                {trend > 0 ? '+' : ''}{trend}%
              </div>
            )}
          </div>
          <div className={`p-3 rounded-lg bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">OmniFy Cloud Connect</h1>
              <p className="text-sm text-gray-600 mt-1">AI-Powered Marketing Automation Platform</p>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Zap className="h-3 w-3 mr-1" />
              Demo Mode
            </Badge>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">
              <LayoutDashboard className="h-4 w-4 mr-2" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="integrations">
              <Settings className="h-4 w-4 mr-2" />
              Integrations
            </TabsTrigger>
            <TabsTrigger value="campaigns">
              <Target className="h-4 w-4 mr-2" />
              Campaigns
            </TabsTrigger>
            <TabsTrigger value="analytics">
              <BarChart3 className="h-4 w-4 mr-2" />
              Analytics
            </TabsTrigger>
            <TabsTrigger value="settings">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Dashboard Overview</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <StatCard
                  title="Total Campaigns"
                  value={stats.totalCampaigns}
                  icon={Target}
                  trend={12}
                  color="blue"
                />
                <StatCard
                  title="Active Campaigns"
                  value={stats.activeCampaigns}
                  icon={Zap}
                  trend={8}
                  color="green"
                />
                <StatCard
                  title="Total Spend"
                  value={`$${stats.totalSpend.toLocaleString()}`}
                  icon={DollarSign}
                  trend={-5}
                  color="red"
                />
                <StatCard
                  title="Total Revenue"
                  value={`$${stats.totalRevenue.toLocaleString()}`}
                  icon={TrendingUp}
                  trend={23}
                  color="green"
                />
                <StatCard
                  title="ROAS"
                  value={stats.roas.toFixed(2)}
                  icon={BarChart3}
                  trend={15}
                  color="purple"
                />
                <StatCard
                  title="Active Users"
                  value={stats.activeUsers.toLocaleString()}
                  icon={Users}
                  trend={8}
                  color="blue"
                />
              </div>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center"
                    onClick={() => setActiveTab('integrations')}
                  >
                    <Settings className="h-6 w-6 mb-2" />
                    <span>Connect Platform</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center"
                    onClick={() => setActiveTab('campaigns')}
                  >
                    <Target className="h-6 w-6 mb-2" />
                    <span>Create Campaign</span>
                  </Button>
                  <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col items-center"
                    onClick={() => setActiveTab('analytics')}
                  >
                    <BarChart3 className="h-6 w-6 mb-2" />
                    <span>View Analytics</span>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-4 text-gray-500">Loading activity...</div>
                ) : stats.recentActivity && stats.recentActivity.length > 0 ? (
                  <div className="space-y-3">
                    {stats.recentActivity.map((activity, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`h-2 w-2 rounded-full ${
                            activity.type === 'campaign_started' ? 'bg-green-500' :
                            activity.type === 'integration_connected' ? 'bg-blue-500' :
                            activity.type === 'user_onboarded' ? 'bg-purple-500' :
                            'bg-gray-500'
                          }`}></div>
                          <span className="text-sm">{activity.description || activity.type}</span>
                        </div>
                        <span className="text-xs text-gray-500">
                          {activity.timestamp ? new Date(activity.timestamp).toLocaleString() : 'Recently'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">No recent activity</div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Integrations Tab */}
          <TabsContent value="integrations">
            <IntegrationSetup />
          </TabsContent>

          {/* Campaigns Tab */}
          <TabsContent value="campaigns">
            <CampaignManagementInterface />
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics">
            <AnalyticsDashboard />
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">Settings panel</p>
              <Button onClick={() => window.location.href = '/settings'}>
                Go to Settings
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DemoDashboard;

