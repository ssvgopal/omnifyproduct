// Error Fallback Component
import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

const ErrorFallback = ({ error, resetErrorBoundary, errorInfo }) => {
  const handleRetry = () => {
    if (resetErrorBoundary) {
      resetErrorBoundary();
    } else {
      window.location.reload();
    }
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="max-w-md w-full p-6 text-center">
        <div className="mb-4">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            Something went wrong
          </h1>
          <p className="text-gray-600 mb-4">
            We're sorry, but something unexpected happened. Please try again.
          </p>
        </div>

        {process.env.NODE_ENV === 'development' && error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-left">
            <h3 className="text-sm font-medium text-red-800 mb-2">Error Details:</h3>
            <pre className="text-xs text-red-700 whitespace-pre-wrap overflow-auto max-h-32">
              {error.toString()}
            </pre>
            {errorInfo && (
              <details className="mt-2">
                <summary className="text-xs text-red-600 cursor-pointer">
                  Component Stack
                </summary>
                <pre className="text-xs text-red-700 whitespace-pre-wrap overflow-auto max-h-32 mt-1">
                  {errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        )}

        <div className="space-y-3">
          <Button
            onClick={handleRetry}
            className="w-full"
            variant="default"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
          
          <Button
            onClick={handleGoHome}
            className="w-full"
            variant="outline"
          >
            <Home className="h-4 w-4 mr-2" />
            Go Home
          </Button>
        </div>

        <div className="mt-4 text-xs text-gray-500">
          If this problem persists, please contact support.
        </div>
      </Card>
    </div>
  );
};

export default ErrorFallback;
