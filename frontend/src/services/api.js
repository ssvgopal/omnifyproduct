import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

class OmnifyAPI {
  // ========== PLATFORM ADAPTER APIs ==========
  
  // AgentKit APIs
  async createAgent(agentData) {
    const response = await axios.post(`${API}/agentkit/agents`, agentData);
    return response.data;
  }

  async listAgents() {
    const response = await axios.get(`${API}/agentkit/agents`);
    return response.data;
  }

  async executeAgent(agentId, inputData) {
    const response = await axios.post(`${API}/agentkit/agents/${agentId}/execute`, { input_data: inputData });
    return response.data;
  }

  async createAgentKitWorkflow(workflowData) {
    const response = await axios.post(`${API}/agentkit/workflows`, workflowData);
    return response.data;
  }

  // GoHighLevel APIs
  async createGHLClient(clientData) {
    const response = await axios.post(`${API}/gohighlevel/clients`, clientData);
    return response.data;
  }

  async listGHLClients() {
    const response = await axios.get(`${API}/gohighlevel/clients`);
    return response.data;
  }

  async createGHLCampaign(campaignData) {
    const response = await axios.post(`${API}/gohighlevel/campaigns`, campaignData);
    return response.data;
  }

  async createGHLWorkflow(workflowData) {
    const response = await axios.post(`${API}/gohighlevel/workflows`, workflowData);
    return response.data;
  }

  // Custom Platform APIs
  async deployMicroservice(serviceData) {
    const response = await axios.post(`${API}/custom/microservices`, serviceData);
    return response.data;
  }

  async listMicroservices() {
    const response = await axios.get(`${API}/custom/microservices`);
    return response.data;
  }

  async scaleMicroservice(serviceId, replicas) {
    const response = await axios.post(`${API}/custom/microservices/${serviceId}/scale`, { service_id: serviceId, replicas });
    return response.data;
  }

  // ========== BRAIN LOGIC APIs ==========
  
  // Creative Intelligence
  async analyzeContent(content, context = null) {
    const response = await axios.post(`${API}/brain/creative/analyze`, { content, context });
    return response.data;
  }

  async repurposeContent(content, targetFormat, brandId = null) {
    const response = await axios.post(`${API}/brain/creative/repurpose`, {
      content,
      target_format: targetFormat,
      brand_id: brandId
    });
    return response.data;
  }

  async optimizeContent(content, platform, objective) {
    const response = await axios.post(`${API}/brain/creative/optimize`, {
      content,
      platform,
      objective
    });
    return response.data;
  }

  async registerBrand(brandData) {
    const response = await axios.post(`${API}/brain/creative/brands`, brandData);
    return response.data;
  }

  // Market Intelligence
  async analyzeVertical(vertical, data = null) {
    const response = await axios.post(`${API}/brain/market/analyze-vertical`, { vertical, data });
    return response.data;
  }

  async predictTrends(vertical, timeframe = '12_months') {
    const response = await axios.post(`${API}/brain/market/predict-trends`, { vertical, timeframe });
    return response.data;
  }

  async identifyOpportunities(vertical, clientProfile) {
    const response = await axios.post(`${API}/brain/market/identify-opportunities`, {
      vertical,
      client_profile: clientProfile
    });
    return response.data;
  }

  // Client Intelligence
  async analyzeClientBehavior(clientId, behaviorData) {
    const response = await axios.post(`${API}/brain/client/analyze-behavior`, {
      client_id: clientId,
      behavior_data: behaviorData
    });
    return response.data;
  }

  async predictClientSuccess(clientId) {
    const response = await axios.post(`${API}/brain/client/predict-success`, {
      client_id: clientId
    });
    return response.data;
  }

  async createClientProfile(profileData) {
    const response = await axios.post(`${API}/brain/client/profiles`, profileData);
    return response.data;
  }

  // Customization Engine
  async createConfiguration(configData) {
    const response = await axios.post(`${API}/brain/customize/configuration`, configData);
    return response.data;
  }

  async applyVerticalTemplate(vertical, clientId) {
    const response = await axios.post(`${API}/brain/customize/apply-template`, {
      vertical,
      client_id: clientId
    });
    return response.data;
  }

  async getCustomizationOptions(vertical, platform) {
    const response = await axios.get(`${API}/brain/customize/options`, {
      params: { vertical, platform }
    });
    return response.data;
  }

  // ========== SHARED COMPONENTS APIs ==========
  
  // Analytics
  async getCrossPlatformAnalytics(timeframe = '30_days') {
    const response = await axios.get(`${API}/analytics/cross-platform`, {
      params: { timeframe }
    });
    return response.data;
  }

  async generateReport(reportConfig) {
    const response = await axios.post(`${API}/analytics/reports`, reportConfig);
    return response.data;
  }

  // Integrations
  async listAvailableIntegrations(category = null) {
    const response = await axios.get(`${API}/integrations/available`, {
      params: category ? { category } : {}
    });
    return response.data;
  }

  async registerIntegration(integrationData) {
    const response = await axios.post(`${API}/integrations/register`, integrationData);
    return response.data;
  }

  async listRegisteredIntegrations() {
    const response = await axios.get(`${API}/integrations`);
    return response.data;
  }

  // Health Check
  async getHealthStatus() {
    const response = await axios.get(`${API}/health`);
    return response.data;
  }
}

export default new OmnifyAPI();
