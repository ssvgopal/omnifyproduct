import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Plus,
  BarChart3,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  Clock,
  Play,
  Pause,
  StopCircle,
  Loader2,
  AlertCircle,
  Target,
  Users,
  DollarSign
} from 'lucide-react';
import api from '@/services/api';

const ABTestingInterface = () => {
  const [abTests, setAbTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  const [showResultsDialog, setShowResultsDialog] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [creating, setCreating] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    test_type: 'creative',
    traffic_split: 50,
    success_metric: 'conversions',
    minimum_sample_size: 1000,
    test_duration_days: 14,
    variants: [{ name: 'Control', description: '' }, { name: 'Variant A', description: '' }]
  });

  useEffect(() => {
    loadABTests();
  }, []);

  const loadABTests = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/api/campaigns/ab-tests', {
        params: { client_id: 'demo-client-123' }
      });
      if (response.data && response.data.ab_tests) {
        setAbTests(response.data.ab_tests);
      }
    } catch (err) {
      console.error('Error loading A/B tests:', err);
      setError('Failed to load A/B tests');
      // Use mock data as fallback
      setAbTests([
        {
          test_id: 'test_1',
          name: 'Creative Variation Test',
          description: 'Testing headline variations',
          test_type: 'creative',
          status: 'running',
          traffic_split: 50,
          variants: [{ name: 'Control' }, { name: 'Variant A' }],
          created_at: new Date().toISOString(),
          test_duration_days: 14
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = async () => {
    try {
      setCreating(true);
      setError(null);

      const response = await api.post('/api/campaigns/ab-tests', {
        client_id: 'demo-client-123',
        ...formData
      });

      if (response.data) {
        await loadABTests();
        setShowCreateDialog(false);
        setFormData({
          name: '',
          description: '',
          test_type: 'creative',
          traffic_split: 50,
          success_metric: 'conversions',
          minimum_sample_size: 1000,
          test_duration_days: 14,
          variants: [{ name: 'Control', description: '' }, { name: 'Variant A', description: '' }]
        });
      }
    } catch (err) {
      console.error('Error creating A/B test:', err);
      setError('Failed to create A/B test');
    } finally {
      setCreating(false);
    }
  };

  const handleViewResults = async (testId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/campaigns/ab-tests/${testId}`, {
        params: { client_id: 'demo-client-123' }
      });
      if (response.data) {
        setTestResults(response.data);
        setSelectedTest(abTests.find(t => t.test_id === testId));
        setShowResultsDialog(true);
      }
    } catch (err) {
      console.error('Error loading test results:', err);
      setError('Failed to load test results');
    } finally {
      setLoading(false);
    }
  };

  const handleAddVariant = () => {
    setFormData({
      ...formData,
      variants: [...formData.variants, { name: `Variant ${String.fromCharCode(65 + formData.variants.length)}`, description: '' }]
    });
  };

  const handleRemoveVariant = (index) => {
    if (formData.variants.length > 2) {
      setFormData({
        ...formData,
        variants: formData.variants.filter((_, i) => i !== index)
      });
    }
  };

  const handleVariantChange = (index, field, value) => {
    const newVariants = [...formData.variants];
    newVariants[index][field] = value;
    setFormData({ ...formData, variants: newVariants });
  };

  const getStatusBadge = (status) => {
    const badges = {
      'running': <Badge className="bg-green-100 text-green-800">Running</Badge>,
      'completed': <Badge className="bg-blue-100 text-blue-800">Completed</Badge>,
      'paused': <Badge className="bg-yellow-100 text-yellow-800">Paused</Badge>,
      'draft': <Badge variant="outline">Draft</Badge>
    };
    return badges[status] || <Badge variant="outline">{status}</Badge>;
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">A/B Testing</h2>
          <p className="text-gray-600 mt-1">Test different campaign variations to optimize performance</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create A/B Test
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create A/B Test</DialogTitle>
              <DialogDescription>Configure a new A/B test to compare campaign variations</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">Test Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Headline Variation Test"
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe what you're testing..."
                  rows={3}
                />
              </div>
              <div>
                <Label htmlFor="test_type">Test Type</Label>
                <Select
                  value={formData.test_type}
                  onValueChange={(value) => setFormData({ ...formData, test_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="creative">Creative</SelectItem>
                    <SelectItem value="audience">Audience</SelectItem>
                    <SelectItem value="budget">Budget</SelectItem>
                    <SelectItem value="targeting">Targeting</SelectItem>
                    <SelectItem value="landing_page">Landing Page</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="traffic_split">Traffic Split (%)</Label>
                <Input
                  id="traffic_split"
                  type="number"
                  min="10"
                  max="90"
                  value={formData.traffic_split}
                  onChange={(e) => setFormData({ ...formData, traffic_split: parseInt(e.target.value) })}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Control: {formData.traffic_split}% | Variants: {100 - formData.traffic_split}%
                </p>
              </div>
              <div>
                <Label htmlFor="success_metric">Success Metric</Label>
                <Select
                  value={formData.success_metric}
                  onValueChange={(value) => setFormData({ ...formData, success_metric: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="conversions">Conversions</SelectItem>
                    <SelectItem value="ctr">Click-Through Rate</SelectItem>
                    <SelectItem value="roas">Return on Ad Spend</SelectItem>
                    <SelectItem value="cpa">Cost Per Acquisition</SelectItem>
                    <SelectItem value="revenue">Revenue</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="minimum_sample_size">Minimum Sample Size</Label>
                  <Input
                    id="minimum_sample_size"
                    type="number"
                    min="100"
                    value={formData.minimum_sample_size}
                    onChange={(e) => setFormData({ ...formData, minimum_sample_size: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <Label htmlFor="test_duration_days">Duration (days)</Label>
                  <Input
                    id="test_duration_days"
                    type="number"
                    min="1"
                    max="90"
                    value={formData.test_duration_days}
                    onChange={(e) => setFormData({ ...formData, test_duration_days: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              {/* Variants */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <Label>Test Variants</Label>
                  <Button type="button" variant="outline" size="sm" onClick={handleAddVariant}>
                    <Plus className="h-3 w-3 mr-1" />
                    Add Variant
                  </Button>
                </div>
                <div className="space-y-3">
                  {formData.variants.map((variant, index) => (
                    <Card key={index} className="p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <Input
                            placeholder="Variant name"
                            value={variant.name}
                            onChange={(e) => handleVariantChange(index, 'name', e.target.value)}
                          />
                          <Textarea
                            placeholder="Variant description (optional)"
                            value={variant.description}
                            onChange={(e) => handleVariantChange(index, 'description', e.target.value)}
                            rows={2}
                          />
                        </div>
                        {formData.variants.length > 2 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveVariant(index)}
                            className="ml-2"
                          >
                            <XCircle className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTest} disabled={creating || !formData.name}>
                  {creating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Create Test
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* A/B Tests List */}
      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">Loading A/B tests...</p>
          </CardContent>
        </Card>
      ) : abTests.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Target className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold mb-2">No A/B Tests Yet</h3>
            <p className="text-gray-600 mb-4">Create your first A/B test to start optimizing campaigns</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create A/B Test
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {abTests.map((test) => (
            <Card key={test.test_id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{test.name}</CardTitle>
                    <CardDescription className="mt-1">{test.description || 'No description'}</CardDescription>
                  </div>
                  {getStatusBadge(test.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Type</p>
                    <p className="font-semibold capitalize">{test.test_type}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Variants</p>
                    <p className="font-semibold">{test.variants?.length || 2}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Traffic Split</p>
                    <p className="font-semibold">{test.traffic_split}%</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Duration</p>
                    <p className="font-semibold">{test.test_duration_days} days</p>
                  </div>
                </div>

                {test.status === 'running' && test.results && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm font-semibold mb-2">Quick Stats</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Control:</span>
                        <span className="ml-2 font-semibold">{test.results.control?.conversion_rate?.toFixed(2)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Variant:</span>
                        <span className="ml-2 font-semibold">{test.results.variant?.conversion_rate?.toFixed(2)}%</span>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-gray-500">
                  Created {new Date(test.created_at).toLocaleDateString()}
                </div>
                <div className="flex space-x-2">
                  {test.status === 'running' && (
                    <>
                      <Button variant="outline" size="sm">
                        <Pause className="h-3 w-3 mr-1" />
                        Pause
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleViewResults(test.test_id)}>
                        <BarChart3 className="h-3 w-3 mr-1" />
                        View Results
                      </Button>
                    </>
                  )}
                  {test.status === 'completed' && (
                    <Button variant="outline" size="sm" onClick={() => handleViewResults(test.test_id)}>
                      <BarChart3 className="h-3 w-3 mr-1" />
                      View Results
                    </Button>
                  )}
                  {test.status === 'paused' && (
                    <Button variant="outline" size="sm">
                      <Play className="h-3 w-3 mr-1" />
                      Resume
                    </Button>
                  )}
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Results Dialog */}
      <Dialog open={showResultsDialog} onOpenChange={setShowResultsDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>A/B Test Results: {selectedTest?.name}</DialogTitle>
            <DialogDescription>Statistical analysis and performance comparison</DialogDescription>
          </DialogHeader>
          {testResults ? (
            <div className="space-y-6">
              {/* Summary Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-gray-600">Total Visitors</p>
                    <p className="text-2xl font-bold">{testResults.total_visitors || 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-gray-600">Conversions</p>
                    <p className="text-2xl font-bold">{testResults.total_conversions || 0}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-gray-600">Conversion Rate</p>
                    <p className="text-2xl font-bold">
                      {testResults.overall_conversion_rate ? formatPercentage(testResults.overall_conversion_rate) : '0%'}
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <p className="text-sm text-gray-600">Statistical Significance</p>
                    <p className="text-2xl font-bold">
                      {testResults.statistical_significance ? formatPercentage(testResults.statistical_significance) : 'N/A'}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Variant Comparison */}
              {testResults.variants && (
                <div>
                  <h3 className="text-lg font-semibold mb-4">Variant Performance</h3>
                  <div className="space-y-4">
                    {testResults.variants.map((variant, index) => (
                      <Card key={index}>
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h4 className="font-semibold">{variant.name}</h4>
                              <p className="text-sm text-gray-600">{variant.description}</p>
                            </div>
                            {variant.is_winner && (
                              <Badge className="bg-green-100 text-green-800">
                                <CheckCircle2 className="h-3 w-3 mr-1" />
                                Winner
                              </Badge>
                            )}
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div>
                              <p className="text-sm text-gray-600">Visitors</p>
                              <p className="text-xl font-bold">{variant.visitors || 0}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Conversions</p>
                              <p className="text-xl font-bold">{variant.conversions || 0}</p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Conversion Rate</p>
                              <p className="text-xl font-bold">
                                {variant.conversion_rate ? formatPercentage(variant.conversion_rate) : '0%'}
                              </p>
                            </div>
                            <div>
                              <p className="text-sm text-gray-600">Improvement</p>
                              <p className={`text-xl font-bold ${variant.improvement > 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {variant.improvement ? `${variant.improvement > 0 ? '+' : ''}${formatPercentage(variant.improvement)}` : '0%'}
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {testResults.recommendations && testResults.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Recommendations</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {testResults.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <AlertCircle className="h-4 w-4 mr-2 mt-0.5 text-blue-500" />
                          <span className="text-sm">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500">Loading results...</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ABTestingInterface;

