import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Zap,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Clock,
  CheckCircle,
  Play,
  Pause,
  RotateCcw,
  BarChart3,
  PieChart,
  LineChart,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Eye,
  Users,
  MousePointer,
  Percent,
  Award,
  Star,
  Sparkles,
  Rocket,
  Timer,
  RefreshCw
} from 'lucide-react';
import api from '@/services/api';

const InstantValueDeliveryDashboard = () => {
  const [sessionId, setSessionId] = useState(null);
  const [sessionProgress, setSessionProgress] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [platforms, setPlatforms] = useState([]);
  const [demoResults, setDemoResults] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadSupportedPlatforms();
    loadDemoResults();
  }, []);

  const loadSupportedPlatforms = async () => {
    try {
      const response = await api.get('/api/instant-value/platforms');
      if (response.data.success) {
        setPlatforms(response.data.platforms);
      }
    } catch (error) {
      console.error('Error loading platforms:', error);
    }
  };

  const loadDemoResults = async () => {
    try {
      const response = await api.get('/api/instant-value/demo-results');
      if (response.data.success) {
        setDemoResults(response.data);
      }
    } catch (error) {
      console.error('Error loading demo results:', error);
    }
  };

  const startInstantValueSession = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/instant-value/start', {
        organization_id: 'org_123',
        target_platforms: ['google_ads', 'meta_ads', 'linkedin_ads']
      });
      
      if (response.data.success) {
        setSessionId(response.data.data.session_id);
        setIsRunning(true);
        
        // Start monitoring progress
        monitorProgress(response.data.data.session_id);
      }
    } catch (error) {
      console.error('Error starting session:', error);
    } finally {
      setLoading(false);
    }
  };

  const monitorProgress = async (sessionId) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/instant-value/progress/${sessionId}`);
        if (response.data.success) {
          setSessionProgress(response.data.data);
          
          // Check if session is completed
          if (response.data.data.status === 'completed') {
            setIsRunning(false);
            clearInterval(interval);
          }
        }
      } catch (error) {
        console.error('Error monitoring progress:', error);
        clearInterval(interval);
      }
    }, 2000); // Check every 2 seconds
  };

  const executePlatformOptimization = async (platform) => {
    try {
      const response = await api.post(`/api/instant-value/optimize/${sessionId}`, {
        platform: platform,
        campaign_ids: null
      });
      
      if (response.data.success) {
        console.log(`Optimization completed for ${platform}`);
      }
    } catch (error) {
      console.error(`Error optimizing ${platform}:`, error);
    }
  };

  const completeSession = async () => {
    try {
      const response = await api.post(`/api/instant-value/complete/${sessionId}`);
      
      if (response.data.success) {
        setIsRunning(false);
        console.log('Session completed successfully');
      }
    } catch (error) {
      console.error('Error completing session:', error);
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      google_ads: '🔍',
      meta_ads: '📱',
      linkedin_ads: '💼',
      tiktok_ads: '🎵',
      shopify: '🛒',
      gohighlevel: '📈'
    };
    return icons[platform] || '🎯';
  };

  const getPlatformColor = (platform) => {
    const colors = {
      google_ads: 'text-blue-600 bg-blue-100',
      meta_ads: 'text-purple-600 bg-purple-100',
      linkedin_ads: 'text-blue-700 bg-blue-100',
      tiktok_ads: 'text-black bg-gray-100',
      shopify: 'text-green-600 bg-green-100',
      gohighlevel: 'text-orange-600 bg-orange-100'
    };
    return colors[platform] || 'text-gray-600 bg-gray-100';
  };

  const formatValue = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">⚡ Instant Value Delivery</h1>
          <p className="text-gray-600 mt-2">Get immediate ROI improvements in minutes, not months</p>
        </div>
        <div className="flex space-x-3">
          {!isRunning ? (
            <Button 
              onClick={startInstantValueSession}
              disabled={loading}
              className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Rocket className="h-4 w-4 mr-2" />
              )}
              Start Instant Optimization
            </Button>
          ) : (
            <Button 
              onClick={completeSession}
              variant="outline"
              className="border-red-300 text-red-600 hover:bg-red-50"
            >
              <Pause className="h-4 w-4 mr-2" />
              Complete Session
            </Button>
          )}
        </div>
      </div>

      {/* Session Status */}
      {sessionId && (
        <Card className="p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">⚡</div>
              <div>
                <h3 className="text-lg font-bold">Instant Value Session Active</h3>
                <p className="text-sm text-gray-600">Session ID: {sessionId}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="bg-green-100 text-green-800">
                <Activity className="h-3 w-3 mr-1" />
                {isRunning ? 'Running' : 'Completed'}
              </Badge>
              {sessionProgress && (
                <div className="text-sm text-gray-600">
                  <Timer className="h-4 w-4 inline mr-1" />
                  {Math.round(sessionProgress.progress.session_duration / 60)} min
                </div>
              )}
            </div>
          </div>
          
          {sessionProgress && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">Progress</span>
                <span className="text-sm font-bold">{Math.round(sessionProgress.progress.percentage)}%</span>
              </div>
              <Progress value={sessionProgress.progress.percentage} className="h-2" />
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {formatValue(sessionProgress.value_metrics.total_value_added)}
                  </div>
                  <div className="text-sm text-gray-600">Value Added</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {sessionProgress.progress.total_optimizations}
                  </div>
                  <div className="text-sm text-gray-600">Optimizations</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {sessionProgress.progress.completed_platforms}
                  </div>
                  <div className="text-sm text-gray-600">Platforms</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {Math.round(sessionProgress.value_metrics.average_improvement.roas || 0)}%
                  </div>
                  <div className="text-sm text-gray-600">Avg ROAS</div>
                </div>
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
          <TabsTrigger value="demo">Demo</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="p-4">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-green-600" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">$426.50</div>
                  <div className="text-sm text-gray-600">Total Value Added</div>
                </div>
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center">
                <Target className="h-8 w-8 text-blue-600" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">9</div>
                  <div className="text-sm text-gray-600">Optimizations</div>
                </div>
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-purple-600" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">+18.5%</div>
                  <div className="text-sm text-gray-600">Avg ROAS</div>
                </div>
              </div>
            </Card>
            
            <Card className="p-4">
              <div className="flex items-center">
                <Clock className="h-8 w-8 text-orange-600" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">12m</div>
                  <div className="text-sm text-gray-600">Time Saved</div>
                </div>
              </div>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4">🚀 Quick Actions</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                onClick={() => executePlatformOptimization('google_ads')}
                className="h-20 flex flex-col items-center justify-center space-y-2"
                variant="outline"
              >
                <div className="text-2xl">🔍</div>
                <div className="text-sm font-bold">Optimize Google Ads</div>
                <div className="text-xs text-gray-600">5 min • +15% ROAS</div>
              </Button>
              
              <Button 
                onClick={() => executePlatformOptimization('meta_ads')}
                className="h-20 flex flex-col items-center justify-center space-y-2"
                variant="outline"
              >
                <div className="text-2xl">📱</div>
                <div className="text-sm font-bold">Optimize Meta Ads</div>
                <div className="text-xs text-gray-600">10 min • +25% CTR</div>
              </Button>
              
              <Button 
                onClick={() => executePlatformOptimization('linkedin_ads')}
                className="h-20 flex flex-col items-center justify-center space-y-2"
                variant="outline"
              >
                <div className="text-2xl">💼</div>
                <div className="text-sm font-bold">Optimize LinkedIn</div>
                <div className="text-xs text-gray-600">7 min • +18% CTR</div>
              </Button>
            </div>
          </Card>

          {/* Recent Optimizations */}
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4">⚡ Recent Optimizations</h3>
            <div className="space-y-3">
              {[
                { platform: 'google_ads', type: 'Bid Optimization', improvement: '+15.2% ROAS', value: '$45.30', time: '2 min ago' },
                { platform: 'meta_ads', type: 'Creative Rotation', improvement: '+25.5% CTR', value: '$52.40', time: '5 min ago' },
                { platform: 'linkedin_ads', type: 'Audience Expansion', improvement: '+18.2% CTR', value: '$48.75', time: '8 min ago' }
              ].map((optimization, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="text-xl">{getPlatformIcon(optimization.platform)}</div>
                    <div>
                      <div className="font-bold">{optimization.type}</div>
                      <div className="text-sm text-gray-600">{optimization.platform.replace('_', ' ').toUpperCase()}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-green-600">{optimization.improvement}</div>
                    <div className="text-sm text-gray-600">{optimization.value}</div>
                  </div>
                  <div className="text-sm text-gray-500">{optimization.time}</div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Platforms Tab */}
        <TabsContent value="platforms" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {platforms.map((platform, index) => (
              <Card key={index} className="p-6">
                <div className="text-center">
                  <div className="text-4xl mb-3">{getPlatformIcon(platform.value)}</div>
                  <h3 className="text-lg font-bold mb-2">{platform.label}</h3>
                  <p className="text-sm text-gray-600 mb-4">{platform.description}</p>
                  
                  <Badge className={getPlatformColor(platform.value)}>
                    {platform.value.replace('_', ' ').toUpperCase()}
                  </Badge>
                  
                  <div className="mt-4 space-y-2">
                    <Button 
                      onClick={() => executePlatformOptimization(platform.value)}
                      className="w-full"
                      size="sm"
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      Optimize Now
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          {sessionProgress && sessionProgress.platform_results ? (
            <div className="space-y-6">
              {Object.entries(sessionProgress.platform_results).map(([platform, results]) => (
                <Card key={platform} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{getPlatformIcon(platform)}</div>
                      <div>
                        <h3 className="text-lg font-bold">{platform.replace('_', ' ').toUpperCase()}</h3>
                        <p className="text-sm text-gray-600">{results.optimizations} optimizations completed</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {formatValue(results.value_added)}
                      </div>
                      <div className="text-sm text-gray-600">Value Added</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    {Object.entries(results.improvements).map(([metric, improvement]) => (
                      <div key={metric} className="text-center">
                        <div className="text-lg font-bold text-blue-600">
                          {formatPercentage(improvement)}
                        </div>
                        <div className="text-sm text-gray-600 capitalize">
                          {metric.replace('_', ' ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-bold text-gray-600">No Results Yet</h3>
              <p className="text-gray-500">Start an optimization session to see results</p>
            </Card>
          )}
        </TabsContent>

        {/* Demo Tab */}
        <TabsContent value="demo" className="space-y-6">
          {demoResults && (
            <div className="space-y-6">
              {/* Demo Summary */}
              <Card className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
                <div className="text-center">
                  <div className="text-4xl mb-4">🎯</div>
                  <h3 className="text-2xl font-bold mb-2">Demo Results</h3>
                  <p className="text-lg opacity-90">See what's possible with instant optimization</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold">{formatValue(demoResults.total_value_added)}</div>
                      <div className="text-sm opacity-80">Total Value Added</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold">{demoResults.total_optimizations}</div>
                      <div className="text-sm opacity-80">Optimizations</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold">12m</div>
                      <div className="text-sm opacity-80">Time to Complete</div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Platform Results */}
              {Object.entries(demoResults.demo_results).map(([platform, results]) => (
                <Card key={platform} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{getPlatformIcon(platform)}</div>
                      <div>
                        <h3 className="text-lg font-bold">{platform.replace('_', ' ').toUpperCase()}</h3>
                        <p className="text-sm text-gray-600">{results.optimizations_completed} optimizations</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        {formatValue(results.total_value_added)}
                      </div>
                      <div className="text-sm text-gray-600">Value Added</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    {Object.entries(results.improvements).map(([metric, improvement]) => (
                      <div key={metric} className="text-center">
                        <div className="text-lg font-bold text-blue-600">
                          {formatPercentage(improvement)}
                        </div>
                        <div className="text-sm text-gray-600 capitalize">
                          {metric.replace('_', ' ')}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="space-y-2">
                    {results.results.map((result, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <CheckCircle className="h-5 w-5 text-green-500" />
                          <div>
                            <div className="font-bold">{result.type.replace('_', ' ').toUpperCase()}</div>
                            <div className="text-sm text-gray-600">{result.campaign_id}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-green-600">
                            {formatValue(result.estimated_value_added)}
                          </div>
                          <div className="text-sm text-gray-600">
                            {Math.round(result.confidence_score * 100)}% confidence
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default InstantValueDeliveryDashboard;
