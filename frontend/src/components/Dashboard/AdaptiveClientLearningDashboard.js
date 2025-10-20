import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain,
  User,
  Target,
  TrendingUp,
  Eye,
  MessageSquare,
  BarChart3,
  Lightbulb,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Play,
  Pause,
  RotateCcw,
  ArrowUpRight,
  ArrowDownRight,
  ArrowRight,
  Calendar,
  Timer,
  Star,
  Award,
  Crown,
  Zap,
  Users,
  BookOpen,
  Settings,
  Activity,
  PieChart,
  LineChart,
  Sparkles
} from 'lucide-react';
import api from '@/services/api';

const AdaptiveClientLearningDashboard = () => {
  const [clientProfile, setClientProfile] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [clientId, setClientId] = useState('client_123');

  useEffect(() => {
    loadClientProfile();
    loadInsights();
  }, [clientId]);

  const loadClientProfile = async () => {
    try {
      const response = await api.get(`/api/adaptive-learning/profile/${clientId}`);
      if (response.data.success) {
        setClientProfile(response.data.profile);
      }
    } catch (error) {
      console.error('Error loading client profile:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const response = await api.post('/api/adaptive-learning/insights', {
        client_id: clientId,
        include_recommendations: true
      });
      if (response.data.success) {
        setInsights(response.data.insights);
      }
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };

  const generateRecommendation = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/adaptive-learning/recommendation', {
        client_id: clientId,
        context: {
          current_campaign_performance: 'moderate',
          budget_available: 10000,
          timeline: '30_days',
          risk_tolerance: 'medium'
        }
      });
      
      if (response.data.success) {
        setRecommendations(prev => [response.data.recommendation, ...prev]);
      }
    } catch (error) {
      console.error('Error generating recommendation:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateDemoData = async () => {
    try {
      setLoading(true);
      
      const response = await api.get(`/api/adaptive-learning/demo-interaction/${clientId}`);
      
      if (response.data.success) {
        await loadClientProfile();
        await loadInsights();
      }
    } catch (error) {
      console.error('Error generating demo data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPersonalityIcon = (personality) => {
    switch (personality) {
      case 'analytical': return <BarChart3 className="h-4 w-4" />;
      case 'intuitive': return <Lightbulb className="h-4 w-4" />;
      case 'collaborative': return <Users className="h-4 w-4" />;
      case 'autonomous': return <User className="h-4 w-4" />;
      case 'cautious': return <AlertTriangle className="h-4 w-4" />;
      case 'aggressive': return <Zap className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getPersonalityColor = (personality) => {
    switch (personality) {
      case 'analytical': return 'text-blue-600 bg-blue-100';
      case 'intuitive': return 'text-purple-600 bg-purple-100';
      case 'collaborative': return 'text-green-600 bg-green-100';
      case 'autonomous': return 'text-orange-600 bg-orange-100';
      case 'cautious': return 'text-yellow-600 bg-yellow-100';
      case 'aggressive': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getLearningStyleIcon = (style) => {
    switch (style) {
      case 'visual': return <Eye className="h-4 w-4" />;
      case 'numerical': return <BarChart3 className="h-4 w-4" />;
      case 'narrative': return <BookOpen className="h-4 w-4" />;
      case 'interactive': return <Play className="h-4 w-4" />;
      case 'expert_guided': return <Award className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const getLearningStyleColor = (style) => {
    switch (style) {
      case 'visual': return 'text-indigo-600 bg-indigo-100';
      case 'numerical': return 'text-blue-600 bg-blue-100';
      case 'narrative': return 'text-green-600 bg-green-100';
      case 'interactive': return 'text-orange-600 bg-orange-100';
      case 'expert_guided': return 'text-purple-600 bg-purple-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🧠 Adaptive Learning</h1>
          <p className="text-gray-600 mt-2">Personalized AI that learns from your preferences</p>
        </div>
        <div className="flex space-x-3">
          <Button 
            onClick={generateRecommendation}
            disabled={loading}
            className="bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Lightbulb className="h-4 w-4 mr-2" />
            )}
            Generate Recommendation
          </Button>
          <Button 
            onClick={generateDemoData}
            variant="outline"
            disabled={loading}
          >
            <Play className="h-4 w-4 mr-2" />
            Generate Demo Data
          </Button>
        </div>
      </div>

      {/* Client Profile Overview */}
      {clientProfile && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-6">
            <div className="flex items-center">
              {getPersonalityIcon(clientProfile.personality_type)}
              <div className="ml-3">
                <div className="text-sm text-gray-600">Personality</div>
                <div className="font-bold capitalize">{clientProfile.personality_type.replace('_', ' ')}</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              {getLearningStyleIcon(clientProfile.learning_style)}
              <div className="ml-3">
                <div className="text-sm text-gray-600">Learning Style</div>
                <div className="font-bold capitalize">{clientProfile.learning_style.replace('_', ' ')}</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              <Star className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <div className="text-sm text-gray-600">Learning Score</div>
                <div className="text-2xl font-bold">{formatPercentage(clientProfile.learning_score)}</div>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <div className="text-sm text-gray-600">Confidence</div>
                <div className="text-2xl font-bold">{formatPercentage(clientProfile.confidence_level)}</div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          {clientProfile ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Personality Profile */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Brain className="h-5 w-5 mr-2 text-purple-600" />
                  Personality Profile
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Type</span>
                    <Badge className={getPersonalityColor(clientProfile.personality_type)}>
                      {getPersonalityIcon(clientProfile.personality_type)}
                      <span className="ml-1 capitalize">{clientProfile.personality_type.replace('_', ' ')}</span>
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Learning Style</span>
                    <Badge className={getLearningStyleColor(clientProfile.learning_style)}>
                      {getLearningStyleIcon(clientProfile.learning_style)}
                      <span className="ml-1 capitalize">{clientProfile.learning_style.replace('_', ' ')}</span>
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Communication</span>
                    <Badge variant="outline">
                      <MessageSquare className="h-3 w-3 mr-1" />
                      <span className="capitalize">{clientProfile.communication_preference.replace('_', ' ')}</span>
                    </Badge>
                  </div>
                </div>
              </Card>

              {/* Behavior Patterns */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-blue-600" />
                  Behavior Patterns
                </h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Decision Speed</span>
                      <span>{formatPercentage(clientProfile.behavior_patterns.decision_speed)}</span>
                    </div>
                    <Progress value={clientProfile.behavior_patterns.decision_speed * 100} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Risk Tolerance</span>
                      <span>{formatPercentage(clientProfile.behavior_patterns.risk_tolerance)}</span>
                    </div>
                    <Progress value={clientProfile.behavior_patterns.risk_tolerance * 100} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Data Reliance</span>
                      <span>{formatPercentage(clientProfile.behavior_patterns.data_reliance)}</span>
                    </div>
                    <Progress value={clientProfile.behavior_patterns.data_reliance * 100} />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Collaboration Level</span>
                      <span>{formatPercentage(clientProfile.behavior_patterns.collaboration_level)}</span>
                    </div>
                    <Progress value={clientProfile.behavior_patterns.collaboration_level * 100} />
                  </div>
                </div>
              </Card>

              {/* Success Patterns */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                  Success Patterns
                </h3>
                <div className="space-y-2">
                  {clientProfile.success_patterns.length > 0 ? (
                    clientProfile.success_patterns.map((pattern, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm capitalize">{pattern.replace('_', ' ')}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-gray-500">No success patterns identified yet</div>
                  )}
                </div>
              </Card>

              {/* Failure Patterns */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
                  Failure Patterns
                </h3>
                <div className="space-y-2">
                  {clientProfile.failure_patterns.length > 0 ? (
                    clientProfile.failure_patterns.map((pattern, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-orange-500" />
                        <span className="text-sm capitalize">{pattern.replace('_', ' ')}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-gray-500">No failure patterns identified yet</div>
                  )}
                </div>
              </Card>
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🧠</div>
              <h3 className="text-lg font-bold text-gray-600">No Profile Data</h3>
              <p className="text-gray-500">Generate demo data to see adaptive learning in action</p>
            </Card>
          )}
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          {recommendations.length > 0 ? (
            <div className="space-y-4">
              {recommendations.map((recommendation, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">💡</div>
                      <div>
                        <h3 className="text-lg font-bold capitalize">{recommendation.type.replace('_', ' ')} Recommendation</h3>
                        <p className="text-sm text-gray-600">{recommendation.presentation_style.replace('_', ' ')} presentation</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {formatPercentage(recommendation.confidence_level)} confidence
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-700 mb-3">{recommendation.content}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h4 className="font-bold text-sm mb-2">Reasoning</h4>
                      <p className="text-sm text-gray-600">{recommendation.reasoning}</p>
                    </div>
                    <div>
                      <h4 className="font-bold text-sm mb-2">Expected Outcome</h4>
                      <p className="text-sm text-gray-600">{recommendation.expected_outcome}</p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-bold text-sm mb-2">Alternatives</h4>
                    <div className="flex flex-wrap gap-2">
                      {recommendation.alternatives.map((alt, idx) => (
                        <Badge key={idx} variant="outline">{alt}</Badge>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Risk: {recommendation.risk_assessment}
                    </div>
                    <div className="text-sm text-gray-500">
                      {new Date().toLocaleDateString()}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">💡</div>
              <h3 className="text-lg font-bold text-gray-600">No Recommendations</h3>
              <p className="text-gray-500">Generate a recommendation to see personalized suggestions</p>
            </Card>
          )}
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          {insights ? (
            <div className="space-y-4">
              {insights.status === 'success' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center">
                      <Sparkles className="h-5 w-5 mr-2 text-yellow-600" />
                      Learning Insights
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Total Interactions</span>
                        <span className="font-bold">{insights.total_interactions}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Learning Progress</span>
                        <span className="font-bold">{formatPercentage(insights.learning_progress)}</span>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6">
                    <h3 className="text-lg font-bold mb-4 flex items-center">
                      <Target className="h-5 w-5 mr-2 text-blue-600" />
                      Personalized Recommendations
                    </h3>
                    <div className="space-y-2">
                      {Object.entries(insights.recommendations).map(([key, value]) => (
                        <div key={key} className="flex items-start space-x-2">
                          <Sparkles className="h-3 w-3 text-yellow-500 mt-1 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{value}</span>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              ) : (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    {insights.message}
                    {insights.required_interactions && (
                      <span> Need {insights.required_interactions} more interactions.</span>
                    )}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-lg font-bold text-gray-600">No Insights Available</h3>
              <p className="text-gray-500">Generate demo data to see learning insights</p>
            </Card>
          )}
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <PieChart className="h-5 w-5 mr-2 text-green-600" />
              Learning Pattern Analysis
            </h3>
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-4">📊</div>
              <p>Pattern analysis will be available as more interaction data is collected</p>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdaptiveClientLearningDashboard;
