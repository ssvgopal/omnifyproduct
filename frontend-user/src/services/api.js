/**
 * API Service - Centralized HTTP client for backend communication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Get authentication headers
   */
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  /**
   * Handle API response
   */
  async handleResponse(response) {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || error.message || 'An error occurred');
    }
    return response.json();
  }

  /**
   * Generic request method
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      return await this.handleResponse(response);
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // ========== AUTHENTICATION ==========

  async login(email, password, rememberMe = false) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        remember_me: rememberMe,
      }),
    });
  }

  async register(organizationData, adminData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        org_data: organizationData,
        admin_data: adminData,
      }),
    });
  }

  async logout() {
    return this.request('/api/auth/logout', {
      method: 'POST',
    });
  }

  async refreshToken(refreshToken) {
    return this.request('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  async changePassword(currentPassword, newPassword) {
    return this.request('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }

  // ========== USER PROFILE ==========

  async getUserProfile(userId) {
    return this.request(`/api/personalization/profiles/${userId}`);
  }

  async updateUserProfile(userId, profileData) {
    return this.request(`/api/personalization/profiles/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // ========== INTEGRATIONS ==========

  async getIntegrations() {
    return this.request('/api/integrations');
  }

  async connectIntegration(platform, credentials) {
    return this.request(`/api/integrations/${platform}/connect`, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async disconnectIntegration(platform) {
    return this.request(`/api/integrations/${platform}/disconnect`, {
      method: 'DELETE',
    });
  }

  // ========== DASHBOARD DATA ==========

  async getDashboardMetrics(organizationId) {
    return this.request(`/api/brain-modules/memory/attribution/${organizationId}`);
  }

  async getPredictiveAlerts(organizationId) {
    return this.request(`/api/brain-modules/oracle/predictions/${organizationId}`);
  }

  async getRecommendations(organizationId) {
    return this.request(`/api/brain-modules/curiosity/recommendations/${organizationId}`);
  }

  // ========== WORKFLOWS ==========

  async getWorkflows(organizationId) {
    return this.request(`/api/workflows?organization_id=${organizationId}`);
  }

  async getWorkflowTraces(workflowId) {
    return this.request(`/api/workflows/${workflowId}/traces`);
  }
}

export default new ApiService();

