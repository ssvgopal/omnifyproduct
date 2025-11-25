import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Plus,
  Save,
  Play,
  Download,
  BarChart3,
  LineChart,
  PieChart,
  Table,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Trash2,
  Edit
} from 'lucide-react';
import api from '@/services/api';

const ReportBuilder = () => {
  const [report, setReport] = useState({
    name: '',
    description: '',
    report_type: 'campaign_performance',
    format: 'pdf',
    date_range: 'last_30_days',
    metrics: [],
    filters: {},
    charts: []
  });
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [templates, setTemplates] = useState([]);

  const reportTypes = [
    { value: 'campaign_performance', label: 'Campaign Performance' },
    { value: 'platform_analytics', label: 'Platform Analytics' },
    { value: 'revenue_analysis', label: 'Revenue Analysis' },
    { value: 'customer_insights', label: 'Customer Insights' },
    { value: 'custom', label: 'Custom Report' }
  ];

  const formats = [
    { value: 'pdf', label: 'PDF' },
    { value: 'excel', label: 'Excel' },
    { value: 'csv', label: 'CSV' },
    { value: 'json', label: 'JSON' }
  ];

  const dateRanges = [
    { value: 'last_7_days', label: 'Last 7 Days' },
    { value: 'last_30_days', label: 'Last 30 Days' },
    { value: 'last_90_days', label: 'Last 90 Days' },
    { value: 'last_year', label: 'Last Year' },
    { value: 'custom', label: 'Custom Range' }
  ];

  const chartTypes = [
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
    { value: 'line', label: 'Line Chart', icon: LineChart },
    { value: 'pie', label: 'Pie Chart', icon: PieChart },
    { value: 'table', label: 'Table', icon: Table }
  ];

  const availableMetrics = [
    { value: 'impressions', label: 'Impressions' },
    { value: 'clicks', label: 'Clicks' },
    { value: 'conversions', label: 'Conversions' },
    { value: 'revenue', label: 'Revenue' },
    { value: 'spend', label: 'Spend' },
    { value: 'roas', label: 'ROAS' },
    { value: 'ctr', label: 'CTR' },
    { value: 'cpa', label: 'CPA' }
  ];

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await api.get('/api/metabase/templates');
      if (response.data && response.data.templates) {
        setTemplates(Object.entries(response.data.templates).map(([key, value]) => ({
          id: key,
          ...value
        })));
      }
    } catch (err) {
      console.error('Error loading templates:', err);
    }
  };

  const handleAddChart = () => {
    setReport({
      ...report,
      charts: [
        ...report.charts,
        {
          id: `chart_${Date.now()}`,
          name: 'New Chart',
          type: 'bar',
          metric: 'revenue',
          dimension: 'platform'
        }
      ]
    });
  };

  const handleRemoveChart = (chartId) => {
    setReport({
      ...report,
      charts: report.charts.filter(c => c.id !== chartId)
    });
  };

  const handleChartChange = (chartId, field, value) => {
    setReport({
      ...report,
      charts: report.charts.map(chart =>
        chart.id === chartId ? { ...chart, [field]: value } : chart
      )
    });
  };

  const handleAddMetric = (metric) => {
    if (!report.metrics.includes(metric)) {
      setReport({
        ...report,
        metrics: [...report.metrics, metric]
      });
    }
  };

  const handleRemoveMetric = (metric) => {
    setReport({
      ...report,
      metrics: report.metrics.filter(m => m !== metric)
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      const response = await api.post('/api/reporting/reports', {
        name: report.name,
        description: report.description,
        report_type: report.report_type,
        format: report.format,
        date_range: report.date_range,
        metrics: report.metrics,
        filters: report.filters,
        charts: report.charts,
        organization_id: 'demo-org-123' // Get from user context
      });

      if (response.data) {
        setSuccess('Report saved successfully');
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error saving report:', err);
      setError('Failed to save report');
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setGenerating(true);
      setError(null);

      const response = await api.post('/api/reporting/generate', {
        report_config: report,
        organization_id: 'demo-org-123'
      });

      if (response.data && response.data.download_url) {
        // Download the report
        window.open(response.data.download_url, '_blank');
        setSuccess('Report generated successfully');
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Report Builder</h2>
          <p className="text-gray-600 mt-1">Create custom analytics reports</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleSave} disabled={saving || !report.name}>
            {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
            Save Report
          </Button>
          <Button onClick={handleGenerate} disabled={generating || !report.name}>
            {generating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
            Generate Report
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="basic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="basic">Basic Info</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="charts">Charts</TabsTrigger>
          <TabsTrigger value="filters">Filters</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Report Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">Report Name</Label>
                <Input
                  id="name"
                  value={report.name}
                  onChange={(e) => setReport({ ...report, name: e.target.value })}
                  placeholder="e.g., Q4 Campaign Performance"
                />
              </div>
              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={report.description}
                  onChange={(e) => setReport({ ...report, description: e.target.value })}
                  placeholder="Describe what this report covers..."
                  rows={3}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="report_type">Report Type</Label>
                  <Select
                    value={report.report_type}
                    onValueChange={(value) => setReport({ ...report, report_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {reportTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="format">Export Format</Label>
                  <Select
                    value={report.format}
                    onValueChange={(value) => setReport({ ...report, format: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {formats.map(format => (
                        <SelectItem key={format.value} value={format.value}>
                          {format.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label htmlFor="date_range">Date Range</Label>
                <Select
                  value={report.date_range}
                  onValueChange={(value) => setReport({ ...report, date_range: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {dateRanges.map(range => (
                      <SelectItem key={range.value} value={range.value}>
                        {range.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Select Metrics</CardTitle>
              <CardDescription>Choose which metrics to include in your report</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {availableMetrics.map(metric => (
                  <Badge
                    key={metric.value}
                    variant={report.metrics.includes(metric.value) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => {
                      if (report.metrics.includes(metric.value)) {
                        handleRemoveMetric(metric.value);
                      } else {
                        handleAddMetric(metric.value);
                      }
                    }}
                  >
                    {metric.label}
                  </Badge>
                ))}
              </div>
              {report.metrics.length > 0 && (
                <div>
                  <p className="text-sm font-semibold mb-2">Selected Metrics:</p>
                  <div className="flex flex-wrap gap-2">
                    {report.metrics.map(metric => (
                      <Badge key={metric} variant="default">
                        {availableMetrics.find(m => m.value === metric)?.label || metric}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="charts" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Charts</CardTitle>
                  <CardDescription>Add visualizations to your report</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={handleAddChart}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Chart
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {report.charts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>No charts added</p>
                  <p className="text-sm mt-2">Add charts to visualize your data</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {report.charts.map((chart, index) => {
                    const ChartIcon = chartTypes.find(t => t.value === chart.type)?.icon || BarChart3;
                    return (
                      <Card key={chart.id} className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 space-y-3">
                            <div className="flex items-center space-x-2">
                              <ChartIcon className="h-4 w-4" />
                              <Badge variant="outline">Chart {index + 1}</Badge>
                            </div>
                            <div>
                              <Label>Chart Name</Label>
                              <Input
                                value={chart.name}
                                onChange={(e) => handleChartChange(chart.id, 'name', e.target.value)}
                                placeholder="Chart name"
                              />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <Label>Chart Type</Label>
                                <Select
                                  value={chart.type}
                                  onValueChange={(value) => handleChartChange(chart.id, 'type', value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {chartTypes.map(type => (
                                      <SelectItem key={type.value} value={type.value}>
                                        {type.label}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div>
                                <Label>Metric</Label>
                                <Select
                                  value={chart.metric}
                                  onValueChange={(value) => handleChartChange(chart.id, 'metric', value)}
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {availableMetrics.map(metric => (
                                      <SelectItem key={metric.value} value={metric.value}>
                                        {metric.label}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveChart(chart.id)}
                            className="ml-2"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="filters" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
              <CardDescription>Apply filters to narrow down your data</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-500">Filter configuration coming soon...</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReportBuilder;

