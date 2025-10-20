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
  Globe, 
  Facebook,
  Twitter,
  Pinterest,
  Camera,
  MessageSquare,
  HelpCircle,
  Target,
  BarChart3,
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
  HelpCircle as HelpCircleIcon,
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
  Camera as CameraIcon,
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

const AdditionalPlatformIntegrationsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [campaigns, setCampaigns] = useState([]);
  const [credentials, setCredentials] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateCampaignDialog, setShowCreateCampaignDialog] = useState(false);
  const [showCredentialsDialog, setShowCredentialsDialog] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('facebook_ads');
  
  const organizationId = "demo-org-123"; // Mock organization ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, campaignsData, credentialsData, metricsData] = await Promise.all([
        api.get(`/api/platforms/dashboard/${organizationId}`),
        api.get('/api/platforms/campaigns'),
        api.get('/api/platforms/credentials'),
        api.get('/api/platforms/metrics')
      ]);
      
      setDashboardData(dashboardData.data);
      setCampaigns(campaignsData.data || []);
      setCredentials(credentialsData.data.credentials || []);
      setMetrics(metricsData.data.platform_summary || {});
      
    } catch (err) {
      console.error("Failed to fetch platform integrations data:", err);
      setError("Failed to load platform integrations. Please try again.");
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

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'facebook_ads': return <Facebook className="h-5 w-5 text-blue-600" />;
      case 'twitter_ads': return <Twitter className="h-5 w-5 text-blue-400" />;
      case 'pinterest': return <Pinterest className="h-5 w-5 text-red-500" />;
      case 'snapchat': return <Camera className="h-5 w-5 text-yellow-500" />;
      case 'reddit': return <MessageSquare className="h-5 w-5 text-orange-500" />;
      case 'quora': return <HelpCircle className="h-5 w-5 text-red-600" />;
      default: return <Globe className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPlatformColor = (platform) => {
    switch (platform) {
      case 'facebook_ads': return 'text-blue-600';
      case 'twitter_ads': return 'text-blue-400';
      case 'pinterest': return 'text-red-500';
      case 'snapchat': return 'text-yellow-500';
      case 'reddit': return 'text-orange-500';
      case 'quora': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getPlatformBadge = (platform) => {
    switch (platform) {
      case 'facebook_ads': return 'bg-blue-500';
      case 'twitter_ads': return 'bg-blue-400';
      case 'pinterest': return 'bg-red-500';
      case 'snapchat': return 'bg-yellow-500';
      case 'reddit': return 'bg-orange-500';
      case 'quora': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'text-green-600';
      case 'PAUSED': return 'text-yellow-600';
      case 'DELETED': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-500';
      case 'PAUSED': return 'bg-yellow-500';
      case 'DELETED': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const handleCreateCampaign = async (campaignData) => {
    try {
      await api.post('/api/platforms/campaigns', campaignData);
      await fetchData(); // Refresh data
      setShowCreateCampaignDialog(false);
    } catch (err) {
      console.error("Failed to create campaign:", err);
    }
  };

  const handleStoreCredentials = async (credentialsData) => {
    try {
      await api.post('/api/platforms/credentials', credentialsData);
      await fetchData(); // Refresh data
      setShowCredentialsDialog(false);
    } catch (err) {
      console.error("Failed to store credentials:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Additional Platform Integrations...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-purple-50 to-pink-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-purple-800 flex items-center">
              <Globe className="mr-2 h-6 w-6 text-purple-500" /> Additional Platform Integrations
            </CardTitle>
            <CardDescription className="text-gray-700">
              Facebook Ads, Twitter Ads, Pinterest, Snapchat, Reddit, and Quora integrations
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showCredentialsDialog} onOpenChange={setShowCredentialsDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-purple-600 border-purple-300 hover:bg-purple-50">
                  <Key className="mr-2 h-4 w-4" /> Credentials
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Store Platform Credentials</DialogTitle>
                  <DialogDescription>
                    Add credentials for platform API access
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="platform">Platform</Label>
                    <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="facebook_ads">Facebook Ads</SelectItem>
                        <SelectItem value="twitter_ads">Twitter Ads</SelectItem>
                        <SelectItem value="pinterest">Pinterest</SelectItem>
                        <SelectItem value="snapchat">Snapchat</SelectItem>
                        <SelectItem value="reddit">Reddit</SelectItem>
                        <SelectItem value="quora">Quora</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="access-token">Access Token</Label>
                    <Input id="access-token" placeholder="Enter access token" />
                  </div>
                  <div>
                    <Label htmlFor="account-id">Account ID</Label>
                    <Input id="account-id" placeholder="Enter account ID" />
                  </div>
                  <Button className="w-full" onClick={() => handleStoreCredentials({})}>
                    <Key className="mr-2 h-4 w-4" /> Store Credentials
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-purple-600 border-purple-300 hover:bg-purple-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreateCampaignDialog} onOpenChange={setShowCreateCampaignDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-purple-600 hover:bg-purple-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Campaign
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Platform Campaign</DialogTitle>
                  <DialogDescription>
                    Create a new campaign on selected platform
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="campaign-platform">Platform</Label>
                    <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="facebook_ads">Facebook Ads</SelectItem>
                        <SelectItem value="twitter_ads">Twitter Ads</SelectItem>
                        <SelectItem value="pinterest">Pinterest</SelectItem>
                        <SelectItem value="snapchat">Snapchat</SelectItem>
                        <SelectItem value="reddit">Reddit</SelectItem>
                        <SelectItem value="quora">Quora</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="campaign-name">Campaign Name</Label>
                    <Input id="campaign-name" placeholder="Enter campaign name" />
                  </div>
                  <div>
                    <Label htmlFor="campaign-budget">Budget</Label>
                    <Input id="campaign-budget" type="number" placeholder="Enter budget" />
                  </div>
                  <Button className="w-full" onClick={() => handleCreateCampaign({})}>
                    <Target className="mr-2 h-4 w-4" /> Create Campaign
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Platform Integrations Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-purple-500" /> Platform Integrations Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {dashboardData?.total_campaigns || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Campaigns</div>
              <div className="text-sm text-gray-600">Across all platforms</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {dashboardData?.active_campaigns || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Active Campaigns</div>
              <div className="text-sm text-gray-600">Currently running</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {dashboardData?.supported_platforms?.length || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Supported Platforms</div>
              <div className="text-sm text-gray-600">Integrated platforms</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {formatCurrency(dashboardData?.total_budget || 0)}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Budget</div>
              <div className="text-sm text-gray-600">Campaign budgets</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Platform Integrations Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-purple-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="campaigns" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Campaigns</TabsTrigger>
          <TabsTrigger value="platforms" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Platforms</TabsTrigger>
          <TabsTrigger value="credentials" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Credentials</TabsTrigger>
          <TabsTrigger value="metrics" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Metrics</TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Platform Statistics */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Platform Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(dashboardData?.platform_statistics || {}).map(([platform, stats]) => (
                    <div key={platform} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getPlatformIcon(platform)}
                          <span className="ml-2 font-semibold capitalize">
                            {platform.replace('_', ' ')}
                          </span>
                        </div>
                        <Badge className={`${getPlatformBadge(platform)} text-white`}>
                          {stats.active_campaigns} active
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="text-gray-600">Campaigns</div>
                          <div className="font-semibold">{stats.total_campaigns}</div>
                        </div>
                        <div>
                          <div className="text-gray-600">Budget</div>
                          <div className="font-semibold">{formatCurrency(stats.total_budget)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Campaigns */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                  <Target className="mr-2 h-5 w-5 text-green-500" /> Recent Campaigns
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {campaigns.slice(0, 5).map((campaign) => (
                      <div key={campaign.campaign_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getPlatformIcon(campaign.platform)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{campaign.name}</div>
                          <div className="text-xs text-gray-600">
                            {campaign.platform.replace('_', ' ')} • {formatCurrency(campaign.budget)}
                          </div>
                        </div>
                        <Badge className={`${getStatusBadge(campaign.status)} text-white`}>
                          {campaign.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Campaigns Tab */}
        <TabsContent value="campaigns">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800">Campaign Management</CardTitle>
              <CardDescription>Manage campaigns across all integrated platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {campaigns.map((campaign) => (
                  <Card key={campaign.campaign_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getPlatformIcon(campaign.platform)}
                        <div>
                          <div className="font-semibold text-lg">{campaign.name}</div>
                          <div className="text-sm text-gray-600">
                            {campaign.platform.replace('_', ' ')} • {campaign.objective}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getStatusBadge(campaign.status)} text-white`}>
                          {campaign.status}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Budget</div>
                        <div className="text-lg font-semibold">{formatCurrency(campaign.budget)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Daily Budget</div>
                        <div className="text-lg font-semibold">
                          {campaign.daily_budget ? formatCurrency(campaign.daily_budget) : 'N/A'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Platform</div>
                        <div className="text-lg font-semibold">{campaign.platform.replace('_', ' ')}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="text-lg font-semibold">{formatDate(campaign.created_at)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Targeting:</div>
                      <div className="text-sm text-gray-600">
                        {Object.keys(campaign.targeting).length > 0 ? 
                          Object.keys(campaign.targeting).join(', ') : 'No targeting specified'}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Platforms Tab */}
        <TabsContent value="platforms">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800">Supported Platforms</CardTitle>
              <CardDescription>Overview of all integrated advertising platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData?.supported_platforms?.map((platform) => {
                  const stats = dashboardData.platform_statistics[platform];
                  return (
                    <Card key={platform} className="p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center">
                          {getPlatformIcon(platform)}
                          <span className="ml-2 font-semibold capitalize">
                            {platform.replace('_', ' ')}
                          </span>
                        </div>
                        <Badge className={`${getPlatformBadge(platform)} text-white`}>
                          Active
                        </Badge>
                      </div>
                      
                      <div className="space-y-2 mb-3">
                        <div className="flex justify-between text-sm">
                          <span>Campaigns:</span>
                          <span className="font-semibold">{stats?.total_campaigns || 0}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Active:</span>
                          <span className="font-semibold">{stats?.active_campaigns || 0}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Budget:</span>
                          <span className="font-semibold">{formatCurrency(stats?.total_budget || 0)}</span>
                        </div>
                      </div>
                      
                      <Button className="w-full" size="sm">
                        <Settings className="h-3 w-3 mr-1" /> Manage
                      </Button>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Credentials Tab */}
        <TabsContent value="credentials">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800">Platform Credentials</CardTitle>
              <CardDescription>Manage API credentials for platform integrations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {credentials.map((credential) => (
                  <Card key={`${credential.platform}-${credential.account_id}`} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getPlatformIcon(credential.platform)}
                        <div>
                          <div className="font-semibold text-lg capitalize">
                            {credential.platform.replace('_', ' ')}
                          </div>
                          <div className="text-sm text-gray-600">
                            Account: {credential.account_id}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-green-600 border-green-300">
                          Connected
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Edit className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Client ID</div>
                        <div className="font-semibold">{credential.client_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Expires</div>
                        <div className="font-semibold">
                          {credential.expires_at ? formatDate(credential.expires_at) : 'Never'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="font-semibold">{formatDate(credential.created_at)}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800">Platform Metrics</CardTitle>
              <CardDescription>Performance metrics across all platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(metrics).map(([platform, platformMetrics]) => (
                  <Card key={platform} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getPlatformIcon(platform)}
                        <div>
                          <div className="font-semibold text-lg capitalize">
                            {platform.replace('_', ' ')}
                          </div>
                          <div className="text-sm text-gray-600">Platform metrics</div>
                        </div>
                      </div>
                      <Badge className={`${getPlatformBadge(platform)} text-white`}>
                        Active
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div>
                        <div className="text-gray-600">Total Campaigns</div>
                        <div className="text-2xl font-bold text-blue-600">
                          {platformMetrics.total_campaigns}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Total Metrics</div>
                        <div className="text-2xl font-bold text-green-600">
                          {platformMetrics.total_metrics}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Status</div>
                        <div className="text-lg font-semibold text-green-600">
                          Connected
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Platform Analytics
              </CardTitle>
              <CardDescription>Comprehensive analytics across all integrated platforms</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Performance Overview */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-purple-600">Performance Overview</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-purple-600">
                            {dashboardData?.total_campaigns || 0}
                          </div>
                          <div className="text-sm text-gray-600">Total Campaigns</div>
                        </div>
                        <Target className="h-8 w-8 text-purple-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {dashboardData?.active_campaigns || 0}
                          </div>
                          <div className="text-sm text-gray-600">Active Campaigns</div>
                        </div>
                        <Activity className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {formatCurrency(dashboardData?.total_budget || 0)}
                          </div>
                          <div className="text-sm text-gray-600">Total Budget</div>
                        </div>
                        <DollarSign className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Platform Performance */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Platform Performance</h3>
                  <div className="space-y-3">
                    {Object.entries(dashboardData?.platform_statistics || {}).map(([platform, stats]) => (
                      <div key={platform} className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {getPlatformIcon(platform)}
                            <span className="ml-2 font-semibold capitalize">
                              {platform.replace('_', ' ')}
                            </span>
                          </div>
                          <Badge className={`${getPlatformBadge(platform)} text-white`}>
                            {stats.active_campaigns} Active
                          </Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          {stats.total_campaigns} campaigns • {formatCurrency(stats.total_budget)} budget
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Recent Activity */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-orange-600">Recent Activity</h3>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Facebook Ads campaign "Summer Sale" created</div>
                        <div className="text-xs text-gray-600">2 hours ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <Activity className="h-4 w-4 text-blue-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Twitter Ads campaign "Brand Awareness" activated</div>
                        <div className="text-xs text-gray-600">4 hours ago</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                      <BarChart3 className="h-4 w-4 text-purple-500" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Pinterest metrics updated for campaign "Product Launch"</div>
                        <div className="text-xs text-gray-600">6 hours ago</div>
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

export default AdditionalPlatformIntegrationsDashboard;
