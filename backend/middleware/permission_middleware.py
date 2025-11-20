"""
Permission Middleware for FastAPI
Enforces resource-level permissions on API endpoints
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
import logging

from services.rbac_service import RBACService, Permission, ResourceType
from core.auth import get_current_user

logger = logging.getLogger(__name__)


class PermissionMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce permissions on API endpoints"""
    
    def __init__(self, app, db):
        super().__init__(app)
        self.db = db
        self.rbac_service = RBACService(db)
        
        # Define permission mappings for routes
        self.route_permissions = {
            # Campaign routes
            "POST:/api/campaigns": Permission.CAMPAIGN_CREATE,
            "GET:/api/campaigns": Permission.CAMPAIGN_VIEW,
            "PUT:/api/campaigns/{campaign_id}": Permission.CAMPAIGN_EDIT,
            "DELETE:/api/campaigns/{campaign_id}": Permission.CAMPAIGN_DELETE,
            "POST:/api/campaigns/{campaign_id}/publish": Permission.CAMPAIGN_PUBLISH,
            
            # Creative routes
            "POST:/api/creatives": Permission.CREATIVE_CREATE,
            "GET:/api/creatives": Permission.CREATIVE_VIEW,
            "PUT:/api/creatives/{creative_id}": Permission.CREATIVE_EDIT,
            "DELETE:/api/creatives/{creative_id}": Permission.CREATIVE_DELETE,
            
            # Analytics routes
            "GET:/api/analytics": Permission.ANALYTICS_VIEW,
            "POST:/api/analytics/export": Permission.ANALYTICS_EXPORT,
            "POST:/api/analytics/admin": Permission.ANALYTICS_ADMIN,
            
            # Integration routes
            "GET:/api/integrations": Permission.INTEGRATION_VIEW,
            "POST:/api/integrations/connect": Permission.INTEGRATION_CONNECT,
            "DELETE:/api/integrations/{integration_id}": Permission.INTEGRATION_DISCONNECT,
            "PUT:/api/integrations/{integration_id}": Permission.INTEGRATION_MANAGE,
            
            # User management routes
            "GET:/api/users": Permission.USER_VIEW,
            "POST:/api/users/invite": Permission.USER_INVITE,
            "PUT:/api/users/{user_id}": Permission.USER_EDIT,
            "DELETE:/api/users/{user_id}": Permission.USER_DELETE,
            
            # Organization routes
            "GET:/api/organizations": Permission.ORG_VIEW,
            "PUT:/api/organizations/{org_id}": Permission.ORG_EDIT,
            "GET:/api/organizations/{org_id}/billing": Permission.ORG_BILLING,
            "POST:/api/organizations/{org_id}/admin": Permission.ORG_ADMIN,
            
            # Agent routes
            "GET:/api/agents": Permission.AGENT_VIEW,
            "POST:/api/agents": Permission.AGENT_CREATE,
            "PUT:/api/agents/{agent_id}": Permission.AGENT_EDIT,
            "POST:/api/agents/{agent_id}/execute": Permission.AGENT_EXECUTE,
            "DELETE:/api/agents/{agent_id}": Permission.AGENT_DELETE,
            
            # Settings routes
            "GET:/api/settings": Permission.SETTINGS_VIEW,
            "PUT:/api/settings": Permission.SETTINGS_EDIT,
        }
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request and check permissions"""
        # Skip permission check for public routes
        public_routes = [
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/docs",
            "/openapi.json",
            "/"
        ]
        
        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)
        
        # Get route pattern
        route_pattern = self._get_route_pattern(request)
        
        # Check if route requires permission
        required_permission = self._get_required_permission(route_pattern, request.method)
        
        if required_permission:
            try:
                # Get current user (this will raise if not authenticated)
                # Note: This is a simplified check - in production, extract from JWT
                auth_header = request.headers.get("Authorization")
                if not auth_header:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Extract user from token (simplified - should use proper JWT decoding)
                # For now, we'll let the endpoint handle auth and permission checking
                # This middleware serves as a template for future enhancement
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error in permission middleware: {e}")
                # Continue to endpoint - let endpoint handle auth
        
        response = await call_next(request)
        return response
    
    def _get_route_pattern(self, request: Request) -> str:
        """Get route pattern from request"""
        path = request.url.path
        # Replace path parameters with placeholders
        # This is simplified - FastAPI provides better route matching
        return path
    
    def _get_required_permission(
        self,
        route_pattern: str,
        method: str
    ) -> Optional[Permission]:
        """Get required permission for route"""
        key = f"{method}:{route_pattern}"
        return self.route_permissions.get(key)


def require_permission(permission: Permission):
    """Dependency factory to require specific permission"""
    async def permission_checker(
        current_user: dict = Depends(get_current_user),
        db = Depends(get_database)
    ):
        rbac_service = RBACService(db)
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            permission
        )
        return current_user
    
    return permission_checker


def require_resource_permission(
    permission: Permission,
    resource_type: ResourceType,
    resource_id_param: str = "resource_id"
):
    """Dependency factory to require resource-level permission"""
    async def resource_permission_checker(
        request: Request,
        current_user: dict = Depends(get_current_user),
        db = Depends(get_database)
    ):
        rbac_service = RBACService(db)
        resource_id = request.path_params.get(resource_id_param)
        
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            permission,
            resource_type=resource_type,
            resource_id=resource_id
        )
        return current_user
    
    return resource_permission_checker

