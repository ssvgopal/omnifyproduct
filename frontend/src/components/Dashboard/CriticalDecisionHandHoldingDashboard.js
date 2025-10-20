import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Target,
  User,
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
  BookOpen,
  Settings,
  Activity,
  PieChart,
  LineChart,
  Sparkles,
  Clock,
  Shield,
  AlertCircle,
  UserCheck,
  UserX,
  UserPlus,
  UserMinus,
  Bell,
  BellRing,
  Phone,
  Mail,
  MessageCircle,
  FileText,
  Upload,
  Download,
  ExternalLink,
  Lock,
  Unlock,
  Key,
  Search,
  Filter,
  SortAsc,
  SortDesc,
  Brain,
  Users,
  Hand,
  Compass,
  MapPin,
  Navigation,
  Route,
  Flag,
  CheckSquare,
  Square,
  List,
  Grid,
  Layers,
  Workflow,
  GitBranch,
  GitCommit,
  GitMerge,
  GitPullRequest,
  GitCompare,
  GitBranchPlus,
  GitCommitHorizontal,
  GitMergeHorizontal,
  GitPullRequestHorizontal,
  GitCompareHorizontal,
  GitBranchMinus,
  GitCommitVertical,
  GitMergeVertical,
  GitPullRequestVertical,
  GitCompareVertical
} from 'lucide-react';
import api from '@/services/api';

