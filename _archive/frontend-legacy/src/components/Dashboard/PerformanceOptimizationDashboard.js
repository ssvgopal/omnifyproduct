import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Switch,
  FormControlLabel,
  Slider
} from '@mui/material';
import {
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  Cached,
  Database,
  QueryStats,
  Settings,
  Refresh,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  ExpandMore,
  PlayArrow,
  Stop,
  Delete,
  Edit,
  Visibility,
  Download,
  Upload
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

const PERFORMANCE_OPTIMIZATION_DASHBOARD = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [cacheDialog, setCacheDialog] = useState(false);
  const [queryDialog, setQueryDialog] = useState(false);
  const [settingsDialog, setSettingsDialog] = useState(false);
  const [optimizationDialog, setOptimizationDialog] = useState(false);

  // Form states
  const [cacheRequest, setCacheRequest] = useState({
    key: '',
    value: '',
    ttl: 3600
  });

  const [queryRequest, setQueryRequest] = useState({
    query: '',
    params: {}
  });

  const [performanceSettings, setPerformanceSettings] = useState({
    cache_ttl: 3600,
    max_cache_size: 10000,
    slow_query_threshold: 1.0,
    performance_check_interval: 60,
    auto_optimize: true
  });

  const [optimizationResults, setOptimizationResults] = useState(null);

  useEffect(() => {
    loadDashboardData();
    loadMetrics();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/performance/dashboard?organization_id=default');
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await fetch('/api/v1/performance/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError('Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  const cacheGet = async () => {
    try {
      const response = await fetch('/api/v1/performance/cache/get', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: cacheRequest.key })
      });

      const result = await response.json();
      if (result.found) {
        setCacheRequest({ ...cacheRequest, value: result.value });
      } else {
        setCacheRequest({ ...cacheRequest, value: 'Not found' });
      }
    } catch (err) {
      setError('Failed to get from cache');
    }
  };

  const cacheSet = async () => {
    try {
      const response = await fetch('/api/v1/performance/cache/set', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cacheRequest)
      });

      if (response.ok) {
        setCacheDialog(false);
        loadMetrics();
      }
    } catch (err) {
      setError('Failed to set cache');
    }
  };

  const cacheClear = async () => {
    try {
      const response = await fetch('/api/v1/performance/cache/clear', {
        method: 'POST'
      });

      if (response.ok) {
        loadMetrics();
      }
    } catch (err) {
      setError('Failed to clear cache');
    }
  };

  const analyzeQuery = async () => {
    try {
      const response = await fetch('/api/v1/performance/query/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryRequest)
      });

      const result = await response.json();
      alert(`Query Analysis: ${result.optimization_count} optimizations found`);
      setQueryDialog(false);
    } catch (err) {
      setError('Failed to analyze query');
    }
  };

  const runOptimization = async () => {
    try {
      const response = await fetch('/api/v1/performance/optimize', {
        method: 'POST'
      });

      const result = await response.json();
      setOptimizationResults(result);
      setOptimizationDialog(true);
    } catch (err) {
      setError('Failed to run optimization');
    }
  };

  const updateSettings = async () => {
    try {
      const response = await fetch('/api/v1/performance/settings/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(performanceSettings)
      });

      if (response.ok) {
        setSettingsDialog(false);
        loadDashboardData();
      }
    } catch (err) {
      setError('Failed to update settings');
    }
  };

  const getPerformanceColor = (value, thresholds) => {
    if (value >= thresholds.critical) return 'error';
    if (value >= thresholds.warning) return 'warning';
    return 'success';
  };

  const getAlertIcon = (severity) => {
    switch (severity) {
      case 'critical': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      default: return <CheckCircle color="success" />;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Performance Optimization Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Cache" />
        <Tab label="Database" />
        <Tab label="System" />
        <Tab label="Optimization" />
        <Tab label="Settings" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* System Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Performance
                </Typography>
                {metrics?.system_metrics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color={getPerformanceColor(metrics.system_metrics.cpu_usage, { warning: 70, critical: 90 })}>
                          {metrics.system_metrics.cpu_usage?.toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">CPU Usage</Typography>
                        <LinearProgress
                          variant="determinate"
                          value={metrics.system_metrics.cpu_usage || 0}
                          color={getPerformanceColor(metrics.system_metrics.cpu_usage, { warning: 70, critical: 90 })}
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color={getPerformanceColor(metrics.system_metrics.memory_usage, { warning: 80, critical: 95 })}>
                          {metrics.system_metrics.memory_usage?.toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">Memory Usage</Typography>
                        <LinearProgress
                          variant="determinate"
                          value={metrics.system_metrics.memory_usage || 0}
                          color={getPerformanceColor(metrics.system_metrics.memory_usage, { warning: 80, critical: 95 })}
                        />
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {metrics.system_metrics.disk_read_rate?.toFixed(1)} MB/s
                        </Typography>
                        <Typography variant="body2">Disk Read</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {metrics.system_metrics.network_sent_rate?.toFixed(1)} MB/s
                        </Typography>
                        <Typography variant="body2">Network Sent</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Cache Performance */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cache Performance
                </Typography>
                {metrics?.cache_metrics && (
                  <Grid container spacing={2}>
                    {Object.entries(metrics.cache_metrics).map(([level, cacheMetrics]) => (
                      <Grid item xs={6} key={level}>
                        <Box textAlign="center">
                          <Typography variant="h4" color="primary">
                            {(cacheMetrics.hit_rate * 100).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2">{level} Hit Rate</Typography>
                          <LinearProgress
                            variant="determinate"
                            value={cacheMetrics.hit_rate * 100}
                            color={cacheMetrics.hit_rate > 0.8 ? 'success' : 'warning'}
                          />
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Alerts */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Alerts
                </Typography>
                {metrics?.alerts && metrics.alerts.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Type</TableCell>
                          <TableCell>Message</TableCell>
                          <TableCell>Severity</TableCell>
                          <TableCell>Timestamp</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {metrics.alerts.map((alert, index) => (
                          <TableRow key={index}>
                            <TableCell>{alert.type}</TableCell>
                            <TableCell>{alert.message}</TableCell>
                            <TableCell>
                              <Chip
                                icon={getAlertIcon(alert.severity)}
                                label={alert.severity}
                                color={alert.severity === 'critical' ? 'error' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {new Date(alert.timestamp).toLocaleString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography color="text.secondary">No performance alerts</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Cache Management</Typography>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<Cached />}
                  onClick={() => setCacheDialog(true)}
                  sx={{ mr: 1 }}
                >
                  Cache Operations
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Delete />}
                  onClick={cacheClear}
                  color="error"
                >
                  Clear Cache
                </Button>
              </Box>
            </Box>
          </Grid>

          {/* Cache Statistics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cache Statistics
                </Typography>
                {metrics?.cache_metrics && (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={Object.entries(metrics.cache_metrics).map(([level, cacheMetrics]) => ({
                      level,
                      hitRate: cacheMetrics.hit_rate * 100,
                      missRate: cacheMetrics.miss_rate * 100,
                      totalRequests: cacheMetrics.total_requests
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="level" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="hitRate" fill="#4caf50" name="Hit Rate %" />
                      <Bar dataKey="missRate" fill="#f44336" name="Miss Rate %" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cache Performance Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={[
                    { time: '00:00', hitRate: 85 },
                    { time: '04:00', hitRate: 82 },
                    { time: '08:00', hitRate: 88 },
                    { time: '12:00', hitRate: 92 },
                    { time: '16:00', hitRate: 89 },
                    { time: '20:00', hitRate: 87 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="hitRate" stroke="#4caf50" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Database Performance</Typography>
              <Button
                variant="outlined"
                startIcon={<QueryStats />}
                onClick={() => setQueryDialog(true)}
              >
                Analyze Query
              </Button>
            </Box>
          </Grid>

          {/* Database Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Metrics
                </Typography>
                {dashboardData?.database_metrics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary">
                          {dashboardData.database_metrics.slow_queries_count}
                        </Typography>
                        <Typography variant="body2">Slow Queries</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          99.2%
                        </Typography>
                        <Typography variant="body2">Uptime</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Slow Queries */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Slow Queries
                </Typography>
                {dashboardData?.database_metrics?.recent_slow_queries && dashboardData.database_metrics.recent_slow_queries.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Query</TableCell>
                          <TableCell>Execution Time</TableCell>
                          <TableCell>Timestamp</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dashboardData.database_metrics.recent_slow_queries.map((query, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              <Typography variant="body2" sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {query.query}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={`${query.execution_time?.toFixed(2)}s`}
                                color={query.execution_time > 2 ? 'error' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {new Date(query.timestamp).toLocaleString()}
                            </TableCell>
                            <TableCell>
                              <Tooltip title="Optimize">
                                <IconButton size="small">
                                  <Speed />
                                </IconButton>
                              </Tooltip>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography color="text.secondary">No slow queries detected</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              System Performance Monitoring
            </Typography>
          </Grid>

          {/* System Performance Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Trends (24h)
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={[
                    { time: '00:00', cpu: 45, memory: 60, disk: 20 },
                    { time: '04:00', cpu: 35, memory: 55, disk: 15 },
                    { time: '08:00', cpu: 65, memory: 70, disk: 35 },
                    { time: '12:00', cpu: 80, memory: 75, disk: 40 },
                    { time: '16:00', cpu: 70, memory: 68, disk: 30 },
                    { time: '20:00', cpu: 55, memory: 62, disk: 25 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <RechartsTooltip />
                    <Area type="monotone" dataKey="cpu" stackId="1" stroke="#8884d8" fill="#8884d8" />
                    <Area type="monotone" dataKey="memory" stackId="1" stroke="#82ca9d" fill="#82ca9d" />
                    <Area type="monotone" dataKey="disk" stackId="1" stroke="#ffc658" fill="#ffc658" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Performance Optimization</Typography>
              <Button
                variant="contained"
                startIcon={<PlayArrow />}
                onClick={runOptimization}
              >
                Run Optimization
              </Button>
            </Box>
          </Grid>

          {/* Optimization Results */}
          {optimizationResults && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Optimization Results
                  </Typography>
                  {optimizationResults.optimizations?.map((opt, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Typography variant="subtitle1">
                          {opt.type.replace('_', ' ').toUpperCase()}: {opt.action}
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2">
                          {opt.type === 'cache_optimization' && (
                            <>Current hit rate: {(opt.current_hit_rate * 100).toFixed(1)}%</>
                          )}
                          {opt.type === 'database_optimization' && (
                            <>Slow query count: {opt.slow_query_count}</>
                          )}
                          {opt.type === 'memory_optimization' && (
                            <>Current usage: {opt.current_usage?.toFixed(1)}%</>
                          )}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Optimization Tools */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Cache Optimization
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Optimize cache performance and hit rates
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setCacheDialog(true)}
                >
                  Manage Cache
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Database Optimization
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Optimize queries and database performance
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setQueryDialog(true)}
                >
                  Analyze Queries
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 5 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Performance Settings</Typography>
              <Button
                variant="contained"
                startIcon={<Settings />}
                onClick={() => setSettingsDialog(true)}
              >
                Configure Settings
              </Button>
            </Box>
          </Grid>

          {/* Current Settings */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Current Settings
                </Typography>
                {dashboardData?.settings && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="body2">Cache TTL: {dashboardData.settings.cache_ttl}s</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Max Cache Size: {dashboardData.settings.max_cache_size}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Slow Query Threshold: {dashboardData.settings.slow_query_threshold}s</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Check Interval: {dashboardData.settings.performance_check_interval}s</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2">Auto Optimize: {dashboardData.settings.auto_optimize ? 'Enabled' : 'Disabled'}</Typography>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Cache Operations Dialog */}
      <Dialog open={cacheDialog} onClose={() => setCacheDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Cache Operations</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Cache Key"
                value={cacheRequest.key}
                onChange={(e) => setCacheRequest({ ...cacheRequest, key: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Cache Value"
                multiline
                rows={3}
                value={cacheRequest.value}
                onChange={(e) => setCacheRequest({ ...cacheRequest, value: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="TTL (seconds)"
                type="number"
                value={cacheRequest.ttl}
                onChange={(e) => setCacheRequest({ ...cacheRequest, ttl: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCacheDialog(false)}>Cancel</Button>
          <Button onClick={cacheGet} variant="outlined">Get</Button>
          <Button onClick={cacheSet} variant="contained">Set</Button>
        </DialogActions>
      </Dialog>

      {/* Query Analysis Dialog */}
      <Dialog open={queryDialog} onClose={() => setQueryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Query Analysis</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="SQL Query"
                multiline
                rows={8}
                value={queryRequest.query}
                onChange={(e) => setQueryRequest({ ...queryRequest, query: e.target.value })}
                placeholder="SELECT * FROM users WHERE..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setQueryDialog(false)}>Cancel</Button>
          <Button onClick={analyzeQuery} variant="contained">Analyze</Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsDialog} onClose={() => setSettingsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Performance Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Cache TTL (seconds)"
                type="number"
                value={performanceSettings.cache_ttl}
                onChange={(e) => setPerformanceSettings({ ...performanceSettings, cache_ttl: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Max Cache Size"
                type="number"
                value={performanceSettings.max_cache_size}
                onChange={(e) => setPerformanceSettings({ ...performanceSettings, max_cache_size: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Slow Query Threshold (seconds)"
                type="number"
                step="0.1"
                value={performanceSettings.slow_query_threshold}
                onChange={(e) => setPerformanceSettings({ ...performanceSettings, slow_query_threshold: parseFloat(e.target.value) })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Check Interval (seconds)"
                type="number"
                value={performanceSettings.performance_check_interval}
                onChange={(e) => setPerformanceSettings({ ...performanceSettings, performance_check_interval: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={performanceSettings.auto_optimize}
                    onChange={(e) => setPerformanceSettings({ ...performanceSettings, auto_optimize: e.target.checked })}
                  />
                }
                label="Auto Optimize"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialog(false)}>Cancel</Button>
          <Button onClick={updateSettings} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>

      {/* Optimization Results Dialog */}
      <Dialog open={optimizationDialog} onClose={() => setOptimizationDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Optimization Results</DialogTitle>
        <DialogContent>
          {optimizationResults && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Found {optimizationResults.optimization_count} optimization opportunities
              </Typography>
              {optimizationResults.optimizations?.map((opt, index) => (
                <Card key={index} sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      {opt.type.replace('_', ' ').toUpperCase()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {opt.action}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOptimizationDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PERFORMANCE_OPTIMIZATION_DASHBOARD;
