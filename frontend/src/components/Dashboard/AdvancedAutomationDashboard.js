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
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  Workflow, 
  Play, 
  Pause, 
  Square,
  Settings,
  Plus,
  Edit,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Upload,
  Zap,
  Target,
  Mail,
  BarChart3,
  Users,
  Calendar,
  Bell,
  Globe,
  Smartphone,
  Monitor,
  Database,
  Cpu,
  Memory,
  HardDrive,
  Wifi,
  Signal,
  Battery,
  Power,
  Activity,
  TrendingUp,
  TrendingDown,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Award,
  Trophy,
  Filter,
  Search,
  Copy,
  Share,
  Link,
  Unlink,
  Lock,
  Unlock,
  Key,
  Shield,
  AlertCircle,
  Info,
  HelpCircle,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  MoreHorizontal,
  MoreVertical,
  Menu,
  X,
  Check,
  PlusCircle,
  MinusCircle,
  Circle,
  Dot,
  Square as SquareIcon,
  Triangle,
  Hexagon,
  Octagon,
  Diamond,
  Heart,
  Smile,
  Frown,
  Meh,
  ThumbsUp,
  ThumbsDown,
  Bookmark,
  BookmarkCheck,
  BookmarkX,
  Flag,
  FlagTriangleLeft,
  FlagTriangleRight,
  Home,
  Building,
  Building2,
  Factory,
  Store,
  Warehouse,
  Office,
  School,
  Hospital,
  Bank,
  Church,
  Mosque,
  Synagogue,
  Temple,
  Castle,
  Tent,
  Car,
  Truck,
  Bus,
  Train,
  Plane,
  Ship,
  Bike,
  Scooter,
  Motorcycle,
  Rocket,
  Satellite,
  Telescope,
  Microscope,
  Camera,
  Video,
  Image,
  File,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  FilePdf,
  FileSpreadsheet,
  FilePresentation,
  FileCode,
  FileArchive,
  Folder,
  FolderOpen,
  FolderPlus,
  FolderMinus,
  FolderX,
  FolderCheck,
  FolderLock,
  FolderUnlock,
  FolderHeart,
  FolderStar,
  FolderBookmark,
  FolderFlag,
  FolderHome,
  FolderBuilding,
  FolderCar,
  FolderPlane,
  FolderShip,
  FolderRocket,
  FolderSatellite,
  FolderTelescope,
  FolderMicroscope,
  FolderCamera,
  FolderVideo,
  FolderImage,
  FolderFile,
  FolderFileText,
  FolderFileImage,
  FolderFileVideo,
  FolderFileAudio,
  FolderFilePdf,
  FolderFileSpreadsheet,
  FolderFilePresentation,
  FolderFileCode,
  FolderFileArchive
} from 'lucide-react';
import api from '@/services/api';

const AdvancedAutomationDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [triggers, setTriggers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showTemplateDialog, setShowTemplateDialog] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [executionDetails, setExecutionDetails] = useState(null);
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [workflowsData, executionsData, templatesData, triggersData] = await Promise.all([
        api.get('/api/automation/workflows'),
        api.get('/api/automation/workflows/demo-workflow-1/executions'),
        api.get('/api/automation/templates'),
        api.get('/api/automation/triggers')
      ]);
      
      setWorkflows(workflowsData.data || []);
      setExecutions(executionsData.data || []);
      setTemplates(templatesData.data || []);
      setTriggers(triggersData.data.triggers || []);
      
    } catch (err) {
      console.error("Failed to fetch automation data:", err);
      setError("Failed to load automation workflows. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'completed': return 'text-blue-600';
      case 'failed': return 'text-red-600';
      case 'paused': return 'text-yellow-600';
      case 'draft': return 'text-gray-600';
      case 'running': return 'text-blue-600';
      case 'pending': return 'text-gray-600';
      case 'skipped': return 'text-orange-600';
      case 'retrying': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'completed': return 'bg-blue-500';
      case 'failed': return 'bg-red-500';
      case 'paused': return 'bg-yellow-500';
      case 'draft': return 'bg-gray-500';
      case 'running': return 'bg-blue-500';
      case 'pending': return 'bg-gray-500';
      case 'skipped': return 'bg-orange-500';
      case 'retrying': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4 text-green-500" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'paused': return <Pause className="h-4 w-4 text-yellow-500" />;
      case 'draft': return <Edit className="h-4 w-4 text-gray-500" />;
      case 'running': return <Activity className="h-4 w-4 text-blue-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-gray-500" />;
      case 'skipped': return <Minus className="h-4 w-4 text-orange-500" />;
      case 'retrying': return <RefreshCw className="h-4 w-4 text-purple-500" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'send_email': return <Mail className="h-4 w-4 text-blue-500" />;
      case 'create_campaign': return <Target className="h-4 w-4 text-green-500" />;
      case 'update_budget': return <DollarSign className="h-4 w-4 text-purple-500" />;
      case 'pause_campaign': return <Pause className="h-4 w-4 text-orange-500" />;
      case 'resume_campaign': return <Play className="h-4 w-4 text-green-500" />;
      case 'send_notification': return <Bell className="h-4 w-4 text-yellow-500" />;
      case 'update_targeting': return <Target className="h-4 w-4 text-blue-500" />;
      case 'generate_report': return <BarChart3 className="h-4 w-4 text-indigo-500" />;
      case 'call_api': return <Globe className="h-4 w-4 text-gray-500" />;
      case 'wait': return <Clock className="h-4 w-4 text-gray-500" />;
      case 'condition': return <HelpCircle className="h-4 w-4 text-purple-500" />;
      case 'loop': return <RefreshCw className="h-4 w-4 text-orange-500" />;
      case 'parallel': return <MoreHorizontal className="h-4 w-4 text-green-500" />;
      default: return <Settings className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTriggerIcon = (triggerType) => {
    switch (triggerType) {
      case 'scheduled': return <Calendar className="h-4 w-4 text-blue-500" />;
      case 'event_based': return <Zap className="h-4 w-4 text-yellow-500" />;
      case 'manual': return <Play className="h-4 w-4 text-green-500" />;
      case 'api_call': return <Globe className="h-4 w-4 text-purple-500" />;
      case 'webhook': return <Link className="h-4 w-4 text-orange-500" />;
      case 'conditional': return <HelpCircle className="h-4 w-4 text-red-500" />;
      default: return <Settings className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleExecuteWorkflow = async (workflowId) => {
    try {
      await api.post('/api/automation/workflows/execute', {
        workflow_id: workflowId,
        trigger_data: {}
      });
      
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to execute workflow:", err);
    }
  };

  const handleToggleWorkflowStatus = async (workflowId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'paused' : 'active';
      await api.put(`/api/automation/workflows/${workflowId}/status`, newStatus);
      
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to toggle workflow status:", err);
    }
  };

  const handleCreateFromTemplate = async (templateId, workflowName) => {
    try {
      await api.post(`/api/automation/templates/${templateId}/create`, workflowName);
      
      await fetchData(); // Refresh data
      setShowTemplateDialog(false);
    } catch (err) {
      console.error("Failed to create workflow from template:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Advanced Automation Workflows...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-blue-800 flex items-center">
              <Workflow className="mr-2 h-6 w-6 text-blue-500" /> Advanced Automation Workflows
            </CardTitle>
            <CardDescription className="text-gray-700">
              Complex multi-step automation with conditional logic and event triggers
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showTemplateDialog} onOpenChange={setShowTemplateDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-blue-600 border-blue-300 hover:bg-blue-50">
                  <Download className="mr-2 h-4 w-4" /> Templates
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Workflow Templates</DialogTitle>
                  <DialogDescription>
                    Choose a template to create a new workflow
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  {templates.map((template) => (
                    <Card key={template.template_id} className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Workflow className="h-5 w-5 text-blue-500 mr-2" />
                          <span className="font-semibold">{template.name}</span>
                        </div>
                        <Badge variant="outline">{template.complexity}</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">{template.steps.length} steps</span>
                        <Button 
                          size="sm" 
                          onClick={() => handleCreateFromTemplate(template.template_id, `${template.name} - Copy`)}
                        >
                          <Plus className="h-3 w-3 mr-1" /> Create
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-blue-600 border-blue-300 hover:bg-blue-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-blue-600 hover:bg-blue-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Workflow
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Workflow</DialogTitle>
                  <DialogDescription>
                    Create a custom automation workflow
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="workflow-name">Workflow Name</Label>
                    <Input id="workflow-name" placeholder="Enter workflow name" />
                  </div>
                  <div>
                    <Label htmlFor="workflow-description">Description</Label>
                    <Textarea id="workflow-description" placeholder="Enter workflow description" />
                  </div>
                  <Button className="w-full">
                    <Workflow className="mr-2 h-4 w-4" /> Create Workflow
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Automation Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-blue-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-blue-500" /> Automation Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{workflows.length}</div>
              <div className="text-lg font-semibold text-gray-800">Total Workflows</div>
              <div className="text-sm text-gray-600">Automation processes</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {workflows.filter(w => w.status === 'active').length}
              </div>
              <div className="text-lg font-semibold text-gray-800">Active Workflows</div>
              <div className="text-sm text-gray-600">Currently running</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">{executions.length}</div>
              <div className="text-lg font-semibold text-gray-800">Total Executions</div>
              <div className="text-sm text-gray-600">Workflow runs</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">{triggers.length}</div>
              <div className="text-lg font-semibold text-gray-800">Active Triggers</div>
              <div className="text-sm text-gray-600">Event triggers</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Automation Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-blue-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="workflows" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Workflows</TabsTrigger>
          <TabsTrigger value="executions" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Executions</TabsTrigger>
          <TabsTrigger value="triggers" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Triggers</TabsTrigger>
          <TabsTrigger value="templates" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Templates</TabsTrigger>
          <TabsTrigger value="monitoring" className="data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all">Monitoring</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Executions */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-blue-800 flex items-center">
                  <Activity className="mr-2 h-5 w-5 text-green-500" /> Recent Executions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {executions.slice(0, 5).map((execution) => (
                      <div key={execution.execution_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getStatusIcon(execution.status)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">
                            Execution {execution.execution_id.slice(0, 8)}...
                          </div>
                          <div className="text-xs text-gray-600">
                            {formatDateTime(execution.started_at)}
                          </div>
                        </div>
                        <Badge className={`${getStatusBadge(execution.status)} text-white`}>
                          {execution.status.toUpperCase()}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Active Triggers */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-blue-800 flex items-center">
                  <Zap className="mr-2 h-5 w-5 text-yellow-500" /> Active Triggers
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {triggers.slice(0, 5).map((trigger) => (
                      <div key={trigger.trigger_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getTriggerIcon(trigger.trigger_type)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{trigger.name}</div>
                          <div className="text-xs text-gray-600">
                            {trigger.trigger_type.replace('_', ' ')}
                          </div>
                        </div>
                        <Badge variant="outline" className={trigger.enabled ? 'text-green-600 border-green-300' : 'text-red-600 border-red-300'}>
                          {trigger.enabled ? 'Active' : 'Inactive'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Workflows Tab */}
        <TabsContent value="workflows">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-blue-800">Workflow Management</CardTitle>
              <CardDescription>Create, manage, and monitor automation workflows</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {workflows.map((workflow) => (
                  <Card key={workflow.workflow_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Workflow className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{workflow.name}</div>
                          <div className="text-sm text-gray-600">{workflow.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getStatusBadge(workflow.status)} text-white`}>
                          {getStatusIcon(workflow.status)}
                          <span className="ml-1">{workflow.status.toUpperCase()}</span>
                        </Badge>
                        <Button 
                          onClick={() => handleExecuteWorkflow(workflow.workflow_id)}
                          size="sm"
                          variant="outline"
                        >
                          <Play className="h-3 w-3" />
                        </Button>
                        <Button 
                          onClick={() => handleToggleWorkflowStatus(workflow.workflow_id, workflow.status)}
                          size="sm"
                          variant="outline"
                        >
                          {workflow.status === 'active' ? <Pause className="h-3 w-3" /> : <Play className="h-3 w-3" />}
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Steps</div>
                        <div className="font-semibold">{workflow.steps_count}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Triggers</div>
                        <div className="font-semibold">{workflow.triggers_count}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="font-semibold">{formatDate(workflow.created_at)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Updated</div>
                        <div className="font-semibold">{formatDate(workflow.updated_at)}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Executions Tab */}
        <TabsContent value="executions">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-blue-800">Execution History</CardTitle>
              <CardDescription>Monitor workflow execution history and performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {executions.map((execution) => (
                  <Card key={execution.execution_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(execution.status)}
                        <div>
                          <div className="font-semibold text-lg">
                            Execution {execution.execution_id.slice(0, 8)}...
                          </div>
                          <div className="text-sm text-gray-600">
                            Workflow: {execution.workflow_id.slice(0, 8)}...
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getStatusBadge(execution.status)} text-white`}>
                          {execution.status.toUpperCase()}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Started</div>
                        <div className="font-semibold">{formatDateTime(execution.started_at)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Completed</div>
                        <div className="font-semibold">
                          {execution.completed_at ? formatDateTime(execution.completed_at) : 'Ongoing'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Current Step</div>
                        <div className="font-semibold">
                          {execution.current_step || 'N/A'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Error</div>
                        <div className="font-semibold text-red-600">
                          {execution.error_message ? 'Yes' : 'No'}
                        </div>
                      </div>
                    </div>
                    
                    {execution.error_message && (
                      <div className="mt-3 p-2 bg-red-50 rounded text-sm text-red-700">
                        {execution.error_message}
                      </div>
                    )}
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Triggers Tab */}
        <TabsContent value="triggers">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-blue-800">Trigger Management</CardTitle>
              <CardDescription>Configure and manage workflow triggers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {triggers.map((trigger) => (
                  <Card key={trigger.trigger_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getTriggerIcon(trigger.trigger_type)}
                        <div>
                          <div className="font-semibold text-lg">{trigger.name}</div>
                          <div className="text-sm text-gray-600">{trigger.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className={trigger.enabled ? 'text-green-600 border-green-300' : 'text-red-600 border-red-300'}>
                          {trigger.enabled ? 'Active' : 'Inactive'}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Type</div>
                        <div className="font-semibold">{trigger.trigger_type.replace('_', ' ')}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Workflow</div>
                        <div className="font-semibold">{trigger.workflow_id?.slice(0, 8)}...</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="font-semibold">{formatDate(trigger.created_at)}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-blue-800">Workflow Templates</CardTitle>
              <CardDescription>Pre-built workflow templates for common automation scenarios</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <Card key={template.template_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        <Workflow className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-semibold">{template.name}</span>
                      </div>
                      <Badge variant="outline">{template.complexity}</Badge>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                    
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs text-gray-500">{template.steps.length} steps</span>
                      <span className="text-xs text-gray-500">{template.category}</span>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="text-xs font-medium text-gray-700">Steps:</div>
                      {template.steps.slice(0, 3).map((step, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-600">
                          {getActionIcon(step.action_type)}
                          <span className="ml-2">{step.name}</span>
                        </div>
                      ))}
                      {template.steps.length > 3 && (
                        <div className="text-xs text-gray-500">+{template.steps.length - 3} more steps</div>
                      )}
                    </div>
                    
                    <Button 
                      className="w-full mt-3" 
                      onClick={() => handleCreateFromTemplate(template.template_id, `${template.name} - Copy`)}
                    >
                      <Plus className="h-3 w-3 mr-1" /> Create from Template
                    </Button>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-blue-800 flex items-center">
                <Activity className="mr-2 h-5 w-5 text-green-500" /> System Monitoring
              </CardTitle>
              <CardDescription>Monitor automation system health and performance</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* System Health */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-green-600">System Health</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-lg font-semibold text-green-600">Database</div>
                          <div className="text-sm text-gray-600">Connected</div>
                        </div>
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-lg font-semibold text-green-600">Redis</div>
                          <div className="text-sm text-gray-600">Connected</div>
                        </div>
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-lg font-semibold text-green-600">Celery</div>
                          <div className="text-sm text-gray-600">Running</div>
                        </div>
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Performance Metrics */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Performance Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">98.5%</div>
                          <div className="text-sm text-gray-600">Success Rate</div>
                        </div>
                        <TrendingUp className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-purple-600">2.3s</div>
                          <div className="text-sm text-gray-600">Avg Execution Time</div>
                        </div>
                        <Clock className="h-8 w-8 text-purple-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Recent Activity */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-orange-600">Recent Activity</h3>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Workflow "Campaign Optimization" completed successfully</div>
                        <div className="text-xs text-gray-600">2 minutes ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <Play className="h-4 w-4 text-blue-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Workflow "Lead Nurturing" started execution</div>
                        <div className="text-xs text-gray-600">5 minutes ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <Zap className="h-4 w-4 text-yellow-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Trigger "Daily Report" activated</div>
                        <div className="text-xs text-gray-600">10 minutes ago</div>
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

export default AdvancedAutomationDashboard;
