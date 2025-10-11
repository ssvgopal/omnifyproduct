"""
Tracing Middleware for OmnifyProduct
Provides request tracing, correlation IDs, and performance monitoring
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import time
import uuid
from typing import Callable
from services.structured_logging import logger, request_id, user_id, organization_id

class TracingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for comprehensive request tracing and monitoring
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request with full tracing
        """
        start_time = time.time()

        # Generate or use existing request ID
        req_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request_id.set(req_id)

        # Extract user context from JWT if available
        await self._extract_user_context(request)

        # Log request start
        self._log_request_start(request, req_id)

        try:
            # Process the request
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful request completion
            self._log_request_complete(request, response, duration_ms)

            # Add tracing headers to response
            response.headers['X-Request-ID'] = req_id
            response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration_ms = (time.time() - start_time) * 1000

            # Log request failure
            self._log_request_error(request, e, duration_ms)

            # Re-raise the exception
            raise

    async def _extract_user_context(self, request: Request):
        """
        Extract user and organization context from request
        """
        try:
            # Check for JWT token in Authorization header
            auth_header = request.headers.get('authorization', '')
            if auth_header.startswith('Bearer '):
                # In a real implementation, you'd decode the JWT here
                # For now, we'll extract from a custom header for demo purposes
                pass

            # Extract from custom headers (for development/testing)
            user_id_header = request.headers.get('X-User-ID')
            org_id_header = request.headers.get('X-Organization-ID')

            if user_id_header:
                user_id.set(user_id_header)
            if org_id_header:
                organization_id.set(org_id_header)

        except Exception as e:
            # Don't fail the request if context extraction fails
            logger.warning(f"Failed to extract user context: {str(e)}")

    def _log_request_start(self, request: Request, req_id: str):
        """Log request initiation"""
        logger.request_start(
            method=request.method,
            path=request.url.path,
            event_type='request_start',
            user_agent=request.headers.get('user-agent', ''),
            ip_address=self._get_client_ip(request),
            query_params=dict(request.query_params),
            content_length=request.headers.get('content-length', 0)
        )

    def _log_request_complete(self, request: Request, response: Response, duration_ms: float):
        """Log successful request completion"""
        logger.request_complete(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            response_size=len(response.body) if hasattr(response, 'body') else 0
        )

    def _log_request_error(self, request: Request, error: Exception, duration_ms: float):
        """Log request failure"""
        logger.request_error(
            method=request.method,
            path=request.url.path,
            error=str(error),
            duration_ms=duration_ms,
            error_type=type(error).__name__,
            exc_info=error
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()

        # Check other proxy headers
        for header in ['X-Real-IP', 'X-Forwarded-For', 'CF-Connecting-IP']:
            ip = request.headers.get(header)
            if ip:
                return ip.split(',')[0].strip()

        # Fall back to direct connection
        if hasattr(request, 'client') and request.client:
            return request.client.host

        return 'unknown'


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Additional middleware for detailed performance monitoring
    """

    def __init__(self, app, slow_request_threshold: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        # Log slow requests
        if duration_ms > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                event_type='slow_request',
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                threshold_ms=self.slow_request_threshold
            )

        # Add performance header
        response.headers['X-Request-Duration'] = f"{duration_ms:.2f}ms"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers and logging security events
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log potential security events
        self._check_security_events(request)

        response = await call_next(request)

        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response

    def _check_security_events(self, request: Request):
        """Check for potential security issues"""
        # Log suspicious patterns
        user_agent = request.headers.get('user-agent', '').lower()

        # Check for common attack patterns
        suspicious_patterns = [
            '../../',  # Path traversal
            '<script',  # XSS attempts
            'union select',  # SQL injection
            'eval(',  # Code injection
        ]

        path = request.url.path.lower()
        query = str(request.query_params).lower()

        for pattern in suspicious_patterns:
            if pattern in path or pattern in query:
                logger.warning(
                    f"Suspicious request pattern detected: {pattern}",
                    event_type='security_event',
                    pattern=pattern,
                    method=request.method,
                    path=request.url.path,
                    user_agent=user_agent,
                    ip_address=self._get_client_ip(request)
                )
                break

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()

        if hasattr(request, 'client') and request.client:
            return request.client.host

        return 'unknown'
