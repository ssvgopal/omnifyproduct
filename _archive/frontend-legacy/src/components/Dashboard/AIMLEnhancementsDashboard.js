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
  AccordionDetails
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  AutoGraph,
  BugReport,
  Analytics,
  PlayArrow,
  Stop,
  Delete,
  Edit,
  Visibility,
  ExpandMore,
  Refresh,
  Download,
  Upload,
  Settings
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const AI_ML_ENHANCEMENTS_DASHBOARD = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [createModelDialog, setCreateModelDialog] = useState(false);
  const [trainModelDialog, setTrainModelDialog] = useState(false);
  const [selectedModel, setSelectedModel] = useState(null);
  const [predictionDialog, setPredictionDialog] = useState(false);
  const [sentimentDialog, setSentimentDialog] = useState(false);
  const [anomalyDialog, setAnomalyDialog] = useState(false);

  // Form states
  const [newModel, setNewModel] = useState({
    name: '',
    description: '',
    model_type: 'regression',
    framework: 'scikit_learn',
    version: '1.0.0',
    hyperparameters: {}
  });

  const [trainingData, setTrainingData] = useState({
    target_column: '',
    training_data: []
  });

  const [predictionData, setPredictionData] = useState({});
  const [sentimentTexts, setSentimentTexts] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);

  useEffect(() => {
    loadDashboardData();
    loadModels();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/api/v1/ai-ml/dashboard?organization_id=default');
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data');
    }
  };

  const loadModels = async () => {
    try {
      const response = await fetch('/api/v1/ai-ml/models?organization_id=default');
      const data = await response.json();
      setModels(data.models || []);
    } catch (err) {
      setError('Failed to load models');
    } finally {
      setLoading(false);
    }
  };

  const createModel = async () => {
    try {
      const response = await fetch('/api/v1/ai-ml/models', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newModel)
      });

      if (response.ok) {
        setCreateModelDialog(false);
        setNewModel({
          name: '',
          description: '',
          model_type: 'regression',
          framework: 'scikit_learn',
          version: '1.0.0',
          hyperparameters: {}
        });
        loadModels();
      }
    } catch (err) {
      setError('Failed to create model');
    }
  };

  const trainModel = async () => {
    try {
      const response = await fetch(`/api/v1/ai-ml/models/${selectedModel.model_id}/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(trainingData)
      });

      if (response.ok) {
        setTrainModelDialog(false);
        loadModels();
        loadDashboardData();
      }
    } catch (err) {
      setError('Failed to train model');
    }
  };

  const makePrediction = async () => {
    try {
      const response = await fetch(`/api/v1/ai-ml/models/${selectedModel.model_id}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_data: predictionData })
      });

      const result = await response.json();
      alert(`Prediction: ${result.prediction} (Confidence: ${result.confidence})`);
      setPredictionDialog(false);
    } catch (err) {
      setError('Failed to make prediction');
    }
  };

  const analyzeSentiment = async () => {
    try {
      const response = await fetch('/api/v1/ai-ml/sentiment/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts: sentimentTexts })
      });

      const result = await response.json();
      alert(`Sentiment Analysis Complete: ${result.total_texts} texts analyzed`);
      setSentimentDialog(false);
    } catch (err) {
      setError('Failed to analyze sentiment');
    }
  };

  const detectAnomalies = async () => {
    try {
      const response = await fetch('/api/v1/ai-ml/anomaly-detection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: anomalyData })
      });

      const result = await response.json();
      alert(`Anomaly Detection Complete: ${result.anomaly_count} anomalies found`);
      setAnomalyDialog(false);
    } catch (err) {
      setError('Failed to detect anomalies');
    }
  };

  const deployModel = async (modelId) => {
    try {
      const response = await fetch(`/api/v1/ai-ml/models/${modelId}/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ environment: 'production' })
      });

      if (response.ok) {
        loadModels();
      }
    } catch (err) {
      setError('Failed to deploy model');
    }
  };

  const retireModel = async (modelId) => {
    try {
      const response = await fetch(`/api/v1/ai-ml/models/${modelId}/retire`, {
        method: 'POST'
      });

      if (response.ok) {
        loadModels();
      }
    } catch (err) {
      setError('Failed to retire model');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'trained': return 'success';
      case 'training': return 'warning';
      case 'deployed': return 'primary';
      case 'failed': return 'error';
      case 'retired': return 'default';
      default: return 'default';
    }
  };

  const getModelTypeIcon = (type) => {
    switch (type) {
      case 'regression': return <TrendingUp />;
      case 'classification': return <Psychology />;
      case 'clustering': return <AutoGraph />;
      case 'anomaly_detection': return <BugReport />;
      default: return <Analytics />;
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
        AI/ML Enhancements Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Models" />
        <Tab label="Predictions" />
        <Tab label="Analytics" />
        <Tab label="Tools" />
      </Tabs>

      {activeTab === 0 && (
        <Grid container spacing={3}>
          {/* Model Statistics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Statistics
                </Typography>
                {dashboardData?.model_statistics && (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="primary">
                          {dashboardData.model_statistics.total_models}
                        </Typography>
                        <Typography variant="body2">Total Models</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="success.main">
                          {dashboardData.model_statistics.trained_models}
                        </Typography>
                        <Typography variant="body2">Trained Models</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="info.main">
                          {dashboardData.model_statistics.deployed_models}
                        </Typography>
                        <Typography variant="body2">Deployed Models</Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box textAlign="center">
                        <Typography variant="h4" color="warning.main">
                          {(dashboardData.model_statistics.training_success_rate * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">Success Rate</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Model Performance */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Performance
                </Typography>
                {dashboardData?.model_performance && (
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={Object.entries(dashboardData.model_performance).map(([type, score]) => ({
                      type,
                      score: score * 100
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="type" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="score" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Models */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Models
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Framework</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Accuracy</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {dashboardData?.recent_models?.map((model) => (
                        <TableRow key={model.model_id}>
                          <TableCell>{model.name}</TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center">
                              {getModelTypeIcon(model.model_type)}
                              <Typography sx={{ ml: 1 }}>{model.model_type}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{model.framework}</TableCell>
                          <TableCell>
                            <Chip
                              label={model.status}
                              color={getStatusColor(model.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {model.accuracy_score ? `${(model.accuracy_score * 100).toFixed(1)}%` : 'N/A'}
                          </TableCell>
                          <TableCell>
                            {new Date(model.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton size="small">
                                <Visibility />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Deploy">
                              <IconButton size="small" onClick={() => deployModel(model.model_id)}>
                                <PlayArrow />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Retire">
                              <IconButton size="small" onClick={() => retireModel(model.model_id)}>
                                <Stop />
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
              <Typography variant="h6">ML Models</Typography>
              <Button
                variant="contained"
                startIcon={<Upload />}
                onClick={() => setCreateModelDialog(true)}
              >
                Create Model
              </Button>
            </Box>
          </Grid>

          {models.map((model) => (
            <Grid item xs={12} md={6} lg={4} key={model.model_id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={2}>
                    <Typography variant="h6">{model.name}</Typography>
                    <Chip
                      label={model.status}
                      color={getStatusColor(model.status)}
                      size="small"
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    {model.description}
                  </Typography>

                  <Box display="flex" alignItems="center" mb={1}>
                    {getModelTypeIcon(model.model_type)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {model.model_type} • {model.framework}
                    </Typography>
                  </Box>

                  {model.accuracy_score && (
                    <Box mb={2}>
                      <Typography variant="body2" gutterBottom>
                        Accuracy: {(model.accuracy_score * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={model.accuracy_score * 100}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}

                  <Box display="flex" justifyContent="space-between" mt={2}>
                    <Button
                      size="small"
                      onClick={() => {
                        setSelectedModel(model);
                        setTrainModelDialog(true);
                      }}
                      disabled={model.status === 'training'}
                    >
                      Train
                    </Button>
                    <Button
                      size="small"
                      onClick={() => {
                        setSelectedModel(model);
                        setPredictionDialog(true);
                      }}
                      disabled={model.status !== 'trained'}
                    >
                      Predict
                    </Button>
                    <Button
                      size="small"
                      onClick={() => deployModel(model.model_id)}
                      disabled={model.status !== 'trained'}
                    >
                      Deploy
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
              Prediction Tools
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Campaign Performance Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Predict campaign performance based on historical data
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setPredictionDialog(true)}
                >
                  Make Prediction
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Customer LTV Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Predict customer lifetime value
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setPredictionDialog(true)}
                >
                  Predict LTV
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Churn Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Predict customer churn probability
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setPredictionDialog(true)}
                >
                  Predict Churn
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Conversion Prediction
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Predict conversion probability
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setPredictionDialog(true)}
                >
                  Predict Conversion
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Analytics & Insights
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Performance Trends
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={[
                    { month: 'Jan', accuracy: 85 },
                    { month: 'Feb', accuracy: 87 },
                    { month: 'Mar', accuracy: 89 },
                    { month: 'Apr', accuracy: 91 },
                    { month: 'May', accuracy: 88 },
                    { month: 'Jun', accuracy: 92 }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip />
                    <Line type="monotone" dataKey="accuracy" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Model Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Regression', value: 40 },
                        { name: 'Classification', value: 35 },
                        { name: 'Clustering', value: 15 },
                        { name: 'NLP', value: 10 }
                      ]}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {[
                        { name: 'Regression', value: 40 },
                        { name: 'Classification', value: 35 },
                        { name: 'Clustering', value: 15 },
                        { name: 'NLP', value: 10 }
                      ].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={`hsl(${index * 90}, 70%, 50%)`} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              AI/ML Tools
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sentiment Analysis
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Analyze sentiment of customer feedback and social media posts
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setSentimentDialog(true)}
                >
                  Analyze Sentiment
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Anomaly Detection
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Detect anomalies in campaign performance and customer behavior
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => setAnomalyDialog(true)}
                >
                  Detect Anomalies
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Text Classification
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Classify customer support tickets and feedback
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  disabled
                >
                  Classify Text
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recommendation Engine
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  Generate personalized recommendations for customers
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  disabled
                >
                  Generate Recommendations
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Create Model Dialog */}
      <Dialog open={createModelDialog} onClose={() => setCreateModelDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create ML Model</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Model Name"
                value={newModel.name}
                onChange={(e) => setNewModel({ ...newModel, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={newModel.description}
                onChange={(e) => setNewModel({ ...newModel, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Model Type</InputLabel>
                <Select
                  value={newModel.model_type}
                  onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
                >
                  <MenuItem value="regression">Regression</MenuItem>
                  <MenuItem value="classification">Classification</MenuItem>
                  <MenuItem value="clustering">Clustering</MenuItem>
                  <MenuItem value="time_series">Time Series</MenuItem>
                  <MenuItem value="nlp">NLP</MenuItem>
                  <MenuItem value="anomaly_detection">Anomaly Detection</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Framework</InputLabel>
                <Select
                  value={newModel.framework}
                  onChange={(e) => setNewModel({ ...newModel, framework: e.target.value })}
                >
                  <MenuItem value="scikit_learn">Scikit-learn</MenuItem>
                  <MenuItem value="tensorflow">TensorFlow</MenuItem>
                  <MenuItem value="pytorch">PyTorch</MenuItem>
                  <MenuItem value="transformers">Transformers</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateModelDialog(false)}>Cancel</Button>
          <Button onClick={createModel} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Train Model Dialog */}
      <Dialog open={trainModelDialog} onClose={() => setTrainModelDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Train Model: {selectedModel?.name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Target Column"
                value={trainingData.target_column}
                onChange={(e) => setTrainingData({ ...trainingData, target_column: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary">
                Upload training data (CSV format)
              </Typography>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const csv = event.target.result;
                      // Parse CSV and set training data
                      setTrainingData({ ...trainingData, training_data: csv });
                    };
                    reader.readAsText(file);
                  }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTrainModelDialog(false)}>Cancel</Button>
          <Button onClick={trainModel} variant="contained">Train</Button>
        </DialogActions>
      </Dialog>

      {/* Prediction Dialog */}
      <Dialog open={predictionDialog} onClose={() => setPredictionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Make Prediction: {selectedModel?.name}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Enter input data for prediction
              </Typography>
              <TextField
                fullWidth
                label="Input Data (JSON)"
                multiline
                rows={6}
                value={JSON.stringify(predictionData, null, 2)}
                onChange={(e) => {
                  try {
                    setPredictionData(JSON.parse(e.target.value));
                  } catch (err) {
                    // Invalid JSON, keep as string
                  }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPredictionDialog(false)}>Cancel</Button>
          <Button onClick={makePrediction} variant="contained">Predict</Button>
        </DialogActions>
      </Dialog>

      {/* Sentiment Analysis Dialog */}
      <Dialog open={sentimentDialog} onClose={() => setSentimentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Sentiment Analysis</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Enter texts to analyze (one per line)
              </Typography>
              <TextField
                fullWidth
                label="Texts to Analyze"
                multiline
                rows={8}
                value={sentimentTexts.join('\n')}
                onChange={(e) => setSentimentTexts(e.target.value.split('\n').filter(t => t.trim()))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSentimentDialog(false)}>Cancel</Button>
          <Button onClick={analyzeSentiment} variant="contained">Analyze</Button>
        </DialogActions>
      </Dialog>

      {/* Anomaly Detection Dialog */}
      <Dialog open={anomalyDialog} onClose={() => setAnomalyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Anomaly Detection</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Upload data for anomaly detection (CSV format)
              </Typography>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      const csv = event.target.result;
                      setAnomalyData(csv);
                    };
                    reader.readAsText(file);
                  }
                }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnomalyDialog(false)}>Cancel</Button>
          <Button onClick={detectAnomalies} variant="contained">Detect</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AI_ML_ENHANCEMENTS_DASHBOARD;
