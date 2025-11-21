/**
 * Enhanced API Client for OmnifyProduct
 * Provides HTTP client with comprehensive logging and tracing
 * Upgraded from basic axios to include full observability
 */

import axios from 'axios';
import { logger } from './logger';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${BACKEND_URL}/api`;

// Configure axios instance with enhanced logging
const axiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30 second timeout
});

// Request interceptor for logging and tracing
axiosInstance.interceptors.request.use(
  (config) => {
    const startTime = Date.now();
    config.metadata = { startTime };

    // Log request start
    logger.info(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      eventType: 'api_request',
      method: config.method?.toUpperCase(),
      url: config.url,
      headers: config.headers,
      hasBody: !!config.data,
      timeout: config.timeout
    });

    return config;
  },
  (error) => {
    logger.error('API Request Error', error, {
      eventType: 'api_request_error',
      url: error.config?.url
    });
    return Promise.reject(error);
  }
);

// Response interceptor for logging and tracing
axiosInstance.interceptors.response.use(
  (response) => {
    const startTime = response.config.metadata?.startTime || Date.now();
    const duration = Date.now() - startTime;

    // Log successful response
    logger.trackApiCall(
      response.config.method?.toUpperCase(),
      response.config.url,
      startTime,
      true,
      null,
      {
        status: response.status,
        duration,
        responseSize: JSON.stringify(response.data || {}).length,
        contentType: response.headers['content-type']
      }
    );

    return response;
  },
  (error) => {
    const startTime = error.config?.metadata?.startTime || Date.now();
    const duration = Date.now() - startTime;

    // Determine error details
    const status = error.response?.status || 'NETWORK_ERROR';
    const statusText = error.response?.statusText || error.message;
    const url = error.config?.url || 'unknown';
    const method = error.config?.method?.toUpperCase() || 'UNKNOWN';

    // Log failed request
    logger.trackApiCall(
      method,
      url,
      startTime,
      false,
      error,
      {
        status,
        statusText,
        duration,
        errorCode: error.code,
        isTimeout: error.code === 'ECONNABORTED',
        isNetworkError: !error.response
      }
    );

    return Promise.reject(error);
  }
);

class OmnifyAPI {
  constructor() {
    this.client = axiosInstance;
  }

  // ========== PLATFORM ADAPTER APIs ==========

  // AgentKit APIs
  async createAgent(agentData) {
    try {
      logger.trackUserAction('create_agent', { agentType: agentData.agent_type });
      const response = await this.client.post('/agentkit/agents', agentData);
      logger.trackFeatureUsage('agentkit', 'agent_created', {
        agentId: response.data?.agent_id,
        agentType: agentData.agent_type
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to create agent', error, { agentData });
      throw error;
    }
  }

  async listAgents() {
    try {
      const response = await this.client.get('/agentkit/agents');
      logger.trackFeatureUsage('agentkit', 'agents_listed', {
        count: response.data?.length || 0
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to list agents', error);
      throw error;
    }
  }

  async executeAgent(agentId, inputData) {
    try {
      logger.trackFeatureUsage('agentkit', 'agent_execution_started', { agentId });
      const response = await this.client.post(`/agentkit/agents/${agentId}/execute`, {
        input_data: inputData
      });
      logger.trackFeatureUsage('agentkit', 'agent_execution_completed', {
        agentId,
        executionId: response.data?.execution_id
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to execute agent', error, { agentId, inputData });
      throw error;
    }
  }

  async createAgentKitWorkflow(workflowData) {
    try {
      logger.trackUserAction('create_workflow', {
        workflowName: workflowData.name,
        agentType: workflowData.agent_type
      });
      const response = await this.client.post('/agentkit/workflows', workflowData);
      logger.trackWorkflowStart(response.data?.workflow_id, {
        workflowName: workflowData.name,
        source: 'agentkit'
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to create AgentKit workflow', error, { workflowData });
      throw error;
    }
  }

  // ========== WORKFLOW EXECUTION WITH TRACING ==========

  async executeWorkflow(workflowId, inputData, userId = null, organizationId = null) {
    try {
      logger.trackWorkflowStart(workflowId, {
        inputSize: JSON.stringify(inputData).length,
        userId,
        organizationId
      });

      const response = await this.client.post(`/agentkit/workflows/${workflowId}/execute`, {
        input_data: inputData,
        user_id: userId,
        organization_id: organizationId
      });

      logger.trackWorkflowComplete(workflowId, {
        executionId: response.data?.execution_id,
        outputSize: JSON.stringify(response.data?.output_data || {}).length
      });

      return response.data;
    } catch (error) {
      logger.trackWorkflowError(workflowId, error, {
        inputData,
        userId,
        organizationId
      });
      throw error;
    }
  }

  // ========== BRAIN LOGIC APIs WITH TRACING ==========

  // Creative Intelligence
  async analyzeContent(content, context = null) {
    try {
      logger.trackFeatureUsage('brain_creative', 'content_analysis');
      const response = await this.client.post('/brain/creative/analyze', { content, context });
      return response.data;
    } catch (error) {
      logger.error('Failed to analyze content', error, { contentLength: content?.length });
      throw error;
    }
  }

  async repurposeContent(content, targetFormat, brandId = null) {
    try {
      logger.trackFeatureUsage('brain_creative', 'content_repurposing', { targetFormat });
      const response = await this.client.post('/brain/creative/repurpose', {
        content,
        target_format: targetFormat,
        brand_id: brandId
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to repurpose content', error, { targetFormat, brandId });
      throw error;
    }
  }

  async optimizeContent(content, platform, objective) {
    try {
      logger.trackFeatureUsage('brain_creative', 'content_optimization', { platform, objective });
      const response = await this.client.post('/brain/creative/optimize', {
        content,
        platform,
        objective
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to optimize content', error, { platform, objective });
      throw error;
    }
  }

  async registerBrand(brandData) {
    try {
      logger.trackUserAction('register_brand', { brandName: brandData.name });
      const response = await this.client.post('/brain/creative/brands', brandData);
      return response.data;
    } catch (error) {
      logger.error('Failed to register brand', error, { brandData });
      throw error;
    }
  }

  // Market Intelligence
  async analyzeVertical(vertical, data = null) {
    try {
      logger.trackFeatureUsage('brain_market', 'vertical_analysis', { vertical });
      const response = await this.client.post('/brain/market/analyze-vertical', { vertical, data });
      return response.data;
    } catch (error) {
      logger.error('Failed to analyze vertical', error, { vertical });
      throw error;
    }
  }

  async predictTrends(vertical, timeframe = '12_months') {
    try {
      logger.trackFeatureUsage('brain_market', 'trend_prediction', { vertical, timeframe });
      const response = await this.client.post('/brain/market/predict-trends', { vertical, timeframe });
      return response.data;
    } catch (error) {
      logger.error('Failed to predict trends', error, { vertical, timeframe });
      throw error;
    }
  }

  // ========== ANALYTICS & MONITORING APIs ==========

  async getCrossPlatformAnalytics(timeframe = '30_days') {
    try {
      logger.trackFeatureUsage('analytics', 'cross_platform_view', { timeframe });
      const response = await this.client.get('/analytics/cross-platform', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to get cross-platform analytics', error, { timeframe });
      throw error;
    }
  }

  async generateReport(reportConfig) {
    try {
      logger.trackUserAction('generate_report', {
        reportType: reportConfig.type,
        timeframe: reportConfig.timeframe
      });
      const response = await this.client.post('/analytics/reports', reportConfig);
      return response.data;
    } catch (error) {
      logger.error('Failed to generate report', error, { reportConfig });
      throw error;
    }
  }

  // ========== ADMIN DASHBOARD APIs ==========

  async getSystemHealth() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      logger.error('Failed to get system health', error);
      throw error;
    }
  }

  async getLogs(filters = {}) {
    try {
      logger.trackFeatureUsage('admin', 'logs_view', { filters });
      const response = await this.client.get('/admin/logs', { params: filters });
      return response.data;
    } catch (error) {
      logger.error('Failed to get logs', error, { filters });
      throw error;
    }
  }

  async analyzeClientIssue(clientId, issueDescription) {
    try {
      logger.trackFeatureUsage('admin', 'client_issue_analysis', { clientId });
      const response = await this.client.post('/admin/client-support', {
        clientId,
        issueDescription
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to analyze client issue', error, { clientId });
      throw error;
    }
  }

  async getWorkflowStats(timeRange = '24h') {
    try {
      const response = await this.client.get('/admin/workflow-stats', {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to get workflow stats', error, { timeRange });
      throw error;
    }
  }

  async getPerformanceMetrics(timeRange = '1h') {
    try {
      const response = await this.client.get('/admin/performance-metrics', {
        params: { timeRange }
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to get performance metrics', error, { timeRange });
      throw error;
    }
  }

  // ========== METABASE & BI APIs ==========

  async getMetabaseEmbedUrl(dashboardId, organizationId, userId) {
    try {
      const response = await this.client.get('/metabase/embedding/url', {
        params: { dashboard_id: dashboardId, organization_id: organizationId, user_id: userId }
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to get Metabase embed URL', error, { dashboardId });
      throw error;
    }
  }

  async generateMetabaseToken(dashboardId, organizationId, userId, expiresHours = 24) {
    try {
      const response = await this.client.post('/metabase/embedding/token', {
        dashboard_id: dashboardId,
        organization_id: organizationId,
        user_id: userId,
        expires_hours: expiresHours
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to generate Metabase token', error, { dashboardId });
      throw error;
    }
  }

  async getMetabaseTemplates() {
    try {
      const response = await this.client.get('/metabase/templates');
      return response.data;
    } catch (error) {
      logger.error('Failed to get Metabase templates', error);
      throw error;
    }
  }

  async createMetabaseDashboard(templateName, organizationId, customName = null) {
    try {
      const response = await this.client.post('/metabase/dashboard/create', {
        template_name: templateName,
        organization_id: organizationId,
        custom_name: customName
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to create Metabase dashboard', error, { templateName });
      throw error;
    }
  }

  // ========== REPORTING APIs ==========

  async createReport(reportData) {
    try {
      const response = await this.client.post('/reporting/reports', reportData);
      return response.data;
    } catch (error) {
      logger.error('Failed to create report', error, { reportData });
      throw error;
    }
  }

  async generateReport(reportConfig, organizationId) {
    try {
      const response = await this.client.post('/reporting/generate', {
        report_config: reportConfig,
        organization_id: organizationId
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to generate report', error, { reportConfig });
      throw error;
    }
  }

  async getScheduledReports(organizationId) {
    try {
      const response = await this.client.get('/reporting/scheduled-reports', {
        params: { organization_id: organizationId }
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to get scheduled reports', error, { organizationId });
      throw error;
    }
  }

  async createScheduledReport(scheduleData) {
    try {
      const response = await this.client.post('/reporting/scheduled-reports', scheduleData);
      return response.data;
    } catch (error) {
      logger.error('Failed to create scheduled report', error, { scheduleData });
      throw error;
    }
  }

  async updateScheduledReportStatus(scheduleId, status) {
    try {
      const response = await this.client.put(`/reporting/scheduled-reports/${scheduleId}/status`, {
        status
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to update scheduled report status', error, { scheduleId, status });
      throw error;
    }
  }

  async deleteScheduledReport(scheduleId) {
    try {
      const response = await this.client.delete(`/reporting/scheduled-reports/${scheduleId}`);
      return response.data;
    } catch (error) {
      logger.error('Failed to delete scheduled report', error, { scheduleId });
      throw error;
    }
  }

  // ========== INTEGRATIONS APIs ==========

  async listAvailableIntegrations(category = null) {
    try {
      const response = await this.client.get('/integrations/available', {
        params: category ? { category } : {}
      });
      return response.data;
    } catch (error) {
      logger.error('Failed to list available integrations', error, { category });
      throw error;
    }
  }

  async registerIntegration(integrationData) {
    try {
      logger.trackUserAction('register_integration', {
        type: integrationData.type,
        platform: integrationData.platform
      });
      const response = await this.client.post('/integrations/register', integrationData);
      return response.data;
    } catch (error) {
      logger.error('Failed to register integration', error, { integrationData });
      throw error;
    }
  }

  async listRegisteredIntegrations() {
    try {
      const response = await this.client.get('/integrations');
      return response.data;
    } catch (error) {
      logger.error('Failed to list registered integrations', error);
      throw error;
    }
  }

  // ========== INTEGRATION OAUTH APIs ==========

  async getIntegrationAuthUrl(platform) {
    try {
      const response = await this.client.get(`/integrations/${platform}/oauth/authorize`);
      return response.data;
    } catch (error) {
      logger.error(`Failed to get ${platform} auth URL`, error);
      throw error;
    }
  }

  async handleIntegrationCallback(platform, code, state) {
    try {
      const response = await this.client.post(`/integrations/${platform}/oauth/callback`, {
        code,
        state
      });
      return response.data;
    } catch (error) {
      logger.error(`Failed to handle ${platform} callback`, error);
      throw error;
    }
  }

  async refreshIntegrationToken(platform) {
    try {
      const response = await this.client.post(`/integrations/${platform}/oauth/refresh`);
      return response.data;
    } catch (error) {
      logger.error(`Failed to refresh ${platform} token`, error);
      throw error;
    }
  }

  async disconnectIntegration(platform) {
    try {
      const response = await this.client.delete(`/integrations/${platform}/oauth/disconnect`);
      return response.data;
    } catch (error) {
      logger.error(`Failed to disconnect ${platform}`, error);
      throw error;
    }
  }

  async getIntegrationStatus(platform) {
    try {
      const response = await this.client.get(`/integrations/${platform}/status`);
      return response.data;
    } catch (error) {
      // Return disconnected status if endpoint doesn't exist
      return { connected: false };
    }
  }

  // ========== HEALTH CHECK ==========

  async getHealthStatus() {
    return this.getSystemHealth();
  }
}

export default new OmnifyAPI();
