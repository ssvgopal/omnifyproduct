import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Eye, 
  Users, 
  TrendingDown, 
  TrendingUp,
  Target,
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  PieChart,
  Shield,
  Zap,
  Brain,
  ArrowRight
} from 'lucide-react';
import api from '@/services/api';

const EyesModule = () => {
  const [segments, setSegments] = useState(null);
  const [churnPredictions, setChurnPredictions] = useState(null);
  const [crossPlatformInsights, setCrossPlatformInsights] = useState(null);
  const [learningInsights, setLearningInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('segments');
  const [timeRange, setTimeRange] = useState('30d');

  useEffect(() => {
    loadEyesData();
  }, [timeRange]);

  const loadEyesData = async () => {
    try {
      setLoading(true);
      const data = await api.getEyesModuleData(timeRange);
      setSegments(data.segments);
      setChurnPredictions(data.churn_predictions);
      setCrossPlatformInsights(data.cross_platform_insights);
      setLearningInsights(data.learning_insights);
    } catch (error) {
      console.error('Error loading EYES data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Clock className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <div className="text-gray-500">Analyzing customer segments...</div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6" data-testid="eyes-module">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Eye className="mr-3 text-purple-500" />
            EYES - At-Risk Segments
          </h2>
          <p className="text-gray-600 mt-1">Advanced customer segmentation and churn prediction</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="px-3 py-1">
            <Shield className="w-4 h-4 mr-1" />
            Consent Compliant
          </Badge>
          <Badge variant="outline" className="px-3 py-1">
            <Brain className="w-4 h-4 mr-1" />
            Learning Active
          </Badge>
        </div>
      </div>

      {/* Time Range Selector */}
      <Card className="p-4">
        <Tabs value={timeRange} onValueChange={setTimeRange}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="30d">30-Day Churn</TabsTrigger>
            <TabsTrigger value="60d">60-Day Churn</TabsTrigger>
            <TabsTrigger value="90d">90-Day Churn</TabsTrigger>
          </TabsList>
        </Tabs>
      </Card>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="segments">Segments</TabsTrigger>
          <TabsTrigger value="churn">Churn Risk</TabsTrigger>
          <TabsTrigger value="patterns">Cross-Platform</TabsTrigger>
          <TabsTrigger value="learning">Learning</TabsTrigger>
        </TabsList>

        {/* Segments Tab */}
        <TabsContent value="segments" className="space-y-6">
          {/* Segmentation Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-800">Silhouette Score</p>
                  <p className="text-3xl font-bold text-purple-900">
                    {segments?.silhouette_score?.toFixed(3) || '0.000'}
                  </p>
                  <div className="flex items-center mt-1">
                    <CheckCircle className="w-4 h-4 text-purple-500" />
                    <span className="text-sm ml-1 text-purple-600">Excellent</span>
                  </div>
                </div>
                <Target className="w-8 h-8 text-purple-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-800">Total Segments</p>
                  <p className="text-3xl font-bold text-blue-900">
                    {segments?.segments?.length || 0}
                  </p>
                  <div className="flex items-center mt-1">
                    <Users className="w-4 h-4 text-blue-500" />
                    <span className="text-sm ml-1 text-blue-600">Clustered</span>
                  </div>
                </div>
                <PieChart className="w-8 h-8 text-blue-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-800">Algorithm</p>
                  <p className="text-lg font-bold text-green-900 capitalize">
                    {segments?.algorithm || 'Unknown'}
                  </p>
                  <div className="flex items-center mt-1">
                    <Zap className="w-4 h-4 text-green-500" />
                    <span className="text-sm ml-1 text-green-600">Optimized</span>
                  </div>
                </div>
                <Brain className="w-8 h-8 text-green-600" />
              </div>
            </Card>
          </div>

          {/* Segment Details */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Users className="mr-2 text-purple-500" />
              Customer Segments
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {segments?.segments?.map((segment) => (
                <Card key={segment.segment_id} className="p-4 border-l-4 border-l-purple-500">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-bold text-gray-900">{segment.label}</h4>
                    <Badge variant="outline" className="text-purple-600 border-purple-200">
                      {segment.size} users
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Size:</span>
                      <span className="font-semibold">{segment.size} ({segment.percentage.toFixed(1)}%)</span>
                    </div>
                    
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-2">Top Features:</p>
                      <div className="space-y-1">
                        {segment.top_features?.slice(0, 3).map((feature, index) => (
                          <div key={index} className="flex justify-between text-xs">
                            <span className="text-gray-600">{feature.feature}:</span>
                            <span className="font-medium">{feature.importance.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mt-3 pt-2 border-t">
                      <p className="text-xs text-gray-500">Sample Users: {segment.sample_user_ids?.length || 0}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Churn Risk Tab */}
        <TabsContent value="churn" className="space-y-6">
          {/* Churn Risk Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="p-6 bg-gradient-to-br from-red-50 to-red-100 border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-red-800">High Risk Users</p>
                  <p className="text-3xl font-bold text-red-900">
                    {churnPredictions?.[timeRange]?.high_risk_users || 0}
                  </p>
                  <div className="flex items-center mt-1">
                    <AlertTriangle className="w-4 h-4 text-red-500" />
                    <span className="text-sm ml-1 text-red-600">Immediate Action</span>
                  </div>
                </div>
                <TrendingDown className="w-8 h-8 text-red-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-yellow-800">Medium Risk Users</p>
                  <p className="text-3xl font-bold text-yellow-900">
                    {churnPredictions?.[timeRange]?.medium_risk_users || 0}
                  </p>
                  <div className="flex items-center mt-1">
                    <Clock className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm ml-1 text-yellow-600">Monitor</span>
                  </div>
                </div>
                <Activity className="w-8 h-8 text-yellow-600" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-800">Low Risk Users</p>
                  <p className="text-3xl font-bold text-green-900">
                    {churnPredictions?.[timeRange]?.low_risk_users || 0}
                  </p>
                  <div className="flex items-center mt-1">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    <span className="text-sm ml-1 text-green-600">Stable</span>
                  </div>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </Card>
          </div>

          {/* Model Performance */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <BarChart3 className="mr-2 text-purple-500" />
              Model Performance - {timeRange.toUpperCase()}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-blue-800">AUC Score</span>
                  <span className="font-bold text-blue-900">
                    {churnPredictions?.[timeRange]?.auc_score?.toFixed(3) || '0.000'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-green-800">Accuracy</span>
                  <span className="font-bold text-green-900">
                    {(churnPredictions?.[timeRange]?.accuracy * 100)?.toFixed(1) || '0.0'}%
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm text-purple-800">Overall Churn Rate</span>
                  <span className="font-bold text-purple-900">
                    {(churnPredictions?.[timeRange]?.overall_churn_rate * 100)?.toFixed(1) || '0.0'}%
                  </span>
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <span className="text-sm text-yellow-800">Precision</span>
                  <span className="font-bold text-yellow-900">
                    {(churnPredictions?.[timeRange]?.model_performance?.precision * 100)?.toFixed(1) || '0.0'}%
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                  <span className="text-sm text-red-800">Recall</span>
                  <span className="font-bold text-red-900">
                    {(churnPredictions?.[timeRange]?.model_performance?.recall * 100)?.toFixed(1) || '0.0'}%
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-indigo-50 rounded-lg">
                  <span className="text-sm text-indigo-800">F1 Score</span>
                  <span className="font-bold text-indigo-900">
                    {(churnPredictions?.[timeRange]?.model_performance?.f1_score * 100)?.toFixed(1) || '0.0'}%
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Segment Risk Analysis */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Target className="mr-2 text-purple-500" />
              Segment Risk Analysis
            </h3>
            <div className="space-y-4">
              {Object.entries(churnPredictions?.[timeRange]?.segment_churn_risk || {}).map(([segmentId, risk]) => (
                <div key={segmentId} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${getRiskColor(risk.risk_level)}`}>
                      {getRiskIcon(risk.risk_level)}
                    </div>
                    <div>
                      <h4 className="font-semibold">Segment {segmentId}</h4>
                      <p className="text-sm text-gray-600">{risk.sample_size} users</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">
                      {(risk.risk_score * 100).toFixed(1)}%
                    </div>
                    <Badge className={`${getRiskColor(risk.risk_level)}`}>
                      {risk.risk_level.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Cross-Platform Patterns Tab */}
        <TabsContent value="patterns" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Activity className="mr-2 text-purple-500" />
              Cross-Platform Behavior Patterns
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-blue-800">Multi-Channel Users</span>
                  <span className="font-bold text-blue-900">
                    {crossPlatformInsights?.multi_channel_users || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-green-800">Single-Channel Users</span>
                  <span className="font-bold text-green-900">
                    {crossPlatformInsights?.single_channel_users || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm text-purple-800">Avg Channels/User</span>
                  <span className="font-bold text-purple-900">
                    {crossPlatformInsights?.avg_channels_per_user?.toFixed(1) || '0.0'}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                  <span className="text-sm text-yellow-800">Avg Switching Rate</span>
                  <span className="font-bold text-yellow-900">
                    {crossPlatformInsights?.avg_switching_rate?.toFixed(1) || '0.0'}
                  </span>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Top Journey Patterns</h4>
                <div className="space-y-2">
                  {crossPlatformInsights?.top_journey_patterns?.slice(0, 5).map((journey, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm text-gray-700">{journey[0]}</span>
                      <Badge variant="outline">{journey[1]} users</Badge>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Learning Tab */}
        <TabsContent value="learning" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Brain className="mr-2 text-purple-500" />
              Learning Insights & Evolution
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Model Performance Trends</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <span className="text-sm text-blue-800">Silhouette Evolution</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-blue-900">
                        {learningInsights?.model_performance_trends?.silhouette_evolution?.slice(-1)[0]?.toFixed(3) || '0.000'}
                      </span>
                      <ArrowRight className="w-4 h-4 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="text-sm text-green-800">AUC Evolution (30d)</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-green-900">
                        {learningInsights?.model_performance_trends?.auc_evolution?.d30?.slice(-1)[0]?.toFixed(3) || '0.000'}
                      </span>
                      <ArrowRight className="w-4 h-4 text-green-600" />
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-semibold text-gray-900">Learning Recommendations</h4>
                <div className="space-y-2">
                  {learningInsights?.learning_recommendations?.map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-2 p-2 bg-yellow-50 rounded">
                      <Zap className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-yellow-800">{recommendation}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EyesModule;

