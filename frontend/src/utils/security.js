// Content Security Policy Configuration
const CSP_CONFIG = {
  // Default CSP policy
  defaultSrc: ["'self'"],
  scriptSrc: [
    "'self'",
    "'unsafe-inline'", // Required for React development
    "'unsafe-eval'",   // Required for React development
    "https://www.googletagmanager.com",
    "https://www.google-analytics.com",
    "https://cdn.jsdelivr.net",
    "https://unpkg.com"
  ],
  styleSrc: [
    "'self'",
    "'unsafe-inline'", // Required for TailwindCSS
    "https://fonts.googleapis.com"
  ],
  fontSrc: [
    "'self'",
    "https://fonts.gstatic.com",
    "data:"
  ],
  imgSrc: [
    "'self'",
    "data:",
    "https:",
    "blob:"
  ],
  connectSrc: [
    "'self'",
    "https://www.google-analytics.com",
    "https://analytics.google.com",
    "wss://localhost:8000", // WebSocket for development
    "ws://localhost:8000"   // WebSocket for development
  ],
  mediaSrc: [
    "'self'",
    "data:",
    "blob:"
  ],
  objectSrc: ["'none'"],
  baseUri: ["'self'"],
  formAction: ["'self'"],
  frameAncestors: ["'none'"],
  upgradeInsecureRequests: true
};

// Generate CSP header
export const generateCSPHeader = () => {
  const directives = [];
  
  Object.entries(CSP_CONFIG).forEach(([directive, sources]) => {
    if (Array.isArray(sources)) {
      directives.push(`${directive} ${sources.join(' ')}`);
    } else {
      directives.push(`${directive} ${sources}`);
    }
  });
  
  return directives.join('; ');
};

// Set CSP meta tag
export const setCSPMetaTag = () => {
  const cspHeader = generateCSPHeader();
  
  // Remove existing CSP meta tag
  const existingMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
  if (existingMeta) {
    existingMeta.remove();
  }
  
  // Add new CSP meta tag
  const meta = document.createElement('meta');
  meta.setAttribute('http-equiv', 'Content-Security-Policy');
  meta.setAttribute('content', cspHeader);
  document.head.appendChild(meta);
  
  console.log('CSP header set:', cspHeader);
};

// Security headers configuration
export const SECURITY_HEADERS = {
  'Content-Security-Policy': generateCSPHeader(),
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'Cross-Origin-Embedder-Policy': 'require-corp',
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Resource-Policy': 'same-origin'
};

export default CSP_CONFIG;
