import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnalyticsDashboard from '@/components/Dashboard/AnalyticsDashboard';

// Mock the API service
jest.mock('@/services/api', () => ({
  getCrossPlatformAnalytics: jest.fn(),
}));

describe('AnalyticsDashboard', () => {
  const mockAnalyticsData = {
    aggregated_metrics: {
      total_impressions: 1250000,
      total_clicks: 45000,
      total_conversions: 1250,
      total_spend: 25000,
      ctr: 3.6,
      conversion_rate: 2.78,
      cpc: 0.56,
      cpa: 20.0
    },
    platforms: {
      google_ads: {
        impressions: 500000,
        clicks: 18000,
        conversions: 500,
        spend: 10000
      },
      meta_ads: {
        impressions: 750000,
        clicks: 27000,
        conversions: 750,
        spend: 15000
      }
    },
    trends: {
      impressions_trend: 12.5,
      clicks_trend: 8.3,
      conversions_trend: 15.2,
      spend_trend: 5.7
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    const { getCrossPlatformAnalytics } = require('@/services/api');
    getCrossPlatformAnalytics.mockResolvedValue(mockAnalyticsData);
  });

  it('renders analytics dashboard correctly', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Cross-Platform Analytics')).toBeInTheDocument();
      expect(screen.getByText('Overview')).toBeInTheDocument();
      expect(screen.getByText('Platforms')).toBeInTheDocument();
      expect(screen.getByText('Trends')).toBeInTheDocument();
    });
  });

  it('displays aggregated metrics correctly', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('1.25M')).toBeInTheDocument(); // Total impressions
      expect(screen.getByText('45K')).toBeInTheDocument(); // Total clicks
      expect(screen.getByText('1.25K')).toBeInTheDocument(); // Total conversions
      expect(screen.getByText('$25K')).toBeInTheDocument(); // Total spend
    });
  });

  it('shows platform-specific data', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Google Ads')).toBeInTheDocument();
      expect(screen.getByText('Meta Ads')).toBeInTheDocument();
    });
  });

  it('handles time range changes', async () => {
    render(<AnalyticsDashboard />);
    
    const timeRangeSelect = screen.getByDisplayValue('30 Days');
    fireEvent.change(timeRangeSelect, { target: { value: '7_days' } });
    
    await waitFor(() => {
      const { getCrossPlatformAnalytics } = require('@/services/api');
      expect(getCrossPlatformAnalytics).toHaveBeenCalledWith('7_days');
    });
  });

  it('displays trend indicators correctly', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('+12.5%')).toBeInTheDocument(); // Impressions trend
      expect(screen.getByText('+8.3%')).toBeInTheDocument(); // Clicks trend
      expect(screen.getByText('+15.2%')).toBeInTheDocument(); // Conversions trend
    });
  });

  it('handles loading state', () => {
    const { getCrossPlatformAnalytics } = require('@/services/api');
    getCrossPlatformAnalytics.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<AnalyticsDashboard />);
    
    expect(screen.getByText('Loading analytics...')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    const { getCrossPlatformAnalytics } = require('@/services/api');
    getCrossPlatformAnalytics.mockRejectedValue(new Error('API Error'));
    
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load analytics data')).toBeInTheDocument();
    });
  });

  it('switches between tabs correctly', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      const platformsTab = screen.getByText('Platforms');
      fireEvent.click(platformsTab);
      
      expect(screen.getByText('Platform Performance')).toBeInTheDocument();
    });
  });

  it('formats numbers correctly', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      // Test various number formats
      expect(screen.getByText('1.25M')).toBeInTheDocument(); // 1,250,000
      expect(screen.getByText('45K')).toBeInTheDocument(); // 45,000
      expect(screen.getByText('1.25K')).toBeInTheDocument(); // 1,250
    });
  });
});



