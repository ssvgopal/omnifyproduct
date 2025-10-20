import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
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
  Percent,
  Shield,
  Settings,
  Play,
  Pause,
  RotateCcw,
  UserCheck,
  UserX,
  AlertCircle,
  BarChart3,
  PieChart,
  LineChart
} from 'lucide-react';
import api from '@/services/api';

const ProactiveIntelligenceDashboard = () => {
  const [clientProfile, setClientProfile] = useState(null);
  const [activeActions, setActiveActions] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [expertRequired, setExpertRequired] = useState([]);
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedClient, setSelectedClient] = useState('client_123');

  useEffect(() => {
    loadProactiveIntelligenceData();
  }, [selectedClient]);

  const loadProactiveIntelligenceData = async () => {
    try {
      setLoading(true);
      
      // Load client profile and insights
      const [profileResponse, insightsResponse, actionsResponse, approvalsResponse, expertResponse, recommendationsResponse] = await Promise.all([
        api.get(`/api/proactive-intelligence/client/${selectedClient}/analyze-preferences`),
        api.get(`/api/proactive-intelligence/client/${selectedClient}/insights`),
        api.get(`/api/proactive-intelligence/client/${selectedClient}/actions`),
        api.get('/api/proactive-intelligence/actions/pending-approval'),
        api.get('/api/proactive-intelligence/actions/expert-required'),
        api.get(`/api/proactive-intelligence/client/${selectedClient}/recommendations`)
      ]);

      setClientProfile(profileResponse.data.profile);
      setInsights(insightsResponse.data.insights);
      setActiveActions(actionsResponse.data.actions);
      setPendingApprovals(approvalsResponse.data.pending_actions);
      setExpertRequired(expertResponse.data.expert_required_actions);
      setRecommendations(recommendationsResponse.data.recommendations);
      
    } catch (error) {
      console.error('Error loading proactive intelligence data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateNewActions = async () => {
    try {
      const response = await api.post(`/api/proactive-intelligence/client/${selectedClient}/generate-actions`);
      setActiveActions(response.data.actions);
      
      // Show success message
      console.log('New actions generated successfully');
    } catch (error) {
      console.error('Error generating actions:', error);
    }
  };

  const executeAction = async (actionId, expertDecision = null) => {
    try {
      const response = await api.post(`/api/proactive-intelligence/action/${actionId}/execute`, {
        action_id: actionId,
        execute_immediately: true,
        expert_override: expertDecision
      });
      
      // Refresh data after execution
      loadProactiveIntelligenceData();
      
      console.log('Action executed successfully');
    } catch (error) {
      console.error('Error executing action:', error);
    }
  };

  const submitExpertDecision = async (actionId, decision) => {
    try {
      const response = await api.post(`/api/proactive-intelligence/action/${actionId}/expert-decision`, {
        action_id: actionId,
        expert_id: 'expert_001',
        decision: decision.decision,
        reasoning: decision.reasoning,
        modifications: decision.modifications
      });
      
      // Refresh data after decision
      loadProactiveIntelligenceData();
      
      console.log('Expert decision submitted successfully');
    } catch (error) {
      console.error('Error submitting expert decision:', error);
    }
  };

  const getPreferenceLevelColor = (level) => {
    switch (level) {
      case 'fully_autonomous': return 'text-green-600 bg-green-100';
      case 'guided_automation': return 'text-blue-600 bg-blue-100';
      case 'human_led': return 'text-yellow-600 bg-yellow-100';
      case 'expert_required': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getPreferenceLevelIcon = (level) => {
    switch (level) {
      case 'fully_autonomous': return <Zap className="h-4 w-4" />;
      case 'guided_automation': return <Target className="h-4 w-4" />;
      case 'human_led': return <Users className="h-4 w-4" />;
      case 'expert_required': return <UserCheck className="h-4 w-4" />;
      default: return <Settings className="h-4 w-4" />;
    }
  };

  const getActionTypeIcon = (type) => {
    switch (type) {
      case 'creative_fatigue_prediction': return <Eye className="h-4 w-4" />;
      case 'ltv_forecasting': return <TrendingUp className="h-4 w-4" />;
      case 'churn_prevention': return <UserX className="h-4 w-4" />;
      case 'budget_optimization': return <DollarSign className="h-4 w-4" />;
      case 'bid_optimization': return <Target className="h-4 w-4" />;
      case 'audience_expansion': return <Users className="h-4 w-4" />;
      case 'campaign_scaling': return <ArrowUpRight className="h-4 w-4" />;
      case 'performance_anomaly_detection': return <AlertCircle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 8) return 'text-red-600 bg-red-100';
    if (priority >= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getRiskColor = (risk) => {
    if (risk >= 0.7) return 'text-red-600 bg-red-100';
    if (risk >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <div className="text-gray-500">Loading proactive intelligence...</div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🧠 Proactive Intelligence</h1>
          <p className="text-gray-600 mt-2">Hybrid AI with human expert oversight</p>
        </div>
        <div className="flex space-x-3">
          <Button onClick={generateNewActions} className="bg-blue-600 hover:bg-blue-700">
            <Brain className="h-4 w-4 mr-2" />
            Generate Actions
          </Button>
          <Button variant="outline" onClick={loadProactiveIntelligenceData}>
            <RotateCcw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Client Profile Overview */}
      {clientProfile && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Client Profile: {selectedClient}</h2>
            <Badge className={getPreferenceLevelColor(clientProfile.preference_level)}>
              {getPreferenceLevelIcon(clientProfile.preference_level)}
              <span className="ml-2 capitalize">{clientProfile.preference_level.replace('_', ' ')}</span>
            </Badge>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{Math.round(clientProfile.risk_tolerance * 100)}%</div>
              <div className="text-sm text-gray-600">Risk Tolerance</div>
              <Progress value={clientProfile.risk_tolerance * 100} className="mt-2" />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{Math.round(clientProfile.learning_rate * 100)}%</div>
              <div className="text-sm text-gray-600">Learning Rate</div>
              <Progress value={clientProfile.learning_rate * 100} className="mt-2" />
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {new Date(clientProfile.last_updated).toLocaleDateString()}
              </div>
              <div className="text-sm text-gray-600">Last Updated</div>
            </div>
          </div>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="actions">Active Actions</TabsTrigger>
          <TabsTrigger value="approvals">Pending Approvals</TabsTrigger>
          <TabsTrigger value="expert">Expert Required</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          {insights && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="flex items-center">
                  <Activity className="h-8 w-8 text-blue-600" />
                  <div className="ml-3">
                    <div className="text-2xl font-bold">{insights.active_actions}</div>
                    <div className="text-sm text-gray-600">Active Actions</div>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center">
                  <Clock className="h-8 w-8 text-yellow-600" />
                  <div className="ml-3">
                    <div className="text-2xl font-bold">{insights.pending_approvals}</div>
                    <div className="text-sm text-gray-600">Pending Approvals</div>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center">
                  <UserCheck className="h-8 w-8 text-red-600" />
                  <div className="ml-3">
                    <div className="text-2xl font-bold">{insights.expert_required}</div>
                    <div className="text-sm text-gray-600">Expert Required</div>
                  </div>
                </div>
              </Card>
              
              <Card className="p-4">
                <div className="flex items-center">
                  <BarChart3 className="h-8 w-8 text-green-600" />
                  <div className="ml-3">
                    <div className="text-2xl font-bold">{insights.recent_interventions}</div>
                    <div className="text-sm text-gray-600">Recent Interventions</div>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Recommendations */}
          {recommendations.length > 0 && (
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4">💡 Personalized Recommendations</h3>
              <div className="space-y-3">
                {recommendations.map((recommendation, index) => (
                  <Alert key={index}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{recommendation}</AlertDescription>
                  </Alert>
                ))}
              </div>
            </Card>
          )}
        </TabsContent>

        {/* Active Actions Tab */}
        <TabsContent value="actions" className="space-y-4">
          {activeActions.length > 0 ? (
            activeActions.map((action) => (
              <Card key={action.action_id} className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {getActionTypeIcon(action.action_type)}
                    <div>
                      <h3 className="font-bold capitalize">{action.action_type.replace('_', ' ')}</h3>
                      <p className="text-sm text-gray-600">Campaign: {action.campaign_id || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Badge className={getPriorityColor(action.priority)}>
                      Priority {action.priority}
                    </Badge>
                    <Badge className={getRiskColor(action.risk_level)}>
                      Risk {Math.round(action.risk_level * 100)}%
                    </Badge>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-sm text-gray-600">Confidence</div>
                    <div className="text-lg font-bold">{Math.round(action.confidence * 100)}%</div>
                    <Progress value={action.confidence * 100} className="mt-1" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Expected Impact</div>
                    <div className="text-lg font-bold text-green-600">+{action.expected_impact}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Created</div>
                    <div className="text-sm">{new Date(action.created_at).toLocaleString()}</div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm text-gray-600 mb-2">Reasoning</div>
                  <p className="text-sm bg-gray-50 p-3 rounded">{action.reasoning}</p>
                </div>
                
                <div className="flex space-x-2">
                  {!action.requires_human_approval && (
                    <Button 
                      onClick={() => executeAction(action.action_id)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <Play className="h-4 w-4 mr-2" />
                      Execute
                    </Button>
                  )}
                  {action.requires_human_approval && (
                    <Button 
                      onClick={() => executeAction(action.action_id, { decision: 'approved', reasoning: 'Approved by user' })}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve & Execute
                    </Button>
                  )}
                  <Button variant="outline">
                    <Pause className="h-4 w-4 mr-2" />
                    Hold
                  </Button>
                </div>
              </Card>
            ))
          ) : (
            <Card className="p-6 text-center">
              <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-gray-600">No Active Actions</h3>
              <p className="text-gray-500">Generate new actions to see proactive recommendations</p>
            </Card>
          )}
        </TabsContent>

        {/* Pending Approvals Tab */}
        <TabsContent value="approvals" className="space-y-4">
          {pendingApprovals.length > 0 ? (
            pendingApprovals.map((action) => (
              <Card key={action.action_id} className="p-6 border-l-4 border-yellow-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    <div>
                      <h3 className="font-bold capitalize">{action.action_type.replace('_', ' ')}</h3>
                      <p className="text-sm text-gray-600">Client: {action.client_id}</p>
                    </div>
                  </div>
                  <Badge className="bg-yellow-100 text-yellow-800">Pending Approval</Badge>
                </div>
                
                <div className="mb-4">
                  <p className="text-sm bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
                    {action.reasoning}
                  </p>
                </div>
                
                <div className="flex space-x-2">
                  <Button 
                    onClick={() => executeAction(action.action_id, { decision: 'approved', reasoning: 'Approved by user' })}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Approve
                  </Button>
                  <Button 
                    onClick={() => executeAction(action.action_id, { decision: 'rejected', reasoning: 'Rejected by user' })}
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                  >
                    <UserX className="h-4 w-4 mr-2" />
                    Reject
                  </Button>
                </div>
              </Card>
            ))
          ) : (
            <Card className="p-6 text-center">
              <CheckCircle className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-gray-600">No Pending Approvals</h3>
              <p className="text-gray-500">All actions are either executed or don't require approval</p>
            </Card>
          )}
        </TabsContent>

        {/* Expert Required Tab */}
        <TabsContent value="expert" className="space-y-4">
          {expertRequired.length > 0 ? (
            expertRequired.map((action) => (
              <Card key={action.action_id} className="p-6 border-l-4 border-red-500">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <UserCheck className="h-5 w-5 text-red-600" />
                    <div>
                      <h3 className="font-bold capitalize">{action.action_type.replace('_', ' ')}</h3>
                      <p className="text-sm text-gray-600">Client: {action.client_id}</p>
                    </div>
                  </div>
                  <Badge className="bg-red-100 text-red-800">Expert Required</Badge>
                </div>
                
                <div className="mb-4">
                  <p className="text-sm bg-red-50 p-3 rounded border-l-4 border-red-400">
                    {action.reasoning}
                  </p>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm text-gray-600 mb-2">Data Evidence</div>
                  <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                    {JSON.stringify(action.data_evidence, null, 2)}
                  </pre>
                </div>
                
                <div className="flex space-x-2">
                  <Button 
                    onClick={() => submitExpertDecision(action.action_id, { 
                      decision: 'approved', 
                      reasoning: 'Expert approved based on analysis' 
                    })}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <UserCheck className="h-4 w-4 mr-2" />
                    Expert Approve
                  </Button>
                  <Button 
                    onClick={() => submitExpertDecision(action.action_id, { 
                      decision: 'modified', 
                      reasoning: 'Expert modified parameters',
                      modifications: { risk_level: 0.5 }
                    })}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Expert Modify
                  </Button>
                  <Button 
                    onClick={() => submitExpertDecision(action.action_id, { 
                      decision: 'rejected', 
                      reasoning: 'Expert rejected due to high risk' 
                    })}
                    variant="outline"
                    className="border-red-300 text-red-600 hover:bg-red-50"
                  >
                    <UserX className="h-4 w-4 mr-2" />
                    Expert Reject
                  </Button>
                </div>
              </Card>
            ))
          ) : (
            <Card className="p-6 text-center">
              <UserCheck className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-lg font-bold text-gray-600">No Expert Required Actions</h3>
              <p className="text-gray-500">All actions can be handled automatically or with basic approval</p>
            </Card>
          )}
        </TabsContent>

        {/* Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          {insights && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Client Profile Insights</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Preference Level:</span>
                    <Badge className={getPreferenceLevelColor(insights.client_profile.preference_level)}>
                      {insights.client_profile.preference_level.replace('_', ' ')}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Tolerance:</span>
                    <span className="font-bold">{Math.round(insights.client_profile.risk_tolerance * 100)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Learning Rate:</span>
                    <span className="font-bold">{Math.round(insights.client_profile.learning_rate * 100)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Updated:</span>
                    <span className="text-sm">{new Date(insights.client_profile.last_updated).toLocaleString()}</span>
                  </div>
                </div>
              </Card>
              
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4">Action Summary</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Active Actions:</span>
                    <span className="font-bold text-blue-600">{insights.active_actions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Pending Approvals:</span>
                    <span className="font-bold text-yellow-600">{insights.pending_approvals}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Expert Required:</span>
                    <span className="font-bold text-red-600">{insights.expert_required}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recent Interventions:</span>
                    <span className="font-bold text-green-600">{insights.recent_interventions}</span>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProactiveIntelligenceDashboard;
