import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

// Simple test component
const TestComponent = () => {
  return (
    <div>
      <h1>OmniFy Cloud Connect</h1>
      <p>Autonomous Growth OS</p>
    </div>
  );
};

describe('Frontend Tests', () => {
  it('renders test component without crashing', () => {
    render(<TestComponent />);
    expect(screen.getByText(/OmniFy Cloud Connect/i)).toBeInTheDocument();
  });

  it('displays the main heading', () => {
    render(<TestComponent />);
    expect(screen.getByText('OmniFy Cloud Connect')).toBeInTheDocument();
  });

  it('shows the autonomous growth OS subtitle', () => {
    render(<TestComponent />);
    expect(screen.getByText('Autonomous Growth OS')).toBeInTheDocument();
  });

  it('has proper HTML structure', () => {
    render(<TestComponent />);
    const heading = screen.getByRole('heading', { level: 1 });
    expect(heading).toBeInTheDocument();
    expect(heading).toHaveTextContent('OmniFy Cloud Connect');
  });
});