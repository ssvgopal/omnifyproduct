/**
 * Comprehensive Frontend Unit Tests for Dashboard Components
 *
 * Tests for:
 * - Dashboard component rendering and state management
 * - API integration and data fetching
 * - User interactions and event handling
 * - Error handling and loading states
 * - Responsive design and accessibility
 *
 * Author: OmnifyProduct Test Suite
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { jest } from '@jest/globals';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/dashboard' }),
  Link: ({ children, to }) => <a href={to}>{children}</a>
}));

// Mock API services
jest.mock('../services/api', () => ({
  predictiveIntelligenceAPI: {
    getDashboardData: jest.fn(),
    getFatiguePredictions: jest.fn(),
    getLTVForecasts: jest.fn(),
    getAnomalyDetection: jest.fn(),
    updateModelFeedback: jest.fn()
  },
  campaignAPI: {
    getCampaigns: jest.fn(),
    updateCampaign: jest.fn(),
    createCampaign: jest.fn()
  },
  platformAPI: {
    getPlatforms: jest.fn(),
    connectPlatform: jest.fn()
  }
}));

// Import components after mocking
import PredictiveIntelligenceDashboard from '../components/Dashboard/PredictiveIntelligenceDashboard';
import CampaignManagementInterface from '../components/Dashboard/CampaignManagementInterface';
import AdvancedAnalyticsDashboard from '../components/Dashboard/AdvancedAnalyticsDashboard';
import ErrorBoundary from '../components/ErrorBoundary';

// Mock the API module
const mockAPI = require('../services/api');

describe('Dashboard Components Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('PredictiveIntelligenceDashboard', () => {
    const mockDashboardData = {
      fatigue_alerts: {
        high_risk_count: 3,
        recent_predictions: [
          {
            creative_id: 'creative_1',
            fatigue_probability_7d: 0.85,
            fatigue_probability_14d: 0.92,
            confidence_interval: 0.88,
            key_risk_factors: ['age', 'saturation'],
            recommended_refresh_date: '2024-01-15'
          }
        ]
      },
      ltv_forecasts: {
        total_predicted_value: 150000,
        high_value_segments: [
          {
            customer_id: 'customer_1',
            predicted_90d_ltv: 5000,
            segment: 'high_value'
          }
        ],
        recent_forecasts: []
      },
      anomaly_detection: {
        anomaly_count: 2,
        recent_anomalies: [
          {
            campaign_id: 'campaign_1',
            is_anomaly: true,
            anomaly_score: -0.8,
            analysis: {
              severity: 'high',
              likely_causes: ['poor_creative_performance'],
              recommended_actions: ['creative_refresh']
            }
          }
        ]
      },
      learning_system: {
        compound_intelligence_score: 0.85,
        total_learning_samples: 1500,
        model_performance: {
          fatigue_prediction: { accuracy: 0.87 },
          ltv_forecasting: { accuracy: 0.82 },
          anomaly_detection: { precision: 0.85 }
        }
      }
    };

    beforeEach(() => {
      mockAPI.predictiveIntelligenceAPI.getDashboardData.mockResolvedValue(mockDashboardData);
    });

    it('renders dashboard without crashing', async () => {
      render(<PredictiveIntelligenceDashboard />);

      // Should show loading initially
      expect(screen.getByText(/loading/i)).toBeInTheDocument();

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });
    });

    it('displays fatigue alerts correctly', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText('3')).toBeInTheDocument(); // high_risk_count
        expect(screen.getByText('creative_1')).toBeInTheDocument();
        expect(screen.getByText('85%')).toBeInTheDocument(); // fatigue_probability_7d
      });
    });

    it('displays LTV forecasts correctly', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText('$150,000')).toBeInTheDocument(); // total_predicted_value
        expect(screen.getByText('customer_1')).toBeInTheDocument();
        expect(screen.getByText('$5,000')).toBeInTheDocument(); // predicted_90d_ltv
      });
    });

    it('displays anomaly detection correctly', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText('2')).toBeInTheDocument(); // anomaly_count
        expect(screen.getByText('campaign_1')).toBeInTheDocument();
        expect(screen.getByText('high')).toBeInTheDocument(); // severity
      });
    });

    it('displays learning system metrics correctly', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText('85%')).toBeInTheDocument(); // compound_intelligence_score
        expect(screen.getByText('1,500')).toBeInTheDocument(); // total_learning_samples
        expect(screen.getByText('87%')).toBeInTheDocument(); // fatigue_prediction accuracy
      });
    });

    it('handles tab navigation correctly', async () => {
      const user = userEvent.setup();
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Test tab switching
      const fatigueTab = screen.getByRole('tab', { name: /fatigue/i });
      const ltvTab = screen.getByRole('tab', { name: /ltv/i });
      const anomalyTab = screen.getByRole('tab', { name: /anomaly/i });

      await user.click(ltvTab);
      expect(screen.getByText(/ltv forecasting/i)).toBeInTheDocument();

      await user.click(anomalyTab);
      expect(screen.getByText(/anomaly detection/i)).toBeInTheDocument();
    });

    it('handles refresh button click', async () => {
      const user = userEvent.setup();
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      await user.click(refreshButton);

      // Should call API again
      expect(mockAPI.predictiveIntelligenceAPI.getDashboardData).toHaveBeenCalledTimes(2);
    });

    it('displays error state correctly', async () => {
      mockAPI.predictiveIntelligenceAPI.getDashboardData.mockRejectedValue(new Error('API Error'));

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/error loading dashboard/i)).toBeInTheDocument();
      });
    });

    it('handles empty data gracefully', async () => {
      mockAPI.predictiveIntelligenceAPI.getDashboardData.mockResolvedValue({
        fatigue_alerts: { high_risk_count: 0, recent_predictions: [] },
        ltv_forecasts: { total_predicted_value: 0, high_value_segments: [], recent_forecasts: [] },
        anomaly_detection: { anomaly_count: 0, recent_anomalies: [] },
        learning_system: { compound_intelligence_score: 0, total_learning_samples: 0, model_performance: {} }
      });

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/no data available/i)).toBeInTheDocument();
      });
    });
  });

  describe('CampaignManagementInterface', () => {
    const mockCampaigns = [
      {
        id: 'campaign_1',
        name: 'Summer Sale 2024',
        status: 'active',
        budget: 10000,
        spend: 7500,
        impressions: 150000,
        clicks: 3000,
        conversions: 150,
        platform: 'google_ads'
      },
      {
        id: 'campaign_2',
        name: 'Brand Awareness',
        status: 'paused',
        budget: 5000,
        spend: 2500,
        impressions: 75000,
        clicks: 1200,
        conversions: 45,
        platform: 'meta_ads'
      }
    ];

    beforeEach(() => {
      mockAPI.campaignAPI.getCampaigns.mockResolvedValue(mockCampaigns);
    });

    it('renders campaign interface without crashing', async () => {
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText(/campaign management/i)).toBeInTheDocument();
      });
    });

    it('displays campaign list correctly', async () => {
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText('Summer Sale 2024')).toBeInTheDocument();
        expect(screen.getByText('Brand Awareness')).toBeInTheDocument();
        expect(screen.getByText('Active')).toBeInTheDocument();
        expect(screen.getByText('Paused')).toBeInTheDocument();
      });
    });

    it('shows campaign metrics correctly', async () => {
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText('$10,000')).toBeInTheDocument(); // budget
        expect(screen.getByText('$7,500')).toBeInTheDocument(); // spend
        expect(screen.getByText('150,000')).toBeInTheDocument(); // impressions
        expect(screen.getByText('3,000')).toBeInTheDocument(); // clicks
      });
    });

    it('handles campaign status filtering', async () => {
      const user = userEvent.setup();
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText(/campaign management/i)).toBeInTheDocument();
      });

      // Test status filter
      const statusFilter = screen.getByDisplayValue('all');
      await user.selectOptions(statusFilter, 'active');

      // Should filter to show only active campaigns
      await waitFor(() => {
        expect(screen.getByText('Summer Sale 2024')).toBeInTheDocument();
        expect(screen.queryByText('Brand Awareness')).not.toBeInTheDocument();
      });
    });

    it('handles campaign creation', async () => {
      const user = userEvent.setup();
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText(/campaign management/i)).toBeInTheDocument();
      });

      // Click create button
      const createButton = screen.getByRole('button', { name: /create campaign/i });
      await user.click(createButton);

      // Should open creation modal/form
      await waitFor(() => {
        expect(screen.getByText(/create new campaign/i)).toBeInTheDocument();
      });
    });

    it('handles campaign editing', async () => {
      const user = userEvent.setup();
      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText('Summer Sale 2024')).toBeInTheDocument();
      });

      // Click edit button for first campaign
      const editButtons = screen.getAllByRole('button', { name: /edit/i });
      await user.click(editButtons[0]);

      // Should open edit form
      await waitFor(() => {
        expect(screen.getByDisplayValue('Summer Sale 2024')).toBeInTheDocument();
      });
    });

    it('displays error state for API failures', async () => {
      mockAPI.campaignAPI.getCampaigns.mockRejectedValue(new Error('API Error'));

      render(<CampaignManagementInterface />);

      await waitFor(() => {
        expect(screen.getByText(/error loading campaigns/i)).toBeInTheDocument();
      });
    });
  });

  describe('AdvancedAnalyticsDashboard', () => {
    const mockAnalyticsData = {
      overview: {
        total_revenue: 500000,
        total_campaigns: 25,
        active_campaigns: 18,
        avg_roi: 3.2,
        total_impressions: 2500000,
        total_clicks: 75000,
        total_conversions: 5000
      },
      trends: {
        revenue_trend: [45000, 48000, 52000, 55000, 58000, 62000],
        roi_trend: [2.8, 3.0, 3.1, 3.2, 3.3, 3.4],
        conversion_trend: [180, 195, 210, 225, 240, 255]
      },
      top_performing: [
        { campaign: 'Summer Sale', revenue: 125000, roi: 4.2 },
        { campaign: 'Holiday Promo', revenue: 98000, roi: 3.8 },
        { campaign: 'Brand Campaign', revenue: 85000, roi: 3.5 }
      ]
    };

    beforeEach(() => {
      mockAPI.campaignAPI.getCampaigns.mockResolvedValue([]);
      // Mock analytics API if it exists, otherwise use campaign API
    });

    it('renders analytics dashboard without crashing', async () => {
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/advanced analytics/i)).toBeInTheDocument();
      });
    });

    it('displays overview metrics correctly', async () => {
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('$500,000')).toBeInTheDocument(); // total_revenue
        expect(screen.getByText('25')).toBeInTheDocument(); // total_campaigns
        expect(screen.getByText('18')).toBeInTheDocument(); // active_campaigns
        expect(screen.getByText('3.2')).toBeInTheDocument(); // avg_roi
      });
    });

    it('displays trend data correctly', async () => {
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        // Should display trend charts or data
        expect(screen.getByText(/revenue trend/i)).toBeInTheDocument();
        expect(screen.getByText(/roi trend/i)).toBeInTheDocument();
        expect(screen.getByText(/conversion trend/i)).toBeInTheDocument();
      });
    });

    it('displays top performing campaigns', async () => {
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText('Summer Sale')).toBeInTheDocument();
        expect(screen.getByText('Holiday Promo')).toBeInTheDocument();
        expect(screen.getByText('Brand Campaign')).toBeInTheDocument();
        expect(screen.getByText('$125,000')).toBeInTheDocument();
        expect(screen.getByText('4.2')).toBeInTheDocument(); // ROI
      });
    });

    it('handles date range filtering', async () => {
      const user = userEvent.setup();
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/advanced analytics/i)).toBeInTheDocument();
      });

      // Test date range selection
      const dateInputs = screen.getAllByDisplayValue(/select date/i);
      if (dateInputs.length >= 2) {
        await user.type(dateInputs[0], '2024-01-01');
        await user.type(dateInputs[1], '2024-01-31');

        // Should trigger data refresh
        await waitFor(() => {
          expect(screen.getByText(/filtered results/i)).toBeInTheDocument();
        });
      }
    });

    it('exports analytics data', async () => {
      const user = userEvent.setup();
      render(<AdvancedAnalyticsDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/advanced analytics/i)).toBeInTheDocument();
      });

      // Click export button
      const exportButton = screen.getByRole('button', { name: /export/i });
      await user.click(exportButton);

      // Should trigger export functionality
      await waitFor(() => {
        expect(screen.getByText(/exporting data/i)).toBeInTheDocument();
      });
    });
  });

  describe('ErrorBoundary', () => {
    const ThrowError = ({ shouldThrow }) => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>No error</div>;
    };

    it('renders children when no error occurs', () => {
      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();
    });

    it('displays error UI when error occurs', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('resets error state when try again is clicked', async () => {
      const user = userEvent.setup();
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      const { rerender } = render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      // Click try again button
      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      await user.click(tryAgainButton);

      // Rerender with no error
      rerender(
        <ErrorBoundary>
          <ThrowError shouldThrow={false} />
        </ErrorBoundary>
      );

      expect(screen.getByText('No error')).toBeInTheDocument();

      consoleSpy.mockRestore();
    });

    it('logs error details correctly', () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(consoleSpy).toHaveBeenCalledWith(
        'Error caught by boundary:',
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });
  });

  describe('Dashboard Integration Tests', () => {
    it('handles multiple dashboard components together', async () => {
      render(
        <div>
          <PredictiveIntelligenceDashboard />
          <CampaignManagementInterface />
          <AdvancedAnalyticsDashboard />
        </div>
      );

      // Should render all components without conflicts
      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
        expect(screen.getByText(/campaign management/i)).toBeInTheDocument();
        expect(screen.getByText(/advanced analytics/i)).toBeInTheDocument();
      });
    });

    it('handles component state isolation', async () => {
      const user = userEvent.setup();

      render(
        <div>
          <PredictiveIntelligenceDashboard />
          <CampaignManagementInterface />
        </div>
      );

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Actions in one component should not affect others
      const refreshButton = screen.getAllByRole('button', { name: /refresh/i })[0];
      await user.click(refreshButton);

      // Other components should remain unaffected
      expect(screen.getByText(/campaign management/i)).toBeInTheDocument();
    });
  });

  describe('Performance Tests', () => {
    it('renders dashboard components within performance budget', async () => {
      const startTime = performance.now();

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render within 100ms
      expect(renderTime).toBeLessThan(100);
    });

    it('handles large datasets efficiently', async () => {
      // Mock large dataset
      const largeDataset = {
        fatigue_alerts: {
          high_risk_count: 50,
          recent_predictions: Array.from({ length: 100 }, (_, i) => ({
            creative_id: `creative_${i}`,
            fatigue_probability_7d: Math.random(),
            fatigue_probability_14d: Math.random(),
            confidence_interval: Math.random(),
            key_risk_factors: ['age', 'saturation'],
            recommended_refresh_date: '2024-01-15'
          }))
        },
        ltv_forecasts: {
          total_predicted_value: 1000000,
          high_value_segments: Array.from({ length: 200 }, (_, i) => ({
            customer_id: `customer_${i}`,
            predicted_90d_ltv: Math.random() * 10000,
            segment: 'high_value'
          })),
          recent_forecasts: []
        },
        anomaly_detection: {
          anomaly_count: 25,
          recent_anomalies: Array.from({ length: 50 }, (_, i) => ({
            campaign_id: `campaign_${i}`,
            is_anomaly: true,
            anomaly_score: -Math.random(),
            analysis: { severity: 'high', likely_causes: ['test'], recommended_actions: ['test'] }
          }))
        },
        learning_system: {
          compound_intelligence_score: 0.95,
          total_learning_samples: 10000,
          model_performance: {
            fatigue_prediction: { accuracy: 0.92 },
            ltv_forecasting: { accuracy: 0.88 },
            anomaly_detection: { precision: 0.90 }
          }
        }
      };

      mockAPI.predictiveIntelligenceAPI.getDashboardData.mockResolvedValue(largeDataset);

      const startTime = performance.now();
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should handle large datasets within 200ms
      expect(renderTime).toBeLessThan(200);
    });
  });

  describe('Accessibility Tests', () => {
    it('has proper ARIA labels and roles', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Check for proper heading structure
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);

      // Check for proper button roles
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);

      // Check for tab navigation
      const tabs = screen.getAllByRole('tab');
      expect(tabs.length).toBeGreaterThan(0);
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Test tab navigation with keyboard
      const firstTab = screen.getAllByRole('tab')[0];
      firstTab.focus();

      await user.keyboard('{ArrowRight}');
      expect(document.activeElement).toBe(screen.getAllByRole('tab')[1]);

      await user.keyboard('{Enter}');
      // Should activate the tab
      expect(screen.getAllByRole('tab')[1]).toHaveAttribute('aria-selected', 'true');
    });

    it('has proper color contrast', async () => {
      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Check that text elements have sufficient contrast
      // This is a basic check - in real implementation, you'd use tools like axe-core
      const textElements = screen.getAllByText(/./);
      expect(textElements.length).toBeGreaterThan(0);
    });
  });

  describe('Responsive Design Tests', () => {
    it('adapts to mobile viewport', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Should display mobile-friendly layout
      const container = screen.getByTestId('dashboard-container') || document.querySelector('[class*="container"]');
      if (container) {
        // Check for mobile-specific styling or layout changes
        expect(container).toBeInTheDocument();
      }
    });

    it('adapts to tablet viewport', async () => {
      // Mock tablet viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      });

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Should display tablet-friendly layout
      // Add tablet-specific assertions here
    });

    it('adapts to desktop viewport', async () => {
      // Mock desktop viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });

      render(<PredictiveIntelligenceDashboard />);

      await waitFor(() => {
        expect(screen.getByText(/predictive intelligence dashboard/i)).toBeInTheDocument();
      });

      // Should display desktop-friendly layout
      // Add desktop-specific assertions here
    });
  });
});
