import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Users, 
  Eye, 
  MousePointer, 
  Target,
  Download,
  Calendar,
  Settings,
  Plus,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';
import api from '@/services/api';

const AdvancedAnalyticsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [metrics, setMetrics] = useState(null);
  const [dashboards, setDashboards] = useState([]);
  const [reports, setReports] = useState([]);
  const [audienceInsights, setAudienceInsights] = useState(null);
  const [creativePerformance, setCreativePerformance] = useState(null);
  const [executiveData, setExecutiveData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('30d');
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [metricsData, dashboardsData, reportsData, audienceData, creativeData, executiveData] = await Promise.all([
        api.get(`/api/analytics/metrics/${clientId}`),
        api.get(`/api/analytics/dashboards?client_id=${clientId}`),
        api.get(`/api/analytics/reports/scheduled?client_id=${clientId}`),
        api.get(`/api/analytics/audience/${clientId}?time_range=${timeRange}`),
        api.get(`/api/analytics/creative/${clientId}?time_range=${timeRange}`),
        api.get(`/api/analytics/executive/${clientId}`)
      ]);
      
      setMetrics(metricsData.data);
      setDashboards(dashboardsData.data.dashboards || []);
      setReports(reportsData.data.scheduled_reports || []);
      setAudienceInsights(audienceData.data);
      setCreativePerformance(creativeData.data);
      setExecutiveData(executiveData.data);
    } catch (err) {
      console.error("Failed to fetch analytics data:", err);
      setError("Failed to load analytics data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Auto-refresh every 30 seconds
    return () => clearInterval(interval);
  }, [timeRange]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  const getTrendIcon = (value, threshold = 0) => {
    if (value > threshold) return <TrendingUp className="h-4 w-4 text-green-500" />;
    if (value < threshold) return <TrendingDown className="h-4 w-4 text-red-500" />;
    return <TrendingUp className="h-4 w-4 text-gray-500" />;
  };

  const getPerformanceColor = (value, thresholds) => {
    if (value >= thresholds.high) return 'text-green-600';
    if (value >= thresholds.medium) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) return <div className="text-center p-8">Loading Advanced Analytics...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertCircle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-indigo-800 flex items-center">
              <BarChart3 className="mr-2 h-6 w-6 text-blue-500" /> Advanced Analytics Dashboard
            </CardTitle>
            <CardDescription className="text-gray-700">
              Comprehensive analytics, reporting, and insights for your marketing campaigns
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7d">Last 7 days</SelectItem>
                <SelectItem value="30d">Last 30 days</SelectItem>
                <SelectItem value="90d">Last 90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Executive KPIs */}
      {executiveData && (
        <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
              <Target className="mr-2 h-5 w-5 text-green-500" /> Executive KPIs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card className="p-4 bg-green-50 border-green-200">
                <CardTitle className="text-lg font-semibold text-green-800">Total Revenue</CardTitle>
                <CardContent className="text-3xl font-bold text-green-600">
                  {formatCurrency(executiveData.executive_kpis.total_revenue)}
                </CardContent>
                <div className="flex items-center text-sm text-green-700">
                  {getTrendIcon(executiveData.executive_kpis.roas, 2)}
                  <span className="ml-1">ROAS: {executiveData.executive_kpis.roas.toFixed(2)}x</span>
                </div>
              </Card>
              
              <Card className="p-4 bg-blue-50 border-blue-200">
                <CardTitle className="text-lg font-semibold text-blue-800">Total Spend</CardTitle>
                <CardContent className="text-3xl font-bold text-blue-600">
                  {formatCurrency(executiveData.executive_kpis.total_spend)}
                </CardContent>
                <div className="flex items-center text-sm text-blue-700">
                  {getTrendIcon(executiveData.executive_kpis.cpa, 50)}
                  <span className="ml-1">CPA: {formatCurrency(executiveData.executive_kpis.cpa)}</span>
                </div>
              </Card>
              
              <Card className="p-4 bg-purple-50 border-purple-200">
                <CardTitle className="text-lg font-semibold text-purple-800">Conversion Rate</CardTitle>
                <CardContent className="text-3xl font-bold text-purple-600">
                  {formatPercentage(executiveData.executive_kpis.conversion_rate)}
                </CardContent>
                <div className="flex items-center text-sm text-purple-700">
                  {getTrendIcon(executiveData.executive_kpis.ctr, 3)}
                  <span className="ml-1">CTR: {formatPercentage(executiveData.executive_kpis.ctr)}</span>
                </div>
              </Card>
              
              <Card className="p-4 bg-orange-50 border-orange-200">
                <CardTitle className="text-lg font-semibold text-orange-800">Active Campaigns</CardTitle>
                <CardContent className="text-3xl font-bold text-orange-600">
                  {executiveData.executive_kpis.total_campaigns}
                </CardContent>
                <div className="text-sm text-orange-700">
                  Top Platform: {executiveData.executive_kpis.top_performing_platform || 'N/A'}
                </div>
              </Card>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Analytics Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-indigo-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="dashboards" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Dashboards</TabsTrigger>
          <TabsTrigger value="reports" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Reports</TabsTrigger>
          <TabsTrigger value="audience" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Audience</TabsTrigger>
          <TabsTrigger value="creative" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Creative</TabsTrigger>
          <TabsTrigger value="insights" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Platform Performance */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Platform Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                {metrics?.metrics?.platforms?.map((platform, index) => (
                  <div key={index} className="mb-4 p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-lg text-gray-900">{platform._id.replace('_', ' ').toUpperCase()}</h3>
                      <Badge className="bg-blue-500 text-white">Active</Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Revenue:</span>
                        <span className="ml-2 font-semibold text-green-600">{formatCurrency(platform.total_revenue)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Cost:</span>
                        <span className="ml-2 font-semibold text-red-600">{formatCurrency(platform.total_cost)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">ROAS:</span>
                        <span className={`ml-2 font-semibold ${getPerformanceColor(platform.avg_roas, {high: 3, medium: 2})}`}>
                          {platform.avg_roas.toFixed(2)}x
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">CPA:</span>
                        <span className="ml-2 font-semibold">{formatCurrency(platform.avg_cpa)}</span>
                      </div>
                    </div>
                    <div className="mt-2">
                      <Progress value={(platform.total_revenue / Math.max(...metrics.metrics.platforms.map(p => p.total_revenue))) * 100} className="h-2" />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Real-time Metrics */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> Real-time Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                {metrics?.metrics?.overall && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center">
                        <Eye className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-medium">Impressions</span>
                      </div>
                      <span className="text-2xl font-bold text-blue-600">{formatNumber(metrics.metrics.overall.total_impressions)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <MousePointer className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Clicks</span>
                      </div>
                      <span className="text-2xl font-bold text-green-600">{formatNumber(metrics.metrics.overall.total_clicks)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center">
                        <Target className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="font-medium">Conversions</span>
                      </div>
                      <span className="text-2xl font-bold text-purple-600">{formatNumber(metrics.metrics.overall.total_conversions)}</span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div className="flex items-center">
                        <DollarSign className="h-5 w-5 text-orange-500 mr-2" />
                        <span className="font-medium">Revenue</span>
                      </div>
                      <span className="text-2xl font-bold text-orange-600">{formatCurrency(metrics.metrics.overall.total_revenue)}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Dashboards Tab */}
        <TabsContent value="dashboards">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-indigo-800">Custom Dashboards</CardTitle>
                <CardDescription>Create and manage your custom analytics dashboards</CardDescription>
              </div>
              <Button className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
                <Plus className="mr-2 h-4 w-4" /> Create Dashboard
              </Button>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboards.map((dashboard) => (
                  <Card key={dashboard.dashboard_id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">{dashboard.name}</CardTitle>
                      <CardDescription>{dashboard.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>Type: {dashboard.dashboard_type}</span>
                        <Badge variant="outline">{dashboard.charts.length} charts</Badge>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Created: {new Date(dashboard.created_at).toLocaleDateString()}
                      </div>
                    </CardContent>
                    <CardFooter className="pt-2">
                      <Button variant="outline" size="sm" className="w-full">
                        <Settings className="mr-2 h-3 w-3" /> Configure
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-indigo-800">Scheduled Reports</CardTitle>
                <CardDescription>Manage your automated reports and schedules</CardDescription>
              </div>
              <Button className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
                <Plus className="mr-2 h-4 w-4" /> Create Report
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports.map((report) => (
                  <Card key={report.report_id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-lg">{report.name}</h3>
                        <p className="text-gray-600">{report.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="mr-1 h-3 w-3" />
                            {report.schedule}
                          </span>
                          <span className="flex items-center">
                            <Clock className="mr-1 h-3 w-3" />
                            Next: {new Date(report.next_run).toLocaleDateString()}
                          </span>
                          <span>Format: {report.format.toUpperCase()}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm">
                          <Download className="mr-2 h-3 w-3" /> Download
                        </Button>
                        <Button variant="outline" size="sm">
                          <Settings className="mr-2 h-3 w-3" /> Edit
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audience Tab */}
        <TabsContent value="audience">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <Users className="mr-2 h-5 w-5 text-blue-500" /> Audience Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {audienceInsights && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Age Groups */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Age Groups</h3>
                    <div className="space-y-2">
                      {Object.entries(audienceInsights.age_groups).map(([ageGroup, data]) => (
                        <div key={ageGroup} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{ageGroup}</span>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(data.revenue)}</div>
                            <div className="text-sm text-gray-600">{formatNumber(data.conversions)} conversions</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Genders */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Gender Distribution</h3>
                    <div className="space-y-2">
                      {Object.entries(audienceInsights.genders).map(([gender, data]) => (
                        <div key={gender} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{gender}</span>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(data.revenue)}</div>
                            <div className="text-sm text-gray-600">{formatNumber(data.conversions)} conversions</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Locations */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Top Locations</h3>
                    <div className="space-y-2">
                      {Object.entries(audienceInsights.locations).slice(0, 5).map(([location, data]) => (
                        <div key={location} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="font-medium">{location}</span>
                          <div className="text-right">
                            <div className="font-semibold">{formatCurrency(data.revenue)}</div>
                            <div className="text-sm text-gray-600">{formatNumber(data.conversions)} conversions</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Creative Tab */}
        <TabsContent value="creative">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <PieChart className="mr-2 h-5 w-5 text-purple-500" /> Creative Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              {creativePerformance && (
                <div className="space-y-6">
                  {/* Top Performers */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Top Performing Creatives</h3>
                    <div className="space-y-3">
                      {creativePerformance.top_performers.slice(0, 5).map((creative, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <div className="font-semibold">{creative._id.creative_id}</div>
                            <div className="text-sm text-gray-600">
                              {creative._id.creative_type} • {creative._id.platform}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-green-600">{formatCurrency(creative.revenue)}</div>
                            <div className="text-sm text-gray-600">ROAS: {creative.roas.toFixed(2)}x</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Creative Types */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Performance by Creative Type</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(creativePerformance.creative_types).map(([type, data]) => (
                        <Card key={type} className="p-4">
                          <CardTitle className="text-lg">{type}</CardTitle>
                          <CardContent className="pt-2">
                            <div className="space-y-2">
                              <div className="flex justify-between">
                                <span>Count:</span>
                                <span className="font-semibold">{data.count}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Revenue:</span>
                                <span className="font-semibold text-green-600">{formatCurrency(data.total_revenue)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Avg ROAS:</span>
                                <span className="font-semibold">{data.avg_roas.toFixed(2)}x</span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> AI Insights & Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-green-800">High-Performing Campaign Detected</h4>
                  <p className="text-green-700 mt-1">
                    Your Google Ads campaign "Summer Sale 2024" is performing exceptionally well with a 4.2x ROAS.
                    Consider increasing budget allocation by 25% to maximize returns.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-green-600 border-green-300 hover:bg-green-50">
                    Optimize Budget
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <AlertCircle className="h-6 w-6 text-blue-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-blue-800">Audience Opportunity Identified</h4>
                  <p className="text-blue-700 mt-1">
                    The 25-34 age group shows 40% higher conversion rates but only 15% of your budget allocation.
                    Consider reallocating budget to capture this high-value segment.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-blue-600 border-blue-300 hover:bg-blue-50">
                    Adjust Targeting
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <TrendingUp className="h-6 w-6 text-purple-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-purple-800">Creative Refresh Recommendation</h4>
                  <p className="text-purple-700 mt-1">
                    Your video creatives are showing signs of fatigue with declining CTR. 
                    Create 3 new video variations focusing on product benefits to maintain performance.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-purple-600 border-purple-300 hover:bg-purple-50">
                    Create New Creatives
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <DollarSign className="h-6 w-6 text-orange-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-orange-800">Budget Optimization Opportunity</h4>
                  <p className="text-orange-700 mt-1">
                    Meta Ads campaigns are underperforming with 1.8x ROAS vs 3.2x on Google Ads.
                    Consider reducing Meta budget by 30% and reallocating to Google Ads for better returns.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-orange-600 border-orange-300 hover:bg-orange-50">
                    Reallocate Budget
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedAnalyticsDashboard;
