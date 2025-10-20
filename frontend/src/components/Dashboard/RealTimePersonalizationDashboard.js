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
  Users, 
  Target,
  Eye,
  Brain,
  Zap,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
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

const RealTimePersonalizationDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [userProfiles, setUserProfiles] = useState([]);
  const [audienceSegments, setAudienceSegments] = useState([]);
  const [personalizedContent, setPersonalizedContent] = useState([]);
  const [behavioralEvents, setBehavioralEvents] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateProfileDialog, setShowCreateProfileDialog] = useState(false);
  const [showCreateSegmentDialog, setShowCreateSegmentDialog] = useState(false);
  const [showPersonalizeDialog, setShowPersonalizeDialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedSegment, setSelectedSegment] = useState(null);
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, segmentsData, eventsData, contentData] = await Promise.all([
        api.get(`/api/personalization/dashboard/${clientId}`),
        api.get('/api/personalization/segments'),
        api.get('/api/personalization/events/demo-user-1'),
        api.get('/api/personalization/content/demo-user-1')
      ]);
      
      setDashboardData(dashboardData.data);
      setAudienceSegments(segmentsData.data || []);
      setBehavioralEvents(eventsData.data.events || []);
      setPersonalizedContent(contentData.data.content_items || []);
      
      // Mock user profiles data
      setUserProfiles([
        {
          user_id: "demo-user-1",
          demographics: { age: 28, gender: "female", location: "US" },
          behaviors: eventsData.data.events || [],
          preferences: { click_preferences: { "product": 5, "service": 3 }, conversion_preferences: { "electronics": 2 } },
          segments: ["high_engagement", "millennial"],
          engagement_score: 0.85,
          last_updated: new Date().toISOString()
        },
        {
          user_id: "demo-user-2",
          demographics: { age: 35, gender: "male", location: "UK" },
          behaviors: [],
          preferences: { click_preferences: { "service": 4 }, conversion_preferences: { "software": 1 } },
          segments: ["professional", "tech_savvy"],
          engagement_score: 0.72,
          last_updated: new Date().toISOString()
        }
      ]);
      
    } catch (err) {
      console.error("Failed to fetch personalization data:", err);
      setError("Failed to load personalization data. Please try again.");
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

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getEngagementColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEngagementBadge = (score) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getEngagementLevel = (score) => {
    if (score >= 0.8) return 'HIGH';
    if (score >= 0.6) return 'MEDIUM';
    return 'LOW';
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'page_view': return <Eye className="h-4 w-4 text-blue-500" />;
      case 'click': return <MousePointer className="h-4 w-4 text-green-500" />;
      case 'conversion': return <CheckCircle className="h-4 w-4 text-purple-500" />;
      case 'email_open': return <Mail className="h-4 w-4 text-orange-500" />;
      case 'email_click': return <Mail className="h-4 w-4 text-yellow-500" />;
      case 'cart_add': return <ShoppingCart className="h-4 w-4 text-indigo-500" />;
      case 'cart_abandon': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'search': return <Search className="h-4 w-4 text-gray-500" />;
      case 'download': return <Download className="h-4 w-4 text-blue-500" />;
      case 'video_view': return <Video className="h-4 w-4 text-red-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getContentTypeIcon = (contentType) => {
    switch (contentType) {
      case 'email': return <Mail className="h-4 w-4 text-blue-500" />;
      case 'ad_creative': return <Target className="h-4 w-4 text-green-500" />;
      case 'landing_page': return <Globe className="h-4 w-4 text-purple-500" />;
      case 'product_recommendation': return <Star className="h-4 w-4 text-yellow-500" />;
      case 'notification': return <Bell className="h-4 w-4 text-orange-500" />;
      case 'banner': return <Image className="h-4 w-4 text-indigo-500" />;
      default: return <File className="h-4 w-4 text-gray-500" />;
    }
  };

  const getSegmentTypeIcon = (segmentType) => {
    switch (segmentType) {
      case 'demographic': return <Users className="h-4 w-4 text-blue-500" />;
      case 'behavioral': return <Activity className="h-4 w-4 text-green-500" />;
      case 'psychographic': return <Brain className="h-4 w-4 text-purple-500" />;
      case 'geographic': return <Globe className="h-4 w-4 text-orange-500" />;
      case 'technological': return <Cpu className="h-4 w-4 text-indigo-500" />;
      case 'custom': return <Settings className="h-4 w-4 text-gray-500" />;
      default: return <Target className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleCreateProfile = async (profileData) => {
    try {
      await api.post('/api/personalization/profiles', profileData);
      await fetchData(); // Refresh data
      setShowCreateProfileDialog(false);
    } catch (err) {
      console.error("Failed to create profile:", err);
    }
  };

  const handleCreateSegment = async (segmentData) => {
    try {
      await api.post('/api/personalization/segments', segmentData);
      await fetchData(); // Refresh data
      setShowCreateSegmentDialog(false);
    } catch (err) {
      console.error("Failed to create segment:", err);
    }
  };

  const handlePersonalizeContent = async (personalizationData) => {
    try {
      await api.post('/api/personalization/content', personalizationData);
      await fetchData(); // Refresh data
      setShowPersonalizeDialog(false);
    } catch (err) {
      console.error("Failed to personalize content:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Real-Time Personalization...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-green-50 to-blue-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-green-800 flex items-center">
              <Brain className="mr-2 h-6 w-6 text-green-500" /> Real-Time Personalization Engine
            </CardTitle>
            <CardDescription className="text-gray-700">
              Dynamic content, audience segmentation, and behavioral targeting
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showPersonalizeDialog} onOpenChange={setShowPersonalizeDialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-green-600 border-green-300 hover:bg-green-50">
                  <Zap className="mr-2 h-4 w-4" /> Personalize
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Personalize Content</DialogTitle>
                  <DialogDescription>
                    Create personalized content for a specific user
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="user-id">User ID</Label>
                    <Input id="user-id" placeholder="Enter user ID" />
                  </div>
                  <div>
                    <Label htmlFor="content-type">Content Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select content type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="email">Email</SelectItem>
                        <SelectItem value="ad_creative">Ad Creative</SelectItem>
                        <SelectItem value="landing_page">Landing Page</SelectItem>
                        <SelectItem value="product_recommendation">Product Recommendation</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button className="w-full" onClick={() => handlePersonalizeContent({})}>
                    <Brain className="mr-2 h-4 w-4" /> Personalize Content
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-green-600 border-green-300 hover:bg-green-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreateProfileDialog} onOpenChange={setShowCreateProfileDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-green-600 hover:bg-green-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Profile
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create User Profile</DialogTitle>
                  <DialogDescription>
                    Create a new user profile for personalization
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="profile-user-id">User ID</Label>
                    <Input id="profile-user-id" placeholder="Enter user ID" />
                  </div>
                  <div>
                    <Label htmlFor="profile-demographics">Demographics</Label>
                    <Textarea id="profile-demographics" placeholder="Enter demographic data (JSON)" />
                  </div>
                  <Button className="w-full" onClick={() => handleCreateProfile({})}>
                    <UserPlus className="mr-2 h-4 w-4" /> Create Profile
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Personalization Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-green-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-green-500" /> Personalization Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {dashboardData?.user_statistics?.total_users || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Users</div>
              <div className="text-sm text-gray-600">User profiles</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {dashboardData?.segment_statistics?.active_segments || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Active Segments</div>
              <div className="text-sm text-gray-600">Audience segments</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {dashboardData?.behavioral_statistics?.total_events || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Behavioral Events</div>
              <div className="text-sm text-gray-600">Tracked events</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {dashboardData?.personalization_statistics?.total_personalized_content || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Personalized Content</div>
              <div className="text-sm text-gray-600">Content items</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Personalization Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-green-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="profiles" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Profiles</TabsTrigger>
          <TabsTrigger value="segments" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Segments</TabsTrigger>
          <TabsTrigger value="content" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Content</TabsTrigger>
          <TabsTrigger value="behavior" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Behavior</TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* User Engagement */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                  <Users className="mr-2 h-5 w-5 text-blue-500" /> User Engagement
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userProfiles.slice(0, 3).map((profile) => (
                    <div key={profile.user_id} className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <User className="h-5 w-5 text-blue-500 mr-2" />
                          <span className="font-semibold">{profile.user_id}</span>
                        </div>
                        <Badge className={`${getEngagementBadge(profile.engagement_score)} text-white`}>
                          {getEngagementLevel(profile.engagement_score)}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">
                        Age: {profile.demographics.age} • {profile.demographics.gender} • {profile.demographics.location}
                      </div>
                      <div className="text-sm text-gray-600">
                        Segments: {profile.segments.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Active Segments */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                  <Target className="mr-2 h-5 w-5 text-green-500" /> Active Segments
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {audienceSegments.slice(0, 3).map((segment) => (
                    <div key={segment.segment_id} className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          {getSegmentTypeIcon(segment.segment_type)}
                          <span className="ml-2 font-semibold">{segment.name}</span>
                        </div>
                        <Badge variant="outline">{segment.size} users</Badge>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">{segment.description}</div>
                      <div className="text-sm text-gray-600">
                        Type: {segment.segment_type.replace('_', ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Profiles Tab */}
        <TabsContent value="profiles">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-green-800">User Profiles</CardTitle>
              <CardDescription>Manage user profiles and behavioral data</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {userProfiles.map((profile) => (
                  <Card key={profile.user_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{profile.user_id}</div>
                          <div className="text-sm text-gray-600">
                            {profile.demographics.age} • {profile.demographics.gender} • {profile.demographics.location}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getEngagementBadge(profile.engagement_score)} text-white`}>
                          {getEngagementLevel(profile.engagement_score)}
                        </Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Engagement Score</div>
                        <div className="text-lg font-semibold">{formatPercentage(profile.engagement_score)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Behaviors</div>
                        <div className="text-lg font-semibold">{profile.behaviors.length}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Segments</div>
                        <div className="text-lg font-semibold">{profile.segments.length}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Last Updated</div>
                        <div className="text-lg font-semibold">{formatDate(profile.last_updated)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Segments:</div>
                      <div className="flex flex-wrap gap-1">
                        {profile.segments.map((segment, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {segment.replace('_', ' ')}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Preferences:</div>
                      <div className="text-sm text-gray-600">
                        Click: {Object.keys(profile.preferences.click_preferences || {}).join(', ')} • 
                        Convert: {Object.keys(profile.preferences.conversion_preferences || {}).join(', ')}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Segments Tab */}
        <TabsContent value="segments">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-green-800">Audience Segments</CardTitle>
              <CardDescription>Create and manage audience segments for targeting</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {audienceSegments.map((segment) => (
                  <Card key={segment.segment_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getSegmentTypeIcon(segment.segment_type)}
                        <div>
                          <div className="font-semibold text-lg">{segment.name}</div>
                          <div className="text-sm text-gray-600">{segment.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{segment.size} users</Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Type</div>
                        <div className="text-lg font-semibold">{segment.segment_type.replace('_', ' ')}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Size</div>
                        <div className="text-lg font-semibold">{segment.size} users</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="text-lg font-semibold">{formatDate(segment.created_at)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Criteria:</div>
                      <div className="text-sm text-gray-600">
                        {Object.keys(segment.criteria).map(key => 
                          `${key}: ${JSON.stringify(segment.criteria[key])}`
                        ).join(' • ')}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Content Tab */}
        <TabsContent value="content">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-green-800">Personalized Content</CardTitle>
              <CardDescription>View and manage personalized content for users</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {personalizedContent.map((content) => (
                  <Card key={content.content_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getContentTypeIcon(content.content_type)}
                        <div>
                          <div className="font-semibold text-lg">
                            {content.content_type.replace('_', ' ')}
                          </div>
                          <div className="text-sm text-gray-600">User: {content.user_id}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{content.segment_id}</Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Content Type</div>
                        <div className="text-lg font-semibold">{content.content_type}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">User</div>
                        <div className="text-lg font-semibold">{content.user_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="text-lg font-semibold">{formatDate(content.created_at)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Personalization Rules:</div>
                      <div className="text-sm text-gray-600">
                        {content.personalization_rules.map((rule, index) => 
                          `${rule.type}: ${rule.applied ? 'Applied' : 'Not Applied'}`
                        ).join(' • ')}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Content Data:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {JSON.stringify(content.content_data, null, 2)}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Behavior Tab */}
        <TabsContent value="behavior">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-green-800">Behavioral Events</CardTitle>
              <CardDescription>Track and analyze user behavioral events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {behavioralEvents.map((event) => (
                  <Card key={event.event_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getEventIcon(event.event_type)}
                        <div>
                          <div className="font-semibold text-lg">
                            {event.event_type.replace('_', ' ')}
                          </div>
                          <div className="text-sm text-gray-600">User: {event.user_id}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{event.session_id}</Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Event Type</div>
                        <div className="text-lg font-semibold">{event.event_type}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">User</div>
                        <div className="text-lg font-semibold">{event.user_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Session</div>
                        <div className="text-lg font-semibold">{event.session_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Timestamp</div>
                        <div className="text-lg font-semibold">{formatDateTime(event.timestamp)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Properties:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {JSON.stringify(event.properties, null, 2)}
                      </div>
                    </div>
                    
                    {event.page_url && (
                      <div className="text-sm text-gray-600">
                        Page: {event.page_url}
                      </div>
                    )}
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
              <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Personalization Analytics
              </CardTitle>
              <CardDescription>Analyze personalization performance and user engagement</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Engagement Metrics */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-green-600">Engagement Metrics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {formatPercentage(dashboardData?.user_statistics?.engagement_rate || 0)}
                          </div>
                          <div className="text-sm text-gray-600">Engagement Rate</div>
                        </div>
                        <TrendingUp className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {dashboardData?.behavioral_statistics?.events_per_user || 0}
                          </div>
                          <div className="text-sm text-gray-600">Events per User</div>
                        </div>
                        <Activity className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-purple-600">
                            {formatPercentage(dashboardData?.personalization_statistics?.personalization_rate || 0)}
                          </div>
                          <div className="text-sm text-gray-600">Personalization Rate</div>
                        </div>
                        <Brain className="h-8 w-8 text-purple-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Segment Performance */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Segment Performance</h3>
                  <div className="space-y-3">
                    {audienceSegments.slice(0, 3).map((segment) => (
                      <div key={segment.segment_id} className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {getSegmentTypeIcon(segment.segment_type)}
                            <span className="ml-2 font-semibold">{segment.name}</span>
                          </div>
                          <Badge variant="outline">{segment.size} users</Badge>
                        </div>
                        <div className="text-sm text-gray-600">
                          Type: {segment.segment_type.replace('_', ' ')} • 
                          Created: {formatDate(segment.created_at)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Behavioral Insights */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-orange-600">Behavioral Insights</h3>
                  <div className="space-y-3">
                    <div className="p-4 bg-orange-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Eye className="h-5 w-5 text-orange-500 mr-2" />
                        <span className="font-semibold">Top Event Types</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Page views: 45% • Clicks: 30% • Conversions: 15% • Email opens: 10%
                      </div>
                    </div>
                    
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Target className="h-5 w-5 text-yellow-500 mr-2" />
                        <span className="font-semibold">Engagement Patterns</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Peak engagement: 2-4 PM • High-value users: 25% • Mobile users: 60%
                      </div>
                    </div>
                    
                    <div className="p-4 bg-indigo-50 rounded-lg">
                      <div className="flex items-center mb-2">
                        <Brain className="h-5 w-5 text-indigo-500 mr-2" />
                        <span className="font-semibold">Personalization Impact</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        Personalized content: 40% higher engagement • Segment targeting: 25% better conversion
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

export default RealTimePersonalizationDashboard;
