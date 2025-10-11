/**
 * Frontend Logging Service for OmnifyProduct
 * Provides comprehensive client-side logging and tracing
 */

class FrontendLogger {
  constructor() {
    this.sessionId = this.generateId();
    this.userId = null;
    this.organizationId = null;
    this.buffer = [];
    this.maxBufferSize = 50;
    this.flushInterval = 30000; // 30 seconds
    this.apiEndpoint = '/api/logs/frontend';

    // Start periodic flush
    this.startPeriodicFlush();

    // Log session start
    this.info('Frontend session started', {
      eventType: 'session_start',
      userAgent: navigator.userAgent,
      url: window.location.href,
      screenResolution: `${window.screen.width}x${window.screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    });
  }

  generateId() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  setUser(userId, organizationId) {
    this.userId = userId;
    this.organizationId = organizationId;

    this.info('User context set', {
      eventType: 'user_context_set',
      userId,
      organizationId
    });
  }

  _createLogEntry(level, message, extra = {}) {
    return {
      timestamp: new Date().toISOString(),
      level: level.toUpperCase(),
      logger: 'frontend',
      message,
      sessionId: this.sessionId,
      userId: this.userId,
      organizationId: this.organizationId,
      url: window.location.href,
      userAgent: navigator.userAgent,
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      ...extra
    };
  }

  _log(level, message, extra = {}) {
    const logEntry = this._createLogEntry(level, message, extra);

    // Add to buffer
    this.buffer.push(logEntry);

    // Flush if buffer is full
    if (this.buffer.length >= this.maxBufferSize) {
      this.flush();
    }

    // Also log to console for development
    console[level](message, extra);
  }

  async flush() {
    if (this.buffer.length === 0) return;

    const logsToSend = [...this.buffer];
    this.buffer = [];

    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ logs: logsToSend })
      });

      if (!response.ok) {
        // Re-add to buffer if send failed
        this.buffer.unshift(...logsToSend);
        console.warn('Failed to send logs to server:', response.status);
      }
    } catch (error) {
      // Re-add to buffer if send failed
      this.buffer.unshift(...logsToSend);
      console.warn('Failed to send logs to server:', error);
    }
  }

  startPeriodicFlush() {
    setInterval(() => {
      this.flush();
    }, this.flushInterval);
  }

  // Logging methods
  debug(message, extra = {}) {
    this._log('debug', message, extra);
  }

  info(message, extra = {}) {
    this._log('info', message, extra);
  }

  warning(message, extra = {}) {
    this._log('warn', message, extra);
  }

  error(message, error = null, extra = {}) {
    const errorData = {
      ...extra,
      error: error?.toString(),
      stack: error?.stack,
      errorType: error?.name
    };
    this._log('error', message, errorData);
  }

  critical(message, error = null, extra = {}) {
    const errorData = {
      ...extra,
      error: error?.toString(),
      stack: error?.stack,
      errorType: error?.name
    };
    this._log('error', message, { ...errorData, critical: true });
  }

  // Specialized logging methods for OmnifyProduct

  trackUserAction(action, data = {}) {
    this.info(`User action: ${action}`, {
      eventType: 'user_action',
      action,
      ...data
    });
  }

  trackPageView(page, data = {}) {
    this.info(`Page view: ${page}`, {
      eventType: 'page_view',
      page,
      referrer: document.referrer,
      ...data
    });
  }

  trackApiCall(method, url, startTime, success, error = null, data = {}) {
    const duration = Date.now() - startTime;
    const logData = {
      eventType: 'api_call',
      method: method.toUpperCase(),
      url,
      duration,
      success,
      error: error?.toString(),
      ...data
    };

    if (success) {
      this.info(`API call completed: ${method} ${url}`, logData);
    } else {
      this.error(`API call failed: ${method} ${url}`, error, logData);
    }
  }

  trackWorkflowStart(workflowId, data = {}) {
    this.info(`Workflow started: ${workflowId}`, {
      eventType: 'workflow_start',
      workflowId,
      ...data
    });
  }

  trackWorkflowStep(workflowId, stepId, status, data = {}) {
    this.info(`Workflow step: ${workflowId} -> ${stepId}`, {
      eventType: 'workflow_step',
      workflowId,
      stepId,
      status,
      ...data
    });
  }

  trackWorkflowComplete(workflowId, data = {}) {
    this.info(`Workflow completed: ${workflowId}`, {
      eventType: 'workflow_complete',
      workflowId,
      ...data
    });
  }

  trackWorkflowError(workflowId, error, data = {}) {
    this.error(`Workflow failed: ${workflowId}`, error, {
      eventType: 'workflow_error',
      workflowId,
      ...data
    });
  }

  trackFormSubmission(formName, success, data = {}) {
    const eventType = success ? 'form_submit_success' : 'form_submit_error';
    const message = success ?
      `Form submitted successfully: ${formName}` :
      `Form submission failed: ${formName}`;

    if (success) {
      this.info(message, { eventType, formName, ...data });
    } else {
      this.error(message, null, { eventType, formName, ...data });
    }
  }

  trackPerformanceMetric(metric, value, data = {}) {
    this.info(`Performance metric: ${metric}`, {
      eventType: 'performance_metric',
      metric,
      value,
      ...data
    });
  }

  // Error boundary logging
  trackErrorBoundary(error, errorInfo, componentStack) {
    this.error('React Error Boundary caught an error', error, {
      eventType: 'error_boundary',
      componentStack,
      errorBoundary: true
    });
  }

  // Navigation tracking
  trackNavigation(from, to, data = {}) {
    this.info(`Navigation: ${from} -> ${to}`, {
      eventType: 'navigation',
      from,
      to,
      ...data
    });
  }

  // Feature usage tracking
  trackFeatureUsage(feature, action, data = {}) {
    this.info(`Feature used: ${feature} - ${action}`, {
      eventType: 'feature_usage',
      feature,
      action,
      ...data
    });
  }

  // Performance monitoring
  trackPageLoad(data = {}) {
    const loadTime = performance.now();
    this.trackPerformanceMetric('page_load', loadTime, {
      page: window.location.pathname,
      ...data
    });
  }

  trackInteraction(element, action, data = {}) {
    this.info(`User interaction: ${element} - ${action}`, {
      eventType: 'user_interaction',
      element,
      action,
      ...data
    });
  }
}

// Create global logger instance
export const logger = new FrontendLogger();

// Export for backward compatibility
export default logger;
