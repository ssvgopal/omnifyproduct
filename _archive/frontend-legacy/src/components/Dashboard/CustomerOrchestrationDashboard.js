import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Play,
  Pause,
  RotateCcw,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  Zap,
  Users,
  Target,
  BarChart3,
  TrendingUp,
  Eye,
  Brain,
  Sparkles,
  Rocket,
  Timer,
  RefreshCw,
  ArrowRight,
  ArrowLeft,
  Star,
  Award,
  Crown
} from 'lucide-react';
import api from '@/services/api';

const CustomerOrchestrationDashboard = () => {
  const [sessionId, setSessionId] = useState(null);
  const [orchestrationFeed, setOrchestrationFeed] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('feed');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadDemoFeed();
  }, []);

  useEffect(() => {
    if (autoRefresh && sessionId) {
      const interval = setInterval(() => {
        loadOrchestrationFeed(sessionId);
      }, 3000); // Refresh every 3 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh, sessionId]);

  const loadDemoFeed = async () => {
    try {
      const response = await api.get('/api/orchestration/demo-feed');
      if (response.data.success) {
        setOrchestrationFeed(response.data.data);
        setSessionId(response.data.data.session_id);
        setIsRunning(true);
      }
    } catch (error) {
      console.error('Error loading demo feed:', error);
    }
  };

  const startOrchestrationSession = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/orchestration/start', {
        organization_id: 'org_123',
        campaign_ids: ['campaign_1', 'campaign_2', 'campaign_3']
      });
      
      if (response.data.success) {
        setSessionId(response.data.data.session_id);
        setIsRunning(true);
        
        // Start monitoring feed
        loadOrchestrationFeed(response.data.data.session_id);
      }
    } catch (error) {
      console.error('Error starting orchestration:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOrchestrationFeed = async (sessionId) => {
    try {
      const response = await api.get(`/api/orchestration/feed/${sessionId}`);
      if (response.data.success) {
        setOrchestrationFeed(response.data.data);
      }
    } catch (error) {
      console.error('Error loading orchestration feed:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'planned': return 'text-yellow-600 bg-yellow-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'in_progress': return <Activity className="h-4 w-4" />;
      case 'planned': return <Clock className="h-4 w-4" />;
      case 'failed': return <AlertCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const getAgentColor = (color) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-100',
      purple: 'text-purple-600 bg-purple-100',
      green: 'text-green-600 bg-green-100',
      yellow: 'text-yellow-600 bg-yellow-100',
      pink: 'text-pink-600 bg-pink-100',
      red: 'text-red-600 bg-red-100',
      orange: 'text-orange-600 bg-orange-100',
      teal: 'text-teal-600 bg-teal-100'
    };
    return colors[color] || 'text-gray-600 bg-gray-100';
  };

  const formatTime = (timeString) => {
    const time = new Date(timeString);
    const now = new Date();
    const diffMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return time.toLocaleDateString();
  };

  const formatDuration = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🎭 AI Orchestration Center</h1>
          <p className="text-gray-600 mt-2">Watch your AI agents work 24/7 to optimize your campaigns</p>
        </div>
        <div className="flex space-x-3">
          {!isRunning ? (
            <Button 
              onClick={startOrchestrationSession}
              disabled={loading}
              className="bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white"
            >
              {loading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Start Orchestration
            </Button>
          ) : (
            <div className="flex space-x-2">
              <Button 
                onClick={() => setAutoRefresh(!autoRefresh)}
                variant="outline"
                className={autoRefresh ? "bg-green-50 border-green-300 text-green-700" : ""}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
                {autoRefresh ? 'Live' : 'Paused'}
              </Button>
              <Button 
                onClick={() => setIsRunning(false)}
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50"
              >
                <Pause className="h-4 w-4 mr-2" />
                Stop
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Session Status */}
      {orchestrationFeed && (
        <Card className="p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🎭</div>
              <div>
                <h3 className="text-lg font-bold">AI Orchestration Active</h3>
                <p className="text-sm text-gray-600">Session: {orchestrationFeed.session_id}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge className="bg-purple-100 text-purple-800">
                <Activity className="h-3 w-3 mr-1" />
                {orchestrationFeed.session_stats.active_events} Active
              </Badge>
              <div className="text-sm text-gray-600">
                <Timer className="h-4 w-4 inline mr-1" />
                {Math.round(orchestrationFeed.session_stats.session_duration / 60)} min
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {orchestrationFeed.session_stats.total_events}
              </div>
              <div className="text-sm text-gray-600">Total Events</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {orchestrationFeed.session_stats.completed_events}
              </div>
              <div className="text-sm text-gray-600">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {orchestrationFeed.session_stats.active_events}
              </div>
              <div className="text-sm text-gray-600">In Progress</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {orchestrationFeed.active_agents.length}
              </div>
              <div className="text-sm text-gray-600">AI Agents</div>
            </div>
          </div>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="feed">Live Feed</TabsTrigger>
          <TabsTrigger value="agents">AI Agents</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Live Feed Tab */}
        <TabsContent value="feed" className="space-y-4">
          {orchestrationFeed && orchestrationFeed.events.length > 0 ? (
            <div className="space-y-4">
              {orchestrationFeed.events.map((event, index) => (
                <Card key={event.event_id} className="p-6">
                  <div className="flex items-start space-x-4">
                    {/* Agent Avatar */}
                    <div className="flex-shrink-0">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${getAgentColor(event.agent.color)}`}>
                        {event.agent.avatar}
                      </div>
                    </div>
                    
                    {/* Event Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <h3 className="text-lg font-bold">{event.title}</h3>
                          <Badge className={getStatusColor(event.status)}>
                            {getStatusIcon(event.status)}
                            <span className="ml-1 capitalize">{event.status.replace('_', ' ')}</span>
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatTime(event.start_time)}
                        </div>
                      </div>
                      
                      <div className="mb-3">
                        <p className="text-gray-700 mb-2">{event.description}</p>
                        <div className="text-sm text-blue-600 bg-blue-50 p-3 rounded-lg">
                          {event.customer_message}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        <div>
                          <div className="text-sm text-gray-600">Campaign</div>
                          <div className="font-bold">{event.campaign_id}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Platform</div>
                          <div className="font-bold">{event.platform}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-600">Duration</div>
                          <div className="font-bold">
                            {event.actual_duration ? formatDuration(event.actual_duration) : formatDuration(event.estimated_duration)}
                          </div>
                        </div>
                      </div>
                      
                      {/* Results */}
                      {event.results && Object.keys(event.results).length > 0 && (
                        <div className="mt-4 p-4 bg-green-50 rounded-lg">
                          <h4 className="font-bold text-green-800 mb-2">Results</h4>
                          {event.results.metrics_improved && event.results.metrics_improved.length > 0 && (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
                              {event.results.metrics_improved.map((metric, idx) => (
                                <div key={idx} className="flex justify-between">
                                  <span className="text-sm text-gray-600">{metric.metric}:</span>
                                  <span className="text-sm font-bold text-green-600">{metric.improvement}</span>
                                </div>
                              ))}
                            </div>
                          )}
                          {event.results.value_added > 0 && (
                            <div className="text-sm text-green-700">
                              <strong>Value Added:</strong> ${event.results.value_added.toFixed(2)}
                            </div>
                          )}
                          {event.results.recommendations && event.results.recommendations.length > 0 && (
                            <div className="mt-2">
                              <div className="text-sm text-gray-600 mb-1">Recommendations:</div>
                              <ul className="text-sm text-gray-700 list-disc list-inside">
                                {event.results.recommendations.map((rec, idx) => (
                                  <li key={idx}>{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                      
                      {/* Progress Bar for In Progress Events */}
                      {event.status === 'in_progress' && (
                        <div className="mt-4">
                          <div className="flex justify-between text-sm text-gray-600 mb-1">
                            <span>Progress</span>
                            <span>{Math.round((event.actual_duration || 0) / event.estimated_duration * 100)}%</span>
                          </div>
                          <Progress 
                            value={((event.actual_duration || 0) / event.estimated_duration) * 100} 
                            className="h-2" 
                          />
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🎭</div>
              <h3 className="text-lg font-bold text-gray-600">No Orchestration Events</h3>
              <p className="text-gray-500">Start an orchestration session to see AI agents in action</p>
            </Card>
          )}
        </TabsContent>

        {/* AI Agents Tab */}
        <TabsContent value="agents" className="space-y-6">
          {orchestrationFeed && orchestrationFeed.active_agents.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {orchestrationFeed.active_agents.map((agent, index) => (
                <Card key={index} className="p-6">
                  <div className="text-center">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center text-3xl mx-auto mb-4 ${getAgentColor(agent.color)}`}>
                      {agent.avatar}
                    </div>
                    <h3 className="text-lg font-bold mb-2">{agent.name}</h3>
                    <p className="text-sm text-gray-600 mb-3">{agent.specialty}</p>
                    <p className="text-xs text-gray-500 mb-4">{agent.description}</p>
                    
                    <div className="space-y-2">
                      <div className="text-sm font-bold text-gray-700">Capabilities:</div>
                      <div className="flex flex-wrap gap-1">
                        {agent.capabilities.map((capability, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {capability}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mt-4">
                      <Badge className="bg-green-100 text-green-800">
                        <Activity className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-lg font-bold text-gray-600">No Active Agents</h3>
              <p className="text-gray-500">Start an orchestration session to activate AI agents</p>
            </Card>
          )}
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          {orchestrationFeed ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Event Distribution */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Event Distribution</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Completed</span>
                    <span className="font-bold text-green-600">
                      {orchestrationFeed.session_stats.completed_events}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">In Progress</span>
                    <span className="font-bold text-blue-600">
                      {orchestrationFeed.session_stats.active_events}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Planned</span>
                    <span className="font-bold text-yellow-600">
                      {orchestrationFeed.session_stats.total_events - orchestrationFeed.session_stats.completed_events - orchestrationFeed.session_stats.active_events}
                    </span>
                  </div>
                </div>
              </Card>
              
              {/* Agent Activity */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Agent Activity</h3>
                <div className="space-y-3">
                  {orchestrationFeed.active_agents.map((agent, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="text-lg">{agent.avatar}</div>
                        <span className="text-sm font-bold">{agent.name}</span>
                      </div>
                      <Badge className="bg-green-100 text-green-800">
                        Active
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Performance Metrics */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Performance Metrics</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Completion Rate</span>
                    <span className="font-bold text-blue-600">
                      {Math.round((orchestrationFeed.session_stats.completed_events / orchestrationFeed.session_stats.total_events) * 100)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Active Events</span>
                    <span className="font-bold text-green-600">
                      {orchestrationFeed.session_stats.active_events}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Session Duration</span>
                    <span className="font-bold text-purple-600">
                      {Math.round(orchestrationFeed.session_stats.session_duration / 60)} min
                    </span>
                  </div>
                </div>
              </Card>
              
              {/* Recent Activity */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Recent Activity</h3>
                <div className="space-y-2">
                  {orchestrationFeed.events.slice(0, 5).map((event, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm">
                      <div className="text-lg">{event.agent.avatar}</div>
                      <span className="text-gray-600">{event.title}</span>
                      <Badge className={getStatusColor(event.status)} size="sm">
                        {event.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-bold text-gray-600">No Analytics Data</h3>
              <p className="text-gray-500">Start an orchestration session to see analytics</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CustomerOrchestrationDashboard;
