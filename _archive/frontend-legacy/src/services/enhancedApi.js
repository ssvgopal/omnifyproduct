// Enhanced API Service with Retry Logic and Error Handling
import axios from 'axios';
import { apiErrorHandler, networkErrorHandler, errorRecoveryStrategies } from '@/utils/errorHandling';

// Create axios instance with retry configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Check if error is retryable
    if (apiErrorHandler.isRetryableError(error) && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Retry with exponential backoff
        const response = await errorRecoveryStrategies.retry(
          () => apiClient(originalRequest),
          { maxRetries: 3, delay: 1000 }
        );
        return response;
      } catch (retryError) {
        // If retry fails, handle the error
        return Promise.reject(apiErrorHandler.handleApiError(retryError));
      }
    }
    
    // Handle non-retryable errors
    return Promise.reject(apiErrorHandler.handleApiError(error));
  }
);

// Enhanced API service with retry logic
class EnhancedApiService {
  constructor() {
    this.client = apiClient;
    this.cache = new Map();
    this.pendingRequests = new Map();
  }
  
  // Generic request method with retry logic
  async request(config) {
    const cacheKey = this.getCacheKey(config);
    
    // Check cache first
    if (config.method === 'GET' && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 300000) { // 5 minutes
        return cached.data;
      }
    }
    
    // Check if request is already pending
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }
    
    // Make request with retry logic
    const requestPromise = this.client.request(config)
      .then(response => {
        // Cache successful responses
        if (config.method === 'GET') {
          this.cache.set(cacheKey, {
            data: response.data,
            timestamp: Date.now(),
          });
        }
        
        // Remove from pending requests
        this.pendingRequests.delete(cacheKey);
        
        return response.data;
      })
      .catch(error => {
        // Remove from pending requests
        this.pendingRequests.delete(cacheKey);
        
        // Handle error with fallback strategies
        return this.handleRequestError(error, config);
      });
    
    // Store pending request
    this.pendingRequests.set(cacheKey, requestPromise);
    
    return requestPromise;
  }
  
  // Handle request errors with fallback strategies
  async handleRequestError(error, config) {
    // Try fallback to cache for GET requests
    if (config.method === 'GET') {
      const cacheKey = this.getCacheKey(config);
      const cached = this.cache.get(cacheKey);
      
      if (cached) {
        console.warn('Using cached data due to request failure');
        return cached.data;
      }
    }
    
    // Try graceful degradation
    if (config.fallback) {
      try {
        return await config.fallback();
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    }
    
    // Re-throw the original error
    throw error;
  }
  
  // Get cache key for request
  getCacheKey(config) {
    return `${config.method}:${config.url}:${JSON.stringify(config.params || {})}`;
  }
  
  // Clear cache
  clearCache() {
    this.cache.clear();
  }
  
  // Health check with retry logic
  async getHealthStatus() {
    return this.request({
      method: 'GET',
      url: '/api/health',
      fallback: () => ({
        status: 'unknown',
        timestamp: new Date().toISOString(),
        services: {
          backend: 'unknown',
          database: 'unknown',
          redis: 'unknown'
        }
      })
    });
  }
  
  // Cross-platform analytics with retry logic
  async getCrossPlatformAnalytics(timeRange = '30_days') {
    return this.request({
      method: 'GET',
      url: '/api/analytics/cross-platform',
      params: { time_range: timeRange },
      fallback: () => ({
        aggregated_metrics: {
          total_impressions: 0,
          total_clicks: 0,
          total_conversions: 0,
          total_spend: 0,
          ctr: 0,
          conversion_rate: 0,
          cpc: 0,
          cpa: 0
        },
        platforms: {},
        trends: {}
      })
    });
  }
  
  // EYES module data with retry logic
  async getEyesModuleData(timeRange = '30d') {
    return this.request({
      method: 'GET',
      url: '/api/eyes/module-data',
      params: { time_range: timeRange },
      fallback: () => ({
        segments: [],
        churn_predictions: [],
        cross_platform_insights: {
          total_customers: 0,
          active_customers: 0,
          churned_customers: 0,
          avg_engagement_score: 0
        },
        learning_insights: {
          patterns_identified: 0,
          accuracy_improvement: 0,
          new_segments_discovered: 0
        }
      })
    });
  }
  
  // Brain module stats with retry logic
  async getBrainModuleStats() {
    return this.request({
      method: 'GET',
      url: '/api/brain/module-stats',
      fallback: () => ({
        creative: { accuracy: 0, predictions: 0, status: 'unknown' },
        market: { accuracy: 0, predictions: 0, status: 'unknown' },
        client: { accuracy: 0, predictions: 0, status: 'unknown' },
        eyes: { accuracy: 0, predictions: 0, status: 'unknown' },
        customization: { accuracy: 0, predictions: 0, status: 'unknown' }
      })
    });
  }
  
  // Agent operations with retry logic
  async getAgents() {
    return this.request({
      method: 'GET',
      url: '/api/agentkit/agents',
      fallback: () => []
    });
  }
  
  async createAgent(agentData) {
    return this.request({
      method: 'POST',
      url: '/api/agentkit/agents',
      data: agentData
    });
  }
  
  async executeAgent(agentId, inputData) {
    return this.request({
      method: 'POST',
      url: `/api/agentkit/agents/${agentId}/execute`,
      data: inputData
    });
  }
  
  // Workflow operations with retry logic
  async getWorkflows() {
    return this.request({
      method: 'GET',
      url: '/api/agentkit/workflows',
      fallback: () => []
    });
  }
  
  async createWorkflow(workflowData) {
    return this.request({
      method: 'POST',
      url: '/api/agentkit/workflows',
      data: workflowData
    });
  }
  
  async executeWorkflow(workflowId, inputData) {
    return this.request({
      method: 'POST',
      url: `/api/agentkit/workflows/${workflowId}/execute`,
      data: inputData
    });
  }
  
  // Offline support
  async isOnline() {
    return navigator.onLine;
  }
  
  // Queue requests for offline mode
  queueRequest(config) {
    const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    queue.push({
      ...config,
      timestamp: Date.now()
    });
    localStorage.setItem('offline_queue', JSON.stringify(queue));
  }
  
  // Process offline queue when back online
  async processOfflineQueue() {
    if (!this.isOnline()) return;
    
    const queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    if (queue.length === 0) return;
    
    console.log(`Processing ${queue.length} queued requests`);
    
    for (const request of queue) {
      try {
        await this.request(request);
        console.log('Processed queued request:', request.url);
      } catch (error) {
        console.error('Failed to process queued request:', error);
      }
    }
    
    // Clear the queue
    localStorage.removeItem('offline_queue');
  }
}

// Create singleton instance
const enhancedApiService = new EnhancedApiService();

// Listen for online/offline events
window.addEventListener('online', () => {
  console.log('Back online, processing queued requests');
  enhancedApiService.processOfflineQueue();
});

window.addEventListener('offline', () => {
  console.log('Gone offline, requests will be queued');
});

export default enhancedApiService;



