import React from 'react';
import { logger } from '../services/logger';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error with comprehensive context
    logger.trackErrorBoundary(error, errorInfo, errorInfo.componentStack);

    this.setState({
      error,
      errorInfo
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReload = () => {
    logger.trackUserAction('error_boundary_reload');
    window.location.reload();
  };

  handleReportIssue = () => {
    logger.trackUserAction('error_boundary_report_issue');

    // Create issue report
    const issueReport = {
      error: this.state.error?.toString(),
      stack: this.state.error?.stack,
      componentStack: this.state.errorInfo?.componentStack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    };

    // Copy to clipboard for easy reporting
    navigator.clipboard.writeText(JSON.stringify(issueReport, null, 2))
      .then(() => {
        alert('Error details copied to clipboard. Please paste in your issue report.');
      })
      .catch(() => {
        alert('Error details generated. Please check console for details.');
        console.error('Error Boundary Report:', issueReport);
      });
  };

  render() {
    if (this.state.hasError) {
      // Custom error UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="error-boundary" style={{
          padding: '20px',
          margin: '20px',
          border: '2px solid #ff6b6b',
          borderRadius: '8px',
          backgroundColor: '#fff5f5',
          textAlign: 'center'
        }}>
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ color: '#d63031', marginBottom: '10px' }}>
              😵 Oops! Something went wrong
            </h2>
            <p style={{ color: '#636e72', marginBottom: '20px' }}>
              We're sorry for the inconvenience. An unexpected error occurred.
            </p>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <p style={{ color: '#636e72', fontSize: '14px', marginBottom: '10px' }}>
              Error: {this.state.error?.message || 'Unknown error'}
            </p>
            {process.env.NODE_ENV === 'development' && (
              <details style={{ textAlign: 'left', marginTop: '10px' }}>
                <summary style={{ cursor: 'pointer', color: '#0984e3' }}>
                  Technical Details (Development Only)
                </summary>
                <pre style={{
                  backgroundColor: '#f8f9fa',
                  padding: '10px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  overflow: 'auto',
                  marginTop: '10px',
                  maxHeight: '200px'
                }}>
                  {this.state.error?.stack}
                </pre>
              </details>
            )}
          </div>

          <div>
            <button
              onClick={this.handleReload}
              style={{
                padding: '10px 20px',
                marginRight: '10px',
                backgroundColor: '#0984e3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🔄 Reload Page
            </button>

            <button
              onClick={this.handleReportIssue}
              style={{
                padding: '10px 20px',
                backgroundColor: '#e17055',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              📋 Report Issue
            </button>
          </div>

          <div style={{
            marginTop: '20px',
            padding: '10px',
            backgroundColor: '#ffeaa7',
            borderRadius: '4px',
            fontSize: '12px',
            color: '#d63031'
          }}>
            If this problem persists, please contact support with the error details.
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
