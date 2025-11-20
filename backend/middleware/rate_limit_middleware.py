"""
Rate Limiting Middleware
Applies rate limiting to all API routes
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable
import time
import logging

from services.production_rate_limiter import ProductionRateLimiter, get_rate_limiter

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to all requests"""
    
    def __init__(self, app, rate_limiter: ProductionRateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or get_rate_limiter()
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/metrics", "/api/health"]:
            return await call_next(request)
        
        # Get user identifier
        user_id = None
        organization_id = None
        
        try:
            # Try to get from request state (set by auth middleware)
            user_id = getattr(request.state, 'user_id', None)
            organization_id = getattr(request.state, 'organization_id', None)
        except:
            pass
        
        # Fallback to IP address
        if not user_id:
            client = request.client
            user_id = getattr(client, 'host', 'anonymous') if client else 'anonymous'
        
        # Check rate limit
        try:
            allowed, retry_after = await self.rate_limiter.check_rate_limit(
                identifier=user_id or organization_id or 'anonymous',
                endpoint=request.url.path,
                method=request.method
            )
            
            if not allowed:
                # Rate limit exceeded
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after": retry_after
                    }
                )
                response.headers["Retry-After"] = str(int(retry_after))
                return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Allow request to proceed if rate limiter fails
            pass
        
        # Process request
        response = await call_next(request)
        
        # Record request for rate limiting
        try:
            await self.rate_limiter.record_request(
                identifier=user_id or organization_id or 'anonymous',
                endpoint=request.url.path,
                method=request.method
            )
        except Exception as e:
            logger.error(f"Failed to record request for rate limiting: {e}")
        
        return response

