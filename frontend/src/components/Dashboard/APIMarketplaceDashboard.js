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
  Store, 
  Package,
  Download,
  Upload,
  Users,
  Star,
  TrendingUp,
  TrendingDown,
  Activity,
  Gauge,
  ArrowUp,
  ArrowDown,
  Minus,
  Award,
  Trophy,
  Filter,
  Search,
  RefreshCw,
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
  Store as StoreIcon,
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

const APIMarketplaceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [packages, setPackages] = useState([]);
  const [developers, setDevelopers] = useState([]);
  const [installations, setInstallations] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateDeveloperDialog, setShowCreateDeveloperDialog] = useState(false);
  const [showCreatePackageDialog, setShowCreatePackageDialog] = useState(false);
  const [showInstallDialog, setShowInstallDialog] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  const organizationId = "demo-org-123"; // Mock organization ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, packagesData, installationsData] = await Promise.all([
        api.get(`/api/marketplace/dashboard/${organizationId}`),
        api.get('/api/marketplace/packages'),
        api.get(`/api/marketplace/installations?organization_id=${organizationId}`)
      ]);
      
      setDashboardData(dashboardData.data);
      setPackages(packagesData.data || []);
      setInstallations(installationsData.data || []);
      
    } catch (err) {
      console.error("Failed to fetch marketplace data:", err);
      setError("Failed to load marketplace data. Please try again.");
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

  const getIntegrationTypeIcon = (integrationType) => {
    switch (integrationType) {
      case 'webhook': return <Globe className="h-5 w-5 text-blue-500" />;
      case 'api_client': return <Cpu className="h-5 w-5 text-green-500" />;
      case 'data_source': return <Database className="h-5 w-5 text-purple-500" />;
      case 'workflow_action': return <Activity className="h-5 w-5 text-orange-500" />;
      case 'custom_widget': return <Monitor className="h-5 w-5 text-indigo-500" />;
      case 'report_template': return <FileText className="h-5 w-5 text-red-500" />;
      case 'ai_model': return <Brain className="h-5 w-5 text-pink-500" />;
      case 'automation_rule': return <Settings className="h-5 w-5 text-yellow-500" />;
      default: return <Package className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPricingModelColor = (pricingModel) => {
    switch (pricingModel) {
      case 'free': return 'text-green-600';
      case 'one_time': return 'text-blue-600';
      case 'subscription': return 'text-purple-600';
      case 'usage_based': return 'text-orange-600';
      case 'freemium': return 'text-indigo-600';
      default: return 'text-gray-600';
    }
  };

  const getPricingModelBadge = (pricingModel) => {
    switch (pricingModel) {
      case 'free': return 'bg-green-500';
      case 'one_time': return 'bg-blue-500';
      case 'subscription': return 'bg-purple-500';
      case 'usage_based': return 'bg-orange-500';
      case 'freemium': return 'bg-indigo-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'text-green-600';
      case 'pending_review': return 'text-yellow-600';
      case 'rejected': return 'text-red-600';
      case 'draft': return 'text-gray-600';
      case 'deprecated': return 'text-orange-600';
      case 'suspended': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-500';
      case 'pending_review': return 'bg-yellow-500';
      case 'rejected': return 'bg-red-500';
      case 'draft': return 'bg-gray-500';
      case 'deprecated': return 'bg-orange-500';
      case 'suspended': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const handleCreateDeveloper = async (developerData) => {
    try {
      await api.post('/api/marketplace/developers', developerData);
      await fetchData(); // Refresh data
      setShowCreateDeveloperDialog(false);
    } catch (err) {
      console.error("Failed to create developer:", err);
    }
  };

  const handleCreatePackage = async (packageData) => {
    try {
      await api.post('/api/marketplace/packages', packageData);
      await fetchData(); // Refresh data
      setShowCreatePackageDialog(false);
    } catch (err) {
      console.error("Failed to create package:", err);
    }
  };

  const handleInstallPackage = async (packageId, configuration) => {
    try {
      await api.post('/api/marketplace/installations', {
        package_id: packageId,
        configuration: configuration
      }, {
        params: { organization_id: organizationId }
      });
      await fetchData(); // Refresh data
      setShowInstallDialog(false);
    } catch (err) {
      console.error("Failed to install package:", err);
    }
  };

  const handleSearch = async () => {
    try {
      const response = await api.post('/api/marketplace/search', {
        query: searchQuery,
        integration_type: null,
        pricing_model: null,
        tags: [],
        developer_id: null
      });
      setPackages(response.data.results || []);
    } catch (err) {
      console.error("Failed to search packages:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading API Marketplace...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-orange-50 to-red-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-orange-800 flex items-center">
              <Store className="mr-2 h-6 w-6 text-orange-500" /> API Marketplace
            </CardTitle>
            <CardDescription className="text-gray-700">
              Third-party integrations, extensions, and developer ecosystem
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showCreateDeveloperDialog} onOpenChange={setShowCreateDeveloperDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-orange-600 border-orange-300 hover:bg-orange-50">
                  <UserPlus className="mr-2 h-4 w-4" /> Developer
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Developer Profile</DialogTitle>
                  <DialogDescription>
                    Register as a developer to publish integrations
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="dev-name">Name</Label>
                    <Input id="dev-name" placeholder="Enter developer name" />
                  </div>
                  <div>
                    <Label htmlFor="dev-email">Email</Label>
                    <Input id="dev-email" type="email" placeholder="Enter email" />
                  </div>
                  <div>
                    <Label htmlFor="dev-company">Company</Label>
                    <Input id="dev-company" placeholder="Enter company name" />
                  </div>
                  <div>
                    <Label htmlFor="dev-tier">Tier</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select tier" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="individual">Individual</SelectItem>
                        <SelectItem value="startup">Startup</SelectItem>
                        <SelectItem value="enterprise">Enterprise</SelectItem>
                        <SelectItem value="partner">Partner</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button className="w-full" onClick={() => handleCreateDeveloper({})}>
                    <UserPlus className="mr-2 h-4 w-4" /> Create Profile
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-orange-600 border-orange-300 hover:bg-orange-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreatePackageDialog} onOpenChange={setShowCreatePackageDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-orange-600 hover:bg-orange-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Package
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Integration Package</DialogTitle>
                  <DialogDescription>
                    Upload a new integration package to the marketplace
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="package-name">Package Name</Label>
                    <Input id="package-name" placeholder="Enter package name" />
                  </div>
                  <div>
                    <Label htmlFor="package-description">Description</Label>
                    <Textarea id="package-description" placeholder="Enter package description" />
                  </div>
                  <div>
                    <Label htmlFor="package-type">Integration Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="webhook">Webhook</SelectItem>
                        <SelectItem value="api_client">API Client</SelectItem>
                        <SelectItem value="data_source">Data Source</SelectItem>
                        <SelectItem value="workflow_action">Workflow Action</SelectItem>
                        <SelectItem value="custom_widget">Custom Widget</SelectItem>
                        <SelectItem value="report_template">Report Template</SelectItem>
                        <SelectItem value="ai_model">AI Model</SelectItem>
                        <SelectItem value="automation_rule">Automation Rule</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="package-file">Package File</Label>
                    <Input id="package-file" type="file" accept=".zip" />
                  </div>
                  <Button className="w-full" onClick={() => handleCreatePackage({})}>
                    <Upload className="mr-2 h-4 w-4" /> Upload Package
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Marketplace Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-orange-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-orange-500" /> Marketplace Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {dashboardData?.package_statistics?.total_packages || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Packages</div>
              <div className="text-sm text-gray-600">Available integrations</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {dashboardData?.package_statistics?.approved_packages || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Approved Packages</div>
              <div className="text-sm text-gray-600">Ready to install</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {dashboardData?.organization_statistics?.installed_packages || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Installed</div>
              <div className="text-sm text-gray-600">In your organization</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {dashboardData?.package_statistics?.free_packages || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Free Packages</div>
              <div className="text-sm text-gray-600">No cost integrations</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search Bar */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <Input
                placeholder="Search integrations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Button onClick={handleSearch} className="flex items-center">
              <Search className="mr-2 h-4 w-4" /> Search
            </Button>
            <Select>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="webhook">Webhook</SelectItem>
                <SelectItem value="api_client">API Client</SelectItem>
                <SelectItem value="data_source">Data Source</SelectItem>
                <SelectItem value="workflow_action">Workflow Action</SelectItem>
                <SelectItem value="custom_widget">Custom Widget</SelectItem>
                <SelectItem value="report_template">Report Template</SelectItem>
                <SelectItem value="ai_model">AI Model</SelectItem>
                <SelectItem value="automation_rule">Automation Rule</SelectItem>
              </SelectContent>
            </Select>
            <Select>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by pricing" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Pricing</SelectItem>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="one_time">One Time</SelectItem>
                <SelectItem value="subscription">Subscription</SelectItem>
                <SelectItem value="usage_based">Usage Based</SelectItem>
                <SelectItem value="freemium">Freemium</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Main Marketplace Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-orange-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="packages" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Packages</TabsTrigger>
          <TabsTrigger value="installations" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Installations</TabsTrigger>
          <TabsTrigger value="developers" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Developers</TabsTrigger>
          <TabsTrigger value="popular" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Popular</TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-orange-600 data-[state=active]:text-white transition-all">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Popular Packages */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-orange-800 flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> Popular Packages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {dashboardData?.popular_packages?.slice(0, 5).map((pkg) => (
                      <div key={pkg.package_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getIntegrationTypeIcon(pkg.integration_type)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{pkg.name}</div>
                          <div className="text-xs text-gray-600">
                            {pkg.integration_type.replace('_', ' ')} • {pkg.download_count || 0} downloads
                          </div>
                        </div>
                        <Badge className={`${getPricingModelBadge(pkg.pricing_model)} text-white`}>
                          {pkg.pricing_model}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Recent Packages */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-orange-800 flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-blue-500" /> Recent Packages
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {dashboardData?.recent_packages?.slice(0, 5).map((pkg) => (
                      <div key={pkg.package_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getIntegrationTypeIcon(pkg.integration_type)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{pkg.name}</div>
                          <div className="text-xs text-gray-600">
                            {formatDate(pkg.created_at)} • {pkg.developer_id}
                          </div>
                        </div>
                        <Badge className={`${getStatusBadge(pkg.status)} text-white`}>
                          {pkg.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Packages Tab */}
        <TabsContent value="packages">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-orange-800">Integration Packages</CardTitle>
              <CardDescription>Browse and install integration packages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {packages.map((pkg) => (
                  <Card key={pkg.package_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getIntegrationTypeIcon(pkg.integration_type)}
                        <div>
                          <div className="font-semibold text-lg">{pkg.name}</div>
                          <div className="text-sm text-gray-600">{pkg.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getPricingModelBadge(pkg.pricing_model)} text-white`}>
                          {pkg.pricing_model}
                        </Badge>
                        <Badge className={`${getStatusBadge(pkg.status)} text-white`}>
                          {pkg.status}
                        </Badge>
                        <Button size="sm" variant="outline" onClick={() => setSelectedPackage(pkg)}>
                          <Eye className="h-3 w-3" />
                        </Button>
                        {pkg.status === 'approved' && (
                          <Button size="sm" onClick={() => handleInstallPackage(pkg.package_id, {})}>
                            <Download className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Version</div>
                        <div className="text-lg font-semibold">{pkg.version}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Type</div>
                        <div className="text-lg font-semibold">{pkg.integration_type.replace('_', ' ')}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Price</div>
                        <div className="text-lg font-semibold">
                          {pkg.price ? formatCurrency(pkg.price) : 'Free'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Downloads</div>
                        <div className="text-lg font-semibold">{pkg.download_count || 0}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Tags:</div>
                      <div className="flex flex-wrap gap-1">
                        {pkg.tags.map((tag, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">API Endpoints:</div>
                      <div className="text-sm text-gray-600">
                        {pkg.api_endpoints.length} endpoints available
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Installations Tab */}
        <TabsContent value="installations">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-orange-800">Installed Packages</CardTitle>
              <CardDescription>Manage your installed integration packages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {installations.map((installation) => (
                  <Card key={installation.installation_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Package className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{installation.package_id}</div>
                          <div className="text-sm text-gray-600">
                            Installed {formatDateTime(installation.installed_at)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-green-600 border-green-300">
                          {installation.status}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Package ID</div>
                        <div className="text-lg font-semibold">{installation.package_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Developer</div>
                        <div className="text-lg font-semibold">{installation.developer_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Last Used</div>
                        <div className="text-lg font-semibold">
                          {installation.last_used ? formatDateTime(installation.last_used) : 'Never'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Configuration:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {JSON.stringify(installation.configuration, null, 2)}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Developers Tab */}
        <TabsContent value="developers">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-orange-800">Developer Profiles</CardTitle>
              <CardDescription>Browse developer profiles and their contributions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {developers.map((developer) => (
                  <Card key={developer.developer_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{developer.name}</div>
                          <div className="text-sm text-gray-600">
                            {developer.company || 'Individual Developer'}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{developer.tier}</Badge>
                        {developer.verified && (
                          <Badge className="bg-green-500 text-white">
                            <CheckCircle className="h-3 w-3 mr-1" /> Verified
                          </Badge>
                        )}
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Integrations</div>
                        <div className="text-lg font-semibold">{developer.integrations_count}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Downloads</div>
                        <div className="text-lg font-semibold">{developer.total_downloads}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Rating</div>
                        <div className="text-lg font-semibold">{developer.rating.toFixed(1)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Joined</div>
                        <div className="text-lg font-semibold">{formatDate(developer.created_at)}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Popular Tab */}
        <TabsContent value="popular">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-orange-800">Popular Integrations</CardTitle>
              <CardDescription>Most downloaded and highly rated packages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData?.popular_packages?.map((pkg) => (
                  <Card key={pkg.package_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center">
                        {getIntegrationTypeIcon(pkg.integration_type)}
                        <span className="ml-2 font-semibold">{pkg.name}</span>
                      </div>
                      <Badge className={`${getPricingModelBadge(pkg.pricing_model)} text-white`}>
                        {pkg.pricing_model}
                      </Badge>
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-3">
                      {pkg.description}
                    </div>
                    
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-sm">
                        <span>Downloads:</span>
                        <span className="font-semibold">{pkg.download_count || 0}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Rating:</span>
                        <span className="font-semibold">{pkg.rating?.toFixed(1) || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Version:</span>
                        <span className="font-semibold">{pkg.version}</span>
                      </div>
                    </div>
                    
                    <Button className="w-full" size="sm">
                      <Download className="h-3 w-3 mr-1" /> Install
                    </Button>
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
              <CardTitle className="text-xl font-bold text-orange-800 flex items-center">
                <Activity className="mr-2 h-5 w-5 text-blue-500" /> Marketplace Analytics
              </CardTitle>
              <CardDescription>Marketplace usage and performance analytics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Package Statistics */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-orange-600">Package Statistics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-orange-600">
                            {dashboardData?.package_statistics?.total_packages || 0}
                          </div>
                          <div className="text-sm text-gray-600">Total Packages</div>
                        </div>
                        <Package className="h-8 w-8 text-orange-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {dashboardData?.package_statistics?.approved_packages || 0}
                          </div>
                          <div className="text-sm text-gray-600">Approved Packages</div>
                        </div>
                        <CheckCircle className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {dashboardData?.package_statistics?.free_packages || 0}
                          </div>
                          <div className="text-sm text-gray-600">Free Packages</div>
                        </div>
                        <Gift className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Integration Type Distribution */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Integration Type Distribution</h3>
                  <div className="space-y-3">
                    {[
                      { type: 'api_client', count: 15, percentage: 30 },
                      { type: 'webhook', count: 12, percentage: 24 },
                      { type: 'data_source', count: 8, percentage: 16 },
                      { type: 'workflow_action', count: 7, percentage: 14 },
                      { type: 'custom_widget', count: 5, percentage: 10 },
                      { type: 'report_template', count: 3, percentage: 6 }
                    ].map((integrationType) => (
                      <div key={integrationType.type} className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {getIntegrationTypeIcon(integrationType.type)}
                            <span className="ml-2 font-semibold capitalize">
                              {integrationType.type.replace('_', ' ')}
                            </span>
                          </div>
                          <Badge variant="outline">{integrationType.count} packages</Badge>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${integrationType.percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          {integrationType.percentage}% of total packages
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
                        <span className="font-semibold">Top Categories</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        API Clients: 30% • Webhooks: 24% • Data Sources: 16% • Workflow Actions: 14%
                      </div>
                    </div>
                    
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Star className="h-5 w-5 text-yellow-500 mr-2" />
                        <span className="font-semibold">Pricing Preferences</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Free: 60% • Subscription: 25% • One-time: 10% • Usage-based: 5%
                      </div>
                    </div>
                    
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Download className="h-5 w-5 text-indigo-500 mr-2" />
                        <span className="font-semibold">Installation Trends</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Peak installation times: 10-11 AM and 2-3 PM • Most popular day: Tuesday
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

export default APIMarketplaceDashboard;
