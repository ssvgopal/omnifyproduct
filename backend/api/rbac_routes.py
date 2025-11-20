"""
RBAC (Role-Based Access Control) API Routes
Resource-level permissions management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.rbac_service import (
    RBACService, Permission, ResourceType, Role
)
from datetime import datetime

router = APIRouter(prefix="/api/rbac", tags=["RBAC"])


class CreateRoleRequest(BaseModel):
    name: str
    description: str
    permissions: List[str]  # List of permission strings


class UpdateRoleRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class GrantResourcePermissionRequest(BaseModel):
    user_id: str
    resource_type: str
    resource_id: str
    permissions: List[str]
    expires_at: Optional[datetime] = None


class CheckPermissionRequest(BaseModel):
    permission: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


def get_rbac_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> RBACService:
    """Get RBAC service instance"""
    return RBACService(db)


@router.get("/roles")
async def list_roles(
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """List all roles for organization"""
    try:
        roles = await rbac_service.list_roles(current_user["organization_id"])
        return {
            "success": True,
            "data": [
                {
                    "role_id": r.role_id,
                    "name": r.name,
                    "description": r.description,
                    "permissions": [p.value for p in r.permissions],
                    "is_system_role": r.is_system_role
                }
                for r in roles
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/roles/{role_id}")
async def get_role(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Get role details"""
    try:
        role = await rbac_service.get_role(role_id, current_user["organization_id"])
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return {
            "success": True,
            "data": {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "permissions": [p.value for p in role.permissions],
                "is_system_role": role.is_system_role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/roles")
async def create_role(
    request: CreateRoleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Create custom role"""
    try:
        # Check permission
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            Permission.ORG_ADMIN
        )
        
        # Convert permission strings to Permission enum
        permissions = [Permission(p) for p in request.permissions]
        
        role = await rbac_service.create_custom_role(
            organization_id=current_user["organization_id"],
            name=request.name,
            description=request.description,
            permissions=permissions,
            created_by=current_user["user_id"]
        )
        
        return {
            "success": True,
            "data": {
                "role_id": role.role_id,
                "name": role.name,
                "description": role.description,
                "permissions": [p.value for p in role.permissions]
            }
        }
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/roles/{role_id}")
async def update_role(
    role_id: str,
    request: UpdateRoleRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Update custom role"""
    try:
        # Check permission
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            Permission.ORG_ADMIN
        )
        
        permissions = None
        if request.permissions:
            permissions = [Permission(p) for p in request.permissions]
        
        result = await rbac_service.update_role(
            role_id=role_id,
            organization_id=current_user["organization_id"],
            name=request.name,
            description=request.description,
            permissions=permissions
        )
        
        if result:
            return {"success": True, "message": "Role updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Delete custom role"""
    try:
        # Check permission
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            Permission.ORG_ADMIN
        )
        
        result = await rbac_service.delete_role(
            role_id=role_id,
            organization_id=current_user["organization_id"]
        )
        
        if result:
            return {"success": True, "message": "Role deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/permissions/check")
async def check_permission(
    request: CheckPermissionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Check if current user has permission"""
    try:
        resource_type = None
        if request.resource_type:
            resource_type = ResourceType(request.resource_type)
        
        has_permission = await rbac_service.check_permission(
            user_id=current_user["user_id"],
            organization_id=current_user["organization_id"],
            permission=Permission(request.permission),
            resource_type=resource_type,
            resource_id=request.resource_id
        )
        
        return {
            "success": True,
            "data": {
                "has_permission": has_permission,
                "permission": request.permission
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/permissions")
async def get_user_permissions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Get all permissions for current user"""
    try:
        permissions = await rbac_service.get_user_permissions(
            user_id=current_user["user_id"],
            organization_id=current_user["organization_id"]
        )
        
        return {"success": True, "data": permissions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/permissions/resource/grant")
async def grant_resource_permission(
    request: GrantResourcePermissionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Grant resource-level permission to user"""
    try:
        # Check permission (must be admin or org admin)
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            Permission.ORG_ADMIN
        )
        
        permissions = [Permission(p) for p in request.permissions]
        
        result = await rbac_service.grant_resource_permission(
            user_id=request.user_id,
            organization_id=current_user["organization_id"],
            resource_type=ResourceType(request.resource_type),
            resource_id=request.resource_id,
            permissions=permissions,
            granted_by=current_user["user_id"],
            expires_at=request.expires_at
        )
        
        return {"success": True, "message": "Permission granted successfully"}
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/permissions/resource/revoke")
async def revoke_resource_permission(
    user_id: str,
    resource_type: str,
    resource_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Revoke resource-level permission"""
    try:
        # Check permission
        await rbac_service.require_permission(
            current_user["user_id"],
            current_user["organization_id"],
            Permission.ORG_ADMIN
        )
        
        result = await rbac_service.revoke_resource_permission(
            user_id=user_id,
            organization_id=current_user["organization_id"],
            resource_type=ResourceType(resource_type),
            resource_id=resource_id
        )
        
        if result:
            return {"success": True, "message": "Permission revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

