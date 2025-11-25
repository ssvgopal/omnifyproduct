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
  Link, 
  Music, 
  Play, 
  ShoppingCart, 
  CreditCard,
  Plus,
  Settings,
  BarChart3,
  TrendingUp,
  Users,
  Eye,
  MousePointer,
  DollarSign,
  Package,
  ShoppingBag,
  Zap,
  CheckCircle,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Upload,
  Globe,
  Smartphone,
  Monitor,
  Target,
  Calendar,
  Clock,
  Star,
  Award,
  Activity,
  PieChart,
  LineChart
} from 'lucide-react';
import api from '@/services/api';

const AdvancedPlatformIntegrationsDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [platformOverview, setPlatformOverview] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [products, setProducts] = useState([]);
  const [payments, setPayments] = useState([]);
  const [unifiedAnalytics, setUnifiedAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCampaignDialog, setShowCampaignDialog] = useState(false);
  const [showProductDialog, setShowProductDialog] = useState(false);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState('linkedin_ads');
  
  const clientId = "demo-client-123"; // Mock client ID

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [overviewData, analyticsData] = await Promise.all([
        api.get('/api/platforms/overview'),
        api.get('/api/platforms/analytics/unified?start_date=2024-01-01&end_date=2024-12-31')
      ]);
      
      setPlatformOverview(overviewData.data);
      setUnifiedAnalytics(analyticsData.data);
      
      // Mock data for campaigns, products, payments
      setCampaigns([
        {
          campaign_id: '1',
          platform: 'linkedin_ads',
          name: 'LinkedIn B2B Campaign',
          status: 'active',
          budget: 5000,
          spend: 2500,
          impressions: 125000,
          clicks: 2500,
          conversions: 125
        },
        {
          campaign_id: '2',
          platform: 'tiktok_ads',
          name: 'TikTok Gen Z Campaign',
          status: 'active',
          budget: 3000,
          spend: 1500,
          impressions: 85000,
          clicks: 1700,
          conversions: 85
        },
        {
          campaign_id: '3',
          platform: 'youtube_ads',
          name: 'YouTube Video Campaign',
          status: 'paused',
          budget: 8000,
          spend: 4000,
          impressions: 200000,
          clicks: 4000,
          conversions: 200
        }
      ]);
      
      setProducts([
        {
          product_id: '1',
          title: 'Premium Widget',
          price: 99.99,
          inventory_quantity: 50,
          status: 'active',
          tags: ['featured', 'premium']
        },
        {
          product_id: '2',
          title: 'Basic Widget',
          price: 49.99,
          inventory_quantity: 100,
          status: 'active',
          tags: ['basic', 'popular']
        }
      ]);
      
      setPayments([
        {
          payment_id: '1',
          amount: 99.99,
          currency: 'usd',
          status: 'succeeded',
          description: 'Premium Widget Purchase',
          created_at: '2024-01-15T10:30:00Z'
        },
        {
          payment_id: '2',
          amount: 49.99,
          currency: 'usd',
          status: 'succeeded',
          description: 'Basic Widget Purchase',
          created_at: '2024-01-14T15:45:00Z'
        }
      ]);
      
    } catch (err) {
      console.error("Failed to fetch platform data:", err);
      setError("Failed to load platform integrations. Please try again.");
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
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  const formatNumber = (number) => {
    return new Intl.NumberFormat('en-US').format(number);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'linkedin_ads': return <Link className="h-5 w-5 text-blue-500" />;
      case 'tiktok_ads': return <Music className="h-5 w-5 text-black" />;
      case 'youtube_ads': return <Play className="h-5 w-5 text-red-500" />;
      case 'shopify': return <ShoppingCart className="h-5 w-5 text-green-500" />;
      case 'stripe': return <CreditCard className="h-5 w-5 text-purple-500" />;
      default: return <Globe className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPlatformColor = (platform) => {
    switch (platform) {
      case 'linkedin_ads': return 'bg-blue-500';
      case 'tiktok_ads': return 'bg-black';
      case 'youtube_ads': return 'bg-red-500';
      case 'shopify': return 'bg-green-500';
      case 'stripe': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600';
      case 'paused': return 'text-yellow-600';
      case 'draft': return 'text-gray-600';
      case 'completed': return 'text-blue-600';
      case 'archived': return 'text-red-600';
      case 'succeeded': return 'text-green-600';
      case 'failed': return 'text-red-600';
      case 'pending': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'paused': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'draft': return <AlertTriangle className="h-4 w-4 text-gray-500" />;
      case 'completed': return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'archived': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'succeeded': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      default: return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const handleCreateCampaign = async (campaignData) => {
    try {
      await api.post(`/api/platforms/${selectedPlatform}/campaigns`, campaignData);
      await fetchData(); // Refresh data
      setShowCampaignDialog(false);
    } catch (err) {
      console.error("Failed to create campaign:", err);
    }
  };

  const handleCreateProduct = async (productData) => {
    try {
      await api.post('/api/platforms/shopify/products', productData);
      await fetchData(); // Refresh data
      setShowProductDialog(false);
    } catch (err) {
      console.error("Failed to create product:", err);
    }
  };

  const handleCreatePayment = async (paymentData) => {
    try {
      await api.post('/api/platforms/stripe/payments', paymentData);
      await fetchData(); // Refresh data
      setShowPaymentDialog(false);
    } catch (err) {
      console.error("Failed to create payment:", err);
    }
  };

  if (loading) return <div className="text-center p-8">Loading Advanced Platform Integrations...</div>;
  if (error) return <div className="text-center p-8 text-red-600 flex items-center justify-center"><AlertTriangle className="mr-2"/> {error}</div>;

  return (
    <div className="p-6 space-y-6 bg-gradient-to-br from-green-50 to-blue-100 min-h-screen">
      {/* Header */}
      <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle className="text-2xl font-bold text-green-800 flex items-center">
              <Globe className="mr-2 h-6 w-6 text-green-500" /> Advanced Platform Integrations
            </CardTitle>
            <CardDescription className="text-gray-700">
              LinkedIn Ads, TikTok Ads, YouTube Ads, Shopify, and Stripe integrations
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button onClick={fetchData} variant="outline" className="flex items-center text-green-600 border-green-300 hover:bg-green-50">
              <RefreshCw className="mr-2 h-4 w-4" /> Refresh
            </Button>
            <Button className="flex items-center text-white bg-green-600 hover:bg-green-700">
              <Download className="mr-2 h-4 w-4" /> Export Data
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Platform Overview */}
      {platformOverview && (
        <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-green-800 flex items-center">
              <Globe className="mr-2 h-5 w-5 text-blue-500" /> Platform Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-2">{platformOverview.total_campaigns}</div>
                <div className="text-lg font-semibold text-gray-800">Total Campaigns</div>
                <div className="text-sm text-gray-600">Across all platforms</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{platformOverview.total_products}</div>
                <div className="text-lg font-semibold text-gray-800">Shopify Products</div>
                <div className="text-sm text-gray-600">E-commerce inventory</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">{platformOverview.total_payments}</div>
                <div className="text-lg font-semibold text-gray-800">Stripe Payments</div>
                <div className="text-sm text-gray-600">Payment transactions</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">{platformOverview.initialized_platforms.length}</div>
                <div className="text-lg font-semibold text-gray-800">Active Platforms</div>
                <div className="text-sm text-gray-600">Connected integrations</div>
              </div>
            </div>
            
            {/* Platform Status */}
            <div className="mt-6">
              <h3 className="font-semibold text-lg mb-3">Platform Status</h3>
              <div className="flex flex-wrap gap-2">
                {platformOverview.initialized_platforms.map((platform) => (
                  <Badge key={platform} className={`${getPlatformColor(platform)} text-white`}>
                    {getPlatformIcon(platform)}
                    <span className="ml-1">{platform.replace('_', ' ').toUpperCase()}</span>
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Platform Integrations Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6 bg-green-100 p-1 rounded-lg shadow-sm">
          <TabsTrigger value="overview" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Overview</TabsTrigger>
          <TabsTrigger value="campaigns" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Campaigns</TabsTrigger>
          <TabsTrigger value="products" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Products</TabsTrigger>
          <TabsTrigger value="payments" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Payments</TabsTrigger>
          <TabsTrigger value="analytics" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Analytics</TabsTrigger>
          <TabsTrigger value="settings" className="data-[state=active]:bg-green-600 data-[state=active]:text-white transition-all">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Unified Analytics */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                  <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Unified Analytics
                </CardTitle>
              </CardHeader>
              <CardContent>
                {unifiedAnalytics && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{unifiedAnalytics.campaigns.total_campaigns}</div>
                        <div className="text-sm text-gray-600">Campaigns</div>
                      </div>
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{formatCurrency(unifiedAnalytics.campaigns.total_spend)}</div>
                        <div className="text-sm text-gray-600">Total Spend</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-3 bg-purple-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">{formatCurrency(unifiedAnalytics.products.total_revenue)}</div>
                        <div className="text-sm text-gray-600">Revenue</div>
                      </div>
                      <div className="text-center p-3 bg-orange-50 rounded-lg">
                        <div className="text-2xl font-bold text-orange-600">{formatCurrency(unifiedAnalytics.payments.total_amount)}</div>
                        <div className="text-sm text-gray-600">Payments</div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                  <Activity className="mr-2 h-5 w-5 text-orange-500" /> Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  <div className="space-y-3">
                    {platformOverview?.recent_activity?.slice(0, 5).map((activity, index) => (
                      <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded">
                        {activity.type === 'campaign' && <Target className="h-4 w-4 text-blue-500" />}
                        {activity.type === 'product' && <Package className="h-4 w-4 text-green-500" />}
                        {activity.type === 'payment' && <CreditCard className="h-4 w-4 text-purple-500" />}
                        <div className="flex-1">
                          <div className="font-medium text-sm">
                            {activity.type === 'campaign' && `Campaign: ${activity.data.name}`}
                            {activity.type === 'product' && `Product: ${activity.data.title}`}
                            {activity.type === 'payment' && `Payment: ${formatCurrency(activity.data.amount)}`}
                          </div>
                          <div className="text-xs text-gray-600">
                            {new Date(activity.data.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {activity.data.platform}
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
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-green-800">Campaign Management</CardTitle>
                <CardDescription>Manage campaigns across LinkedIn, TikTok, and YouTube</CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="linkedin_ads">LinkedIn Ads</SelectItem>
                    <SelectItem value="tiktok_ads">TikTok Ads</SelectItem>
                    <SelectItem value="youtube_ads">YouTube Ads</SelectItem>
                  </SelectContent>
                </Select>
                <Dialog open={showCampaignDialog} onOpenChange={setShowCampaignDialog}>
                  <DialogTrigger asChild>
                    <Button className="flex items-center text-white bg-green-600 hover:bg-green-700">
                      <Plus className="mr-2 h-4 w-4" /> Create Campaign
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Create Campaign</DialogTitle>
                      <DialogDescription>
                        Create a new campaign on {selectedPlatform.replace('_', ' ')}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="campaign-name">Campaign Name</Label>
                        <Input id="campaign-name" placeholder="Enter campaign name" />
                      </div>
                      <div>
                        <Label htmlFor="campaign-objective">Objective</Label>
                        <Select>
                          <SelectTrigger>
                            <SelectValue placeholder="Select objective" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="traffic">Website Traffic</SelectItem>
                            <SelectItem value="conversions">Conversions</SelectItem>
                            <SelectItem value="awareness">Brand Awareness</SelectItem>
                            <SelectItem value="engagement">Engagement</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="campaign-budget">Budget</Label>
                          <Input id="campaign-budget" type="number" placeholder="5000" />
                        </div>
                        <div>
                          <Label htmlFor="daily-budget">Daily Budget</Label>
                          <Input id="daily-budget" type="number" placeholder="200" />
                        </div>
                      </div>
                      <Button className="w-full">
                        <Target className="mr-2 h-4 w-4" /> Create Campaign
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
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
                          <div className="text-sm text-gray-600">{campaign.platform.replace('_', ' ')}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(campaign.status)}>
                          {getStatusIcon(campaign.status)}
                          <span className="ml-1">{campaign.status.toUpperCase()}</span>
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Budget</div>
                        <div className="font-semibold">{formatCurrency(campaign.budget)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Spend</div>
                        <div className="font-semibold">{formatCurrency(campaign.spend)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Impressions</div>
                        <div className="font-semibold">{formatNumber(campaign.impressions)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Conversions</div>
                        <div className="font-semibold">{formatNumber(campaign.conversions)}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Products Tab */}
        <TabsContent value="products">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-green-800">Shopify Products</CardTitle>
                <CardDescription>Manage your Shopify store products and inventory</CardDescription>
              </div>
              <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
                <DialogTrigger asChild>
                  <Button className="flex items-center text-white bg-green-600 hover:bg-green-700">
                    <Plus className="mr-2 h-4 w-4" /> Add Product
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Add Product</DialogTitle>
                    <DialogDescription>
                      Add a new product to your Shopify store
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="product-title">Product Title</Label>
                      <Input id="product-title" placeholder="Enter product title" />
                    </div>
                    <div>
                      <Label htmlFor="product-description">Description</Label>
                      <Textarea id="product-description" placeholder="Enter product description" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="product-price">Price</Label>
                        <Input id="product-price" type="number" placeholder="99.99" />
                      </div>
                      <div>
                        <Label htmlFor="inventory-quantity">Inventory</Label>
                        <Input id="inventory-quantity" type="number" placeholder="100" />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="product-sku">SKU</Label>
                      <Input id="product-sku" placeholder="SKU-001" />
                    </div>
                    <Button className="w-full">
                      <Package className="mr-2 h-4 w-4" /> Add Product
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {products.map((product) => (
                  <Card key={product.product_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <Package className="h-5 w-5 text-green-500" />
                        <div>
                          <div className="font-semibold text-lg">{product.title}</div>
                          <div className="text-sm text-gray-600">SKU: {product.product_id}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(product.status)}>
                          {getStatusIcon(product.status)}
                          <span className="ml-1">{product.status.toUpperCase()}</span>
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Price</div>
                        <div className="font-semibold">{formatCurrency(product.price)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Inventory</div>
                        <div className="font-semibold">{formatNumber(product.inventory_quantity)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Tags</div>
                        <div className="flex flex-wrap gap-1">
                          {product.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600">Status</div>
                        <div className="font-semibold">{product.status}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payments Tab */}
        <TabsContent value="payments">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-xl font-bold text-green-800">Stripe Payments</CardTitle>
                <CardDescription>Manage Stripe payment processing and transactions</CardDescription>
              </div>
              <Dialog open={showPaymentDialog} onOpenChange={setShowPaymentDialog}>
                <DialogTrigger asChild>
                  <Button className="flex items-center text-white bg-green-600 hover:bg-green-700">
                    <Plus className="mr-2 h-4 w-4" /> Create Payment
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create Payment</DialogTitle>
                    <DialogDescription>
                      Create a new Stripe payment intent
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="payment-amount">Amount</Label>
                      <Input id="payment-amount" type="number" placeholder="99.99" />
                    </div>
                    <div>
                      <Label htmlFor="payment-currency">Currency</Label>
                      <Select defaultValue="usd">
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="usd">USD</SelectItem>
                          <SelectItem value="eur">EUR</SelectItem>
                          <SelectItem value="gbp">GBP</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="payment-description">Description</Label>
                      <Input id="payment-description" placeholder="Payment description" />
                    </div>
                    <div>
                      <Label htmlFor="customer-email">Customer Email</Label>
                      <Input id="customer-email" type="email" placeholder="customer@example.com" />
                    </div>
                    <Button className="w-full">
                      <CreditCard className="mr-2 h-4 w-4" /> Create Payment
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {payments.map((payment) => (
                  <Card key={payment.payment_id} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <CreditCard className="h-5 w-5 text-purple-500" />
                        <div>
                          <div className="font-semibold text-lg">{formatCurrency(payment.amount)}</div>
                          <div className="text-sm text-gray-600">{payment.description}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(payment.status)}>
                          {getStatusIcon(payment.status)}
                          <span className="ml-1">{payment.status.toUpperCase()}</span>
                        </Badge>
                        <Button variant="outline" size="sm">
                          <Eye className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600">Amount</div>
                        <div className="font-semibold">{formatCurrency(payment.amount)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Currency</div>
                        <div className="font-semibold">{payment.currency.toUpperCase()}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Status</div>
                        <div className="font-semibold">{payment.status}</div>
                      </div>
                      <div>
                        <div className="text-gray-600">Date</div>
                        <div className="font-semibold">{new Date(payment.created_at).toLocaleDateString()}</div>
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
              <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-blue-500" /> Platform Analytics
              </CardTitle>
              <CardDescription>Comprehensive analytics across all platforms</CardDescription>
            </CardHeader>
            <CardContent>
              {unifiedAnalytics && (
                <div className="space-y-6">
                  {/* Campaign Analytics */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Campaign Performance</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-2xl font-bold text-blue-600">{unifiedAnalytics.campaigns.total_campaigns}</div>
                            <div className="text-sm text-gray-600">Total Campaigns</div>
                          </div>
                          <Target className="h-8 w-8 text-blue-500" />
                        </div>
                      </div>
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-2xl font-bold text-green-600">{formatCurrency(unifiedAnalytics.campaigns.total_spend)}</div>
                            <div className="text-sm text-gray-600">Total Spend</div>
                          </div>
                          <DollarSign className="h-8 w-8 text-green-500" />
                        </div>
                      </div>
                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-2xl font-bold text-purple-600">{formatNumber(unifiedAnalytics.campaigns.total_conversions)}</div>
                            <div className="text-sm text-gray-600">Total Conversions</div>
                          </div>
                          <TrendingUp className="h-8 w-8 text-purple-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Platform Breakdown */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Platform Breakdown</h3>
                    <div className="space-y-3">
                      {Object.entries(unifiedAnalytics.campaigns.platforms).map(([platform, data]) => (
                        <div key={platform} className="p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center">
                              {getPlatformIcon(platform)}
                              <span className="ml-2 font-semibold">{platform.replace('_', ' ').toUpperCase()}</span>
                            </div>
                            <Badge className={`${getPlatformColor(platform)} text-white`}>
                              {data.campaigns} campaigns
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                              <div className="text-gray-600">Spend</div>
                              <div className="font-semibold">{formatCurrency(data.spend)}</div>
                            </div>
                            <div>
                              <div className="text-gray-600">Impressions</div>
                              <div className="font-semibold">{formatNumber(data.impressions)}</div>
                            </div>
                            <div>
                              <div className="text-gray-600">Clicks</div>
                              <div className="font-semibold">{formatNumber(data.clicks)}</div>
                            </div>
                            <div>
                              <div className="text-gray-600">Conversions</div>
                              <div className="font-semibold">{formatNumber(data.conversions)}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Revenue Analytics */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Revenue Analytics</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-2xl font-bold text-green-600">{formatCurrency(unifiedAnalytics.products.total_revenue)}</div>
                            <div className="text-sm text-gray-600">Shopify Revenue</div>
                          </div>
                          <ShoppingBag className="h-8 w-8 text-green-500" />
                        </div>
                      </div>
                      <div className="p-4 bg-purple-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-2xl font-bold text-purple-600">{formatCurrency(unifiedAnalytics.payments.total_amount)}</div>
                            <div className="text-sm text-gray-600">Stripe Payments</div>
                          </div>
                          <CreditCard className="h-8 w-8 text-purple-500" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings">
          <Card className="shadow-lg border-none bg-white/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-green-800 flex items-center">
                <Settings className="mr-2 h-5 w-5 text-gray-500" /> Platform Settings
              </CardTitle>
              <CardDescription>Configure platform integrations and credentials</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Platform Configuration */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">Platform Configuration</h3>
                  <div className="space-y-4">
                    {['linkedin_ads', 'tiktok_ads', 'youtube_ads', 'shopify', 'stripe'].map((platform) => (
                      <div key={platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center">
                          {getPlatformIcon(platform)}
                          <div className="ml-3">
                            <div className="font-medium">{platform.replace('_', ' ').toUpperCase()}</div>
                            <div className="text-sm text-gray-600">
                              {platformOverview?.initialized_platforms.includes(platform) ? 'Connected' : 'Not connected'}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant="outline" className={platformOverview?.initialized_platforms.includes(platform) ? 'text-green-600 border-green-300' : 'text-red-600 border-red-300'}>
                            {platformOverview?.initialized_platforms.includes(platform) ? 'Connected' : 'Disconnected'}
                          </Badge>
                          <Button variant="outline" size="sm">
                            <Settings className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* API Limits */}
                <div>
                  <h3 className="font-semibold text-lg mb-4">API Limits & Usage</h3>
                  <div className="space-y-3">
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <div className="flex justify-between text-sm mb-1">
                        <span>LinkedIn Ads API</span>
                        <span>850 / 1000 calls</span>
                      </div>
                      <Progress value={85} className="h-2" />
                    </div>
                    <div className="p-3 bg-black text-white rounded-lg">
                      <div className="flex justify-between text-sm mb-1">
                        <span>TikTok Ads API</span>
                        <span>1200 / 2000 calls</span>
                      </div>
                      <Progress value={60} className="h-2" />
                    </div>
                    <div className="p-3 bg-red-50 rounded-lg">
                      <div className="flex justify-between text-sm mb-1">
                        <span>YouTube Ads API</span>
                        <span>450 / 1000 calls</span>
                      </div>
                      <Progress value={45} className="h-2" />
                    </div>
                  </div>
                </div>
                
                <Button className="w-full">
                  <Settings className="mr-2 h-4 w-4" /> Save Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedPlatformIntegrationsDashboard;
