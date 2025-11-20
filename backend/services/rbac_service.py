"""
Enhanced Role-Based Access Control (RBAC) Service
Resource-level permissions with fine-grained access control
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """Resource-level permissions"""
    # Campaign permissions
    CAMPAIGN_VIEW = "campaign:view"
    CAMPAIGN_CREATE = "campaign:create"
    CAMPAIGN_EDIT = "campaign:edit"
    CAMPAIGN_DELETE = "campaign:delete"
    CAMPAIGN_PUBLISH = "campaign:publish"
    
    # Creative permissions
    CREATIVE_VIEW = "creative:view"
    CREATIVE_CREATE = "creative:create"
    CREATIVE_EDIT = "creative:edit"
    CREATIVE_DELETE = "creative:delete"
    
    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_ADMIN = "analytics:admin"
    
    # Integration permissions
    INTEGRATION_VIEW = "integration:view"
    INTEGRATION_CONNECT = "integration:connect"
    INTEGRATION_DISCONNECT = "integration:disconnect"
    INTEGRATION_MANAGE = "integration:manage"
    
    # User management permissions
    USER_VIEW = "user:view"
    USER_INVITE = "user:invite"
    USER_EDIT = "user:edit"
    USER_DELETE = "user:delete"
    
    # Organization permissions
    ORG_VIEW = "org:view"
    ORG_EDIT = "org:edit"
    ORG_BILLING = "org:billing"
    ORG_ADMIN = "org:admin"
    
    # AI Agent permissions
    AGENT_VIEW = "agent:view"
    AGENT_CREATE = "agent:create"
    AGENT_EDIT = "agent:edit"
    AGENT_EXECUTE = "agent:execute"
    AGENT_DELETE = "agent:delete"
    
    # Settings permissions
    SETTINGS_VIEW = "settings:view"
    SETTINGS_EDIT = "settings:edit"


class ResourceType(str, Enum):
    """Resource types for permission checking"""
    CAMPAIGN = "campaign"
    CREATIVE = "creative"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    USER = "user"
    ORGANIZATION = "organization"
    AGENT = "agent"
    SETTINGS = "settings"


@dataclass
class Role:
    """Role definition with permissions"""
    role_id: str
    name: str
    description: str
    permissions: Set[Permission]
    is_system_role: bool = False
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class ResourcePermission:
    """Resource-level permission"""
    resource_type: ResourceType
    resource_id: Optional[str]  # None for type-level permissions
    permissions: Set[Permission]
    granted_by: str  # User ID who granted
    granted_at: datetime
    expires_at: Optional[datetime] = None


class RBACService:
    """Enhanced RBAC service with resource-level permissions"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._system_roles = self._initialize_system_roles()
    
    def _initialize_system_roles(self) -> Dict[str, Role]:
        """Initialize system roles with default permissions"""
        return {
            "owner": Role(
                role_id="owner",
                name="Owner",
                description="Full access to all resources",
                permissions=set(Permission),  # All permissions
                is_system_role=True
            ),
            "admin": Role(
                role_id="admin",
                name="Administrator",
                description="Administrative access with most permissions",
                permissions={
                    Permission.CAMPAIGN_VIEW,
                    Permission.CAMPAIGN_CREATE,
                    Permission.CAMPAIGN_EDIT,
                    Permission.CAMPAIGN_DELETE,
                    Permission.CAMPAIGN_PUBLISH,
                    Permission.CREATIVE_VIEW,
                    Permission.CREATIVE_CREATE,
                    Permission.CREATIVE_EDIT,
                    Permission.CREATIVE_DELETE,
                    Permission.ANALYTICS_VIEW,
                    Permission.ANALYTICS_EXPORT,
                    Permission.ANALYTICS_ADMIN,
                    Permission.INTEGRATION_VIEW,
                    Permission.INTEGRATION_CONNECT,
                    Permission.INTEGRATION_DISCONNECT,
                    Permission.INTEGRATION_MANAGE,
                    Permission.USER_VIEW,
                    Permission.USER_INVITE,
                    Permission.USER_EDIT,
                    Permission.ORG_VIEW,
                    Permission.ORG_EDIT,
                    Permission.AGENT_VIEW,
                    Permission.AGENT_CREATE,
                    Permission.AGENT_EDIT,
                    Permission.AGENT_EXECUTE,
                    Permission.SETTINGS_VIEW,
                    Permission.SETTINGS_EDIT,
                },
                is_system_role=True
            ),
            "manager": Role(
                role_id="manager",
                name="Manager",
                description="Campaign and team management access",
                permissions={
                    Permission.CAMPAIGN_VIEW,
                    Permission.CAMPAIGN_CREATE,
                    Permission.CAMPAIGN_EDIT,
                    Permission.CAMPAIGN_PUBLISH,
                    Permission.CREATIVE_VIEW,
                    Permission.CREATIVE_CREATE,
                    Permission.CREATIVE_EDIT,
                    Permission.ANALYTICS_VIEW,
                    Permission.ANALYTICS_EXPORT,
                    Permission.INTEGRATION_VIEW,
                    Permission.USER_VIEW,
                    Permission.AGENT_VIEW,
                    Permission.AGENT_EXECUTE,
                    Permission.SETTINGS_VIEW,
                },
                is_system_role=True
            ),
            "member": Role(
                role_id="member",
                name="Member",
                description="Basic access to view and create content",
                permissions={
                    Permission.CAMPAIGN_VIEW,
                    Permission.CAMPAIGN_CREATE,
                    Permission.CREATIVE_VIEW,
                    Permission.CREATIVE_CREATE,
                    Permission.ANALYTICS_VIEW,
                    Permission.INTEGRATION_VIEW,
                    Permission.AGENT_VIEW,
                    Permission.AGENT_EXECUTE,
                },
                is_system_role=True
            ),
            "viewer": Role(
                role_id="viewer",
                name="Viewer",
                description="Read-only access",
                permissions={
                    Permission.CAMPAIGN_VIEW,
                    Permission.CREATIVE_VIEW,
                    Permission.ANALYTICS_VIEW,
                    Permission.INTEGRATION_VIEW,
                    Permission.AGENT_VIEW,
                },
                is_system_role=True
            ),
        }
    
    # ========== ROLE MANAGEMENT ==========
    
    async def get_role(self, role_id: str, organization_id: str) -> Optional[Role]:
        """Get role by ID"""
        try:
            # Check system roles first
            if role_id in self._system_roles:
                return self._system_roles[role_id]
            
            # Check custom roles
            role_doc = await self.db.roles.find_one({
                "role_id": role_id,
                "organization_id": organization_id
            })
            
            if role_doc:
                return Role(
                    role_id=role_doc["role_id"],
                    name=role_doc["name"],
                    description=role_doc["description"],
                    permissions=set(Permission(p) for p in role_doc["permissions"]),
                    is_system_role=role_doc.get("is_system_role", False),
                    created_at=role_doc.get("created_at"),
                    updated_at=role_doc.get("updated_at")
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting role: {e}")
            raise
    
    async def create_custom_role(
        self,
        organization_id: str,
        name: str,
        description: str,
        permissions: List[Permission],
        created_by: str
    ) -> Role:
        """Create custom role"""
        try:
            role_id = f"custom_{name.lower().replace(' ', '_')}"
            
            role = Role(
                role_id=role_id,
                name=name,
                description=description,
                permissions=set(permissions),
                is_system_role=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            role_doc = {
                "role_id": role_id,
                "organization_id": organization_id,
                "name": name,
                "description": description,
                "permissions": [p.value for p in permissions],
                "is_system_role": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": created_by
            }
            
            await self.db.roles.insert_one(role_doc)
            
            return role
            
        except Exception as e:
            logger.error(f"Error creating custom role: {e}")
            raise
    
    async def update_role(
        self,
        role_id: str,
        organization_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[Permission]] = None
    ) -> bool:
        """Update role"""
        try:
            # Cannot update system roles
            if role_id in self._system_roles:
                raise ValueError("Cannot update system roles")
            
            update_data = {"updated_at": datetime.utcnow()}
            
            if name:
                update_data["name"] = name
            if description:
                update_data["description"] = description
            if permissions:
                update_data["permissions"] = [p.value for p in permissions]
            
            result = await self.db.roles.update_one(
                {"role_id": role_id, "organization_id": organization_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating role: {e}")
            raise
    
    async def delete_role(self, role_id: str, organization_id: str) -> bool:
        """Delete custom role"""
        try:
            # Cannot delete system roles
            if role_id in self._system_roles:
                raise ValueError("Cannot delete system roles")
            
            result = await self.db.roles.delete_one({
                "role_id": role_id,
                "organization_id": organization_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            raise
    
    async def list_roles(self, organization_id: str) -> List[Role]:
        """List all roles for organization"""
        try:
            roles = []
            
            # Add system roles
            for role in self._system_roles.values():
                roles.append(role)
            
            # Add custom roles
            custom_roles = await self.db.roles.find({
                "organization_id": organization_id
            }).to_list(length=100)
            
            for role_doc in custom_roles:
                roles.append(Role(
                    role_id=role_doc["role_id"],
                    name=role_doc["name"],
                    description=role_doc["description"],
                    permissions=set(Permission(p) for p in role_doc["permissions"]),
                    is_system_role=role_doc.get("is_system_role", False),
                    created_at=role_doc.get("created_at"),
                    updated_at=role_doc.get("updated_at")
                ))
            
            return roles
            
        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            raise
    
    # ========== PERMISSION CHECKING ==========
    
    async def check_permission(
        self,
        user_id: str,
        organization_id: str,
        permission: Permission,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has permission"""
        try:
            # Get user's role
            user_doc = await self.db.users.find_one({
                "user_id": user_id,
                "organization_id": organization_id
            })
            
            if not user_doc:
                return False
            
            role_id = user_doc.get("role", "member")
            role = await self.get_role(role_id, organization_id)
            
            if not role:
                return False
            
            # Check role permissions
            if permission in role.permissions:
                return True
            
            # Check resource-level permissions
            if resource_type and resource_id:
                resource_perms = await self.db.resource_permissions.find({
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "resource_type": resource_type.value,
                    "resource_id": resource_id
                }).to_list(length=10)
                
                for perm_doc in resource_perms:
                    # Check expiration
                    if perm_doc.get("expires_at"):
                        if datetime.utcnow() > perm_doc["expires_at"]:
                            continue
                    
                    if permission.value in perm_doc.get("permissions", []):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    async def grant_resource_permission(
        self,
        user_id: str,
        organization_id: str,
        resource_type: ResourceType,
        resource_id: str,
        permissions: List[Permission],
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Grant resource-level permission to user"""
        try:
            perm_doc = {
                "user_id": user_id,
                "organization_id": organization_id,
                "resource_type": resource_type.value,
                "resource_id": resource_id,
                "permissions": [p.value for p in permissions],
                "granted_by": granted_by,
                "granted_at": datetime.utcnow(),
                "expires_at": expires_at
            }
            
            await self.db.resource_permissions.insert_one(perm_doc)
            return True
            
        except Exception as e:
            logger.error(f"Error granting resource permission: {e}")
            raise
    
    async def revoke_resource_permission(
        self,
        user_id: str,
        organization_id: str,
        resource_type: ResourceType,
        resource_id: str
    ) -> bool:
        """Revoke resource-level permission"""
        try:
            result = await self.db.resource_permissions.delete_one({
                "user_id": user_id,
                "organization_id": organization_id,
                "resource_type": resource_type.value,
                "resource_id": resource_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error revoking resource permission: {e}")
            raise
    
    async def get_user_permissions(
        self,
        user_id: str,
        organization_id: str
    ) -> Dict[str, Any]:
        """Get all permissions for user"""
        try:
            # Get user's role
            user_doc = await self.db.users.find_one({
                "user_id": user_id,
                "organization_id": organization_id
            })
            
            if not user_doc:
                return {"role_permissions": [], "resource_permissions": []}
            
            role_id = user_doc.get("role", "member")
            role = await self.get_role(role_id, organization_id)
            
            role_permissions = [p.value for p in role.permissions] if role else []
            
            # Get resource-level permissions
            resource_perms = await self.db.resource_permissions.find({
                "user_id": user_id,
                "organization_id": organization_id
            }).to_list(length=100)
            
            resource_permissions = []
            for perm_doc in resource_perms:
                # Filter expired
                if perm_doc.get("expires_at"):
                    if datetime.utcnow() > perm_doc["expires_at"]:
                        continue
                
                resource_permissions.append({
                    "resource_type": perm_doc["resource_type"],
                    "resource_id": perm_doc["resource_id"],
                    "permissions": perm_doc.get("permissions", []),
                    "granted_at": perm_doc.get("granted_at"),
                    "expires_at": perm_doc.get("expires_at")
                })
            
            return {
                "role": role_id,
                "role_permissions": role_permissions,
                "resource_permissions": resource_permissions
            }
            
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            raise
    
    # ========== PERMISSION MIDDLEWARE ==========
    
    async def require_permission(
        self,
        user_id: str,
        organization_id: str,
        permission: Permission,
        resource_type: Optional[ResourceType] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """Require permission or raise exception"""
        has_permission = await self.check_permission(
            user_id, organization_id, permission, resource_type, resource_id
        )
        
        if not has_permission:
            raise PermissionError(
                f"User {user_id} does not have permission {permission.value} "
                f"for resource {resource_type.value if resource_type else 'general'}"
            )
        
        return True

