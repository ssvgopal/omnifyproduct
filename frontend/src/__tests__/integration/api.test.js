import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import axios from 'axios';
import api from '@/services/api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

describe('API Service Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Health Status API', () => {
    it('fetches health status successfully', async () => {
      const mockHealthData = {
        status: 'healthy',
        timestamp: '2024-01-15T10:00:00Z',
        services: {
          backend: 'healthy',
          database: 'healthy',
          redis: 'healthy'
        }
      };

      mockedAxios.get.mockResolvedValue({ data: mockHealthData });

      const result = await api.getHealthStatus();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/health');
      expect(result).toEqual(mockHealthData);
    });

    it('handles health status API errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network Error'));

      await expect(api.getHealthStatus()).rejects.toThrow('Network Error');
    });
  });

  describe('Cross Platform Analytics API', () => {
    it('fetches analytics data successfully', async () => {
      const mockAnalyticsData = {
        aggregated_metrics: {
          total_impressions: 1250000,
          total_clicks: 45000,
          total_conversions: 1250,
          total_spend: 25000
        },
        platforms: {
          google_ads: { impressions: 500000, clicks: 18000 },
          meta_ads: { impressions: 750000, clicks: 27000 }
        }
      };

      mockedAxios.get.mockResolvedValue({ data: mockAnalyticsData });

      const result = await api.getCrossPlatformAnalytics('30_days');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/analytics/cross-platform', {
        params: { time_range: '30_days' }
      });
      expect(result).toEqual(mockAnalyticsData);
    });

    it('handles analytics API errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Analytics API Error'));

      await expect(api.getCrossPlatformAnalytics('30_days')).rejects.toThrow('Analytics API Error');
    });
  });

  describe('EYES Module Data API', () => {
    it('fetches EYES module data successfully', async () => {
      const mockEyesData = {
        segments: [
          {
            segment_id: 'seg_1',
            name: 'High Value Customers',
            size: 1250,
            churn_risk: 'low'
          }
        ],
        churn_predictions: [
          {
            customer_id: 'cust_1',
            name: 'John Doe',
            churn_probability: 0.85,
            risk_level: 'high'
          }
        ]
      };

      mockedAxios.get.mockResolvedValue({ data: mockEyesData });

      const result = await api.getEyesModuleData('30d');

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/eyes/module-data', {
        params: { time_range: '30d' }
      });
      expect(result).toEqual(mockEyesData);
    });

    it('handles EYES module API errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('EYES API Error'));

      await expect(api.getEyesModuleData('30d')).rejects.toThrow('EYES API Error');
    });
  });

  describe('Brain Module Stats API', () => {
    it('fetches brain module statistics successfully', async () => {
      const mockStatsData = {
        creative: { accuracy: 94, predictions: 1247, status: 'excellent' },
        market: { accuracy: 89, predictions: 892, status: 'good' },
        client: { accuracy: 91, predictions: 1156, status: 'excellent' }
      };

      mockedAxios.get.mockResolvedValue({ data: mockStatsData });

      const result = await api.getBrainModuleStats();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/brain/module-stats');
      expect(result).toEqual(mockStatsData);
    });

    it('handles brain module stats API errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Brain Stats API Error'));

      await expect(api.getBrainModuleStats()).rejects.toThrow('Brain Stats API Error');
    });
  });

  describe('AgentKit Integration API', () => {
    it('fetches agents successfully', async () => {
      const mockAgentsData = [
        {
          agent_id: 'agent_1',
          name: 'Creative Intelligence Agent',
          agent_type: 'creative_intelligence',
          status: 'active'
        }
      ];

      mockedAxios.get.mockResolvedValue({ data: mockAgentsData });

      const result = await api.getAgents();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/agentkit/agents');
      expect(result).toEqual(mockAgentsData);
    });

    it('creates agent successfully', async () => {
      const mockAgentData = {
        name: 'Test Agent',
        agent_type: 'creative_intelligence',
        description: 'Test agent for integration testing'
      };

      const mockCreatedAgent = {
        agent_id: 'agent_new',
        ...mockAgentData,
        status: 'active',
        created_at: '2024-01-15T10:00:00Z'
      };

      mockedAxios.post.mockResolvedValue({ data: mockCreatedAgent });

      const result = await api.createAgent(mockAgentData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/agentkit/agents', mockAgentData);
      expect(result).toEqual(mockCreatedAgent);
    });

    it('executes agent successfully', async () => {
      const mockExecutionData = {
        agent_id: 'agent_1',
        input_data: {
          asset_url: 'https://example.com/creative.jpg',
          analysis_type: 'aida'
        }
      };

      const mockExecutionResult = {
        execution_id: 'exec_1',
        status: 'completed',
        results: {
          analysis_score: 8.5,
          recommendations: ['Improve headline', 'Add call-to-action']
        }
      };

      mockedAxios.post.mockResolvedValue({ data: mockExecutionResult });

      const result = await api.executeAgent(mockExecutionData.agent_id, mockExecutionData.input_data);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `/api/agentkit/agents/${mockExecutionData.agent_id}/execute`,
        mockExecutionData.input_data
      );
      expect(result).toEqual(mockExecutionResult);
    });
  });

  describe('Workflow Management API', () => {
    it('fetches workflows successfully', async () => {
      const mockWorkflowsData = [
        {
          workflow_id: 'workflow_1',
          name: 'Creative Analysis Workflow',
          status: 'active',
          steps: [
            { step_id: 'step_1', agent_type: 'creative_intelligence' },
            { step_id: 'step_2', agent_type: 'marketing_automation' }
          ]
        }
      ];

      mockedAxios.get.mockResolvedValue({ data: mockWorkflowsData });

      const result = await api.getWorkflows();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/agentkit/workflows');
      expect(result).toEqual(mockWorkflowsData);
    });

    it('creates workflow successfully', async () => {
      const mockWorkflowData = {
        name: 'Test Workflow',
        description: 'Test workflow for integration testing',
        steps: [
          {
            step_id: 'step_1',
            agent_type: 'creative_intelligence',
            input_data: { asset_url: 'https://example.com/test.jpg' }
          }
        ]
      };

      const mockCreatedWorkflow = {
        workflow_id: 'workflow_new',
        ...mockWorkflowData,
        status: 'active',
        created_at: '2024-01-15T10:00:00Z'
      };

      mockedAxios.post.mockResolvedValue({ data: mockCreatedWorkflow });

      const result = await api.createWorkflow(mockWorkflowData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/agentkit/workflows', mockWorkflowData);
      expect(result).toEqual(mockCreatedWorkflow);
    });

    it('executes workflow successfully', async () => {
      const mockExecutionData = {
        workflow_id: 'workflow_1',
        input_data: {
          campaign_name: 'Test Campaign',
          platforms: ['google_ads', 'meta_ads']
        }
      };

      const mockExecutionResult = {
        execution_id: 'exec_workflow_1',
        status: 'in_progress',
        progress: 0,
        current_step: 'step_1'
      };

      mockedAxios.post.mockResolvedValue({ data: mockExecutionResult });

      const result = await api.executeWorkflow(mockExecutionData.workflow_id, mockExecutionData.input_data);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `/api/agentkit/workflows/${mockExecutionData.workflow_id}/execute`,
        mockExecutionData.input_data
      );
      expect(result).toEqual(mockExecutionResult);
    });
  });

  describe('Error Handling', () => {
    it('handles network timeouts', async () => {
      mockedAxios.get.mockRejectedValue(new Error('timeout of 5000ms exceeded'));

      await expect(api.getHealthStatus()).rejects.toThrow('timeout of 5000ms exceeded');
    });

    it('handles 404 errors', async () => {
      mockedAxios.get.mockRejectedValue({
        response: {
          status: 404,
          data: { error: 'Not found' }
        }
      });

      await expect(api.getHealthStatus()).rejects.toMatchObject({
        response: {
          status: 404,
          data: { error: 'Not found' }
        }
      });
    });

    it('handles 500 errors', async () => {
      mockedAxios.get.mockRejectedValue({
        response: {
          status: 500,
          data: { error: 'Internal server error' }
        }
      });

      await expect(api.getHealthStatus()).rejects.toMatchObject({
        response: {
          status: 500,
          data: { error: 'Internal server error' }
        }
      });
    });
  });

  describe('Request Configuration', () => {
    it('sets correct base URL', () => {
      expect(mockedAxios.defaults.baseURL).toBe(process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000');
    });

    it('sets correct timeout', () => {
      expect(mockedAxios.defaults.timeout).toBe(10000);
    });

    it('includes authentication headers when token is available', () => {
      const token = 'test-jwt-token';
      localStorage.setItem('auth_token', token);

      // Re-import API service to get fresh instance
      jest.resetModules();
      require('@/services/api');

      expect(mockedAxios.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });
  });
});
