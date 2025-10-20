import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CrystalBall,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  Target,
  Zap,
  Eye,
  Brain,
  Sparkles,
  Rocket,
  Clock,
  DollarSign,
  BarChart3,
  LineChart,
  PieChart,
  Activity,
  Star,
  Award,
  Crown,
  RefreshCw,
  Play,
  Pause,
  RotateCcw,
  ArrowUpRight,
  ArrowDownRight,
  ArrowRight,
  Calendar,
  Timer,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';
import api from '@/services/api';

const PredictiveIntelligenceDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDemoDashboard();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadDashboard();
      }, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadDemoDashboard = async () => {
    try {
      const response = await api.get('/api/predictive/demo-dashboard');
      if (response.data.success) {
        setDashboardData(response.data.data);
      }
    } catch (error) {
      console.error('Error loading demo dashboard:', error);
    }
  };

  const loadDashboard = async () => {
    try {
      const response = await api.get('/api/predictive/dashboard');
      if (response.data.success) {
        setDashboardData(response.data.data);
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
    }
  };

  const generatePredictions = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/predictive/predictions', {
        organization_id: 'org_123',
        prediction_types: null
      });
      
      if (response.data.success) {
        await loadDashboard();
      }
    } catch (error) {
      console.error('Error generating predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeTrends = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/predictive/trends', {
        organization_id: 'org_123',
        metrics: null
      });
      
      if (response.data.success) {
        await loadDashboard();
      }
    } catch (error) {
      console.error('Error analyzing trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateOpportunities = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/predictive/opportunities', {
        organization_id: 'org_123'
      });
      
      if (response.data.success) {
        await loadDashboard();
      }
    } catch (error) {
      console.error('Error generating opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-orange-600 bg-orange-100';
      case 'very_low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceIcon = (confidence) => {
    switch (confidence) {
      case 'high': return <CheckCircle className="h-4 w-4" />;
      case 'medium': return <AlertCircle className="h-4 w-4" />;
      case 'low': return <AlertTriangle className="h-4 w-4" />;
      case 'very_low': return <XCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'rising': return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'falling': return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'stable': return <Minus className="h-4 w-4 text-gray-600" />;
      case 'volatile': return <Activity className="h-4 w-4 text-orange-600" />;
      default: return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatValue = (value, type) => {
    if (type === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    } else if (type === 'percentage') {
      return `${value.toFixed(1)}%`;
    } else {
      return value.toFixed(1);
    }
  };

  const formatTimeHorizon = (days) => {
    if (days < 7) return `${days} days`;
    if (days < 30) return `${Math.round(days / 7)} weeks`;
    if (days < 365) return `${Math.round(days / 30)} months`;
    return `${Math.round(days / 365)} years`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🔮 Predictive Intelligence</h1>
          <p className="text-gray-600 mt-2">See the future of your marketing with AI-powered predictions</p>
        </div>
        <div className="flex space-x-3">
          <Button 
            onClick={generatePredictions}
            disabled={loading}
            className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <CrystalBall className="h-4 w-4 mr-2" />
            )}
            Generate Predictions
          </Button>
          <Button 
            onClick={() => setAutoRefresh(!autoRefresh)}
            variant="outline"
            className={autoRefresh ? "bg-green-50 border-green-300 text-green-700" : ""}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Live' : 'Paused'}
          </Button>
        </div>
      </div>

      {/* Dashboard Metrics */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-6">
            <div className="flex items-center">
              <CrystalBall className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{dashboardData.dashboard_metrics.total_predictions}</div>
                <div className="text-sm text-gray-600">Total Predictions</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              <Star className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{dashboardData.dashboard_metrics.high_confidence_predictions}</div>
                <div className="text-sm text-gray-600">High Confidence</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{dashboardData.dashboard_metrics.rising_trends}</div>
                <div className="text-sm text-gray-600">Rising Trends</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <div className="text-2xl font-bold">{formatValue(dashboardData.dashboard_metrics.total_potential_value, 'currency')}</div>
                <div className="text-sm text-gray-600">Potential Value</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Insights */}
      {dashboardData && dashboardData.insights && dashboardData.insights.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center">
            <Brain className="h-5 w-5 mr-2 text-purple-600" />
            AI Insights
          </h3>
          <div className="space-y-2">
            {dashboardData.insights.map((insight, index) => (
              <div key={index} className="flex items-start space-x-2">
                <Sparkles className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                <span className="text-sm text-gray-700">{insight}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="predictions">Predictions</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {dashboardData ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Recent Predictions */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Recent Predictions</h3>
                <div className="space-y-3">
                  {dashboardData.predictions.slice(0, 3).map((prediction, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="text-lg">🔮</div>
                        <div>
                          <div className="font-bold text-sm">{prediction.title}</div>
                          <div className="text-xs text-gray-600">{prediction.type.replace('_', ' ').toUpperCase()}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold">
                          {formatValue(prediction.predicted_value, 'percentage')}
                        </div>
                        <Badge className={getConfidenceColor(prediction.confidence_level)} size="sm">
                          {prediction.confidence_level}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Active Trends */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Active Trends</h3>
                <div className="space-y-3">
                  {dashboardData.trend_analyses.slice(0, 3).map((trend, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getTrendIcon(trend.current_trend)}
                        <div>
                          <div className="font-bold text-sm">{trend.metric_name.toUpperCase()}</div>
                          <div className="text-xs text-gray-600">{trend.current_trend}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold">
                          {formatValue(trend.trend_strength, 'percentage')}
                        </div>
                        <div className="text-xs text-gray-600">strength</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* High-Value Opportunities */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">High-Value Opportunities</h3>
                <div className="space-y-3">
                  {dashboardData.opportunity_alerts
                    .filter(alert => alert.potential_value > 1000)
                    .slice(0, 3)
                    .map((alert, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="text-lg">💎</div>
                        <div>
                          <div className="font-bold text-sm">{alert.title}</div>
                          <div className="text-xs text-gray-600">{alert.opportunity_type.replace('_', ' ').toUpperCase()}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-bold text-green-600">
                          {formatValue(alert.potential_value, 'currency')}
                        </div>
                        <Badge className={getUrgencyColor(alert.urgency_level)} size="sm">
                          {alert.urgency_level}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Quick Actions */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Button 
                    onClick={generatePredictions}
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <CrystalBall className="h-4 w-4 mr-2" />
                    Generate New Predictions
                  </Button>
                  <Button 
                    onClick={analyzeTrends}
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Analyze Trends
                  </Button>
                  <Button 
                    onClick={generateOpportunities}
                    className="w-full justify-start"
                    variant="outline"
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Find Opportunities
                  </Button>
                </div>
              </Card>
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🔮</div>
              <h3 className="text-lg font-bold text-gray-600">No Predictive Data</h3>
              <p className="text-gray-500">Generate predictions to see your marketing future</p>
            </Card>
          )}
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions" className="space-y-4">
          {dashboardData && dashboardData.predictions.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.predictions.map((prediction, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">🔮</div>
                      <div>
                        <h3 className="text-lg font-bold">{prediction.title}</h3>
                        <p className="text-sm text-gray-600">{prediction.type.replace('_', ' ').toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getConfidenceColor(prediction.confidence_level)}>
                        {getConfidenceIcon(prediction.confidence_level)}
                        <span className="ml-1">{prediction.confidence_level}</span>
                      </Badge>
                      <Badge variant="outline">
                        {formatTimeHorizon(prediction.time_horizon)}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Current Value</div>
                      <div className="text-xl font-bold">{formatValue(prediction.current_value, 'percentage')}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Predicted Value</div>
                      <div className="text-xl font-bold">{formatValue(prediction.predicted_value, 'percentage')}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Change</div>
                      <div className={`text-xl font-bold flex items-center justify-center ${
                        prediction.predicted_value > prediction.current_value ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {prediction.predicted_value > prediction.current_value ? (
                          <ArrowUpRight className="h-4 w-4 mr-1" />
                        ) : (
                          <ArrowDownRight className="h-4 w-4 mr-1" />
                        )}
                        {formatValue(
                          ((prediction.predicted_value - prediction.current_value) / prediction.current_value) * 100,
                          'percentage'
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        {getTrendIcon(prediction.trend_direction)}
                        <span className="text-sm text-gray-600 capitalize">{prediction.trend_direction}</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        Impact: {formatValue(prediction.impact_score, 'percentage')}
                      </div>
                      <div className="text-sm text-gray-600">
                        Risk: {prediction.risk_level}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(prediction.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🔮</div>
              <h3 className="text-lg font-bold text-gray-600">No Predictions Available</h3>
              <p className="text-gray-500">Generate predictions to see future insights</p>
            </Card>
          )}
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          {dashboardData && dashboardData.trend_analyses.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.trend_analyses.map((trend, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">📈</div>
                      <div>
                        <h3 className="text-lg font-bold">{trend.metric_name.toUpperCase()}</h3>
                        <p className="text-sm text-gray-600">Trend Analysis</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getTrendIcon(trend.current_trend)}
                      <Badge variant="outline">
                        {formatValue(trend.trend_strength, 'percentage')} strength
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-bold text-sm mb-2">Key Insights:</h4>
                    <div className="space-y-1">
                      {trend.key_insights.map((insight, idx) => (
                        <div key={idx} className="text-sm text-gray-700 flex items-start space-x-2">
                          <Sparkles className="h-3 w-3 text-yellow-500 mt-1 flex-shrink-0" />
                          <span>{insight}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    {new Date(trend.created_at).toLocaleDateString()}
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-lg font-bold text-gray-600">No Trend Analysis</h3>
              <p className="text-gray-500">Analyze trends to see market patterns</p>
            </Card>
          )}
        </TabsContent>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          {dashboardData && dashboardData.opportunity_alerts.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.opportunity_alerts.map((alert, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">💎</div>
                      <div>
                        <h3 className="text-lg font-bold">{alert.title}</h3>
                        <p className="text-sm text-gray-600">{alert.opportunity_type.replace('_', ' ').toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getUrgencyColor(alert.urgency_level)}>
                        {alert.urgency_level}
                      </Badge>
                      <Badge variant="outline">
                        {alert.time_sensitivity}h
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-700 mb-3">{alert.description}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Potential Value</div>
                      <div className="text-xl font-bold text-green-600">
                        {formatValue(alert.potential_value, 'currency')}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Confidence</div>
                      <div className="text-xl font-bold">
                        {formatValue(alert.confidence_score, 'percentage')}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Time Sensitive</div>
                      <div className="text-xl font-bold">
                        {alert.time_sensitivity}h
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Action Required: {alert.action_required}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date(alert.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">💎</div>
              <h3 className="text-lg font-bold text-gray-600">No Opportunities Found</h3>
              <p className="text-gray-500">Generate opportunities to discover growth potential</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PredictiveIntelligenceDashboard;
