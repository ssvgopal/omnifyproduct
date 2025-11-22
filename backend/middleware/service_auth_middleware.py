"""
Service Authentication Middleware
Validates service-to-service JWT tokens
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional

from backend.core.service_auth import get_service_auth

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class ServiceAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate service-to-service authentication"""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.service_auth = get_service_auth()
        # Health check and public endpoints that don't need auth
        self.public_paths = {
            "/health",
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Skip auth if disabled (for development)
        if not self.enabled or not self.service_auth.secret:
            return await call_next(request)
        
        # Check for service token in Authorization header
        authorization: Optional[HTTPAuthorizationCredentials] = await security(request)
        
        if not authorization:
            # Check if this is a service-to-service call
            service_name = request.headers.get("X-Service-Name")
            if service_name:
                # Service call without token - reject
                logger.warning(
                    f"Service call without token from {service_name} to {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Service authentication required"
                )
            # Not a service call, allow through (user auth handled elsewhere)
            return await call_next(request)
        
        # Verify service token
        token = authorization.credentials
        payload = self.service_auth.verify_service_token(token)
        
        if not payload:
            logger.warning(f"Invalid service token for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid service token"
            )
        
        # Add service info to request state
        request.state.service_name = payload.get("service")
        request.state.service_token_valid = True
        
        logger.debug(
            f"Service call authenticated: {payload.get('service')} -> {request.url.path}"
        )
        
        return await call_next(request)

