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
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  Target,
  BarChart3,
  PieChart,
  Globe,
  Users,
  Zap,
  Lightbulb,
  Shield,
  Clock,
  RefreshCw,
  Download,
  Settings,
  Activity,
  Gauge,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Award,
  Trophy
} from 'lucide-react';
import api from '@/services/api';

const AdvancedAIDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [marketIntelligence, setMarketIntelligence] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [trends, setTrends] = useState([]);
  const [competitiveIntelligence, setCompetitiveIntelligence] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDays, setSelectedDays] = useState(30);
  const [selectedMetrics, setSelectedMetrics] = useState('impressions,clicks,conversions,revenue');
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [insightsData, marketData, anomaliesData, trendsData, competitiveData] = await Promise.all([
        api.get(`/api/ai/insights-dashboard/${clientId}`),
        api.get(`/api/ai/market-intelligence/${clientId}`),
        api.get(`/api/ai/anomalies/${clientId}?days=${selectedDays}`),
        api.get(`/api/ai/trends/${clientId}?metrics=${selectedMetrics}&days=90`),
        api.get(`/api/ai/competitive-intelligence/${clientId}`)
      ]);
      
      setAiInsights(insightsData.data);
      setMarketIntelligence(marketData.data || []);
      setAnomalies(anomaliesData.data || []);
      setTrends(trendsData.data || []);
      setCompetitiveIntelligence(competitiveData.data);
    } catch (err) {
      console.error("Failed to fetch AI data:", err);
      setError("Failed to load AI insights. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedDays, selectedMetrics]);

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
    return `${value.toFixed(1)}%`;
  };

  const getSeverityColor = (severity) => {
    if (severity >= 8) return 'text-red-600';
    if (severity >= 5) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getSeverityBadge = (severity) => {
    if (severity >= 8) return 'bg-red-500';
    if (severity >= 5) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getTrendIcon = (direction) => {
    switch (direction) {
      case 'rising': return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'falling': return <ArrowDown className="h-4 w-4 text-red-500" />;
      case 'stable': return <Minus className="h-4 w-4 text-gray-500" />;
      case 'volatile': return <Activity className="h-4 w-4 text-yellow-500" />;
      default: return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'bullish': return 'text-green-600';
      case 'bearish': return 'text-red-600';
      case 'neutral': return 'text-gray-600';
      case 'volatile': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'bullish': return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'bearish': return <TrendingDown className="h-4 w-4 text-red-500" />;
      case 'neutral': return <Minus className="h-4 w-4 text-gray-500" />;
      case 'volatile': return <Activity className="h-4 w-4 text-yellow-500" />;
      default: return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getAnomalyTypeIcon = (type) => {
    switch (type) {
      case 'performance_spike': return <ArrowUp className="h-4 w-4 text-green-500" />;
      case 'performance_drop': return <ArrowDown className="h-4 w-4 text-red-500" />;
      case 'cost_anomaly': return <Target className="h-4 w-4 text-orange-500" />;
      case 'traffic_anomaly': return <Users className="h-4 w-4 text-blue-500" />;
      case 'conversion_anomaly': return <CheckCircle className="h-4 w-4 text-purple-500" />;
      case 'competitive_threat': return <Shield className="h-4 w-4 text-red-500" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  if (loading) return <div className="text-center p-8">Loading Advanced AI Insights...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-purple-50 to-pink-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-purple-800 flex items-center">
              <Brain className="mr-2 h-6 w-6 text-purple-500" /> Advanced AI Features
            </CardTitle>
            <CardDescription className="text-gray-700">
              Market intelligence, anomaly detection, trend analysis, and competitive insights
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Select value={selectedDays.toString()} onValueChange={(value) => setSelectedDays(parseInt(value))}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">7 days</SelectItem>
                <SelectItem value="30">30 days</SelectItem>
                <SelectItem value="90">90 days</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-purple-600 border-purple-300 hover:bg-purple-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button className="flex items-center text-white bg-purple-600 hover:bg-purple-700">
              <Download className="mr-2 h-4 w-4" /> Export Insights
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* AI Insights Summary */}
      {aiInsights && (
        <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
              <Lightbulb className="mr-2 h-5 w-5 text-yellow-500" /> AI Insights Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{marketIntelligence.length}</div>
                <div className="text-lg font-semibold text-gray-800">Market Insights</div>
                <div className="text-sm text-gray-600">Industry intelligence</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">{anomalies.length}</div>
                <div className="text-lg font-semibold text-gray-800">Anomalies Detected</div>
                <div className="text-sm text-gray-600">Performance alerts</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{trends.length}</div>
                <div className="text-lg font-semibold text-gray-800">Trends Analyzed</div>
                <div className="text-sm text-gray-600">Predictive insights</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">
                  {competitiveIntelligence?.market_ranking || 5}
                </div>
                <div className="text-lg font-semibold text-gray-800">Market Ranking</div>
                <div className="text-sm text-gray-600">Competitive position</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main AI Features Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-purple-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="intelligence" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Intelligence</TabsTrigger>
          <TabsTrigger value="anomalies" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Anomalies</TabsTrigger>
          <TabsTrigger value="trends" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Trends</TabsTrigger>
          <TabsTrigger value="competitive" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Competitive</TabsTrigger>
          <TabsTrigger value="recommendations" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Recommendations</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Key Insights */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <Lightbulb className="mr-2 h-5 w-5 text-yellow-500" /> Key AI Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aiInsights?.summary_insights?.key_insights?.slice(0, 5).map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Lightbulb className="h-5 w-5 text-blue-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-blue-800">{insight}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Alerts & Risks */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <AlertTriangle className="mr-2 h-5 w-5 text-red-500" /> Alerts & Risks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {aiInsights?.summary_insights?.alerts?.slice(0, 3).map((alert, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                      <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-red-800">{alert}</div>
                      </div>
                    </div>
                  ))}
                  
                  {aiInsights?.summary_insights?.risks?.slice(0, 2).map((risk, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                      <Shield className="h-5 w-5 text-orange-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-orange-800">{risk}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Market Intelligence Tab */}
        <TabsContent value="intelligence">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Globe className="mr-2 h-5 w-5 text-blue-500" /> Market Intelligence
              </CardTitle>
              <CardDescription>Industry news, trends, and competitive analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {marketIntelligence.map((intelligence) => (
                  <Card key={intelligence.intelligence_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getSentimentIcon(intelligence.sentiment)}
                        <span className="ml-2 font-semibold text-lg">{intelligence.title}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getSentimentColor(intelligence.sentiment)} border-current`}>
                          {intelligence.sentiment.toUpperCase()}
                        </Badge>
                        <Badge variant="outline">{intelligence.category}</Badge>
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-3">{intelligence.description}</p>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <span>Impact: {formatPercentage(intelligence.impact_score * 100)}</span>
                        <span>Confidence: {formatPercentage(intelligence.confidence * 100)}</span>
                        <span>Source: {intelligence.source}</span>
                      </div>
                      <div className="text-xs">
                        {new Date(intelligence.published_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="mt-3 flex flex-wrap gap-1">
                      {intelligence.tags.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Anomalies Tab */}
        <TabsContent value="anomalies">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <AlertTriangle className="mr-2 h-5 w-5 text-red-500" /> Anomaly Detection
              </CardTitle>
              <CardDescription>Detected anomalies in campaign performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {anomalies.map((anomaly) => (
                  <Card key={anomaly.anomaly_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getAnomalyTypeIcon(anomaly.anomaly_type)}
                        <span className="ml-2 font-semibold text-lg">{anomaly.description}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getSeverityBadge(anomaly.severity)} text-white`}>
                          Severity: {anomaly.severity.toFixed(1)}
                        </Badge>
                        <Badge variant="outline">
                          Confidence: {formatPercentage(anomaly.confidence * 100)}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Severity</span>
                        <span className={`font-semibold ${getSeverityColor(anomaly.severity)}`}>
                          {anomaly.severity.toFixed(1)}/10
                        </span>
                      </div>
                      <Progress value={anomaly.severity * 10} className="h-2" />
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Recommendations:</div>
                      <ul className="text-sm text-gray-700 space-y-1">
                        {anomaly.recommendations.map((rec, index) => (
                          <li key={index}>• {rec}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <span>Type: {anomaly.anomaly_type.replace('_', ' ')}</span>
                        <span>Impact: {formatPercentage(anomaly.impact_score * 100)}</span>
                      </div>
                      <div className="text-xs">
                        {new Date(anomaly.detected_at).toLocaleDateString()}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> Trend Analysis
              </CardTitle>
              <CardDescription>Performance trends and predictions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {trends.map((trend) => (
                  <Card key={trend.trend_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getTrendIcon(trend.trend_direction)}
                        <span className="ml-2 font-semibold text-lg capitalize">{trend.metric_name}</span>
                      </div>
                      <Badge variant="outline" className={trend.trend_direction === 'rising' ? 'text-green-600 border-green-300' : trend.trend_direction === 'falling' ? 'text-red-600 border-red-300' : 'text-gray-600 border-gray-300'}>
                        {trend.trend_direction.toUpperCase()}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-sm">
                        <span>Trend Strength:</span>
                        <span className="font-semibold">{trend.trend_strength.toFixed(1)}</span>
                      </div>
                      <Progress value={trend.trend_strength * 10} className="h-2" />
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-sm">
                        <span>Confidence:</span>
                        <span className="font-semibold">{formatPercentage(trend.confidence * 100)}</span>
                      </div>
                      <Progress value={trend.confidence * 100} className="h-2" />
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-1">Predicted Value:</div>
                      <div className="text-lg font-bold text-blue-600">
                        {formatNumber(trend.predicted_value)}
                      </div>
                      <div className="text-xs text-gray-600">
                        Predicted for: {new Date(trend.predicted_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-600">
                      <div className="font-medium mb-1">Key Factors:</div>
                      <ul className="space-y-1">
                        {trend.factors.slice(0, 2).map((factor, index) => (
                          <li key={index}>• {factor}</li>
                        ))}
                      </ul>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Competitive Intelligence Tab */}
        <TabsContent value="competitive">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Trophy className="mr-2 h-5 w-5 text-yellow-500" /> Competitive Intelligence
              </CardTitle>
              <CardDescription>Market positioning and competitive analysis</CardDescription>
            </CardHeader>
            <CardContent>
              {competitiveIntelligence && (
                <div className="space-y-6">
                  {/* Market Ranking */}
                  <div className="text-center p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <div className="text-4xl font-bold text-purple-600 mb-2">
                      #{competitiveIntelligence.market_ranking}
                    </div>
                    <div className="text-lg font-semibold text-gray-800">Market Ranking</div>
                    <div className="text-sm text-gray-600">Out of 10 competitors</div>
                  </div>
                  
                  {/* SWOT Analysis */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold text-lg mb-3 text-green-600">Strengths</h3>
                      <div className="space-y-2">
                        {competitiveIntelligence.strengths.map((strength, index) => (
                          <div key={index} className="flex items-center space-x-2 p-2 bg-green-50 rounded">
                            <CheckCircle className="h-4 w-4 text-green-500" />
                            <span className="text-sm">{strength}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-3 text-red-600">Weaknesses</h3>
                      <div className="space-y-2">
                        {competitiveIntelligence.weaknesses.map((weakness, index) => (
                          <div key={index} className="flex items-center space-x-2 p-2 bg-red-50 rounded">
                            <XCircle className="h-4 w-4 text-red-500" />
                            <span className="text-sm">{weakness}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-3 text-blue-600">Opportunities</h3>
                      <div className="space-y-2">
                        {competitiveIntelligence.opportunities.map((opportunity, index) => (
                          <div key={index} className="flex items-center space-x-2 p-2 bg-blue-50 rounded">
                            <ArrowUp className="h-4 w-4 text-blue-500" />
                            <span className="text-sm">{opportunity}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-lg mb-3 text-orange-600">Threats</h3>
                      <div className="space-y-2">
                        {competitiveIntelligence.threats.map((threat, index) => (
                          <div key={index} className="flex items-center space-x-2 p-2 bg-orange-50 rounded">
                            <Shield className="h-4 w-4 text-orange-500" />
                            <span className="text-sm">{threat}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  {/* Recommendations */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-purple-600">Recommendations</h3>
                    <div className="space-y-2">
                      {competitiveIntelligence.recommendations.map((recommendation, index) => (
                        <div key={index} className="flex items-start space-x-2 p-3 bg-purple-50 rounded-lg">
                          <Lightbulb className="h-4 w-4 text-purple-500 flex-shrink-0 mt-1" />
                          <span className="text-sm">{recommendation}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Zap className="mr-2 h-5 w-5 text-yellow-500" /> AI Recommendations
              </CardTitle>
              <CardDescription>Actionable insights powered by AI analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* High Priority */}
                {aiInsights?.summary_insights?.recommendations?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-red-600">High Priority</h3>
                    <div className="space-y-2">
                      {aiInsights.summary_insights.recommendations.slice(0, 3).map((rec, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg border border-red-200">
                          <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-1" />
                          <div>
                            <div className="font-medium text-red-800">{rec}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Opportunities */}
                {aiInsights?.summary_insights?.opportunities?.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-green-600">Opportunities</h3>
                    <div className="space-y-2">
                      {aiInsights.summary_insights.opportunities.slice(0, 3).map((opp, index) => (
                        <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg border border-green-200">
                          <ArrowUp className="h-5 w-5 text-green-500 flex-shrink-0 mt-1" />
                          <div>
                            <div className="font-medium text-green-800">{opp}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* General Recommendations */}
                <div>
                  <h3 className="font-semibold text-lg mb-3 text-blue-600">General Recommendations</h3>
                  <div className="space-y-2">
                    <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Lightbulb className="h-5 w-5 text-blue-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-blue-800">Optimize campaign targeting based on trend analysis</div>
                        <div className="text-sm text-blue-700 mt-1">Focus on high-performing audience segments identified by AI</div>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <Target className="h-5 w-5 text-blue-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-blue-800">Implement anomaly detection monitoring</div>
                        <div className="text-sm text-blue-700 mt-1">Set up automated alerts for performance anomalies</div>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <BarChart3 className="h-5 w-5 text-blue-500 flex-shrink-0 mt-1" />
                      <div>
                        <div className="font-medium text-blue-800">Leverage competitive intelligence insights</div>
                        <div className="text-sm text-blue-700 mt-1">Adjust strategy based on competitor positioning</div>
                      </div>
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

export default AdvancedAIDashboard;
