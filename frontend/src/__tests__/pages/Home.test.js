import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Home from '@/pages/Home';

// Mock all the dashboard components
jest.mock('@/components/Dashboard/PlatformSelector', () => {
  return function MockPlatformSelector({ onPlatformChange }) {
    return (
      <div data-testid="platform-selector">
        <button onClick={() => onPlatformChange('agentkit')}>AgentKit</button>
        <button onClick={() => onPlatformChange('gohighlevel')}>GoHighLevel</button>
        <button onClick={() => onPlatformChange('custom')}>Custom</button>
      </div>
    );
  };
});

jest.mock('@/components/Dashboard/BrainLogicPanel', () => {
  return function MockBrainLogicPanel() {
    return <div data-testid="brain-logic-panel">Brain Logic Panel</div>;
  };
});

jest.mock('@/components/Dashboard/AnalyticsDashboard', () => {
  return function MockAnalyticsDashboard() {
    return <div data-testid="analytics-dashboard">Analytics Dashboard</div>;
  };
});

jest.mock('@/components/Dashboard/EyesModule', () => {
  return function MockEyesModule() {
    return <div data-testid="eyes-module">EYES Module</div>;
  };
});

jest.mock('@/components/Dashboard/ProactiveIntelligenceDashboard', () => {
  return function MockProactiveIntelligenceDashboard() {
    return <div data-testid="proactive-intelligence">Proactive Intelligence</div>;
  };
});

jest.mock('@/components/Onboarding/MagicalOnboardingWizard', () => {
  return function MockMagicalOnboardingWizard() {
    return <div data-testid="magical-onboarding">Magical Onboarding</div>;
  };
});

jest.mock('@/components/Dashboard/InstantValueDeliveryDashboard', () => {
  return function MockInstantValueDeliveryDashboard() {
    return <div data-testid="instant-value">Instant Value Delivery</div>;
  };
});

jest.mock('@/components/Dashboard/CustomerOrchestrationDashboard', () => {
  return function MockCustomerOrchestrationDashboard() {
    return <div data-testid="customer-orchestration">Customer Orchestration</div>;
  };
});

jest.mock('@/components/Dashboard/PredictiveIntelligenceDashboard', () => {
  return function MockPredictiveIntelligenceDashboard() {
    return <div data-testid="predictive-intelligence">Predictive Intelligence</div>;
  };
});

jest.mock('@/components/Dashboard/AdaptiveClientLearningDashboard', () => {
  return function MockAdaptiveClientLearningDashboard() {
    return <div data-testid="adaptive-learning">Adaptive Learning</div>;
  };
});

jest.mock('@/components/Dashboard/HumanExpertInterventionDashboard', () => {
  return function MockHumanExpertInterventionDashboard() {
    return <div data-testid="expert-intervention">Expert Intervention</div>;
  };
});

jest.mock('@/components/Dashboard/CriticalDecisionHandHoldingDashboard', () => {
  return function MockCriticalDecisionHandHoldingDashboard() {
    return <div data-testid="critical-decision">Critical Decision</div>;
  };
});

// Mock the API service
jest.mock('@/services/api', () => ({
  getHealthStatus: jest.fn(),
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    const { getHealthStatus } = require('@/services/api');
    getHealthStatus.mockResolvedValue({
      status: 'healthy',
      timestamp: '2024-01-15T10:00:00Z',
      services: {
        backend: 'healthy',
        database: 'healthy',
        redis: 'healthy'
      }
    });
  });

  it('renders home page correctly', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('OmniFy Cloud Connect')).toBeInTheDocument();
      expect(screen.getByText('Autonomous Growth OS')).toBeInTheDocument();
    });
  });

  it('displays platform selector', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByTestId('platform-selector')).toBeInTheDocument();
    });
  });

  it('shows health status when available', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('System Status: Healthy')).toBeInTheDocument();
    });
  });

  it('handles platform changes correctly', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const agentkitButton = screen.getByText('AgentKit');
      fireEvent.click(agentkitButton);
      
      expect(screen.getByText('AI Agents')).toBeInTheDocument();
      expect(screen.getByText('Visual workflow automation')).toBeInTheDocument();
    });
  });

  it('switches between tabs correctly', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const brainLogicTab = screen.getByText('Brain Logic');
      fireEvent.click(brainLogicTab);
      
      expect(screen.getByTestId('brain-logic-panel')).toBeInTheDocument();
    });
  });

  it('displays all magic feature tabs', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('Onboarding')).toBeInTheDocument();
      expect(screen.getByText('Instant Value')).toBeInTheDocument();
      expect(screen.getByText('Orchestration')).toBeInTheDocument();
      expect(screen.getByText('Predictive Intelligence')).toBeInTheDocument();
      expect(screen.getByText('Adaptive Learning')).toBeInTheDocument();
      expect(screen.getByText('Expert Intervention')).toBeInTheDocument();
      expect(screen.getByText('Critical Decision')).toBeInTheDocument();
    });
  });

  it('shows onboarding wizard when onboarding tab is selected', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const onboardingTab = screen.getByText('Onboarding');
      fireEvent.click(onboardingTab);
      
      expect(screen.getByTestId('magical-onboarding')).toBeInTheDocument();
    });
  });

  it('shows instant value dashboard when instant value tab is selected', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const instantValueTab = screen.getByText('Instant Value');
      fireEvent.click(instantValueTab);
      
      expect(screen.getByTestId('instant-value')).toBeInTheDocument();
    });
  });

  it('handles health check errors gracefully', async () => {
    const { getHealthStatus } = require('@/services/api');
    getHealthStatus.mockRejectedValue(new Error('Health check failed'));
    
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('System Status: Unknown')).toBeInTheDocument();
    });
  });

  it('displays platform features based on selection', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      // Default should be AgentKit
      expect(screen.getByText('AI Agents')).toBeInTheDocument();
      expect(screen.getByText('ChatGPT Integration')).toBeInTheDocument();
      expect(screen.getByText('SOC 2 Compliant')).toBeInTheDocument();
      
      // Switch to GoHighLevel
      const gohighlevelButton = screen.getByText('GoHighLevel');
      fireEvent.click(gohighlevelButton);
      
      expect(screen.getByText('CRM System')).toBeInTheDocument();
      expect(screen.getByText('Marketing Automation')).toBeInTheDocument();
      expect(screen.getByText('White Label')).toBeInTheDocument();
    });
  });

  it('shows quick start steps', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('1. Select Your Platform')).toBeInTheDocument();
      expect(screen.getByText('2. Configure Brain Logic')).toBeInTheDocument();
      expect(screen.getByText('3. Connect Integrations')).toBeInTheDocument();
      expect(screen.getByText('4. Monitor Analytics')).toBeInTheDocument();
    });
  });
});



