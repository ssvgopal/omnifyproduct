"""
Authentication API Routes for Omnify Cloud Connect
Handles user registration, login, and JWT token management
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import logging

from models.user_models import (
    UserCreate, UserLogin, UserUpdate, PasswordResetRequest, PasswordResetConfirm,
    OrganizationCreate, OrganizationUpdate, UserInvitationCreate, UserInvitationAccept,
    Token
)
from services.auth_service import AuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()


# ========== AUTHENTICATION ROUTES ==========

@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends()
):
    """Register a new user and organization"""
    try:
        # Create user
        user = await auth_service.create_user(user_data)

        # Get organization
        organization = await auth_service.get_organization(user.organization_id)
        if not organization:
            raise HTTPException(status_code=500, detail="Organization creation failed")

        # Set owner_id if this is the first user
        if not organization.owner_id:
            await auth_service.update_organization(
                organization.organization_id,
                {"owner_id": user.user_id}
            )
            organization.owner_id = user.user_id

        # Create JWT token
        access_token = await auth_service.create_user_token(user, organization)

        return Token(
            access_token=access_token,
            expires_in=86400,  # 24 hours
            user={
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "organization_id": user.organization_id
            },
            organization={
                "organization_id": organization.organization_id,
                "name": organization.name,
                "slug": organization.slug,
                "subscription_tier": organization.subscription_tier
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    request: Request,
    auth_service: AuthService = Depends()
):
    """Authenticate user and return JWT token"""
    try:
        user = await auth_service.authenticate_user(login_data)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account is deactivated")

        # Get organization
        organization = await auth_service.get_organization(user.organization_id)
        if not organization or not organization.is_active:
            raise HTTPException(status_code=401, detail="Organization is inactive")

        # Create JWT token
        access_token = await auth_service.create_user_token(user, organization)

        return Token(
            access_token=access_token,
            expires_in=86400,
            user={
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "organization_id": user.organization_id
            },
            organization={
                "organization_id": organization.organization_id,
                "name": organization.name,
                "slug": organization.slug,
                "subscription_tier": organization.subscription_tier
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Refresh JWT token"""
    try:
        # Decode current token
        payload = auth_service.decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get user and organization
        user = await auth_service.get_user_by_id(payload.get("user_id"))
        organization = await auth_service.get_organization(payload.get("organization_id"))

        if not user or not organization:
            raise HTTPException(status_code=401, detail="User or organization not found")

        # Create new token
        access_token = await auth_service.create_user_token(user, organization)

        return Token(
            access_token=access_token,
            expires_in=86400,
            user={
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            },
            organization={
                "organization_id": organization.organization_id,
                "name": organization.name,
                "slug": organization.slug,
                "subscription_tier": organization.subscription_tier
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")


# ========== USER MANAGEMENT ROUTES ==========

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Get current user information"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "user_id": user.user_id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": user.organization_id,
            "preferences": user.preferences,
            "last_login": user.last_login,
            "created_at": user.created_at
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user information")


@router.put("/me", response_model=Dict[str, Any])
async def update_current_user(
    user_update: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Update current user information"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        success = await auth_service.update_user(user.user_id, user_update)
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        # Get updated user
        updated_user = await auth_service.get_user_by_id(user.user_id)
        return {"success": True, "user": {
            "user_id": updated_user.user_id,
            "email": updated_user.email,
            "full_name": updated_user.full_name,
            "preferences": updated_user.preferences
        }}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {str(e)}")
        raise HTTPException(status_code=500, detail="Update failed")


@router.post("/password/reset-request", response_model=Dict[str, str])
async def request_password_reset(
    reset_data: PasswordResetRequest,
    auth_service: AuthService = Depends()
):
    """Request password reset"""
    try:
        reset_token = await auth_service.initiate_password_reset(reset_data)
        return {"message": "If the email exists, a reset link has been sent", "token": reset_token}

    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset request failed")


@router.post("/password/reset-confirm", response_model=Dict[str, str])
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends()
):
    """Confirm password reset with token"""
    try:
        success = await auth_service.reset_password(reset_data.token, reset_data.new_password)
        if not success:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        return {"message": "Password reset successful"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        raise HTTPException(status_code=500, detail="Password reset failed")


# ========== ORGANIZATION MANAGEMENT ROUTES ==========

@router.get("/organization", response_model=Dict[str, Any])
async def get_current_organization(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Get current organization information"""
    try:
        organization = await auth_service.get_current_organization(credentials.credentials)
        if not organization:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "organization_id": organization.organization_id,
            "name": organization.name,
            "slug": organization.slug,
            "owner_id": organization.owner_id,
            "settings": organization.settings,
            "subscription_tier": organization.subscription_tier,
            "max_users": organization.max_users,
            "max_campaigns": organization.max_campaigns,
            "created_at": organization.created_at
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get organization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get organization information")


@router.put("/organization", response_model=Dict[str, Any])
async def update_organization(
    org_update: OrganizationUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Update organization information"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check permissions (only owner/admin can update)
        if user.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        success = await auth_service.update_organization(user.organization_id, org_update.dict(exclude_unset=True))
        if not success:
            raise HTTPException(status_code=500, detail="Update failed")

        return {"success": True, "message": "Organization updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update organization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Update failed")


# ========== INVITATION MANAGEMENT ROUTES ==========

@router.post("/invitations", response_model=Dict[str, Any])
async def create_invitation(
    invitation_data: UserInvitationCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Create user invitation"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check permissions
        if user.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        invitation = await auth_service.create_invitation(
            user.organization_id,
            invitation_data,
            user.user_id
        )

        return {
            "invitation_id": invitation.invitation_id,
            "email": invitation.email,
            "role": invitation.role,
            "token": invitation.token,
            "expires_at": invitation.expires_at
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create invitation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Invitation creation failed")


@router.post("/invitations/accept", response_model=Token)
async def accept_invitation(
    accept_data: UserInvitationAccept,
    request: Request,
    auth_service: AuthService = Depends()
):
    """Accept user invitation"""
    try:
        user = await auth_service.accept_invitation(accept_data)

        organization = await auth_service.get_organization(user.organization_id)
        if not organization:
            raise HTTPException(status_code=500, detail="Organization not found")

        # Create JWT token
        access_token = await auth_service.create_user_token(user, organization)

        return Token(
            access_token=access_token,
            expires_in=86400,
            user={
                "user_id": user.user_id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            },
            organization={
                "organization_id": organization.organization_id,
                "name": organization.name,
                "slug": organization.slug,
                "subscription_tier": organization.subscription_tier
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Accept invitation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Invitation acceptance failed")


@router.get("/limits", response_model=Dict[str, Any])
async def get_usage_limits(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Get current usage limits and usage"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        organization = await auth_service.get_current_organization(credentials.credentials)

        if not user or not organization:
            raise HTTPException(status_code=401, detail="Invalid token")

        limits = await auth_service.check_user_limits(user, organization)

        return {
            "organization_id": organization.organization_id,
            "subscription_tier": organization.subscription_tier,
            "limits": limits
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get limits error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get usage limits")


# ========== HEALTH CHECK ==========

@router.get("/verify", response_model=Dict[str, Any])
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends()
):
    """Verify JWT token is valid"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        organization = await auth_service.get_current_organization(credentials.credentials)

        if not user or not organization:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "valid": True,
            "user_id": user.user_id,
            "organization_id": organization.organization_id,
            "role": user.role
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"valid": False, "error": str(e)}
