// Global Error Boundary with Retry Logic
import React from 'react';
import { ErrorBoundary } from 'react-error-boundary';
import ErrorFallback from '@/components/ui/ErrorFallback';

// Error logging service
const logError = (error, errorInfo) => {
  console.error('Global Error Boundary:', error, errorInfo);
  
  // Send to error tracking service
  if (window.gtag) {
    window.gtag('event', 'exception', {
      description: error.toString(),
      fatal: false,
    });
  }
  
  // Send to custom error endpoint
  fetch('/api/errors/log', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      error: error.toString(),
      stack: error.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    }),
  }).catch(err => {
    console.error('Failed to log error:', err);
  });
};

// Retry logic for failed operations
const retryOperation = async (operation, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      console.warn(`Attempt ${attempt} failed:`, error);
      
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Exponential backoff
      const waitTime = delay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
};

// Global Error Boundary Component
const GlobalErrorBoundary = ({ children }) => {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={logError}
      onReset={() => {
        // Clear any error state
        window.location.reload();
      }}
    >
      {children}
    </ErrorBoundary>
  );
};

// API Error Handler with Retry Logic
export const apiErrorHandler = {
  // Retry failed API calls
  async retryApiCall(apiCall, maxRetries = 3) {
    return retryOperation(apiCall, maxRetries);
  },
  
  // Handle different types of API errors
  handleApiError(error) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - show access denied message
          throw new Error('Access denied. Please contact your administrator.');
        case 404:
          // Not found - show not found message
          throw new Error('Resource not found.');
        case 429:
          // Rate limited - retry after delay
          throw new Error('Rate limited. Please try again later.');
        case 500:
          // Server error - show generic error
          throw new Error('Server error. Please try again later.');
        default:
          // Generic error
          throw new Error(data?.message || 'An error occurred. Please try again.');
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error. Please check your connection.');
    } else {
      // Other error
      throw new Error(error.message || 'An unexpected error occurred.');
    }
  },
  
  // Check if error is retryable
  isRetryableError(error) {
    if (error.response) {
      const status = error.response.status;
      // Retry on server errors and rate limits
      return status >= 500 || status === 429;
    }
    // Retry on network errors
    return !error.response;
  }
};

// Network Error Handler
export const networkErrorHandler = {
  // Check network connectivity
  isOnline() {
    return navigator.onLine;
  },
  
  // Handle offline state
  handleOfflineState() {
    if (!this.isOnline()) {
      throw new Error('You are currently offline. Please check your connection.');
    }
  },
  
  // Retry with exponential backoff
  async retryWithBackoff(operation, maxRetries = 3) {
    return retryOperation(operation, maxRetries);
  }
};

// Component Error Handler
export const componentErrorHandler = {
  // Handle component errors gracefully
  handleComponentError(error, errorInfo) {
    logError(error, errorInfo);
    
    // Show user-friendly error message
    const userMessage = this.getUserFriendlyMessage(error);
    return userMessage;
  },
  
  // Get user-friendly error messages
  getUserFriendlyMessage(error) {
    const errorMessage = error.toString().toLowerCase();
    
    if (errorMessage.includes('network')) {
      return 'Network error. Please check your connection.';
    } else if (errorMessage.includes('timeout')) {
      return 'Request timed out. Please try again.';
    } else if (errorMessage.includes('unauthorized')) {
      return 'Please log in to continue.';
    } else if (errorMessage.includes('forbidden')) {
      return 'Access denied. Please contact your administrator.';
    } else {
      return 'Something went wrong. Please try again.';
    }
  }
};

// Error Recovery Strategies
export const errorRecoveryStrategies = {
  // Retry failed operations
  async retry(operation, context = {}) {
    const { maxRetries = 3, delay = 1000 } = context;
    return retryOperation(operation, maxRetries, delay);
  },
  
  // Fallback to cached data
  async fallbackToCache(operation, cacheKey) {
    try {
      return await operation();
    } catch (error) {
      console.warn('Operation failed, falling back to cache:', error);
      
      const cachedData = localStorage.getItem(cacheKey);
      if (cachedData) {
        return JSON.parse(cachedData);
      }
      
      throw error;
    }
  },
  
  // Graceful degradation
  async gracefulDegradation(primaryOperation, fallbackOperation) {
    try {
      return await primaryOperation();
    } catch (error) {
      console.warn('Primary operation failed, using fallback:', error);
      return await fallbackOperation();
    }
  }
};

// Error Monitoring and Analytics
export const errorMonitoring = {
  // Track error metrics
  trackError(error, context = {}) {
    const errorData = {
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      context,
    };
    
    // Send to analytics
    if (window.gtag) {
      window.gtag('event', 'error', {
        error_message: error.message,
        error_type: error.name,
        error_context: JSON.stringify(context),
      });
    }
    
    // Send to custom endpoint
    fetch('/api/errors/track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorData),
    }).catch(err => {
      console.error('Failed to track error:', err);
    });
  },
  
  // Get error statistics
  getErrorStats() {
    const errors = JSON.parse(localStorage.getItem('error_stats') || '[]');
    return {
      totalErrors: errors.length,
      recentErrors: errors.filter(error => 
        new Date(error.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
      ).length,
      errorTypes: errors.reduce((acc, error) => {
        acc[error.type] = (acc[error.type] || 0) + 1;
        return acc;
      }, {}),
    };
  }
};

export default GlobalErrorBoundary;



