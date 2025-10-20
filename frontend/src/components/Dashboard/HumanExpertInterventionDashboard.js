import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Users,
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
  SortDesc
} from 'lucide-react';
import api from '@/services/api';

const HumanExpertInterventionDashboard = () => {
  const [activeInterventions, setActiveInterventions] = useState([]);
  const [interventionTypes, setInterventionTypes] = useState([]);
  const [expertLevels, setExpertLevels] = useState([]);
  const [complexityLevels, setComplexityLevels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('interventions');
  const [selectedIntervention, setSelectedIntervention] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [interventionsRes, typesRes, levelsRes, complexityRes] = await Promise.all([
        api.get('/api/expert-intervention/active-interventions'),
        api.get('/api/expert-intervention/intervention-types'),
        api.get('/api/expert-intervention/expert-levels'),
        api.get('/api/expert-intervention/complexity-levels')
      ]);

      if (interventionsRes.data.success) {
        setActiveInterventions(interventionsRes.data.active_interventions);
      }
      if (typesRes.data.success) {
        setInterventionTypes(typesRes.data.intervention_types);
      }
      if (levelsRes.data.success) {
        setExpertLevels(levelsRes.data.expert_levels);
      }
      if (complexityRes.data.success) {
        setComplexityLevels(complexityRes.data.complexity_levels);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const generateDemoIntervention = async () => {
    try {
      setLoading(true);
      
      const response = await api.post('/api/expert-intervention/demo-intervention/client_123');
      
      if (response.data.success) {
        await loadInitialData();
      }
    } catch (error) {
      console.error('Error generating demo intervention:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      case 'in_progress': return 'text-blue-600 bg-blue-100';
      case 'approved': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      case 'escalated': return 'text-orange-600 bg-orange-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'expired': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'in_progress': return <Activity className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      case 'escalated': return <ArrowUpRight className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'expired': return <AlertCircle className="h-4 w-4" />;
      default: return <AlertCircle className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 8) return 'text-red-600 bg-red-100';
    if (priority >= 6) return 'text-orange-600 bg-orange-100';
    if (priority >= 4) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'emergency': return 'text-red-600 bg-red-100';
      case 'critical': return 'text-orange-600 bg-orange-100';
      case 'high': return 'text-yellow-600 bg-yellow-100';
      case 'medium': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimeRemaining = (deadline) => {
    if (!deadline) return 'No deadline';
    
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffMs = deadlineDate - now;
    
    if (diffMs <= 0) return 'Expired';
    
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes}m`;
    } else {
      return `${diffMinutes}m`;
    }
  };

  const getUrgencyLevel = (deadline, priority) => {
    if (!deadline) return 'normal';
    
    const now = new Date();
    const deadlineDate = new Date(deadline);
    const diffMs = deadlineDate - now;
    const diffHours = diffMs / (1000 * 60 * 60);
    
    if (diffHours < 1 || priority >= 9) return 'critical';
    if (diffHours < 4 || priority >= 7) return 'high';
    if (diffHours < 12 || priority >= 5) return 'medium';
    return 'low';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">👥 Human Expert Intervention</h1>
          <p className="text-gray-600 mt-2">AI-Human collaboration for critical decisions</p>
        </div>
        <div className="flex space-x-3">
          <Button 
            onClick={generateDemoIntervention}
            disabled={loading}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
          >
            {loading ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Users className="h-4 w-4 mr-2" />
            )}
            Generate Demo Intervention
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
            <Users className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">{activeInterventions.length}</div>
              <div className="text-sm text-gray-600">Active Interventions</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeInterventions.filter(i => i.status === 'pending').length}
              </div>
              <div className="text-sm text-gray-600">Pending</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeInterventions.filter(i => i.status === 'in_progress').length}
              </div>
              <div className="text-sm text-gray-600">In Progress</div>
            </div>
          </div>
        </Card>
        
        <Card className="p-6">
          <div className="flex items-center">
            <ArrowUpRight className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <div className="text-2xl font-bold">
                {activeInterventions.filter(i => i.status === 'escalated').length}
              </div>
              <div className="text-sm text-gray-600">Escalated</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="interventions">Interventions</TabsTrigger>
          <TabsTrigger value="experts">Experts</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Interventions Tab */}
        <TabsContent value="interventions" className="space-y-4">
          {activeInterventions.length > 0 ? (
            <div className="space-y-4">
              {activeInterventions.map((intervention, index) => (
                <Card key={index} className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">🎯</div>
                      <div>
                        <h3 className="text-lg font-bold">{intervention.title}</h3>
                        <p className="text-sm text-gray-600">Client: {intervention.client_id}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge className={getStatusColor(intervention.status)}>
                        {getStatusIcon(intervention.status)}
                        <span className="ml-1 capitalize">{intervention.status.replace('_', ' ')}</span>
                      </Badge>
                      <Badge className={getPriorityColor(intervention.priority)}>
                        Priority {intervention.priority}
                      </Badge>
                      <Badge className={getComplexityColor(intervention.complexity)}>
                        {intervention.complexity}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Assigned Expert</div>
                      <div className="font-bold">
                        {intervention.assigned_expert || 'Unassigned'}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Created</div>
                      <div className="font-bold">
                        {new Date(intervention.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600">Deadline</div>
                      <div className={`font-bold ${
                        getUrgencyLevel(intervention.deadline, intervention.priority) === 'critical' 
                          ? 'text-red-600' 
                          : getUrgencyLevel(intervention.deadline, intervention.priority) === 'high'
                          ? 'text-orange-600'
                          : 'text-gray-900'
                      }`}>
                        {formatTimeRemaining(intervention.deadline)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      Escalations: {intervention.escalation_count || 0}
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-3 w-3 mr-1" />
                        View Details
                      </Button>
                      <Button size="sm" variant="outline">
                        <MessageCircle className="h-3 w-3 mr-1" />
                        Comment
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">👥</div>
              <h3 className="text-lg font-bold text-gray-600">No Active Interventions</h3>
              <p className="text-gray-500">Generate a demo intervention to see the system in action</p>
            </Card>
          )}
        </TabsContent>

        {/* Experts Tab */}
        <TabsContent value="experts" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <Users className="h-5 w-5 mr-2 text-blue-600" />
              Expert Team
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {/* Demo Expert Profiles */}
              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <div className="font-bold">Dr. Sarah Chen</div>
                    <div className="text-sm text-gray-600">Senior Expert</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Current Load</span>
                    <span>3/8</span>
                  </div>
                  <Progress value={37.5} />
                  <div className="flex justify-between text-sm">
                    <span>Success Rate</span>
                    <span>94%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Response</span>
                    <span>45m</span>
                  </div>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <div className="font-bold">Mike Rodriguez</div>
                    <div className="text-sm text-gray-600">Lead Expert</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Current Load</span>
                    <span>5/10</span>
                  </div>
                  <Progress value={50} />
                  <div className="flex justify-between text-sm">
                    <span>Success Rate</span>
                    <span>89%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Response</span>
                    <span>32m</span>
                  </div>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-bold">Alex Thompson</div>
                    <div className="text-sm text-gray-600">Principal Expert</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Current Load</span>
                    <span>2/6</span>
                  </div>
                  <Progress value={33.3} />
                  <div className="flex justify-between text-sm">
                    <span>Success Rate</span>
                    <span>97%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Response</span>
                    <span>28m</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-bold mb-4 flex items-center">
              <Settings className="h-5 w-5 mr-2 text-green-600" />
              Intervention Workflows
            </h3>
            <div className="space-y-4">
              <div className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold">Approval Required Workflow</h4>
                  <Badge variant="outline">Active</Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Standard workflow for decisions requiring human approval
                </p>
                <div className="flex items-center space-x-4 text-sm">
                  <span>SLA: 4 hours</span>
                  <span>Escalation: 1 hour</span>
                  <span>Max Retries: 3</span>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold">Emergency Intervention</h4>
                  <Badge variant="outline">Active</Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  High-priority workflow for emergency situations
                </p>
                <div className="flex items-center space-x-4 text-sm">
                  <span>SLA: 30 minutes</span>
                  <span>Escalation: 15 minutes</span>
                  <span>Max Retries: 2</span>
                </div>
              </div>

              <div className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold">Expert Consultation</h4>
                  <Badge variant="outline">Active</Badge>
                </div>
                <p className="text-sm text-gray-600 mb-3">
                  Workflow for complex decisions requiring expert consultation
                </p>
                <div className="flex items-center space-x-4 text-sm">
                  <span>SLA: 2 hours</span>
                  <span>Escalation: 45 minutes</span>
                  <span>Max Retries: 3</span>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                Intervention Types
              </h3>
              <div className="space-y-3">
                {interventionTypes.map((type, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm">{type.label}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-20 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${Math.random() * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600">
                        {Math.floor(Math.random() * 20) + 1}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <PieChart className="h-5 w-5 mr-2 text-green-600" />
                Expert Performance
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Average Response Time</span>
                  <span className="font-bold">38 minutes</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Success Rate</span>
                  <span className="font-bold">93%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Escalation Rate</span>
                  <span className="font-bold">12%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">SLA Compliance</span>
                  <span className="font-bold">96%</span>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HumanExpertInterventionDashboard;
