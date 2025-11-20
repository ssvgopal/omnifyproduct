"""
Core Authentication Module for Omnify Cloud Connect
Provides dependency injection for authentication services
"""

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer
from typing import Dict, Any
import os
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.auth_service import AuthService

security = HTTPBearer()

# Global auth service instance
auth_service_instance = None


def get_auth_service(db: AsyncIOMotorDatabase = Depends()) -> AuthService:
    """Dependency to get AuthService instance"""
    global auth_service_instance
    
    if auth_service_instance is None:
        from core.secrets_manager import get_required_secret
        
        # Get JWT secret from secrets manager (required, no default)
        try:
            jwt_secret = get_required_secret('JWT_SECRET_KEY')
        except ValueError:
            # Fallback for development only
            jwt_secret = os.environ.get('JWT_SECRET_KEY')
            if not jwt_secret:
                raise ValueError(
                    "JWT_SECRET_KEY is required. Set it in environment variables or secrets manager."
                )
        
        jwt_algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')
        auth_service_instance = AuthService(db, jwt_secret, jwt_algorithm)
    
    return auth_service_instance


async def get_current_user(
    credentials: HTTPBearer = Security(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": user.organization_id,
            "is_active": user.is_active
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_organization(
    credentials: HTTPBearer = Security(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Get current organization from JWT token"""
    try:
        token = credentials.credentials
        organization = await auth_service.get_current_organization(token)
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return {
            "organization_id": organization.organization_id,
            "name": organization.name,
            "slug": organization.slug,
            "subscription_tier": organization.subscription_tier,
            "is_active": organization.is_active
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_role(required_role: str):
    """Dependency factory to require specific role"""
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "member")
        role_hierarchy = {
            "viewer": 1,
            "member": 2,
            "manager": 3,
            "admin": 4,
            "owner": 5
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {required_role}, Current: {user_role}"
            )
        
        return current_user
    
    return role_checker


# Legacy compatibility
async def get_current_user_legacy(credentials: HTTPBearer = Security(security)) -> Dict[str, Any]:
    """Legacy get_current_user for backward compatibility"""
    return await get_current_user(credentials)


# Create legacy auth service instance for backward compatibility
class LegacyAuthService:
    """Legacy auth service for backward compatibility"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta=None) -> str:
        """Create JWT access token (legacy method)"""
        auth_service = AuthService(None, os.environ.get('JWT_SECRET_KEY', 'default'))
        return auth_service.create_access_token(data)
    
    @staticmethod
    def verify_token(token: str) -> Dict[Any, Any]:
        """Verify JWT token (legacy method)"""
        auth_service = AuthService(None, os.environ.get('JWT_SECRET_KEY', 'default'))
        return auth_service.decode_token(token) or {}
    
    @staticmethod
    async def get_current_user(credentials=None):
        """Get current user (legacy method)"""
        # This will be handled by dependency injection in routes
        pass
    
    @staticmethod
    def check_permission(user: Dict[Any, Any], required_permission: str) -> bool:
        """Check permission (legacy method)"""
        user_role = user.get('role', 'member')
        return (required_permission == 'read' and user_role in ['viewer', 'member', 'manager', 'admin', 'owner']) or \
               (required_permission == 'write' and user_role in ['member', 'manager', 'admin', 'owner']) or \
               (required_permission == 'admin' and user_role in ['admin', 'owner'])

auth_service = LegacyAuthService()
