"""
Multi-Tenancy & User Management API Routes
Production-grade API endpoints for multi-tenancy, user management, and team collaboration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Header
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.multi_tenancy_service import (
    get_multi_tenancy_service, MultiTenancyService,
    UserRole, SubscriptionPlan, SubscriptionStatus, InvitationStatus
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class UserCreateRequest(BaseModel):
    email: str = Field(..., description="User email")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    password: str = Field(..., description="User password")
    role: str = Field(..., description="User role")
    preferences: Optional[Dict[str, Any]] = Field({}, description="User preferences")

class OrganizationCreateRequest(BaseModel):
    name: str = Field(..., description="Organization name")
    domain: Optional[str] = Field("", description="Organization domain")
    billing_email: str = Field(..., description="Billing email")
    subscription_plan: str = Field("free", description="Subscription plan")
    billing_address: Optional[Dict[str, Any]] = Field({}, description="Billing address")
    settings: Optional[Dict[str, Any]] = Field({}, description="Organization settings")

class TeamInvitationRequest(BaseModel):
    email: str = Field(..., description="Email to invite")
    role: str = Field(..., description="Role for invited user")

class SubscriptionUpdateRequest(BaseModel):
    subscription_plan: str = Field(..., description="New subscription plan")

class UserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    role: str
    organization_id: str
    is_active: bool
    is_verified: bool
    last_login: Optional[str]
    created_at: str
    permissions: List[str]

class OrganizationResponse(BaseModel):
    organization_id: str
    name: str
    domain: str
    subscription_plan: str
    subscription_status: str
    max_users: int
    max_campaigns: int
    max_storage_gb: int
    features: List[str]
    created_at: str

class TeamInvitationResponse(BaseModel):
    invitation_id: str
    organization_id: str
    email: str
    role: str
    invited_by: str
    status: str
    expires_at: str
    created_at: str

class QuotaResponse(BaseModel):
    quota_type: str
    current_usage: int
    limit: int
    remaining: int
    is_available: bool
    reset_period: str
    last_reset: str

class OrganizationOverviewResponse(BaseModel):
    organization: OrganizationResponse
    users: List[UserResponse]
    pending_invitations: List[TeamInvitationResponse]
    quotas: Dict[str, QuotaResponse]
    summary: Dict[str, Any]

# Dependency
async def get_tenancy_service(db: AsyncIOMotorClient = Depends(get_database)) -> MultiTenancyService:
    jwt_secret = "omnify_jwt_secret_2024"  # In production, get from environment
    stripe_secret_key = "sk_test_..."  # In production, get from environment
    email_config = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "noreply@omnify.com",
        "smtp_password": "email_password"  # In production, get from environment
    }
    return get_multi_tenancy_service(db, jwt_secret, stripe_secret_key, email_config)

# Authentication Endpoints
@router.post("/api/auth/register", summary="Register Organization and Admin")
async def register_organization(
    org_data: OrganizationCreateRequest = Body(...),
    admin_data: UserCreateRequest = Body(...),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Register a new organization with admin user.
    Creates organization, admin user, and initializes quotas.
    """
    try:
        result = await tenancy_service.create_organization_with_admin(
            org_data.dict(),
            admin_data.dict()
        )
        
        # Generate JWT token for admin
        token = tenancy_service.user_manager.generate_jwt_token(result["admin_user"])
        
        return {
            "organization": OrganizationResponse(**result["organization"].__dict__),
            "admin_user": UserResponse(**result["admin_user"].__dict__),
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error registering organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register organization"
        )

