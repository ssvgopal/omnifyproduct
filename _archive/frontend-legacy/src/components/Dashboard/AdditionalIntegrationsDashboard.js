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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Divider
} from '@mui/material';
import {
  IntegrationInstructions,
  Add,
  Edit,
  Delete,
  PlayArrow,
  Stop,
  Refresh,
  CheckCircle,
  Error,
  Warning,
  Settings,
  Visibility,
  Download,
  Upload,
  Webhook,
  Sync,
  ExpandMore,
  CloudSync,
  Api,
  Security,
  Speed
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts';

const ADDITIONAL_INTEGRATIONS_DASHBOARD = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [createDialog, setCreateDialog] = useState(false);
  const [testDialog, setTestDialog] = useState(false);
  const [syncDialog, setSyncDialog] = useState(false);
  const [webhookDialog, setWebhookDialog] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [supportedPlatforms, setSupportedPlatforms] = useState([]);
  const [platformCapabilities, setPlatformCapabilities] = useState({});

  // Form states
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    description: '',
    platform_type: '',
    integration_type: '',
    credentials: {},
    settings: {},
    webhook_url: ''
  });

  const [testResult, setTestResult] = useState(null);
  const [syncRequest, setSyncRequest] = useState({
    operation: '',
    data: {}
  });

  const [webhookData, setWebhookData] = useState({});

  useEffect(() => {
    loadDashboardData();
    loadIntegrations();
    loadSupportedPlatforms();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/additional-integrations/dashboard?organization_id=default');
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    }
  };

  const loadIntegrations = async () => {
    try {
      const response = await fetch('/api/v1/additional-integrations/integrations?organization_id=default');
      const data = await response.json();
      setIntegrations(data.integrations || []);
    } catch (err) {
      setError('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const loadSupportedPlatforms = async () => {
    try {
      const response = await fetch('/api/v1/additional-integrations/platforms');
      const data = await response.json();
      setSupportedPlatforms(data.platforms || []);
    } catch (err) {
      setError('Failed to load supported platforms');
    }
  };

  const loadPlatformCapabilities = async (platformType) => {
    try {
      const response = await fetch(`/api/v1/additional-integrations/platforms/${platformType}/capabilities`);
      const data = await response.json();
      setPlatformCapabilities(prev => ({
        ...prev,
        [platformType]: data.capabilities
      }));
    } catch (err) {
      setError('Failed to load platform capabilities');
    }
  };

  const createIntegration = async () => {
    try {
      const response = await fetch('/api/v1/additional-integrations/integrations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newIntegration)
      });

      if (response.ok) {
        setCreateDialog(false);
        setNewIntegration({
          name: '',
          description: '',
          platform_type: '',
          integration_type: '',
          credentials: {},
          settings: {},
          webhook_url: ''
        });
        loadIntegrations();
        loadDashboardData();
      }
    } catch (err) {
      setError('Failed to create integration');
    }
  };

  const testIntegration = async () => {
    try {
      const response = await fetch(`/api/v1/additional-integrations/integrations/${selectedIntegration.integration_id}/test`, {
        method: 'POST'
      });

      const result = await response.json();
      setTestResult(result);
      setTestDialog(true);
    } catch (err) {
      setError('Failed to test integration');
    }
  };

  const syncIntegration = async () => {
    try {
      const response = await fetch(`/api/v1/additional-integrations/integrations/${selectedIntegration.integration_id}/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(syncRequest)
      });

      if (response.ok) {
        setSyncDialog(false);
        loadDashboardData();
      }
    } catch (err) {
      setError('Failed to sync integration');
    }
  };

  const deleteIntegration = async (integrationId) => {
    try {
      const response = await fetch(`/api/v1/additional-integrations/integrations/${integrationId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        loadIntegrations();
        loadDashboardData();
      }
    } catch (err) {
      setError('Failed to delete integration');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'pending': return 'warning';
      case 'error': return 'error';
      case 'configuring': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircle color="success" />;
      case 'error': return <Error color="error" />;
      case 'pending': return <Warning color="warning" />;
      case 'configuring': return <Settings color="info" />;
      default: return <Stop color="default" />;
    }
  };

  const getPlatformIcon = (platformType) => {
    switch (platformType) {
      case 'salesforce': return <CloudSync />;
      case 'hubspot': return <Api />;
      case 'mailchimp': return <IntegrationInstructions />;
      case 'wordpress': return <Webhook />;
      case 'woocommerce': return <Sync />;
      case 'twilio': return <Security />;
      case 'slack': return <Speed />;
      default: return <IntegrationInstructions />;
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
        Additional Integrations Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Integrations" />
        <Tab label="Platforms" />
        <Tab label="Sync Results" />
        <Tab label="Webhooks" />
        <Tab label="Settings" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Integration Statistics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Integration Statistics
                </Typography>
                {dashboardData?.integration_statistics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary">
                          {dashboardData.integration_statistics.total_integrations}
                        </Typography>
                        <Typography variant="body2">Total Integrations</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          {dashboardData.integration_statistics.active_integrations}
                        </Typography>
                        <Typography variant="body2">Active Integrations</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="error.main">
                          {dashboardData.integration_statistics.error_integrations}
                        </Typography>
                        <Typography variant="body2">Error Integrations</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {(dashboardData.integration_statistics.success_rate * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">Success Rate</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Sync Statistics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sync Statistics
                </Typography>
                {dashboardData?.sync_statistics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary">
                          {dashboardData.sync_statistics.total_syncs}
                        </Typography>
                        <Typography variant="body2">Total Syncs</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          {dashboardData.sync_statistics.successful_syncs}
                        </Typography>
                        <Typography variant="body2">Successful Syncs</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {(dashboardData.sync_statistics.sync_success_rate * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">Sync Success Rate</Typography>
                        <LinearProgress
                          variant="determinate"
                          value={dashboardData.sync_statistics.sync_success_rate * 100}
                          color="info"
                        />
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Integrations */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Integrations
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Platform</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Last Sync</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData?.recent_integrations?.map((integration) => (
                        <TableRow key={integration.integration_id}>
                          <TableCell>{integration.name}</TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              {getPlatformIcon(integration.platform_type)}
                              <Typography sx={{ ml: 1 }}>{integration.platform_type}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{integration.integration_type}</TableCell>
                          <TableCell>
                            <Chip
                              icon={getStatusIcon(integration.status)}
                              label={integration.status}
                              color={getStatusColor(integration.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(integration.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            {integration.last_sync ? new Date(integration.last_sync).toLocaleDateString() : 'Never'}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Test">
                              <IconButton size="small" onClick={() => {
                                setSelectedIntegration(integration);
                                testIntegration();
                              }}>
                                <PlayArrow />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Sync">
                              <IconButton size="small" onClick={() => {
                                setSelectedIntegration(integration);
                                setSyncDialog(true);
                              }}>
                                <Sync />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton size="small" onClick={() => deleteIntegration(integration.integration_id)}>
                                <Delete />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Integrations</Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setCreateDialog(true)}
              >
                Create Integration
              </Button>
            </Box>
          </Grid>

          {integrations.map((integration) => (
            <Grid item xs={12} md={6} lg={4} key={integration.integration_id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Typography variant="h6">{integration.name}</Typography>
                    <Chip
                      icon={getStatusIcon(integration.status)}
                      label={integration.status}
                      color={getStatusColor(integration.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    {integration.description}
                  </Typography>

                  <Box display="flex" alignItems="center" mb={2}>
                    {getPlatformIcon(integration.platform_type)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {integration.platform_type} • {integration.integration_type}
                    </Typography>
                  </Box>

                  <Box display="flex" justifyContent="space-between" mt={2}>
                    <Button
                      size="small"
                      onClick={() => {
                        setSelectedIntegration(integration);
                        testIntegration();
                      }}
                    >
                      Test
                    </Button>
                    <Button
                      size="small"
                      onClick={() => {
                        setSelectedIntegration(integration);
                        setSyncDialog(true);
                      }}
                    >
                      Sync
                    </Button>
                    <Button
                      size="small"
                      onClick={() => deleteIntegration(integration.integration_id)}
                      color="error"
                    >
                      Delete
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Supported Platforms
            </Typography>
          </Grid>

          {supportedPlatforms.map((platform) => (
            <Grid item xs={12} md={6} lg={4} key={platform}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    {getPlatformIcon(platform)}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {platform.replace('_', ' ').toUpperCase()}
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    Integration capabilities and features
                  </Typography>

                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => loadPlatformCapabilities(platform)}
                  >
                    View Capabilities
                  </Button>

                  {platformCapabilities[platform] && (
                    <Box mt={2}>
                      <Typography variant="subtitle2" gutterBottom>
                        Operations:
                      </Typography>
                      <Box display="flex" flexWrap="wrap" gap={0.5}>
                        {platformCapabilities[platform].operations?.slice(0, 3).map((op) => (
                          <Chip key={op} label={op} size="small" />
                        ))}
                        {platformCapabilities[platform].operations?.length > 3 && (
                          <Chip label={`+${platformCapabilities[platform].operations.length - 3} more`} size="small" />
                        )}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Sync Results
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Sync Operations
                </Typography>
                {dashboardData?.recent_syncs && dashboardData.recent_syncs.length > 0 ? (
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Integration</TableCell>
                          <TableCell>Operation</TableCell>
                          <TableCell>Status</TableCell>
                          <TableCell>Records</TableCell>
                          <TableCell>Duration</TableCell>
                          <TableCell>Started</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dashboardData.recent_syncs.map((sync) => (
                          <TableRow key={sync.sync_id}>
                            <TableCell>{sync.integration_id}</TableCell>
                            <TableCell>{sync.operation}</TableCell>
                            <TableCell>
                              <Chip
                                label={sync.status}
                                color={sync.status === 'completed' ? 'success' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              {sync.records_successful}/{sync.records_processed}
                            </TableCell>
                            <TableCell>{sync.duration?.toFixed(2)}s</TableCell>
                            <TableCell>
                              {new Date(sync.started_at).toLocaleString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Typography color="text.secondary">No sync operations found</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Webhook Events
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Webhook Events
                </Typography>
                <Typography color="text.secondary">
                  Webhook events will appear here when integrations send data to your endpoints.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 5 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Integration Settings
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Global Settings
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Auto-sync enabled"
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Webhook notifications"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Error notifications"
                />
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Rate Limits
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Configure rate limits for different platforms to prevent API throttling.
                </Typography>
                <Button variant="outlined" fullWidth sx={{ mt: 2 }}>
                  Configure Rate Limits
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Create Integration Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Integration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Integration Name"
                value={newIntegration.name}
                onChange={(e) => setNewIntegration({ ...newIntegration, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={newIntegration.description}
                onChange={(e) => setNewIntegration({ ...newIntegration, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Platform Type</InputLabel>
                <Select
                  value={newIntegration.platform_type}
                  onChange={(e) => setNewIntegration({ ...newIntegration, platform_type: e.target.value })}
                >
                  {supportedPlatforms.map((platform) => (
                    <MenuItem key={platform} value={platform}>
                      {platform.replace('_', ' ').toUpperCase()}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Integration Type</InputLabel>
                <Select
                  value={newIntegration.integration_type}
                  onChange={(e) => setNewIntegration({ ...newIntegration, integration_type: e.target.value })}
                >
                  <MenuItem value="crm">CRM</MenuItem>
                  <MenuItem value="email_marketing">Email Marketing</MenuItem>
                  <MenuItem value="social_media">Social Media</MenuItem>
                  <MenuItem value="ecommerce">E-commerce</MenuItem>
                  <MenuItem value="analytics">Analytics</MenuItem>
                  <MenuItem value="payment">Payment</MenuItem>
                  <MenuItem value="communication">Communication</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Webhook URL (Optional)"
                value={newIntegration.webhook_url}
                onChange={(e) => setNewIntegration({ ...newIntegration, webhook_url: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Credentials (JSON format)
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={JSON.stringify(newIntegration.credentials, null, 2)}
                onChange={(e) => {
                  try {
                    setNewIntegration({ ...newIntegration, credentials: JSON.parse(e.target.value) });
                  } catch (err) {
                    // Invalid JSON, keep as string
                  }
                }}
                placeholder='{"api_key": "your_api_key", "base_url": "https://api.example.com"}'
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button onClick={createIntegration} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Test Integration Dialog */}
      <Dialog open={testDialog} onClose={() => setTestDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Test Integration</DialogTitle>
        <DialogContent>
          {testResult && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Test Results
              </Typography>
              <Box display="flex" alignItems="center" mb={2}>
                {testResult.authenticated ? (
                  <CheckCircle color="success" />
                ) : (
                  <Error color="error" />
                )}
                <Typography sx={{ ml: 1 }}>
                  {testResult.authenticated ? 'Connection Successful' : 'Connection Failed'}
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Platform: {testResult.platform_type}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {testResult.status}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Tested at: {new Date(testResult.tested_at).toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Sync Integration Dialog */}
      <Dialog open={syncDialog} onClose={() => setSyncDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Sync Integration: {selectedIntegration?.name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Operation</InputLabel>
                <Select
                  value={syncRequest.operation}
                  onChange={(e) => setSyncRequest({ ...syncRequest, operation: e.target.value })}
                >
                  <MenuItem value="get_contacts">Get Contacts</MenuItem>
                  <MenuItem value="create_contact">Create Contact</MenuItem>
                  <MenuItem value="get_lists">Get Lists</MenuItem>
                  <MenuItem value="add_subscriber">Add Subscriber</MenuItem>
                  <MenuItem value="get_products">Get Products</MenuItem>
                  <MenuItem value="create_order">Create Order</MenuItem>
                  <MenuItem value="send_sms">Send SMS</MenuItem>
                  <MenuItem value="send_message">Send Message</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Data (JSON format - Optional)
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={JSON.stringify(syncRequest.data, null, 2)}
                onChange={(e) => {
                  try {
                    setSyncRequest({ ...syncRequest, data: JSON.parse(e.target.value) });
                  } catch (err) {
                    // Invalid JSON, keep as string
                  }
                }}
                placeholder='{"list_id": "123", "subscriber_data": {"email": "test@example.com"}}'
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSyncDialog(false)}>Cancel</Button>
          <Button onClick={syncIntegration} variant="contained">Sync</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ADDITIONAL_INTEGRATIONS_DASHBOARD;
