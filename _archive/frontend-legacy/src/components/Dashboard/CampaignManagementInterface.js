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
  Plus, 
  Play, 
  Pause, 
  Archive, 
  Settings, 
  Upload, 
  Image, 
  Video, 
  FileText,
  Target,
  TrendingUp,
  Users,
  DollarSign,
  Calendar,
  BarChart3,
  PieChart,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Download,
  Edit,
  Trash2,
  Eye,
  MousePointer,
  Zap
} from 'lucide-react';
import api from '@/services/api';
import ABTestingInterface from '@/components/Dashboard/ABTestingInterface';

const CampaignManagementInterface = () => {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [assets, setAssets] = useState([]);
  const [abTests, setAbTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [campaignsData, templatesData, assetsData, abTestsData] = await Promise.all([
        api.get(`/api/campaigns?client_id=${clientId}`),
        api.get('/api/campaigns/templates'),
        api.get(`/api/campaigns/assets?client_id=${clientId}`),
        api.get(`/api/campaigns/ab-tests?client_id=${clientId}`)
      ]);
      
      setCampaigns(campaignsData.data.campaigns || []);
      setTemplates(templatesData.data || []);
      setAssets(assetsData.data.assets || []);
      setAbTests(abTestsData.data.ab_tests || []);
    } catch (err) {
      console.error("Failed to fetch campaign data:", err);
      setError("Failed to load campaign data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'paused': return 'bg-yellow-500';
      case 'draft': return 'bg-gray-500';
      case 'completed': return 'bg-blue-500';
      case 'archived': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Play className="h-4 w-4" />;
      case 'paused': return <Pause className="h-4 w-4" />;
      case 'draft': return <Edit className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      case 'archived': return <Archive className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  const handleLaunchCampaign = async (campaignId) => {
    try {
      await api.post(`/api/campaigns/${campaignId}/launch?client_id=${clientId}`);
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to launch campaign:", err);
    }
  };

  const handlePauseCampaign = async (campaignId) => {
    try {
      await api.post(`/api/campaigns/${campaignId}/pause?client_id=${clientId}`);
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to pause campaign:", err);
    }
  };

  const handleArchiveCampaign = async (campaignId) => {
    try {
      await api.post(`/api/campaigns/${campaignId}/archive?client_id=${clientId}`);
      await fetchData(); // Refresh data
    } catch (err) {
      console.error("Failed to archive campaign:", err);
    }
  };

  const handleFileUpload = async (file, assetType) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('asset_type', assetType);
      
      await api.post(`/api/campaigns/assets/upload?client_id=${clientId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      await fetchData(); // Refresh data
      setShowUploadDialog(false);
    } catch (err) {
      console.error("Failed to upload asset:", err);
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Campaign Management...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertCircle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-purple-50 to-pink-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-purple-800 flex items-center">
              <Target className="mr-2 h-6 w-6 text-purple-500" /> Campaign Management Interface
            </CardTitle>
            <CardDescription className="text-gray-700">
              Create, manage, and optimize your marketing campaigns with AI-powered insights
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={fetchData} variant="outline" className="flex items-center text-purple-600 border-purple-300 hover:bg-purple-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="flex items-center text-white bg-purple-600 hover:bg-purple-700">
                  <Plus className="mr-2 h-4 w-4" /> Create Campaign
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create New Campaign</DialogTitle>
                  <DialogDescription>
                    Choose a template or create a custom campaign from scratch
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {templates.map((template) => (
                      <Card key={template.template_id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                        <CardHeader className="pb-2">
                          <CardTitle className="text-lg">{template.name}</CardTitle>
                          <CardDescription>{template.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="text-sm text-gray-600">
                            Type: {template.template_data.campaign_type}
                          </div>
                          <div className="text-sm text-gray-600">
                            Budget: {formatCurrency(template.template_data.budget.daily_budget)}/day
                          </div>
                        </CardContent>
                        <CardFooter>
                          <Button variant="outline" size="sm" className="w-full">
                            Use Template
                          </Button>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                  <div className="pt-4 border-t">
                    <Button variant="outline" className="w-full">
                      Create Custom Campaign
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
      </Card>

      {/* Main Campaign Management Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5 bg-purple-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="campaigns" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Campaigns</TabsTrigger>
          <TabsTrigger value="templates" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Templates</TabsTrigger>
          <TabsTrigger value="assets" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Assets</TabsTrigger>
          <TabsTrigger value="testing" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">A/B Testing</TabsTrigger>
          <TabsTrigger value="optimization" className="data-[state=active]:bg-purple-600 data-[state=active]:text-white transition-all">Optimization</TabsTrigger>
        </TabsList>

        {/* Campaigns Tab */}
        <TabsContent value="campaigns">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Campaign List */}
            <div className="lg:col-span-2">
              <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                    <BarChart3 className="mr-2 h-5 w-5 text-purple-500" /> Active Campaigns
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {campaigns.map((campaign) => (
                      <Card key={campaign.campaign_id} className="p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <h3 className="font-semibold text-lg">{campaign.name}</h3>
                            <p className="text-gray-600 text-sm">{campaign.description}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={`${getStatusColor(campaign.status)} text-white`}>
                              {getStatusIcon(campaign.status)}
                              <span className="ml-1">{campaign.status}</span>
                            </Badge>
                            <Button variant="outline" size="sm">
                              <Settings className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                          <div>
                            <span className="text-gray-600">Type:</span>
                            <span className="ml-2 font-semibold">{campaign.campaign_type}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Budget:</span>
                            <span className="ml-2 font-semibold">{formatCurrency(campaign.budget.daily_budget)}/day</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Impressions:</span>
                            <span className="ml-2 font-semibold">{formatNumber(campaign.performance.impressions)}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Clicks:</span>
                            <span className="ml-2 font-semibold">{formatNumber(campaign.performance.clicks)}</span>
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div className="text-sm text-gray-500">
                            Created: {new Date(campaign.created_at).toLocaleDateString()}
                          </div>
                          <div className="flex items-center space-x-1">
                            {campaign.status === 'draft' && (
                              <Button size="sm" onClick={() => handleLaunchCampaign(campaign.campaign_id)}>
                                <Play className="mr-1 h-3 w-3" /> Launch
                              </Button>
                            )}
                            {campaign.status === 'active' && (
                              <Button size="sm" variant="outline" onClick={() => handlePauseCampaign(campaign.campaign_id)}>
                                <Pause className="mr-1 h-3 w-3" /> Pause
                              </Button>
                            )}
                            <Button size="sm" variant="outline" onClick={() => handleArchiveCampaign(campaign.campaign_id)}>
                              <Archive className="mr-1 h-3 w-3" /> Archive
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Campaign Performance Summary */}
            <div>
              <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                    <TrendingUp className="mr-2 h-5 w-5 text-green-500" /> Performance Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <div className="flex items-center">
                        <Eye className="h-5 w-5 text-green-500 mr-2" />
                        <span className="font-medium">Total Impressions</span>
                      </div>
                      <span className="text-2xl font-bold text-green-600">
                        {formatNumber(campaigns.reduce((sum, c) => sum + c.performance.impressions, 0))}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                      <div className="flex items-center">
                        <MousePointer className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="font-medium">Total Clicks</span>
                      </div>
                      <span className="text-2xl font-bold text-blue-600">
                        {formatNumber(campaigns.reduce((sum, c) => sum + c.performance.clicks, 0))}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                      <div className="flex items-center">
                        <Target className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="font-medium">Total Conversions</span>
                      </div>
                      <span className="text-2xl font-bold text-purple-600">
                        {formatNumber(campaigns.reduce((sum, c) => sum + c.performance.conversions, 0))}
                      </span>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                      <div className="flex items-center">
                        <DollarSign className="h-5 w-5 text-orange-500 mr-2" />
                        <span className="font-medium">Total Revenue</span>
                      </div>
                      <span className="text-2xl font-bold text-orange-600">
                        {formatCurrency(campaigns.reduce((sum, c) => sum + c.performance.revenue, 0))}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800">Campaign Templates</CardTitle>
              <CardDescription>Choose from pre-built templates for quick campaign creation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <Card key={template.template_id} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      <CardDescription>{template.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Type:</span>
                          <span className="font-semibold">{template.template_data.campaign_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Budget:</span>
                          <span className="font-semibold">{formatCurrency(template.template_data.budget.daily_budget)}/day</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Goal:</span>
                          <span className="font-semibold">{template.template_data.optimization_goal}</span>
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button variant="outline" size="sm" className="w-full">
                        Use Template
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Assets Tab */}
        <TabsContent value="assets">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-purple-800">Creative Assets</CardTitle>
                <CardDescription>Manage your creative assets for campaigns</CardDescription>
              </div>
              <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
                <DialogTrigger asChild>
                  <Button className="flex items-center text-white bg-purple-600 hover:bg-purple-700">
                    <Upload className="mr-2 h-4 w-4" /> Upload Asset
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Upload Creative Asset</DialogTitle>
                    <DialogDescription>
                      Upload images, videos, or other creative assets for your campaigns
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="file">Select File</Label>
                      <Input id="file" type="file" accept="image/*,video/*" />
                    </div>
                    <div>
                      <Label htmlFor="asset-type">Asset Type</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select asset type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="image">Image</SelectItem>
                          <SelectItem value="video">Video</SelectItem>
                          <SelectItem value="audio">Audio</SelectItem>
                          <SelectItem value="document">Document</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <Button className="w-full" disabled={uploading}>
                      {uploading ? 'Uploading...' : 'Upload Asset'}
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {assets.map((asset) => (
                  <Card key={asset.asset_id} className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center">
                        {asset.asset_type === 'image' && <Image className="h-5 w-5 text-blue-500 mr-2" />}
                        {asset.asset_type === 'video' && <Video className="h-5 w-5 text-purple-500 mr-2" />}
                        {asset.asset_type === 'document' && <FileText className="h-5 w-5 text-green-500 mr-2" />}
                        <span className="font-semibold">{asset.file_name}</span>
                      </div>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      Size: {(asset.file_size / 1024 / 1024).toFixed(2)} MB
                    </div>
                    {asset.asset_type === 'image' && asset.thumbnail_url && (
                      <div className="w-full h-32 bg-gray-100 rounded flex items-center justify-center">
                        <Image className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                    <div className="text-xs text-gray-500 mt-2">
                      Uploaded: {new Date(asset.created_at).toLocaleDateString()}
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* A/B Testing Tab */}
        <TabsContent value="testing">
          <ABTestingInterface />
        </TabsContent>

        {/* Optimization Tab */}
        <TabsContent value="optimization">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-purple-800 flex items-center">
                <Zap className="mr-2 h-5 w-5 text-yellow-500" /> AI-Powered Optimization
              </CardTitle>
              <CardDescription>Automated campaign optimization recommendations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
                <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-green-800">Budget Optimization</h4>
                  <p className="text-green-700 mt-1">
                    Increase daily budget for "Summer Sale 2024" campaign by 25% to capture more high-intent traffic.
                    Expected ROI improvement: 15-20%.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-green-600 border-green-300 hover:bg-green-50">
                    Apply Optimization
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <AlertCircle className="h-6 w-6 text-blue-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-blue-800">Audience Expansion</h4>
                  <p className="text-blue-700 mt-1">
                    Add lookalike audiences based on your top 1% converters. This could increase reach by 30% while maintaining quality.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-blue-600 border-blue-300 hover:bg-blue-50">
                    Expand Audience
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <TrendingUp className="h-6 w-6 text-purple-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-purple-800">Creative Refresh</h4>
                  <p className="text-purple-700 mt-1">
                    Replace underperforming creatives with top performers. Current CTR can be improved by 12% with better creative rotation.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-purple-600 border-purple-300 hover:bg-purple-50">
                    Refresh Creatives
                  </Button>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <DollarSign className="h-6 w-6 text-orange-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-orange-800">Bid Strategy Optimization</h4>
                  <p className="text-orange-700 mt-1">
                    Switch to Target ROAS bidding for better performance. Expected improvement: 8-12% in conversion efficiency.
                  </p>
                  <Button variant="outline" size="sm" className="mt-2 text-orange-600 border-orange-300 hover:bg-orange-50">
                    Optimize Bidding
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CampaignManagementInterface;