@router.post("/api/auth/login", summary="User Login")
async def login_user(
    email: str = Body(..., description="User email"),
    password: str = Body(..., description="User password"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Authenticate user and return JWT token.
    Returns user information and access token.
    """
    try:
        user = await tenancy_service.user_manager.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Generate JWT token
        token = tenancy_service.user_manager.generate_jwt_token(user)
        
        return {
            "user": UserResponse(**user.__dict__),
            "access_token": token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours
            "status": "authenticated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to authenticate user"
        )

@router.post("/api/auth/verify-token", summary="Verify JWT Token")
async def verify_token(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Verify JWT token and return user information.
    Used for token validation and user context.
    """
    try:
        # Extract token from Authorization header
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Get user information
        user = await tenancy_service.user_manager.get_user(payload["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return {
            "user": UserResponse(**user.__dict__),
            "payload": payload,
            "status": "valid"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify token"
        )

# User Management Endpoints
@router.get("/api/users/me", response_model=UserResponse, summary="Get Current User")
async def get_current_user(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Get current user information from JWT token.
    Returns user profile and permissions.
    """
    try:
        # Verify token and get user
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await tenancy_service.user_manager.get_user(payload["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.get("/api/users", summary="List Organization Users")
async def list_organization_users(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    List all users in the organization.
    Returns user list with roles and permissions.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        organization_id = payload["organization_id"]
        users = await tenancy_service.user_manager.get_organization_users(organization_id)
        
        return {
            "users": [UserResponse(**user.__dict__) for user in users],
            "total_count": len(users),
            "organization_id": organization_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing organization users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )

@router.post("/api/users", response_model=UserResponse, summary="Create User")
async def create_user(
    user_data: UserCreateRequest = Body(...),
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Create a new user in the organization.
    Requires appropriate permissions.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check permissions
        if "users:create" not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Add organization ID to user data
        user_data_dict = user_data.dict()
        user_data_dict["organization_id"] = payload["organization_id"]
        
        # Check quota
        quota_check = await tenancy_service.check_organization_quota(payload["organization_id"], "users")
        if not quota_check["is_available"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User quota exceeded"
            )
        
        # Create user
        user = await tenancy_service.user_manager.create_user(user_data_dict)
        
        # Increment quota
        await tenancy_service.quota_manager.increment_quota(payload["organization_id"], "users")
        
        return UserResponse(**user.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

# Organization Management Endpoints
@router.get("/api/organizations/me", response_model=OrganizationResponse, summary="Get Current Organization")
async def get_current_organization(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Get current organization information.
    Returns organization details and subscription info.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        organization = await tenancy_service.organization_manager.get_organization(payload["organization_id"])
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        return OrganizationResponse(**organization.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization information"
        )

@router.get("/api/organizations/overview", response_model=OrganizationOverviewResponse, summary="Get Organization Overview")
async def get_organization_overview(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Get comprehensive organization overview.
    Returns organization, users, invitations, and quotas.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        overview = await tenancy_service.get_organization_overview(payload["organization_id"])
        
        return OrganizationOverviewResponse(
            organization=OrganizationResponse(**overview["organization"].__dict__),
            users=[UserResponse(**user.__dict__) for user in overview["users"]],
            pending_invitations=[TeamInvitationResponse(**inv.__dict__) for inv in overview["pending_invitations"]],
            quotas={k: QuotaResponse(**v) for k, v in overview["quotas"].items()},
            summary=overview["summary"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get organization overview"
        )

@router.put("/api/organizations/subscription", summary="Update Subscription")
async def update_subscription(
    subscription_data: SubscriptionUpdateRequest = Body(...),
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Update organization subscription plan.
    Requires admin permissions.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check permissions
        if "billing:update" not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Update subscription
        organization = await tenancy_service.organization_manager.update_subscription(
            payload["organization_id"],
            SubscriptionPlan(subscription_data.subscription_plan)
        )
        
        return {
            "organization": OrganizationResponse(**organization.__dict__),
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )

# Team Collaboration Endpoints
@router.post("/api/team/invite", response_model=TeamInvitationResponse, summary="Invite Team Member")
async def invite_team_member(
    invitation_data: TeamInvitationRequest = Body(...),
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Invite a team member to join the organization.
    Sends invitation email and creates pending invitation.
    """
    try:
        # Verify token and get user info
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check permissions
        if "users:create" not in payload.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Check quota
        quota_check = await tenancy_service.check_organization_quota(payload["organization_id"], "users")
        if not quota_check["is_available"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User quota exceeded"
            )
        
        # Send invitation
        invitation = await tenancy_service.invite_team_member(
            payload["organization_id"],
            invitation_data.email,
            UserRole(invitation_data.role),
            payload["user_id"]
        )
        
        return TeamInvitationResponse(**invitation.__dict__)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting team member: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite team member"
        )

@router.get("/api/team/invitations", summary="List Pending Invitations")
async def list_pending_invitations(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    List pending team invitations for the organization.
    Returns invitations that are awaiting acceptance.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        invitations = await tenancy_service.team_manager.get_pending_invitations(payload["organization_id"])
        
        return {
            "invitations": [TeamInvitationResponse(**inv.__dict__) for inv in invitations],
            "total_count": len(invitations),
            "organization_id": payload["organization_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing pending invitations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list invitations"
        )

@router.post("/api/team/invitations/{invitation_id}/accept", response_model=UserResponse, summary="Accept Team Invitation")
async def accept_invitation(
    invitation_id: str,
    user_data: UserCreateRequest = Body(...),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Accept a team invitation and create user account.
    Creates user with specified role and organization.
    """
    try:
        # Accept invitation and create user
        user = await tenancy_service.team_manager.accept_invitation(invitation_id, user_data.dict())
        
        return UserResponse(**user.__dict__)
    except Exception as e:
        logger.error(f"Error accepting invitation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept invitation"
        )

# Quota Management Endpoints
@router.get("/api/quotas/{quota_type}", response_model=QuotaResponse, summary="Check Quota")
async def check_quota(
    quota_type: str,
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Check quota usage for specific type.
    Returns current usage, limits, and availability.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        quota_info = await tenancy_service.check_organization_quota(payload["organization_id"], quota_type)
        
        return QuotaResponse(**quota_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking quota: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check quota"
        )

@router.get("/api/quotas", summary="List All Quotas")
async def list_all_quotas(
    authorization: str = Header(..., description="Bearer token"),
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    List all quotas for the organization.
    Returns quota information for all types.
    """
    try:
        # Verify token and get organization ID
        token = authorization.split(" ")[1]
        payload = tenancy_service.user_manager.verify_jwt_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        quotas = {}
        quota_types = ["users", "campaigns", "storage_gb", "api_calls", "reports"]
        
        for quota_type in quota_types:
            quotas[quota_type] = await tenancy_service.check_organization_quota(payload["organization_id"], quota_type)
        
        return {
            "quotas": {k: QuotaResponse(**v) for k, v in quotas.items()},
            "organization_id": payload["organization_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing quotas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list quotas"
        )

# Multi-Tenancy Health Check
@router.get("/api/tenancy/health", summary="Multi-Tenancy Health Check")
async def tenancy_health_check(
    tenancy_service: MultiTenancyService = Depends(get_tenancy_service)
):
    """
    Check the health of the multi-tenancy system.
    Returns service status and capabilities.
    """
    try:
        # Check database connection
        await tenancy_service.db.admin.command('ping')
        
        # Check service components
        components = {
            "user_manager": tenancy_service.user_manager is not None,
            "organization_manager": tenancy_service.organization_manager is not None,
            "team_manager": tenancy_service.team_manager is not None,
            "quota_manager": tenancy_service.quota_manager is not None,
            "email_service": tenancy_service.email_service is not None
        }
        
        all_healthy = all(components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
            "capabilities": {
                "user_management": True,
                "organization_management": True,
                "team_collaboration": True,
                "quota_management": True,
                "subscription_management": True,
                "jwt_authentication": True,
                "email_notifications": True
            },
            "supported_roles": [role.value for role in UserRole],
            "supported_plans": [plan.value for plan in SubscriptionPlan],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking tenancy health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
