import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BrainLogicPanel from '@/components/Dashboard/BrainLogicPanel';

// Mock the API service
jest.mock('@/services/api', () => ({
  getBrainModuleStats: jest.fn(),
  updateBrainModuleConfig: jest.fn(),
}));

describe('BrainLogicPanel', () => {
  const mockOnModuleSelect = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all brain modules correctly', () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    expect(screen.getByText('Creative Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Market Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Client Intelligence')).toBeInTheDocument();
    expect(screen.getByText('EYES Module')).toBeInTheDocument();
    expect(screen.getByText('Customization Engine')).toBeInTheDocument();
  });

  it('displays module statistics correctly', async () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('94%')).toBeInTheDocument(); // Creative accuracy
      expect(screen.getByText('1,247')).toBeInTheDocument(); // Creative predictions
      expect(screen.getByText('89%')).toBeInTheDocument(); // Market accuracy
    });
  });

  it('handles module selection correctly', () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    const creativeModule = screen.getByText('Creative Intelligence');
    fireEvent.click(creativeModule);
    
    expect(mockOnModuleSelect).toHaveBeenCalledWith('creative');
  });

  it('shows module status indicators', async () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Excellent')).toBeInTheDocument();
      expect(screen.getByText('Good')).toBeInTheDocument();
    });
  });

  it('handles module configuration updates', async () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    const configureButton = screen.getByText('Configure');
    fireEvent.click(configureButton);
    
    await waitFor(() => {
      expect(screen.getByText('Module Configuration')).toBeInTheDocument();
    });
  });

  it('displays progress bars for module accuracy', async () => {
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    await waitFor(() => {
      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars).toHaveLength(5); // One for each module
    });
  });

  it('handles error states gracefully', async () => {
    const { getBrainModuleStats } = require('@/services/api');
    getBrainModuleStats.mockRejectedValue(new Error('API Error'));
    
    render(<BrainLogicPanel onModuleSelect={mockOnModuleSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load module statistics')).toBeInTheDocument();
    });
  });
});
