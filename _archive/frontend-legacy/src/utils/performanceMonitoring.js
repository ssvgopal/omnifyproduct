// Bundle Analysis and Performance Monitoring
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

// Performance monitoring configuration
const PERFORMANCE_CONFIG = {
  // Core Web Vitals thresholds
  thresholds: {
    CLS: 0.1,    // Cumulative Layout Shift
    FID: 100,    // First Input Delay (ms)
    FCP: 1800,   // First Contentful Paint (ms)
    LCP: 2500,   // Largest Contentful Paint (ms)
    TTFB: 800,   // Time to First Byte (ms)
  },
  
  // Bundle size thresholds
  bundleSize: {
    maxInitialBundle: 500000,    // 500KB
    maxChunkSize: 200000,       // 200KB
    maxTotalSize: 2000000,       // 2MB
  },
  
  // Performance budgets
  budgets: {
    maxLoadTime: 3000,           // 3 seconds
    maxRenderTime: 1000,         // 1 second
    maxApiResponseTime: 2000,    // 2 seconds
  }
};

// Initialize performance monitoring
export const initPerformanceMonitoring = () => {
  // Monitor Core Web Vitals
  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getFCP(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
  
  // Monitor bundle performance
  monitorBundlePerformance();
  
  // Monitor API performance
  monitorApiPerformance();
  
  // Monitor rendering performance
  monitorRenderingPerformance();
};

// Send metrics to analytics service
function sendToAnalytics(metric) {
  const { name, value, delta, id } = metric;
  
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`Performance Metric: ${name} = ${value}ms (${delta}ms)`);
  }
  
  // Send to analytics service
  if (window.gtag) {
    window.gtag('event', name, {
      event_category: 'Web Vitals',
      value: Math.round(name === 'CLS' ? value * 1000 : value),
      event_label: id,
      non_interaction: true,
    });
  }
  
  // Send to custom analytics endpoint
  sendToCustomAnalytics(metric);
}

// Send to custom analytics endpoint
async function sendToCustomAnalytics(metric) {
  try {
    await fetch('/api/analytics/performance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        metric: metric.name,
        value: metric.value,
        delta: metric.delta,
        id: metric.id,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    });
  } catch (error) {
    console.error('Failed to send performance metrics:', error);
  }
}

// Monitor bundle performance
function monitorBundlePerformance() {
  // Monitor initial bundle load time
  window.addEventListener('load', () => {
    const loadTime = performance.now();
    const navigation = performance.getEntriesByType('navigation')[0];
    
    const metrics = {
      loadTime,
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
      firstPaint: getFirstPaint(),
      firstContentfulPaint: getFirstContentfulPaint(),
      bundleSize: getBundleSize(),
    };
    
    // Check against thresholds
    checkPerformanceThresholds(metrics);
    
    // Send metrics
    sendToCustomAnalytics({
      name: 'BundleLoad',
      value: loadTime,
      delta: loadTime,
      id: 'bundle-load',
    });
  });
}

// Monitor API performance
function monitorApiPerformance() {
  // Intercept fetch requests
  const originalFetch = window.fetch;
  
  window.fetch = async (...args) => {
    const startTime = performance.now();
    
    try {
      const response = await originalFetch(...args);
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Log API performance
      sendToCustomAnalytics({
        name: 'ApiResponse',
        value: duration,
        delta: duration,
        id: `api-${args[0]}`,
      });
      
      // Check against thresholds
      if (duration > PERFORMANCE_CONFIG.budgets.maxApiResponseTime) {
        console.warn(`Slow API response: ${args[0]} took ${duration}ms`);
      }
      
      return response;
    } catch (error) {
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // Log API error performance
      sendToCustomAnalytics({
        name: 'ApiError',
        value: duration,
        delta: duration,
        id: `api-error-${args[0]}`,
      });
      
      throw error;
    }
  };
}

