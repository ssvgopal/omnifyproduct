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
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Target,
  Zap,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw,
  Download,
  Settings,
  BarChart3,
  PieChart,
  LineChart,
  Activity,
  Gauge,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Award,
  Trophy,
  Eye,
  Play,
  Pause,
  RotateCcw,
  Maximize,
  Minimize,
  Filter,
  Search,
  Calendar,
  DollarSign,
  Users,
  MousePointer,
  Globe,
  Shield,
  Lock,
  Key,
  Database,
  Cpu,
  Memory,
  HardDrive,
  Wifi,
  Signal,
  Battery,
  Power
} from 'lucide-react';
import api from '@/services/api';

const PredictiveIntelligenceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [predictions, setPredictions] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [marketForecast, setMarketForecast] = useState(null);
  const [modelPerformance, setModelPerformance] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPredictionType, setSelectedPredictionType] = useState('campaign_performance');
  const [selectedHorizon, setSelectedHorizon] = useState(30);
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, predictionsData, recommendationsData, forecastData] = await Promise.all([
        api.get(`/api/predictive/dashboard/${clientId}`),
        api.get(`/api/predictive/predictions/${clientId}`),
        api.get('/api/predictive/optimization/demo-campaign-1'),
        api.get('/api/predictive/forecast?market_segment=digital_marketing')
      ]);
      
      setPredictions(dashboardData.data.predictions || []);
      setRecommendations(dashboardData.data.optimization_recommendations || []);
      setMarketForecast(dashboardData.data.market_forecast);
      setModelPerformance(dashboardData.data.model_performance || {});
      
    } catch (err) {
      console.error("Failed to fetch predictive intelligence data:", err);
      setError("Failed to load predictive intelligence. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-500';
    if (confidence >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.8) return 'HIGH';
    if (confidence >= 0.6) return 'MEDIUM';
    return 'LOW';
  };

  const getPredictionIcon = (type) => {
    switch (type) {
      case 'campaign_performance': return <Target className="h-5 w-5 text-blue-500" />;
      case 'conversion_rate': return <TrendingUp className="h-5 w-5 text-green-500" />;
      case 'cost_per_acquisition': return <DollarSign className="h-5 w-5 text-orange-500" />;
      case 'return_on_ad_spend': return <BarChart3 className="h-5 w-5 text-purple-500" />;
      case 'audience_growth': return <Users className="h-5 w-5 text-pink-500" />;
      case 'market_trend': return <Globe className="h-5 w-5 text-indigo-500" />;
      default: return <Brain className="h-5 w-5 text-gray-500" />;
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'increase_budget': return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'decrease_budget': return <ArrowDown className="h-4 w-4 text-red-500" />;
      case 'pause_campaign': return <Pause className="h-4 w-4 text-orange-500" />;
      case 'resume_campaign': return <Play className="h-4 w-4 text-green-500" />;
      case 'adjust_targeting': return <Target className="h-4 w-4 text-blue-500" />;
      case 'update_creative': return <Lightbulb className="h-4 w-4 text-yellow-500" />;
      case 'change_bidding': return <DollarSign className="h-4 w-4 text-purple-500" />;
      case 'scale_winners': return <Maximize className="h-4 w-4 text-green-500" />;
      default: return <Settings className="h-4 w-4 text-gray-500" />;
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const handleGeneratePrediction = async () => {
    try {
      const features = {
        budget: 5000,
        daily_budget: 200,
        targeting_score: 0.8,
        creative_score: 0.7,
        seasonality: 0.5,
        competition_level: 0.6
      };
      
      await api.post('/api/predictive/predictions', {
        prediction_types: [selectedPredictionType],
        features: features,
        horizon_days: selectedHorizon
      });
      
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to generate prediction:", err);
    }
  };

  const handleImplementRecommendation = async (recommendationId) => {
    try {
      await api.put(`/api/predictive/optimization/${recommendationId}/implement`, {
        implementation_notes: "Implemented via dashboard"
      });
      
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to implement recommendation:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Predictive Intelligence...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-purple-50 to-pink-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-purple-800 flex items-center">
              <Brain className="mr-2 h-6 w-6 text-purple-500" /> Predictive Intelligence Engine
            </CardTitle>
            <CardDescription className="text-gray-700">
              Future trend prediction, automated optimization, and proactive recommendations
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={selectedPredictionType} onValueChange={setSelectedPredictionType}>
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="campaign_performance">Campaign Performance</SelectItem>
                <SelectItem value="conversion_rate">Conversion Rate</SelectItem>
                <SelectItem value="cost_per_acquisition">Cost Per Acquisition</SelectItem>
                <SelectItem value="return_on_ad_spend">Return on Ad Spend</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleGeneratePrediction} className="flex items-center text-white bg-purple-600 hover:bg-purple-700">
              <Zap className="mr-2 h-4 w-4" /> Generate Prediction
            </Button>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-purple-600 border-purple-300 hover:bg-purple-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Predictive Intelligence Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
            <Cpu className="mr-2 h-5 w-5 text-blue-500" /> Predictive Intelligence Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{predictions.length}</div>
              <div className="text-lg font-semibold text-gray-800">Active Predictions</div>
              <div className="text-sm text-gray-600">Future insights</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{recommendations.length}</div>
              <div className="text-lg font-semibold text-gray-800">Optimization Recommendations</div>
              <div className="text-sm text-gray-600">Actionable insights</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {marketForecast ? formatPercentage(marketForecast.predicted_growth) : '15.2%'}
              </div>
              <div className="text-lg font-semibold text-gray-800">Market Growth Forecast</div>
              <div className="text-sm text-gray-600">6-month prediction</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {Object.keys(modelPerformance).length}
              </div>
              <div className="text-lg font-semibold text-gray-800">Trained Models</div>
              <div className="text-sm text-gray-600">AI accuracy</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Predictive Intelligence Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-purple-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="predictions" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Predictions</TabsTrigger>
          <TabsTrigger value="optimization" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Optimization</TabsTrigger>
          <TabsTrigger value="forecasting" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Forecasting</TabsTrigger>
          <TabsTrigger value="models" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Models</TabsTrigger>
          <TabsTrigger value="insights" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Predictions */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <Eye className="mr-2 h-5 w-5 text-blue-500" /> Key Predictions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {predictions.slice(0, 3).map((prediction) => (
                    <div key={prediction.prediction_id} className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getPredictionIcon(prediction.prediction_type)}
                          <span className="ml-2 font-semibold capitalize">
                            {prediction.prediction_type.replace('_', ' ')}
                          </span>
                        </div>
                        <Badge className={`${getConfidenceBadge(prediction.confidence)} text-white`}>
                          {getConfidenceLevel(prediction.confidence)}
                        </Badge>
                      </div>
                      <div className="text-2xl font-bold text-blue-600 mb-1">
                        {prediction.prediction_type === 'cost_per_acquisition' ? formatCurrency(prediction.predicted_value) : 
                         prediction.prediction_type === 'return_on_ad_spend' ? `${prediction.predicted_value.toFixed(2)}x` :
                         formatPercentage(prediction.predicted_value)}
                      </div>
                      <div className="text-sm text-gray-600">
                        Confidence: {formatPercentage(prediction.confidence)} • 
                        Horizon: {prediction.prediction_horizon} days
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Top Recommendations */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <Lightbulb className="mr-2 h-5 w-5 text-yellow-500" /> Top Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recommendations.slice(0, 3).map((recommendation) => (
                    <div key={recommendation.recommendation_id} className="p-4 bg-yellow-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getActionIcon(recommendation.action)}
                          <span className="ml-2 font-semibold capitalize">
                            {recommendation.action.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={`${getPriorityBadge(recommendation.priority)} text-white`}>
                            {recommendation.priority.toUpperCase()}
                          </Badge>
                          <Badge className={`${getRiskBadge(recommendation.risk_level)} text-white`}>
                            {recommendation.risk_level.toUpperCase()}
                          </Badge>
                        </div>
                      </div>
                      <div className="text-sm text-gray-700 mb-2">{recommendation.reasoning}</div>
                      <div className="text-sm text-gray-600">
                        Expected Impact: {formatPercentage(recommendation.expected_impact - 1)} • 
                        Confidence: {formatPercentage(recommendation.confidence)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Predictions Tab */}
        <TabsContent value="predictions">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> Predictive Analytics
              </CardTitle>
              <CardDescription>AI-powered predictions for campaign performance and market trends</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {predictions.map((prediction) => (
                  <Card key={prediction.prediction_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getPredictionIcon(prediction.prediction_type)}
                        <span className="ml-2 font-semibold text-lg capitalize">
                          {prediction.prediction_type.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getConfidenceBadge(prediction.confidence)} text-white`}>
                          {getConfidenceLevel(prediction.confidence)}
                        </Badge>
                        <Badge variant="outline">
                          {prediction.model_used}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Predicted Value</div>
                        <div className="text-2xl font-bold text-blue-600">
                          {prediction.prediction_type === 'cost_per_acquisition' ? formatCurrency(prediction.predicted_value) : 
                           prediction.prediction_type === 'return_on_ad_spend' ? `${prediction.predicted_value.toFixed(2)}x` :
                           formatPercentage(prediction.predicted_value)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Confidence</div>
                        <div className="text-lg font-semibold">{formatPercentage(prediction.confidence)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Horizon</div>
                        <div className="text-lg font-semibold">{prediction.prediction_horizon} days</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Accuracy</div>
                        <div className="text-lg font-semibold">{formatPercentage(prediction.accuracy_score)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Key Factors:</div>
                      <div className="flex flex-wrap gap-1">
                        {prediction.factors.map((factor, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {factor}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div>Valid until: {new Date(prediction.valid_until).toLocaleDateString()}</div>
                      <div>Created: {new Date(prediction.created_at).toLocaleDateString()}</div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Optimization Tab */}
        <TabsContent value="optimization">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Zap className="mr-2 h-5 w-5 text-yellow-500" /> Optimization Recommendations
              </CardTitle>
              <CardDescription>AI-powered optimization suggestions for campaign improvement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recommendations.map((recommendation) => (
                  <Card key={recommendation.recommendation_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getActionIcon(recommendation.action)}
                        <span className="ml-2 font-semibold text-lg capitalize">
                          {recommendation.action.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getPriorityBadge(recommendation.priority)} text-white`}>
                          {recommendation.priority.toUpperCase()}
                        </Badge>
                        <Badge className={`${getRiskBadge(recommendation.risk_level)} text-white`}>
                          {recommendation.risk_level.toUpperCase()}
                        </Badge>
                        <Button 
                          onClick={() => handleImplementRecommendation(recommendation.recommendation_id)}
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <CheckCircle className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-gray-700">{recommendation.reasoning}</div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Expected Impact</div>
                        <div className="text-lg font-semibold text-green-600">
                          {formatPercentage(recommendation.expected_impact - 1)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Confidence</div>
                        <div className="text-lg font-semibold">{formatPercentage(recommendation.confidence)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Campaign</div>
                        <div className="text-lg font-semibold">{recommendation.target_campaign_id}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Implementation Steps:</div>
                      <ol className="text-sm text-gray-700 space-y-1">
                        {recommendation.implementation_steps.map((step, index) => (
                          <li key={index}>{index + 1}. {step}</li>
                        ))}
                      </ol>
                    </div>
                    
                    <div className="text-sm text-gray-600">
                      Created: {new Date(recommendation.created_at).toLocaleDateString()}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Forecasting Tab */}
        <TabsContent value="forecasting">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Globe className="mr-2 h-5 w-5 text-indigo-500" /> Market Forecasting
              </CardTitle>
              <CardDescription>Market trend predictions and growth forecasts</CardDescription>
            </CardHeader>
            <CardContent>
              {marketForecast && (
                <div className="space-y-6">
                  {/* Market Growth Forecast */}
                  <div className="text-center p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
                    <div className="text-4xl font-bold text-indigo-600 mb-2">
                      {formatPercentage(marketForecast.predicted_growth)}
                    </div>
                    <div className="text-lg font-semibold text-gray-800">Predicted Market Growth</div>
                    <div className="text-sm text-gray-600">{marketForecast.forecast_period} forecast</div>
                    <div className="text-sm text-gray-600 mt-2">
                      Confidence: {formatPercentage(marketForecast.confidence)}
                    </div>
                  </div>
                  
                  {/* Key Drivers */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-green-600">Key Growth Drivers</h3>
                    <div className="space-y-2">
                      {marketForecast.key_drivers.map((driver, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-green-50 rounded">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{driver}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Risks */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-red-600">Market Risks</h3>
                    <div className="space-y-2">
                      {marketForecast.risks.map((risk, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-red-50 rounded">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          <span className="text-sm">{risk}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Opportunities */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-blue-600">Market Opportunities</h3>
                    <div className="space-y-2">
                      {marketForecast.opportunities.map((opportunity, index) => (
                        <div key={index} className="flex items-center space-x-2 p-2 bg-blue-50 rounded">
                          <ArrowUp className="h-4 w-4 text-blue-500" />
                          <span className="text-sm">{opportunity}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Cpu className="mr-2 h-5 w-5 text-blue-500" /> AI Model Performance
              </CardTitle>
              <CardDescription>Machine learning model accuracy and performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(modelPerformance).map(([modelName, performance]) => (
                  <Card key={modelName} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <Cpu className="h-5 w-5 text-blue-500" />
                        <span className="ml-2 font-semibold text-lg capitalize">
                          {modelName.replace('_', ' ')}
                        </span>
                      </div>
                      <Badge variant="outline">
                        {performance.trained_at ? new Date(performance.trained_at).toLocaleDateString() : 'Not trained'}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-gray-600">Accuracy (R²)</div>
                        <div className="text-2xl font-bold text-green-600">
                          {formatPercentage(performance.accuracy || 0)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">MSE</div>
                        <div className="text-lg font-semibold">
                          {(performance.mse || 0).toFixed(4)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Training Samples</div>
                        <div className="text-lg font-semibold">
                          {formatNumber(performance.training_samples || 0)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Status</div>
                        <Badge className={performance.accuracy > 0.7 ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'}>
                          {performance.accuracy > 0.7 ? 'High Accuracy' : 'Needs Training'}
                        </Badge>
                      </div>
                    </div>
                    
                    {performance.feature_importance && Object.keys(performance.feature_importance).length > 0 && (
                      <div className="mt-4">
                        <div className="text-sm font-medium mb-2">Feature Importance:</div>
                        <div className="space-y-1">
                          {Object.entries(performance.feature_importance)
                            .sort(([,a], [,b]) => b - a)
                            .slice(0, 3)
                            .map(([feature, importance]) => (
                            <div key={feature} className="flex items-center justify-between text-sm">
                              <span className="capitalize">{feature.replace('_', ' ')}</span>
                              <div className="flex items-center space-x-2">
                                <Progress value={importance * 100} className="w-20 h-2" />
                                <span>{formatPercentage(importance)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Lightbulb className="mr-2 h-5 w-5 text-yellow-500" /> AI Insights
              </CardTitle>
              <CardDescription>Actionable insights powered by predictive intelligence</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Performance Insights */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Performance Insights</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <TrendingUp className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-semibold">High-Performing Campaigns</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        AI predicts 25% increase in conversion rate for campaigns with budget > $3000 and targeting score > 0.8
                      </p>
                    </div>
                    
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Target className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-semibold">Optimization Opportunity</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Reducing CPA by 15% possible through audience refinement and creative optimization
                      </p>
                    </div>
                    
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <BarChart3 className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="font-semibold">ROAS Improvement</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Scaling high-ROAS campaigns could increase total revenue by 30% within 60 days
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Market Insights */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-indigo-600">Market Insights</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Globe className="h-5 w-5 text-indigo-500 mr-2" />
                        <span className="font-semibold">Market Growth Trend</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Digital marketing market expected to grow 15.2% over next 6 months with mobile-first strategies leading
                      </p>
                    </div>
                    
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Users className="h-5 w-5 text-orange-500 mr-2" />
                        <span className="font-semibold">Audience Expansion</span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Gen Z audience segment showing 40% higher engagement rates - recommend increasing allocation
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Actionable Recommendations */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-yellow-600">Actionable Recommendations</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div className="flex items-center mb-2">
                        <Zap className="h-5 w-5 text-yellow-500 mr-2" />
                        <span className="font-semibold">Immediate Actions</span>
                      </div>
                      <ul className="text-sm text-gray-700 space-y-1">
                        <li>• Increase budget for top-performing campaigns by 25%</li>
                        <li>• Pause campaigns with ROAS < 1.5 for optimization</li>
                        <li>• Update creative assets for underperforming campaigns</li>
                      </ul>
                    </div>
                    
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                      <div className="flex items-center mb-2">
                        <Calendar className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-semibold">30-Day Strategy</span>
                      </div>
                      <ul className="text-sm text-gray-700 space-y-1">
                        <li>• Implement AI-powered audience targeting</li>
                        <li>• Launch A/B tests for creative optimization</li>
                        <li>• Scale successful campaign elements</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PredictiveIntelligenceDashboard;