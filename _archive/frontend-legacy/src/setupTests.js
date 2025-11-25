import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'text-encoding';

// Mock TextEncoder and TextDecoder for Node.js environment
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Mock window.matchMedia for components that use responsive design
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock performance API if not available
if (!global.performance) {
  global.performance = {
    now: () => Date.now(),
    mark: () => {},
    measure: () => {},
    timing: {
      navigationStart: Date.now(),
      loadEventEnd: Date.now() + 100
    }
  };
}