// Monitor rendering performance
function monitorRenderingPerformance() {
  let renderStartTime = 0;
  
  // Monitor React rendering
  const originalCreateElement = React.createElement;
  React.createElement = function(...args) {
    if (renderStartTime === 0) {
      renderStartTime = performance.now();
    }
    return originalCreateElement.apply(this, args);
  };
  
  // Monitor render completion
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      if (entry.entryType === 'measure') {
        const renderTime = entry.duration;
        
        sendToCustomAnalytics({
          name: 'RenderTime',
          value: renderTime,
          delta: renderTime,
          id: 'render-time',
        });
        
        // Check against thresholds
        if (renderTime > PERFORMANCE_CONFIG.budgets.maxRenderTime) {
          console.warn(`Slow render: ${renderTime}ms`);
        }
      }
    }
  });
  
  observer.observe({ entryTypes: ['measure'] });
}

// Helper functions
function getFirstPaint() {
  const paintEntries = performance.getEntriesByType('paint');
  const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
  return firstPaint ? firstPaint.startTime : 0;
}

function getFirstContentfulPaint() {
  const paintEntries = performance.getEntriesByType('paint');
  const firstContentfulPaint = paintEntries.find(entry => entry.name === 'first-contentful-paint');
  return firstContentfulPaint ? firstContentfulPaint.startTime : 0;
}

function getBundleSize() {
  const resources = performance.getEntriesByType('resource');
  let totalSize = 0;
  
  resources.forEach(resource => {
    if (resource.name.includes('.js') || resource.name.includes('.css')) {
      totalSize += resource.transferSize || 0;
    }
  });
  
  return totalSize;
}

function checkPerformanceThresholds(metrics) {
  const warnings = [];
  
  if (metrics.loadTime > PERFORMANCE_CONFIG.budgets.maxLoadTime) {
    warnings.push(`Load time exceeded threshold: ${metrics.loadTime}ms > ${PERFORMANCE_CONFIG.budgets.maxLoadTime}ms`);
  }
  
  if (metrics.bundleSize > PERFORMANCE_CONFIG.bundleSize.maxInitialBundle) {
    warnings.push(`Bundle size exceeded threshold: ${metrics.bundleSize} bytes > ${PERFORMANCE_CONFIG.bundleSize.maxInitialBundle} bytes`);
  }
  
  if (warnings.length > 0) {
    console.warn('Performance warnings:', warnings);
    
    // Send warnings to analytics
    sendToCustomAnalytics({
      name: 'PerformanceWarning',
      value: warnings.length,
      delta: warnings.length,
      id: 'performance-warnings',
    });
  }
}

// Bundle analysis utilities
export const analyzeBundle = () => {
  const analysis = {
    totalSize: 0,
    chunkCount: 0,
    largestChunk: 0,
    duplicateModules: [],
    unusedModules: [],
  };
  
  // Analyze webpack chunks
  if (window.__webpack_require__) {
    const chunks = window.__webpack_require__.cache;
    
    Object.keys(chunks).forEach(moduleId => {
      const module = chunks[moduleId];
      if (module && module.exports) {
        analysis.totalSize += module.exports.toString().length;
        analysis.chunkCount++;
        
        if (module.exports.toString().length > analysis.largestChunk) {
          analysis.largestChunk = module.exports.toString().length;
        }
      }
    });
  }
  
  return analysis;
};

// Performance optimization recommendations
export const getPerformanceRecommendations = () => {
  const recommendations = [];
  
  // Check bundle size
  const bundleSize = getBundleSize();
  if (bundleSize > PERFORMANCE_CONFIG.bundleSize.maxInitialBundle) {
    recommendations.push({
      type: 'bundle-size',
      priority: 'high',
      message: `Initial bundle size is ${Math.round(bundleSize / 1024)}KB. Consider code splitting.`,
      action: 'Implement lazy loading for large components'
    });
  }
  
  // Check for unused modules
  const analysis = analyzeBundle();
  if (analysis.unusedModules.length > 0) {
    recommendations.push({
      type: 'unused-modules',
      priority: 'medium',
      message: `${analysis.unusedModules.length} unused modules detected.`,
      action: 'Remove unused imports and dependencies'
    });
  }
  
  // Check for duplicate modules
  if (analysis.duplicateModules.length > 0) {
    recommendations.push({
      type: 'duplicate-modules',
      priority: 'medium',
      message: `${analysis.duplicateModules.length} duplicate modules detected.`,
      action: 'Consolidate duplicate dependencies'
    });
  }
  
  return recommendations;
};

// Export performance monitoring functions
export default {
  initPerformanceMonitoring,
  analyzeBundle,
  getPerformanceRecommendations,
  PERFORMANCE_CONFIG,
};