const CriticalDecisionHandHoldingDashboard = () => {
  const [activeDecisions, setActiveDecisions] = useState([]);
  const [decisionTypes, setDecisionTypes] = useState([]);
  const [impactLevels, setImpactLevels] = useState([]);
  const [guidanceLevels, setGuidanceLevels] = useState([]);
  const [decisionStages, setDecisionStages] = useState([]);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('decisions');
  const [clientId, setClientId] = useState('client_123');

  useEffect(() => {
    loadInitialData();
  }, [clientId]);

  const loadInitialData = async () => {
    try {
      const [decisionsRes, typesRes, impactRes, guidanceRes, stagesRes] = await Promise.all([
        api.get(`/api/critical-decision/active-decisions/${clientId}`),
        api.get('/api/critical-decision/decision-types'),
        api.get('/api/critical-decision/impact-levels'),
        api.get('/api/critical-decision/guidance-levels'),
        api.get('/api/critical-decision/decision-stages')
      ]);

      if (decisionsRes.data.success) {
        setActiveDecisions(decisionsRes.data.active_decisions);
      }
      if (typesRes.data.success) {
        setDecisionTypes(typesRes.data.decision_types);
      }
      if (impactRes.data.success) {
        setImpactLevels(impactRes.data.impact_levels);
      }
      if (guidanceRes.data.success) {
        setGuidanceLevels(guidanceRes.data.guidance_levels);
      }
      if (stagesRes.data.success) {
        setDecisionStages(decisionsRes.data.decision_stages);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const generateDemoDecision = async () => {
    try {
      setLoading(true);
      
      const response = await api.post(`/api/critical-decision/demo-decision/${clientId}`);
      
      if (response.data.success) {
        await loadInitialData();
      }
    } catch (error) {
      console.error('Error generating demo decision:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDecisionGuidance = async (decisionId) => {
    try {
      const response = await api.get(`/api/critical-decision/guidance/${decisionId}`);
      
      if (response.data.success) {
        setSelectedDecision(response.data.guidance);
      }
    } catch (error) {
      console.error('Error loading decision guidance:', error);
    }
  };

  const completeStep = async (decisionId, stepId) => {
    try {
      const response = await api.post('/api/critical-decision/complete-step', {
        decision_id: decisionId,
        step_id: stepId
      });
      
      if (response.data.success) {
        await loadDecisionGuidance(decisionId);
        await loadInitialData();
      }
    } catch (error) {
      console.error('Error completing step:', error);
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'transformational': return 'text-purple-600 bg-purple-100';
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getGuidanceColor = (guidance) => {
    switch (guidance) {
      case 'hand_holding': return 'text-purple-600 bg-purple-100';
      case 'expert_led': return 'text-blue-600 bg-blue-100';
      case 'interactive': return 'text-green-600 bg-green-100';
      case 'detailed': return 'text-yellow-600 bg-yellow-100';
      case 'basic': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStageColor = (stage) => {
    switch (stage) {
      case 'analysis': return 'text-blue-600 bg-blue-100';
      case 'options': return 'text-green-600 bg-green-100';
      case 'evaluation': return 'text-yellow-600 bg-yellow-100';
      case 'decision': return 'text-orange-600 bg-orange-100';
      case 'implementation': return 'text-purple-600 bg-purple-100';
      case 'monitoring': return 'text-indigo-600 bg-indigo-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStageIcon = (stage) => {
    switch (stage) {
      case 'analysis': return <BarChart3 className="h-4 w-4" />;
      case 'options': return <Lightbulb className="h-4 w-4" />;
      case 'evaluation': return <Target className="h-4 w-4" />;
      case 'decision': return <CheckCircle className="h-4 w-4" />;
      case 'implementation': return <Play className="h-4 w-4" />;
      case 'monitoring': return <Activity className="h-4 w-4" />;
      default: return <Circle className="h-4 w-4" />;
    }
  };

  const formatPercentage = (value) => `${value.toFixed(1)}%`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🤝 Critical Decision Hand-Holding</h1>
          <p className="text-gray-600 mt-2">Expert guidance for your most important decisions</p>
        </div>
        <div className="flex space-x-3">
          <Button 
            onClick={generateDemoDecision}
            disabled={loading}
            className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700 text-white"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Hand className="h-4 w-4 mr-2" />
            )}
            Generate Demo Decision
          </Button>
          <Button 
            onClick={loadInitialData}
            variant="outline"
            disabled={loading}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">{activeDecisions.length}</div>
              <div className="text-sm text-gray-600">Active Decisions</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeDecisions.filter(d => d.current_stage === 'analysis').length}
              </div>
              <div className="text-sm text-gray-600">In Analysis</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <Lightbulb className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeDecisions.filter(d => d.current_stage === 'options').length}
              </div>
              <div className="text-sm text-gray-600">Exploring Options</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeDecisions.filter(d => d.current_stage === 'decision').length}
              </div>
              <div className="text-sm text-gray-600">Ready to Decide</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="decisions">Decisions</TabsTrigger>
          <TabsTrigger value="guidance">Guidance</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
        </TabsList>

        {/* Decisions Tab */}
        <TabsContent value="decisions" className="space-y-4">
          {activeDecisions.length > 0 ? (
            <div className="space-y-4">
              {activeDecisions.map((decision, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">🎯</div>
                      <div>
                        <h3 className="text-lg font-bold">{decision.title}</h3>
                        <p className="text-sm text-gray-600">{decision.decision_type.replace('_', ' ').toUpperCase()}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getImpactColor(decision.impact_level)}>
                        {decision.impact_level}
                      </Badge>
                      <Badge className={getGuidanceColor(decision.guidance_level)}>
                        {decision.guidance_level.replace('_', ' ')}
                      </Badge>
                      <Badge className={getStageColor(decision.current_stage)}>
                        {getStageIcon(decision.current_stage)}
                        <span className="ml-1">{decision.current_stage}</span>
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span>Progress</span>
                      <span>{formatPercentage(decision.progress.percentage)}</span>
                    </div>
                    <Progress value={decision.progress.percentage} />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{decision.progress.completed} of {decision.progress.total} steps completed</span>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Risk Level</div>
                      <div className="font-bold capitalize">{decision.risk_level}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Created</div>
                      <div className="font-bold">
                        {new Date(decision.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Budget Impact</div>
                      <div className="font-bold">
                        {decision.budget_impact ? `$${decision.budget_impact.toLocaleString()}` : 'N/A'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Timeline: {decision.timeline ? new Date(decision.timeline).toLocaleDateString() : 'No deadline'}
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => loadDecisionGuidance(decision.decision_id)}
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View Guidance
                      </Button>
                      <Button size="sm" variant="outline">
                        <MessageCircle className="h-3 w-3 mr-1" />
                        Get Help
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-lg font-bold text-gray-600">No Active Decisions</h3>
              <p className="text-gray-500">Generate a demo decision to see the hand-holding system in action</p>
            </Card>
          )}
        </TabsContent>

        {/* Guidance Tab */}
        <TabsContent value="guidance" className="space-y-4">
          {selectedDecision ? (
            <div className="space-y-6">
              {/* Decision Overview */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Target className="h-5 w-5 mr-2 text-blue-600" />
                  Decision Overview
                </h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-bold mb-2">{selectedDecision.decision.title}</h4>
                    <p className="text-gray-600 mb-4">{selectedDecision.decision.description}</p>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Type:</span>
                        <span className="text-sm font-bold">{selectedDecision.decision.decision_type.replace('_', ' ').toUpperCase()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Impact:</span>
                        <Badge className={getImpactColor(selectedDecision.decision.impact_level)} size="sm">
                          {selectedDecision.decision.impact_level}
                        </Badge>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Guidance Level:</span>
                        <Badge className={getGuidanceColor(selectedDecision.decision.guidance_level)} size="sm">
                          {selectedDecision.decision.guidance_level.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-bold mb-2">Progress</h4>
                    <div className="mb-4">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Overall Progress</span>
                        <span>{formatPercentage(selectedDecision.progress.percentage)}</span>
                      </div>
                      <Progress value={selectedDecision.progress.percentage} />
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Current Stage:</span>
                        <Badge className={getStageColor(selectedDecision.decision.current_stage)} size="sm">
                          {getStageIcon(selectedDecision.decision.current_stage)}
                          <span className="ml-1">{selectedDecision.decision.current_stage}</span>
                        </Badge>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Steps Completed:</span>
                        <span>{selectedDecision.progress.completed}/{selectedDecision.progress.total}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Guidance Steps */}
              <Card className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Compass className="h-5 w-5 mr-2 text-green-600" />
                  Guidance Steps
                </h3>
                <div className="space-y-4">
                  {selectedDecision.steps.map((step, index) => (
                    <div key={index} className={`border rounded-lg p-4 ${
                      step.is_completed ? 'bg-green-50 border-green-200' : 
                      step.stage === selectedDecision.decision.current_stage ? 'bg-blue-50 border-blue-200' : 
                      'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            step.is_completed ? 'bg-green-500 text-white' :
                            step.stage === selectedDecision.decision.current_stage ? 'bg-blue-500 text-white' :
                            'bg-gray-300 text-gray-600'
                          }`}>
                            {step.is_completed ? (
                              <CheckCircle className="h-4 w-4" />
                            ) : (
                              <span className="text-sm font-bold">{index + 1}</span>
                            )}
                          </div>
                          <div>
                            <h4 className="font-bold">{step.title}</h4>
                            <p className="text-sm text-gray-600">{step.description}</p>
                          </div>
                        </div>
                        <Badge className={getStageColor(step.stage)} size="sm">
                          {step.stage}
                        </Badge>
                      </div>
                      
                      {step.instructions.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-semibold text-sm mb-2">Instructions:</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {step.instructions.map((instruction, idx) => (
                              <li key={idx}>{instruction}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {step.questions.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-semibold text-sm mb-2">Questions to Consider:</h5>
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {step.questions.map((question, idx) => (
                              <li key={idx}>{question}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {step.checklist.length > 0 && (
                        <div className="mb-3">
                          <h5 className="font-semibold text-sm mb-2">Checklist:</h5>
                          <div className="space-y-1">
                            {step.checklist.map((item, idx) => (
                              <div key={idx} className="flex items-center space-x-2 text-sm">
                                <Square className="h-3 w-3" />
                                <span>{item}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {!step.is_completed && step.stage === selectedDecision.decision.current_stage && (
                        <div className="flex justify-end">
                          <Button 
                            size="sm"
                            onClick={() => completeStep(selectedDecision.decision.decision_id, step.step_id)}
                          >
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Complete Step
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>

              {/* Next Steps */}
              {selectedDecision.next_steps.length > 0 && (
                <Card className="p-6">
                  <h3 className="text-lg font-bold mb-4 flex items-center">
                    <ArrowRight className="h-5 w-5 mr-2 text-orange-600" />
                    Next Steps
                  </h3>
                  <div className="space-y-2">
                    {selectedDecision.next_steps.map((step, index) => (
                      <div key={index} className="flex items-start space-x-2">
                        <ArrowRight className="h-4 w-4 text-orange-500 mt-0.5 flex-shrink-0" />
                        <span className="text-sm text-gray-700">{step}</span>
                      </div>
                    ))}
                  </div>
                </Card>
              )}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🧭</div>
              <h3 className="text-lg font-bold text-gray-600">No Decision Selected</h3>
              <p className="text-gray-500">Select a decision from the Decisions tab to view guidance</p>
            </Card>
          )}
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          {selectedDecision && selectedDecision.recommendations.length > 0 ? (
            <div className="space-y-4">
              {selectedDecision.recommendations.map((recommendation, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">💡</div>
                      <div>
                        <h3 className="text-lg font-bold">{recommendation.option_name}</h3>
                        <p className="text-sm text-gray-600">{recommendation.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">
                        {formatPercentage(recommendation.success_probability * 100)} success
                      </Badge>
                      <Badge variant="outline">
                        {formatPercentage(recommendation.confidence_score * 100)} confidence
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <h4 className="font-bold text-sm mb-2">Pros</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {recommendation.pros.map((pro, idx) => (
                          <li key={idx} className="text-green-700">{pro}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-bold text-sm mb-2">Cons</h4>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {recommendation.cons.map((con, idx) => (
                          <li key={idx} className="text-red-700">{con}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-bold text-sm mb-2">Expected Outcome</h4>
                    <p className="text-sm text-gray-700">{recommendation.expected_outcome}</p>
                  </div>
                  
                  <div className="mb-4">
                    <h4 className="font-bold text-sm mb-2">Implementation Steps</h4>
                    <ol className="list-decimal list-inside space-y-1 text-sm">
                      {recommendation.implementation_steps.map((step, idx) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Timeline: {recommendation.timeline_estimate}
                    </div>
                    <div className="text-sm text-gray-600">
                      Cost: {recommendation.cost_estimate ? `$${recommendation.cost_estimate.toLocaleString()}` : 'N/A'}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">💡</div>
              <h3 className="text-lg font-bold text-gray-600">No Recommendations</h3>
              <p className="text-gray-500">Select a decision to view recommendations</p>
            </Card>
          )}
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-blue-600" />
                Decision Types
              </h3>
              <div className="space-y-2">
                {decisionTypes.map((type, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{type.label}</span>
                    <span className="text-xs text-gray-500">{type.description}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Layers className="h-5 w-5 mr-2 text-green-600" />
                Decision Stages
              </h3>
              <div className="space-y-2">
                {decisionStages.map((stage, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{stage.label}</span>
                    <span className="text-xs text-gray-500">{stage.description}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Target className="h-5 w-5 mr-2 text-orange-600" />
                Impact Levels
              </h3>
              <div className="space-y-2">
                {impactLevels.map((impact, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{impact.label}</span>
                    <span className="text-xs text-gray-500">{impact.description}</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Hand className="h-5 w-5 mr-2 text-purple-600" />
                Guidance Levels
              </h3>
              <div className="space-y-2">
                {guidanceLevels.map((guidance, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <span className="text-sm font-medium">{guidance.label}</span>
                    <span className="text-xs text-gray-500">{guidance.description}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CriticalDecisionHandHoldingDashboard;
