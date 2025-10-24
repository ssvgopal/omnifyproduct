// API Security and Request Validation
import { sanitizeFormData, validateEmail, validateURL } from '@/utils/inputSanitization';

// API security configuration
const API_SECURITY_CONFIG = {
  maxRequestSize: 10 * 1024 * 1024, // 10MB
  maxRequestTime: 30000, // 30 seconds
  allowedOrigins: [
    'http://localhost:3000',
    'https://omnify-cloud-connect.com',
    'https://www.omnify-cloud-connect.com'
  ],
  rateLimits: {
    default: { requests: 100, window: 60000 }, // 100 requests per minute
    auth: { requests: 5, window: 60000 }, // 5 auth requests per minute
    upload: { requests: 10, window: 60000 } // 10 upload requests per minute
  }
};

// Request validation middleware
export const validateRequest = (config) => {
  return async (request) => {
    // Validate request size
    if (request.body && request.body.length > API_SECURITY_CONFIG.maxRequestSize) {
      throw new Error('Request too large');
    }
    
    // Validate origin
    const origin = request.headers.get('origin');
    if (origin && !API_SECURITY_CONFIG.allowedOrigins.includes(origin)) {
      throw new Error('Invalid origin');
    }
    
    // Sanitize request data
    if (request.body) {
      try {
        const data = JSON.parse(request.body);
        const sanitized = sanitizeFormData(data);
        request.body = JSON.stringify(sanitized);
      } catch (error) {
        // If not JSON, sanitize as string
        request.body = sanitizeFormData({ data: request.body }).data;
      }
    }
    
    return request;
  };
};

// Rate limiting
class RateLimiter {
  constructor() {
    this.requests = new Map();
  }
  
  isAllowed(identifier, limit) {
    const now = Date.now();
    const windowStart = now - limit.window;
    
    if (!this.requests.has(identifier)) {
      this.requests.set(identifier, []);
    }
    
    const userRequests = this.requests.get(identifier);
    
    // Remove old requests outside the window
    const validRequests = userRequests.filter(time => time > windowStart);
    this.requests.set(identifier, validRequests);
    
    // Check if under limit
    if (validRequests.length >= limit.requests) {
      return false;
    }
    
    // Add current request
    validRequests.push(now);
    return true;
  }
  
  getRemainingRequests(identifier, limit) {
    const now = Date.now();
    const windowStart = now - limit.window;
    
    if (!this.requests.has(identifier)) {
      return limit.requests;
    }
    
    const userRequests = this.requests.get(identifier);
    const validRequests = userRequests.filter(time => time > windowStart);
    
    return Math.max(0, limit.requests - validRequests.length);
  }
}

const rateLimiter = new RateLimiter();

// Rate limiting middleware
export const rateLimitMiddleware = (limitType = 'default') => {
  return async (request) => {
    const identifier = getClientIdentifier(request);
    const limit = API_SECURITY_CONFIG.rateLimits[limitType];
    
    if (!rateLimiter.isAllowed(identifier, limit)) {
      throw new Error('Rate limit exceeded');
    }
    
    return request;
  };
};

// Get client identifier for rate limiting
const getClientIdentifier = (request) => {
  // Use IP address if available, otherwise use user agent
  const ip = request.headers.get('x-forwarded-for') || 
             request.headers.get('x-real-ip') || 
             'unknown';
  
  return ip;
};

// CSRF protection
export const csrfProtection = {
  generateToken: () => {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  },
  
  validateToken: (requestToken, sessionToken) => {
    return requestToken && sessionToken && requestToken === sessionToken;
  },
  
  getTokenFromRequest: (request) => {
    return request.headers.get('x-csrf-token') || 
           request.headers.get('csrf-token');
  }
};

// Input validation schemas
export const validationSchemas = {
  email: {
    validate: validateEmail,
    sanitize: (value) => value.toLowerCase().trim()
  },
  
  url: {
    validate: validateURL,
    sanitize: (value) => value.trim()
  },
  
  text: {
    validate: (value) => typeof value === 'string' && value.length > 0,
    sanitize: (value) => value.trim()
  },
  
  number: {
    validate: (value) => !isNaN(value) && isFinite(value),
    sanitize: (value) => Number(value)
  },
  
  boolean: {
    validate: (value) => typeof value === 'boolean',
    sanitize: (value) => Boolean(value)
  }
};

// Validate request data against schema
export const validateData = (data, schema) => {
  const validated = {};
  const errors = [];
  
  Object.entries(schema).forEach(([field, rules]) => {
    const value = data[field];
    
    if (rules.required && (value === undefined || value === null || value === '')) {
      errors.push(`${field} is required`);
      return;
    }
    
    if (value !== undefined && value !== null) {
      if (rules.validate && !rules.validate(value)) {
        errors.push(`${field} is invalid`);
        return;
      }
      
      if (rules.sanitize) {
        validated[field] = rules.sanitize(value);
      } else {
        validated[field] = value;
      }
    }
  });
  
  if (errors.length > 0) {
    throw new Error(`Validation failed: ${errors.join(', ')}`);
  }
  
  return validated;
};

// Security headers for API responses
export const getSecurityHeaders = () => {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
  };
};

export default {
  validateRequest,
  rateLimitMiddleware,
  csrfProtection,
  validationSchemas,
  validateData,
  getSecurityHeaders,
  API_SECURITY_CONFIG
};



