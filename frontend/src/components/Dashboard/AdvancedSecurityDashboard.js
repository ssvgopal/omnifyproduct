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
  Shield, 
  Lock,
  Key,
  Eye,
  EyeOff,
  UserCheck,
  AlertTriangle,
  CheckCircle,
  XCircle,
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
  Settings,
  Plus,
  Edit,
  Trash2,
  Clock,
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
  Unlock,
  User,
  UserPlus,
  UserMinus,
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

const AdvancedSecurityDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [policies, setPolicies] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreatePolicyDialog, setShowCreatePolicyDialog] = useState(false);
  const [showCreateProfileDialog, setShowCreateProfileDialog] = useState(false);
  const [showMFAEnableDialog, setShowMFAEnableDialog] = useState(false);
  const [showSSODialog, setShowSSODialog] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [mfaQRCode, setMfaQRCode] = useState(null);
  
  const organizationId = "demo-org-123"; // Mock organization ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardData, policiesData, profilesData, auditLogsData] = await Promise.all([
        api.get(`/api/security/dashboard/${organizationId}`),
        api.get('/api/security/policies'),
        api.get('/api/security/profiles'),
        api.get('/api/security/audit-logs')
      ]);
      
      setDashboardData(dashboardData.data);
      setPolicies(policiesData.data || []);
      setProfiles(profilesData.data || []);
      setAuditLogs(auditLogsData.data.logs || []);
      
    } catch (err) {
      console.error("Failed to fetch security data:", err);
      setError("Failed to load security data. Please try again.");
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

  const getComplianceStandardIcon = (standard) => {
    switch (standard) {
      case 'gdpr': return <Shield className="h-5 w-5 text-blue-500" />;
      case 'soc2': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'hipaa': return <Lock className="h-5 w-5 text-red-500" />;
      case 'pci_dss': return <CreditCard className="h-5 w-5 text-purple-500" />;
      case 'iso27001': return <Award className="h-5 w-5 text-yellow-500" />;
      case 'ccpa': return <FileText className="h-5 w-5 text-orange-500" />;
      default: return <Shield className="h-5 w-5 text-gray-500" />;
    }
  };

  const getComplianceStandardColor = (standard) => {
    switch (standard) {
      case 'gdpr': return 'text-blue-600';
      case 'soc2': return 'text-green-600';
      case 'hipaa': return 'text-red-600';
      case 'pci_dss': return 'text-purple-600';
      case 'iso27001': return 'text-yellow-600';
      case 'ccpa': return 'text-orange-600';
      default: return 'text-gray-600';
    }
  };

  const getComplianceStandardBadge = (standard) => {
    switch (standard) {
      case 'gdpr': return 'bg-blue-500';
      case 'soc2': return 'bg-green-500';
      case 'hipaa': return 'bg-red-500';
      case 'pci_dss': return 'bg-purple-500';
      case 'iso27001': return 'bg-yellow-500';
      case 'ccpa': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getSecurityLevelColor = (level) => {
    switch (level) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getSecurityLevelBadge = (level) => {
    switch (level) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getEventTypeIcon = (eventType) => {
    switch (eventType) {
      case 'login': return <UserCheck className="h-4 w-4 text-green-500" />;
      case 'logout': return <UserX className="h-4 w-4 text-red-500" />;
      case 'password_change': return <Key className="h-4 w-4 text-blue-500" />;
      case 'mfa_enable': return <Shield className="h-4 w-4 text-purple-500" />;
      case 'mfa_disable': return <Shield className="h-4 w-4 text-orange-500" />;
      case 'permission_change': return <Settings className="h-4 w-4 text-indigo-500" />;
      case 'data_access': return <Eye className="h-4 w-4 text-cyan-500" />;
      case 'data_export': return <Download className="h-4 w-4 text-teal-500" />;
      case 'data_delete': return <Trash2 className="h-4 w-4 text-red-500" />;
      case 'configuration_change': return <Settings className="h-4 w-4 text-gray-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleCreatePolicy = async (policyData) => {
    try {
      await api.post('/api/security/policies', policyData);
      await fetchData(); // Refresh data
      setShowCreatePolicyDialog(false);
    } catch (err) {
      console.error("Failed to create policy:", err);
    }
  };

  const handleCreateProfile = async (profileData) => {
    try {
      await api.post('/api/security/profiles', profileData);
      await fetchData(); // Refresh data
      setShowCreateProfileDialog(false);
    } catch (err) {
      console.error("Failed to create profile:", err);
    }
  };

  const handleEnableMFA = async (userData) => {
    try {
      const response = await api.post('/api/security/mfa/enable', userData);
      setMfaQRCode(response.data.qr_code);
      setShowMFAEnableDialog(false);
    } catch (err) {
      console.error("Failed to enable MFA:", err);
    }
  };

  const handleConfigureSSO = async (ssoData) => {
    try {
      await api.post('/api/security/sso/saml', ssoData);
      await fetchData(); // Refresh data
      setShowSSODialog(false);
    } catch (err) {
      console.error("Failed to configure SSO:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Advanced Security Features...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-red-50 to-orange-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-red-800 flex items-center">
              <Shield className="mr-2 h-6 w-6 text-red-500" /> Advanced Security Features
            </CardTitle>
            <CardDescription className="text-gray-700">
              SSO, advanced authentication, and compliance (GDPR, SOC2, HIPAA)
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Dialog open={showSSODialog} onOpenChange={setShowSSODialog}>
              <DialogTrigger asChild>
                <Button variant="outline" className="flex items-center text-red-600 border-red-300 hover:bg-red-50">
                  <Globe className="mr-2 h-4 w-4" /> SSO
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Configure SSO</DialogTitle>
                  <DialogDescription>
                    Set up Single Sign-On integration
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="sso-type">SSO Type</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select SSO type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="saml">SAML</SelectItem>
                        <SelectItem value="oidc">OpenID Connect</SelectItem>
                        <SelectItem value="oauth2">OAuth2</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="entity-id">Entity ID</Label>
                    <Input id="entity-id" placeholder="Enter entity ID" />
                  </div>
                  <div>
                    <Label htmlFor="sso-url">SSO URL</Label>
                    <Input id="sso-url" placeholder="Enter SSO URL" />
                  </div>
                  <Button className="w-full" onClick={() => handleConfigureSSO({})}>
                    <Globe className="mr-2 h-4 w-4" /> Configure SSO
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
            <Button onClick={fetchData} variant="outline" className="flex items-center text-red-600 border-red-300 hover:bg-red-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreatePolicyDialog} onOpenChange={setShowCreatePolicyDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-red-600 hover:bg-red-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Policy
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Security Policy</DialogTitle>
                  <DialogDescription>
                    Define security requirements and compliance standards
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="policy-name">Policy Name</Label>
                    <Input id="policy-name" placeholder="Enter policy name" />
                  </div>
                  <div>
                    <Label htmlFor="policy-description">Description</Label>
                    <Textarea id="policy-description" placeholder="Enter policy description" />
                  </div>
                  <div>
                    <Label htmlFor="compliance-standards">Compliance Standards</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select standards" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gdpr">GDPR</SelectItem>
                        <SelectItem value="soc2">SOC2</SelectItem>
                        <SelectItem value="hipaa">HIPAA</SelectItem>
                        <SelectItem value="pci_dss">PCI DSS</SelectItem>
                        <SelectItem value="iso27001">ISO 27001</SelectItem>
                        <SelectItem value="ccpa">CCPA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button className="w-full" onClick={() => handleCreatePolicy({})}>
                    <Shield className="mr-2 h-4 w-4" /> Create Policy
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Security Summary */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-red-800 flex items-center">
            <Activity className="mr-2 h-5 w-5 text-red-500" /> Security Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">
                {dashboardData?.security_statistics?.total_users || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Total Users</div>
              <div className="text-sm text-gray-600">Security profiles</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {dashboardData?.security_statistics?.mfa_enabled_users || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">MFA Enabled</div>
              <div className="text-sm text-gray-600">Multi-factor authentication</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {formatPercentage(dashboardData?.security_statistics?.mfa_adoption_rate || 0)}
              </div>
              <div className="text-lg font-semibold text-gray-800">MFA Adoption</div>
              <div className="text-sm text-gray-600">Security adoption rate</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600 mb-2">
                {dashboardData?.security_statistics?.locked_accounts || 0}
              </div>
              <div className="text-lg font-semibold text-gray-800">Locked Accounts</div>
              <div className="text-sm text-gray-600">Security violations</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Security Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-red-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="policies" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Policies</TabsTrigger>
          <TabsTrigger value="profiles" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Profiles</TabsTrigger>
          <TabsTrigger value="mfa" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">MFA</TabsTrigger>
          <TabsTrigger value="audit" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Audit</TabsTrigger>
          <TabsTrigger value="compliance" className="data-[state=active]:bg-red-600 data-[state=active]:text-white transition-all">Compliance</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Security Policies */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                  <Shield className="mr-2 h-5 w-5 text-blue-500" /> Security Policies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {policies.slice(0, 5).map((policy) => (
                    <div key={policy.policy_id} className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <Shield className="h-5 w-5 text-blue-500 mr-2" />
                          <span className="font-semibold">{policy.name}</span>
                        </div>
                        <Badge variant="outline">{policy.compliance_standards.length} standards</Badge>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">{policy.description}</div>
                      <div className="flex flex-wrap gap-1">
                        {policy.compliance_standards.map((standard) => (
                          <Badge key={standard} className={`${getComplianceStandardBadge(standard)} text-white text-xs`}>
                            {standard.toUpperCase()}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Recent Audit Logs */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-green-500" /> Recent Audit Logs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {auditLogs.slice(0, 5).map((log) => (
                      <div key={log.log_id} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {getEventTypeIcon(log.event_type)}
                        <div className="flex-1">
                          <div className="font-medium text-sm">{log.event_type.replace('_', ' ')}</div>
                          <div className="text-xs text-gray-600">
                            {log.user_id} • {formatDateTime(log.timestamp)}
                          </div>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {log.resource_type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Policies Tab */}
        <TabsContent value="policies">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800">Security Policies</CardTitle>
              <CardDescription>Manage security policies and compliance standards</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {policies.map((policy) => (
                  <Card key={policy.policy_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Shield className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{policy.name}</div>
                          <div className="text-sm text-gray-600">{policy.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{policy.compliance_standards.length} standards</Badge>
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
                        <div className="text-gray-600">Compliance Standards</div>
                        <div className="text-lg font-semibold">{policy.compliance_standards.length}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Password Policy</div>
                        <div className="text-lg font-semibold">
                          {policy.password_policy.min_length || 8} chars min
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Created</div>
                        <div className="text-lg font-semibold">{formatDate(policy.created_at)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Compliance Standards:</div>
                      <div className="flex flex-wrap gap-1">
                        {policy.compliance_standards.map((standard) => (
                          <Badge key={standard} className={`${getComplianceStandardBadge(standard)} text-white`}>
                            {getComplianceStandardIcon(standard)}
                            <span className="ml-1">{standard.toUpperCase()}</span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Password Policy:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        Min Length: {policy.password_policy.min_length || 8} • 
                        Uppercase: {policy.password_policy.require_uppercase ? 'Yes' : 'No'} • 
                        Digits: {policy.password_policy.require_digits ? 'Yes' : 'No'} • 
                        Special: {policy.password_policy.require_special ? 'Yes' : 'No'}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Profiles Tab */}
        <TabsContent value="profiles">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800">User Security Profiles</CardTitle>
              <CardDescription>Manage user security settings and authentication</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {profiles.map((profile) => (
                  <Card key={profile.user_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-blue-500" />
                        <div>
                          <div className="font-semibold text-lg">{profile.user_id}</div>
                          <div className="text-sm text-gray-600">
                            Security Level: {profile.security_level}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={`${getSecurityLevelBadge(profile.security_level)} text-white`}>
                          {profile.security_level}
                        </Badge>
                        {profile.mfa_enabled && (
                          <Badge className="bg-green-500 text-white">
                            <CheckCircle className="h-3 w-3 mr-1" /> MFA
                          </Badge>
                        )}
                        <Button size="sm" variant="outline" onClick={() => setSelectedUser(profile)}>
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">MFA Enabled</div>
                        <div className="text-lg font-semibold">
                          {profile.mfa_enabled ? 'Yes' : 'No'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Failed Attempts</div>
                        <div className="text-lg font-semibold">{profile.failed_login_attempts}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Last Login</div>
                        <div className="text-lg font-semibold">
                          {profile.last_login ? formatDateTime(profile.last_login) : 'Never'}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Password Changed</div>
                        <div className="text-lg font-semibold">{formatDate(profile.password_last_changed)}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Compliance Flags:</div>
                      <div className="flex flex-wrap gap-1">
                        {profile.compliance_flags.map((flag) => (
                          <Badge key={flag} className={`${getComplianceStandardBadge(flag)} text-white`}>
                            {getComplianceStandardIcon(flag)}
                            <span className="ml-1">{flag.toUpperCase()}</span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Authentication Methods:</div>
                      <div className="flex flex-wrap gap-1">
                        {profile.authentication_methods.map((method) => (
                          <Badge key={method} variant="outline" className="text-xs">
                            {method.replace('_', ' ')}
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

        {/* MFA Tab */}
        <TabsContent value="mfa">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800">Multi-Factor Authentication</CardTitle>
              <CardDescription>Manage MFA settings and user authentication</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* MFA Statistics */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-red-600">MFA Statistics</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-red-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-red-600">
                            {dashboardData?.security_statistics?.mfa_enabled_users || 0}
                          </div>
                          <div className="text-sm text-gray-600">MFA Enabled Users</div>
                        </div>
                        <Shield className="h-8 w-8 text-red-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-green-600">
                            {formatPercentage(dashboardData?.security_statistics?.mfa_adoption_rate || 0)}
                          </div>
                          <div className="text-sm text-gray-600">Adoption Rate</div>
                        </div>
                        <TrendingUp className="h-8 w-8 text-green-500" />
                      </div>
                    </div>
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-2xl font-bold text-blue-600">
                            {dashboardData?.security_statistics?.total_users || 0}
                          </div>
                          <div className="text-sm text-gray-600">Total Users</div>
                        </div>
                        <Users className="h-8 w-8 text-blue-500" />
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* MFA Methods */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">MFA Methods</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {[
                      { method: 'mfa_totp', name: 'TOTP', description: 'Time-based one-time passwords', icon: <Clock className="h-5 w-5 text-blue-500" /> },
                      { method: 'mfa_sms', name: 'SMS', description: 'SMS-based verification codes', icon: <Smartphone className="h-5 w-5 text-green-500" /> },
                      { method: 'mfa_email', name: 'Email', description: 'Email-based verification codes', icon: <Mail className="h-5 w-5 text-purple-500" /> },
                      { method: 'hardware_token', name: 'Hardware Token', description: 'Physical security tokens', icon: <Key className="h-5 w-5 text-orange-500" /> }
                    ].map((mfaMethod) => (
                      <Card key={mfaMethod.method} className="p-4">
                        <div className="flex items-center mb-3">
                          {mfaMethod.icon}
                          <span className="ml-2 font-semibold">{mfaMethod.name}</span>
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-3">
                          {mfaMethod.description}
                        </div>
                        
                        <Button className="w-full" size="sm">
                          <Settings className="h-3 w-3 mr-1" /> Configure
                        </Button>
                      </Card>
                    ))}
                  </div>
                </div>
                
                {/* MFA QR Code Display */}
                {mfaQRCode && (
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h3 className="font-semibold text-lg mb-4 text-green-600">MFA Setup QR Code</h3>
                    <div className="text-center">
                      <img src={mfaQRCode} alt="MFA QR Code" className="mx-auto mb-4" />
                      <p className="text-sm text-gray-600">
                        Scan this QR code with your authenticator app to set up MFA
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Audit Tab */}
        <TabsContent value="audit">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800">Audit Logs</CardTitle>
              <CardDescription>Security events and compliance audit trail</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {auditLogs.map((log) => (
                  <Card key={log.log_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getEventTypeIcon(log.event_type)}
                        <div>
                          <div className="font-semibold text-lg">{log.event_type.replace('_', ' ')}</div>
                          <div className="text-sm text-gray-600">
                            User: {log.user_id} • Resource: {log.resource_type}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{log.resource_type}</Badge>
                        <Button size="sm" variant="outline">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                      <div>
                        <div className="text-gray-600">Action</div>
                        <div className="text-lg font-semibold">{log.action}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">IP Address</div>
                        <div className="text-lg font-semibold">{log.ip_address}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Timestamp</div>
                        <div className="text-lg font-semibold">{formatDateTime(log.timestamp)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Resource ID</div>
                        <div className="text-lg font-semibold">{log.resource_id}</div>
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Compliance Flags:</div>
                      <div className="flex flex-wrap gap-1">
                        {log.compliance_flags.map((flag) => (
                          <Badge key={flag} className={`${getComplianceStandardBadge(flag)} text-white`}>
                            {getComplianceStandardIcon(flag)}
                            <span className="ml-1">{flag.toUpperCase()}</span>
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-2">Details:</div>
                      <div className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                        {JSON.stringify(log.details, null, 2)}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-red-800 flex items-center">
                <Shield className="mr-2 h-5 w-5 text-blue-500" /> Compliance Management
              </CardTitle>
              <CardDescription>Compliance standards and reporting</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Compliance Standards */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-red-600">Compliance Standards</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { standard: 'gdpr', name: 'GDPR', description: 'General Data Protection Regulation', requirements: 8 },
                      { standard: 'soc2', name: 'SOC 2', description: 'Service Organization Control 2', requirements: 6 },
                      { standard: 'hipaa', name: 'HIPAA', description: 'Health Insurance Portability and Accountability Act', requirements: 5 },
                      { standard: 'pci_dss', name: 'PCI DSS', description: 'Payment Card Industry Data Security Standard', requirements: 4 },
                      { standard: 'iso27001', name: 'ISO 27001', description: 'Information Security Management System', requirements: 7 },
                      { standard: 'ccpa', name: 'CCPA', description: 'California Consumer Privacy Act', requirements: 3 }
                    ].map((compliance) => (
                      <Card key={compliance.standard} className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            {getComplianceStandardIcon(compliance.standard)}
                            <span className="ml-2 font-semibold">{compliance.name}</span>
                          </div>
                          <Badge className={`${getComplianceStandardBadge(compliance.standard)} text-white`}>
                            {compliance.requirements} reqs
                          </Badge>
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-3">
                          {compliance.description}
                        </div>
                        
                        <div className="space-y-2">
                          <Button className="w-full" size="sm">
                            <FileText className="h-3 w-3 mr-1" /> Generate Report
                          </Button>
                          <Button className="w-full" size="sm" variant="outline">
                            <Settings className="h-3 w-3 mr-1" /> Configure
                          </Button>
                        </div>
                      </Card>
                    ))}
                  </div>
                </div>
                
                {/* Compliance Status */}
                <div>
                  <h3 className="font-semibold text-lg mb-4 text-blue-600">Compliance Status</h3>
                  <div className="space-y-3">
                    {[
                      { standard: 'gdpr', status: 'compliant', score: 95, last_audit: '2024-01-15' },
                      { standard: 'soc2', status: 'compliant', score: 92, last_audit: '2024-01-10' },
                      { standard: 'hipaa', status: 'partial', score: 78, last_audit: '2024-01-05' },
                      { standard: 'pci_dss', status: 'compliant', score: 88, last_audit: '2024-01-12' }
                    ].map((status) => (
                      <div key={status.standard} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            {getComplianceStandardIcon(status.standard)}
                            <span className="ml-2 font-semibold capitalize">
                              {status.standard.replace('_', ' ')}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={status.status === 'compliant' ? 'bg-green-500' : 'bg-yellow-500'}>
                              {status.status}
                            </Badge>
                            <span className="text-sm font-semibold">{status.score}%</span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${status.status === 'compliant' ? 'bg-green-600' : 'bg-yellow-600'}`}
                            style={{ width: `${status.score}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          Last audit: {formatDate(status.last_audit)}
                        </div>
                      </div>
                    ))}
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

export default AdvancedSecurityDashboard;
