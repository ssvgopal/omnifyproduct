// Input Sanitization and XSS Protection
import DOMPurify from 'dompurify';

// Sanitization configuration
const SANITIZATION_CONFIG = {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'span'],
  ALLOWED_ATTR: ['class', 'id'],
  ALLOWED_SCHEMES: ['http', 'https', 'mailto'],
  FORBID_TAGS: ['script', 'object', 'embed', 'iframe', 'form', 'input', 'textarea', 'button'],
  FORBID_ATTR: ['onload', 'onerror', 'onclick', 'onmouseover', 'onfocus', 'onblur']
};

// Sanitize HTML content
export const sanitizeHTML = (dirty) => {
  if (!dirty) return '';
  
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: SANITIZATION_CONFIG.ALLOWED_TAGS,
    ALLOWED_ATTR: SANITIZATION_CONFIG.ALLOWED_ATTR,
    ALLOWED_SCHEMES: SANITIZATION_CONFIG.ALLOWED_SCHEMES,
    FORBID_TAGS: SANITIZATION_CONFIG.FORBID_TAGS,
    FORBID_ATTR: SANITIZATION_CONFIG.FORBID_ATTR,
    KEEP_CONTENT: true,
    RETURN_DOM: false,
    RETURN_DOM_FRAGMENT: false,
    RETURN_DOM_IMPORT: false
  });
};

// Sanitize user input
export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  // Remove potentially dangerous characters
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/<[^>]*>/g, '')
    .trim();
};

// Validate email format
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Validate URL format
export const validateURL = (url) => {
  try {
    const urlObj = new URL(url);
    return ['http:', 'https:'].includes(urlObj.protocol);
  } catch {
    return false;
  }
};

// Escape HTML entities
export const escapeHTML = (text) => {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
};

// Validate and sanitize form data
export const sanitizeFormData = (formData) => {
  const sanitized = {};
  
  Object.entries(formData).forEach(([key, value]) => {
    if (typeof value === 'string') {
      sanitized[key] = sanitizeInput(value);
    } else {
      sanitized[key] = value;
    }
  });
  
  return sanitized;
};

export default {
  sanitizeHTML,
  sanitizeInput,
  validateEmail,
  validateURL,
  escapeHTML,
  sanitizeFormData
};



