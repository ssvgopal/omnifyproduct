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
  BarChart3, 
  PieChart,
  LineChart,
  TrendingUp,
  TrendingDown,
  Activity,
  Gauge,
  ArrowUp,
  ArrowDown,
  Minus,
  Star,
  Award,
  Trophy,
  Filter,
  Search,
  RefreshCw,
  Download,
  Upload,
  Settings,
  Plus,
  Edit,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
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
  FolderFileArchive,
  Mail,
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
  Lock,
  Unlock,
  Key,
  Shield,
  AlertCircle,
  Calendar,
  DollarSign,
  MousePointer,
  Users,
  User,
  UserPlus,
  UserMinus,
  UserCheck,
  UserX,
  UserCircle,
  UserSquare,
  UserHexagon,
  UserOctagon,
  UserDiamond,
  UserHeart,
  UserSmile,
  UserFrown,
  UserMeh,
  UserThumbsUp,
  UserThumbsDown,
  UserBookmark,
  UserBookmarkCheck,
  UserBookmarkX,
  UserFlag,
  UserFlagTriangleLeft,
  UserFlagTriangleRight,
  UserHome,
  UserBuilding,
  UserBuilding2,
  UserFactory,
  UserStore,
  UserWarehouse,
  UserOffice,
  UserSchool,
  UserHospital,
  UserBank,
  UserChurch,
  UserMosque,
  UserSynagogue,
  UserTemple,
  UserCastle,
  UserTent,
  UserCar,
  UserTruck,
  UserBus,
  UserTrain,
  UserPlane,
  UserShip,
  UserBike,
  UserScooter,
  UserMotorcycle,
  UserRocket,
  UserSatellite,
  UserTelescope,
  UserMicroscope,
  UserCamera,
  UserVideo,
  UserImage,
  UserFile,
  UserFileText,
  UserFileImage,
  UserFileVideo,
  UserFileAudio,
  UserFilePdf,
  UserFileSpreadsheet,
  UserFilePresentation,
  UserFileCode,
  UserFileArchive,
  UserFolder,
  UserFolderOpen,
  UserFolderPlus,
  UserFolderMinus,
  UserFolderX,
  UserFolderCheck,
  UserFolderLock,
  UserFolderUnlock,
  UserFolderHeart,
  UserFolderStar,
  UserFolderBookmark,
  UserFolderFlag,
  UserFolderHome,
  UserFolderBuilding,
  UserFolderCar,
  UserFolderPlane,
  UserFolderShip,
  UserFolderRocket,
  UserFolderSatellite,
  UserFolderTelescope,
  UserFolderMicroscope,
  UserFolderCamera,
  UserFolderVideo,
  UserFolderImage,
  UserFolderFile,
  UserFolderFileText,
  UserFolderFileImage,
  UserFolderFileVideo,
  UserFolderFileAudio,
  UserFolderFilePdf,
  UserFolderFileSpreadsheet,
  UserFolderFilePresentation,
  UserFolderFileCode,
  UserFolderFileArchive
} from 'lucide-react';
import api from '@/services/api';

const AdvancedReportingDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [templates, setTemplates] = useState([]);
  const [reports, setReports] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateTemplateDialog, setShowCreateTemplateDialog] = useState(false);
  const [showGenerateReportDialog, setShowGenerateReportDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  
  const organizationId = "demo-org-123"; // Mock organization ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, templatesData, reportsData] = await Promise.all([
        api.get(`/api/reporting/dashboard/${organizationId}`),
        api.get('/api/reporting/templates'),
        api.get('/api/reporting/reports')
      ]);
      
      setDashboardData(dashboardData.data);
      setTemplates(templatesData.data || []);
      setReports(reportsData.data || []);
      
    } catch (err) {
      console.error("Failed to fetch reporting data:", err);
      setError("Failed to load reporting data. Please try again.");
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

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getReportTypeIcon = (reportType) => {
    switch (reportType) {
      case 'campaign_performance': return <BarChart3 className="h-5 w-5 text-blue-500" />;
      case 'financial_summary': return <DollarSign className="h-5 w-5 text-green-500" />;
      case 'audience_analytics': return <Users className="h-5 w-5 text-purple-500" />;
      case 'conversion_funnel': return <TrendingUp className="h-5 w-5 text-orange-500" />;
      case 'competitive_analysis': return <Trophy className="h-5 w-5 text-yellow-500" />;
      case 'executive_summary': return <Award className="h-5 w-5 text-indigo-500" />;
      case 'custom_dashboard': return <Monitor className="h-5 w-5 text-gray-500" />;
      default: return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'generating': return 'text-yellow-600';
      case 'failed': return 'text-red-600';
      case 'draft': return 'text-gray-600';
      case 'scheduled': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'generating': return 'bg-yellow-500';
      case 'failed': return 'bg-red-500';
      case 'draft': return 'bg-gray-500';
      case 'scheduled': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getChartTypeIcon = (chartType) => {
    switch (chartType) {
      case 'line': return <LineChart className="h-4 w-4 text-blue-500" />;
      case 'bar': return <BarChart3 className="h-4 w-4 text-green-500" />;
      case 'pie': return <PieChart className="h-4 w-4 text-purple-500" />;
      case 'scatter': return <Activity className="h-4 w-4 text-orange-500" />;
      case 'area': return <TrendingUp className="h-4 w-4 text-indigo-500" />;
      case 'heatmap': return <SquareIcon className="h-4 w-4 text-red-500" />;
      case 'funnel': return <TrendingDown className="h-4 w-4 text-yellow-500" />;
      case 'gauge': return <Gauge className="h-4 w-4 text-pink-500" />;
      default: return <BarChart3 className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleCreateTemplate = async (templateData) => {
    try {
      await api.post('/api/reporting/templates', templateData);
      await fetchData(); // Refresh data
      setShowCreateTemplateDialog(false);
    } catch (err) {
      console.error("Failed to create template:", err);
    }
  };

  const handleGenerateReport = async (reportData) => {
    try {
      await api.post('/api/reporting/reports', reportData);
      await fetchData(); // Refresh data
      setShowGenerateReportDialog(false);
    } catch (err) {
      console.error("Failed to generate report:", err);
    }
  };

  const handleExportReport = async (reportId, format) => {
    try {
      const response = await api.get(`/api/reporting/reports/${reportId}/export?format=${format}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report_${reportId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Failed to export report:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Advanced Reporting & BI...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-indigo-50 to-purple-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-indigo-800 flex items-center">
              <BarChart3 className="mr-2 h-6 w-6 text-indigo-500" /> Advanced Reporting & BI
            </CardTitle>
            <CardDescription className="text-gray-700">
              Custom dashboards, data visualization, and executive reports
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showGenerateReportDialog} onOpenChange={setShowGenerateReportDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
                  <FileText className="mr-2 h-4 w-4" /> Generate Report
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Generate Report</DialogTitle>
                  <DialogDescription>
                    Generate a new report from template
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="template-select">Template</Label>
                    <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select template" />
                      </SelectTrigger>
                      <SelectContent>
                        {templates.map((template) => (
                          <SelectItem key={template.template_id} value={template.template_id}>
                            {template.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="start-date">Start Date</Label>
                    <Input id="start-date" type="date" />
                  </div>
                  <div>
                    <Label htmlFor="end-date">End Date</Label>
                    <Input id="end-date" type="date" />
                  </div>
                  <Button className="w-full" onClick={() => handleGenerateReport({})}>
                    <BarChart3 className="mr-2 h-4 w-4" /> Generate Report
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-indigo-600 border-indigo-300 hover:bg-indigo-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreateTemplateDialog} onOpenChange={setShowCreateTemplateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-indigo-600 hover:bg-indigo-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Template
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Report Template</DialogTitle>
                  <DialogDescription>
                    Create a new report template for automated generation
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="template-name">Template Name</Label>
                    <Input id="template-name" placeholder="Enter template name" />
                  </div>
                  <div>
                    <Label htmlFor="template-description">Description</Label>
                    <Textarea id="template-description" placeholder="Enter template description" />
                  </div>
                  <div>
                    <Label htmlFor="report-type">Report Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select report type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="campaign_performance">Campaign Performance</SelectItem>
                        <SelectItem value="financial_summary">Financial Summary</SelectItem>
                        <SelectItem value="executive_summary">Executive Summary</SelectItem>
                        <SelectItem value="audience_analytics">Audience Analytics</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button className="w-full" onClick={() => handleCreateTemplate({})}>
                    <Settings className="mr-2 h-4 w-4" /> Create Template
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Reporting Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-indigo-500" /> Reporting Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-indigo-600 mb-2">
                {dashboardData?.report_statistics?.total_reports || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Reports</div>
              <div className="text-sm text-gray-600">Generated reports</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {dashboardData?.report_statistics?.completed_reports || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Completed Reports</div>
              <div className="text-sm text-gray-600">Successfully generated</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {dashboardData?.template_statistics?.total_templates || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Templates</div>
              <div className="text-sm text-gray-600">Available templates</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {formatPercentage(dashboardData?.report_statistics?.success_rate || 0)}
              </div>
              <div className="text-lg font-semibold text-gray-800">Success Rate</div>
              <div className="text-sm text-gray-600">Report generation</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Reporting Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-indigo-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="templates" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Templates</TabsTrigger>
          <TabsTrigger value="reports" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Reports</TabsTrigger>
          <TabsTrigger value="charts" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Charts</TabsTrigger>
          <TabsTrigger value="exports" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Exports</TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-indigo-600 data-[state=active]:text-white transition-all">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Report Types */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <FileText className="mr-2 h-5 w-5 text-blue-500" /> Report Types
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { type: 'campaign_performance', name: 'Campaign Performance', count: 12 },
                    { type: 'financial_summary', name: 'Financial Summary', count: 8 },
                    { type: 'executive_summary', name: 'Executive Summary', count: 5 },
                    { type: 'audience_analytics', name: 'Audience Analytics', count: 7 }
                  ].map((reportType) => (
                    <div key={reportType.type} className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getReportTypeIcon(reportType.type)}
                          <span className="ml-2 font-semibold">{reportType.name}</span>
                        </div>
                        <Badge variant="outline">{reportType.count} reports</Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        {reportType.type.replace('_', ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Reports */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-green-500" /> Recent Reports
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {reports.slice(0, 5).map((report) => (
                      <div key={report.report_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getReportTypeIcon(report.template_id)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{report.name}</div>
                          <div className="text-xs text-gray-600">
                            {formatDateTime(report.created_at)} • {report.created_by}
                          </div>
                        </div>
                        <Badge className={`${getStatusBadge(report.status)} text-white`}>
                          {report.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800">Report Templates</CardTitle>
              <CardDescription>Manage report templates for automated generation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {templates.map((template) => (
                  <Card key={template.template_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getReportTypeIcon(template.report_type)}
                        <div>
                          <div className="font-semibold text-lg">{template.name}</div>
                          <div className="text-sm text-gray-600">{template.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{template.report_type}</Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Report Type</div>
                        <div className="text-lg font-semibold">{template.report_type.replace('_', ' ')}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Charts</div>
                        <div className="text-lg font-semibold">{template.chart_configs.length}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="text-lg font-semibold">{formatDate(template.created_at)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Chart Types:</div>
                      <div className="flex flex-wrap gap-1">
                        {template.chart_configs.map((chart, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {getChartTypeIcon(chart.type)}
                            <span className="ml-1">{chart.type}</span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800">Generated Reports</CardTitle>
              <CardDescription>View and manage generated reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reports.map((report) => (
                  <Card key={report.report_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getReportTypeIcon(report.template_id)}
                        <div>
                          <div className="font-semibold text-lg">{report.name}</div>
                          <div className="text-sm text-gray-600">
                            Created by {report.created_by} • {formatDateTime(report.created_at)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getStatusBadge(report.status)} text-white`}>
                          {report.status}
                        </Badge>
                        {report.status === 'completed' && (
                          <>
                            <Button size="sm" variant="outline" onClick={() => handleExportReport(report.report_id, 'pdf')}>
                              <FilePdf className="h-3 w-3" />
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleExportReport(report.report_id, 'excel')}>
                              <FileSpreadsheet className="h-3 w-3" />
                            </Button>
                          </>
                        )}
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Status</div>
                        <div className="text-lg font-semibold">{report.status}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Template</div>
                        <div className="text-lg font-semibold">{report.template_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Generated</div>
                        <div className="text-lg font-semibold">
                          {report.generated_at ? formatDateTime(report.generated_at) : 'N/A'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">File Size</div>
                        <div className="text-lg font-semibold">
                          {report.file_size ? `${(report.file_size / 1024).toFixed(1)} KB` : 'N/A'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Parameters:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {JSON.stringify(report.parameters, null, 2)}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Charts Tab */}
        <TabsContent value="charts">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800">Chart Gallery</CardTitle>
              <CardDescription>Interactive charts and data visualizations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { type: 'line', name: 'ROAS Trend', description: 'Return on ad spend over time' },
                  { type: 'bar', name: 'Platform Performance', description: 'Performance by advertising platform' },
                  { type: 'pie', name: 'Budget Distribution', description: 'Budget allocation across campaigns' },
                  { type: 'funnel', name: 'Conversion Funnel', description: 'User journey through conversion process' },
                  { type: 'gauge', name: 'Overall Performance', description: 'Overall campaign performance score' },
                  { type: 'heatmap', name: 'Engagement Heatmap', description: 'User engagement by time and channel' }
                ].map((chart) => (
                  <Card key={chart.type} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getChartTypeIcon(chart.type)}
                        <span className="ml-2 font-semibold">{chart.name}</span>
                      </div>
                      <Badge variant="outline">{chart.type}</Badge>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-3">
                      {chart.description}
                    </div>
                    
                    <div className="h-32 bg-gray-100 rounded flex items-center justify-center">
                      <div className="text-gray-500 text-sm">Chart Preview</div>
                    </div>
                    
                    <Button className="w-full mt-3" size="sm">
                      <Eye className="h-3 w-3 mr-1" /> View Chart
                    </Button>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Exports Tab */}
        <TabsContent value="exports">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800">Export Management</CardTitle>
              <CardDescription>Export reports in various formats</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    { format: 'pdf', name: 'PDF Report', icon: <FilePdf className="h-5 w-5 text-red-500" />, description: 'Professional PDF reports' },
                    { format: 'excel', name: 'Excel Spreadsheet', icon: <FileSpreadsheet className="h-5 w-5 text-green-500" />, description: 'Data analysis in Excel' },
                    { format: 'csv', name: 'CSV Data', icon: <FileText className="h-5 w-5 text-blue-500" />, description: 'Raw data export' },
                    { format: 'json', name: 'JSON Data', icon: <FileCode className="h-5 w-5 text-purple-500" />, description: 'Structured data export' }
                  ].map((exportFormat) => (
                    <Card key={exportFormat.format} className="p-4">
                      <div className="flex items-center mb-3">
                        {exportFormat.icon}
                        <span className="ml-2 font-semibold">{exportFormat.name}</span>
                      </div>
                      
                      <div className="text-sm text-gray-600 mb-3">
                        {exportFormat.description}
                      </div>
                      
                      <Button className="w-full" size="sm">
                        <Download className="h-3 w-3 mr-1" /> Export {exportFormat.format.toUpperCase()}
                      </Button>
                    </Card>
                  ))}
                </div>
                
                <div className="mt-6">
                  <h3 className="font-semibold text-lg mb-4">Recent Exports</h3>
                  <div className="space-y-2">
                    {reports.filter(r => r.status === 'completed').slice(0, 5).map((report) => (
                      <div key={report.report_id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div className="flex items-center">
                          {getReportTypeIcon(report.template_id)}
                          <div className="ml-3">
                            <div className="font-medium">{report.name}</div>
                            <div className="text-sm text-gray-600">{formatDateTime(report.created_at)}</div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button size="sm" variant="outline" onClick={() => handleExportReport(report.report_id, 'pdf')}>
                            <FilePdf className="h-3 w-3" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleExportReport(report.report_id, 'excel')}>
                            <FileSpreadsheet className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Reporting Analytics
              </CardTitle>
              <CardDescription>Analyze reporting performance and usage patterns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Performance Metrics */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-indigo-600">Performance Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-indigo-600">
                            {formatPercentage(dashboardData?.report_statistics?.success_rate || 0)}
                          </div>
                          <div className="text-sm text-gray-600">Success Rate</div>
                        </div>
                        <CheckCircle className="h-8 w-8 text-indigo-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {dashboardData?.report_statistics?.completed_reports || 0}
                          </div>
                          <div className="text-sm text-gray-600">Completed Reports</div>
                        </div>
                        <FileText className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {dashboardData?.template_statistics?.total_templates || 0}
                          </div>
                          <div className="text-sm text-gray-600">Active Templates</div>
                        </div>
                        <Settings className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Report Type Distribution */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Report Type Distribution</h3>
                  <div className="space-y-3">
                    {[
                      { type: 'campaign_performance', count: 12, percentage: 40 },
                      { type: 'financial_summary', count: 8, percentage: 27 },
                      { type: 'executive_summary', count: 5, percentage: 17 },
                      { type: 'audience_analytics', count: 5, percentage: 16 }
                    ].map((reportType) => (
                      <div key={reportType.type} className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {getReportTypeIcon(reportType.type)}
                            <span className="ml-2 font-semibold capitalize">
                              {reportType.type.replace('_', ' ')}
                            </span>
                          </div>
                          <Badge variant="outline">{reportType.count} reports</Badge>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${reportType.percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {reportType.percentage}% of total reports
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Usage Insights */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-orange-600">Usage Insights</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <TrendingUp className="h-5 w-5 text-orange-500 mr-2" />
                        <span className="font-semibold">Peak Usage Times</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Most reports generated: 9-11 AM and 2-4 PM • Peak day: Tuesday
                      </div>
                    </div>
                    
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <BarChart3 className="h-5 w-5 text-yellow-500 mr-2" />
                        <span className="font-semibold">Popular Chart Types</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Line charts: 35% • Bar charts: 25% • Pie charts: 20% • Gauges: 20%
                      </div>
                    </div>
                    
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Download className="h-5 w-5 text-indigo-500 mr-2" />
                        <span className="font-semibold">Export Preferences</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        PDF: 60% • Excel: 25% • CSV: 10% • JSON: 5%
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

export default AdvancedReportingDashboard;
