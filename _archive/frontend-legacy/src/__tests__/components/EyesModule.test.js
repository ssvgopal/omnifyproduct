import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EyesModule from '@/components/Dashboard/EyesModule';

// Mock the API service
jest.mock('@/services/api', () => ({
  getEyesModuleData: jest.fn(),
}));

describe('EyesModule', () => {
  const mockEyesData = {
    segments: [
      {
        segment_id: 'seg_1',
        name: 'High Value Customers',
        size: 1250,
        avg_lifetime_value: 2500,
        churn_risk: 'low',
        last_activity: '2024-01-15'
      },
      {
        segment_id: 'seg_2',
        name: 'At Risk Customers',
        size: 850,
        avg_lifetime_value: 1200,
        churn_risk: 'high',
        last_activity: '2024-01-10'
      }
    ],
    churn_predictions: [
      {
        customer_id: 'cust_1',
        name: 'John Doe',
        churn_probability: 0.85,
        risk_level: 'high',
        last_activity: '2024-01-05',
        predicted_churn_date: '2024-02-15'
      }
    ],
    cross_platform_insights: {
      total_customers: 10000,
      active_customers: 8500,
      churned_customers: 1500,
      avg_engagement_score: 7.2
    },
    learning_insights: {
      patterns_identified: 15,
      accuracy_improvement: 12.5,
      new_segments_discovered: 3
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    const { getEyesModuleData } = require('@/services/api');
    getEyesModuleData.mockResolvedValue(mockEyesData);
  });

  it('renders EYES module correctly', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('EYES Module')).toBeInTheDocument();
      expect(screen.getByText('Customer Segmentation')).toBeInTheDocument();
      expect(screen.getByText('Churn Prediction')).toBeInTheDocument();
      expect(screen.getByText('Cross-Platform Insights')).toBeInTheDocument();
      expect(screen.getByText('Learning Insights')).toBeInTheDocument();
    });
  });

  it('displays customer segments correctly', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('High Value Customers')).toBeInTheDocument();
      expect(screen.getByText('At Risk Customers')).toBeInTheDocument();
      expect(screen.getByText('1,250')).toBeInTheDocument(); // Segment size
      expect(screen.getByText('850')).toBeInTheDocument(); // At risk size
    });
  });

  it('shows churn predictions with risk levels', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('85%')).toBeInTheDocument(); // Churn probability
      expect(screen.getByText('High Risk')).toBeInTheDocument();
    });
  });

  it('displays cross-platform insights', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('10,000')).toBeInTheDocument(); // Total customers
      expect(screen.getByText('8,500')).toBeInTheDocument(); // Active customers
      expect(screen.getByText('1,500')).toBeInTheDocument(); // Churned customers
      expect(screen.getByText('7.2')).toBeInTheDocument(); // Engagement score
    });
  });

  it('shows learning insights', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('15')).toBeInTheDocument(); // Patterns identified
      expect(screen.getByText('12.5%')).toBeInTheDocument(); // Accuracy improvement
      expect(screen.getByText('3')).toBeInTheDocument(); // New segments
    });
  });

  it('handles time range changes', async () => {
    render(<EyesModule />);
    
    const timeRangeSelect = screen.getByDisplayValue('30d');
    fireEvent.change(timeRangeSelect, { target: { value: '7d' } });
    
    await waitFor(() => {
      const { getEyesModuleData } = require('@/services/api');
      expect(getEyesModuleData).toHaveBeenCalledWith('7d');
    });
  });

  it('switches between tabs correctly', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      const churnTab = screen.getByText('Churn Prediction');
      fireEvent.click(churnTab);
      
      expect(screen.getByText('Churn Risk Analysis')).toBeInTheDocument();
    });
  });

  it('handles loading state', () => {
    const { getEyesModuleData } = require('@/services/api');
    getEyesModuleData.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    render(<EyesModule />);
    
    expect(screen.getByText('Loading EYES data...')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    const { getEyesModuleData } = require('@/services/api');
    getEyesModuleData.mockRejectedValue(new Error('API Error'));
    
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load EYES data')).toBeInTheDocument();
    });
  });

  it('displays risk level colors correctly', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      const highRiskBadge = screen.getByText('High Risk');
      expect(highRiskBadge).toHaveClass('text-red-600', 'bg-red-100');
    });
  });

  it('formats dates correctly', async () => {
    render(<EyesModule />);
    
    await waitFor(() => {
      expect(screen.getByText('Jan 15, 2024')).toBeInTheDocument();
      expect(screen.getByText('Jan 10, 2024')).toBeInTheDocument();
    });
  });
});



