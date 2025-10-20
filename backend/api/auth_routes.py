"""
Authentication Routes with Keycloak Integration
Enterprise-grade auth endpoints with session management and device tracking
"""

import os
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from services.oidc_auth import oidc_auth_service, TokenValidationResult, get_current_user
from services.opa_policy_engine import evaluate_access_policy, PolicyEvaluationResult
from database.mongodb_schema import MongoDBSchema

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[str] = None
    remember_me: bool = False

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]
    session_id: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    organization_id: str
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    last_login: Optional[datetime] = None

class SessionInfo(BaseModel):
    session_id: str
    device_id: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool

class DeviceInfo(BaseModel):
    device_id: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    last_seen: datetime
    is_trusted: bool = False

# ========== KEYCLOAK INTEGRATION ==========

async def authenticate_with_keycloak(email: str, password: str) -> Dict[str, Any]:
    """Authenticate user with Keycloak"""
    try:
        if not oidc_auth_service.keycloak_config:
            raise ValueError("Keycloak not configured")

        # Keycloak token endpoint
        token_url = f"{oidc_auth_service.keycloak_config.issuer_url}/realms/{oidc_auth_service.keycloak_config.realm}/protocol/openid-connect/token"
        
        # Prepare token request
        data = {
            "grant_type": "password",
            "client_id": oidc_auth_service.keycloak_config.client_id,
            "client_secret": oidc_auth_service.keycloak_config.client_secret,
            "username": email,
            "password": password,
            "scope": "openid email profile"
        }

        # Make request to Keycloak
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user info
                user_info_url = f"{oidc_auth_service.keycloak_config.issuer_url}/realms/{oidc_auth_service.keycloak_config.realm}/protocol/openid-connect/userinfo"
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                
                user_response = await client.get(user_info_url, headers=headers)
                user_info = user_response.json() if user_response.status_code == 200 else {}

                return {
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in", 3600),
                    "user_info": user_info
                }
            else:
                logger.error(f"Keycloak authentication failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )

    except httpx.TimeoutException:
        logger.error("Keycloak request timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service timeout"
        )
    except Exception as e:
        logger.error(f"Keycloak authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

async def refresh_keycloak_token(refresh_token: str) -> Dict[str, Any]:
    """Refresh Keycloak token"""
    try:
        if not oidc_auth_service.keycloak_config:
            raise ValueError("Keycloak not configured")

        # Keycloak token refresh endpoint
        token_url = f"{oidc_auth_service.keycloak_config.issuer_url}/realms/{oidc_auth_service.keycloak_config.realm}/protocol/openid-connect/token"
        
        data = {
            "grant_type": "refresh_token",
            "client_id": oidc_auth_service.keycloak_config.client_id,
            "client_secret": oidc_auth_service.keycloak_config.client_secret,
            "refresh_token": refresh_token
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Keycloak token refresh failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

    except Exception as e:
        logger.error(f"Keycloak token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh error"
        )

# ========== INTERNAL AUTHENTICATION ==========

async def authenticate_internal(email: str, password: str, db: MongoDBSchema) -> Dict[str, Any]:
    """Authenticate user with internal system"""
    try:
        # Get user from database
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Verify password
        if not pwd_context.verify(password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )

        # Generate tokens
        tokens = await oidc_auth_service.generate_internal_tokens(
            user_id=user["user_id"],
            organization_id=user["organization_id"],
            email=user["email"],
            roles=user.get("roles", ["user"])
        )

        # Update last login
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return {
            **tokens,
            "user_info": {
                "user_id": user["user_id"],
                "email": user["email"],
                "organization_id": user["organization_id"],
                "roles": user.get("roles", ["user"]),
                "permissions": user.get("permissions", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

# ========== AUTHENTICATION ROUTES ==========

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: MongoDBSchema = Depends(lambda: MongoDBSchema())
):
    """Login user with email and password"""
    try:
        # Get client information
        client_ip = http_request.client.host
        user_agent = http_request.headers.get("user-agent", "")
        device_id = request.device_id or f"device_{client_ip}_{hash(user_agent) % 10000}"

        # Authenticate user
        if oidc_auth_service.enable_keycloak:
            auth_result = await authenticate_with_keycloak(request.email, request.password)
            user_info = auth_result["user_info"]
            
            # Create session
            session = await oidc_auth_service.create_session(
                user_id=user_info.get("sub", user_info.get("user_id")),
                organization_id=user_info.get("organization_id", "default"),
                email=user_info.get("email", request.email),
                roles=user_info.get("roles", ["user"]),
                device_id=device_id,
                ip_address=client_ip,
                user_agent=user_agent
            )

            return LoginResponse(
                access_token=auth_result["access_token"],
                refresh_token=auth_result.get("refresh_token", ""),
                token_type="Bearer",
                expires_in=auth_result["expires_in"],
                user=user_info,
                session_id=session.session_id
            )

        elif oidc_auth_service.enable_internal_auth:
            auth_result = await authenticate_internal(request.email, request.password, db)
            user_info = auth_result["user_info"]
            
            # Create session
            session = await oidc_auth_service.create_session(
                user_id=user_info["user_id"],
                organization_id=user_info["organization_id"],
                email=user_info["email"],
                roles=user_info["roles"],
                device_id=device_id,
                ip_address=client_ip,
                user_agent=user_agent
            )

            return LoginResponse(
                access_token=auth_result["access_token"],
                refresh_token=auth_result["refresh_token"],
                token_type=auth_result["token_type"],
                expires_in=auth_result["expires_in"],
                user=user_info,
                session_id=session.session_id
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No authentication provider configured"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    http_request: Request
):
    """Refresh access token using refresh token"""
    try:
        if oidc_auth_service.enable_keycloak:
            # Refresh Keycloak token
            token_data = await refresh_keycloak_token(request.refresh_token)
            
            # Get user info from new access token
            user_info_url = f"{oidc_auth_service.keycloak_config.issuer_url}/realms/{oidc_auth_service.keycloak_config.realm}/protocol/openid-connect/userinfo"
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            
            async with httpx.AsyncClient() as client:
                user_response = await client.get(user_info_url, headers=headers)
                user_info = user_response.json() if user_response.status_code == 200 else {}

            return LoginResponse(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", request.refresh_token),
                token_type="Bearer",
                expires_in=token_data.get("expires_in", 3600),
                user=user_info,
                session_id=""  # Would need to track session
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Token refresh not implemented for internal auth"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Logout user and revoke session"""
    try:
        # Revoke token
        await oidc_auth_service.revoke_token(credentials.credentials)
        
        # Revoke user sessions (optional - could be more granular)
        await oidc_auth_service.revoke_user_sessions(current_user.user_id)

        return {"message": "Logged out successfully"}

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get current user profile"""
    return UserProfile(
        user_id=current_user.user_id,
        email=current_user.email,
        organization_id=current_user.organization_id,
        roles=current_user.roles,
        permissions=current_user.permissions,
        created_at=datetime.utcnow(),  # Would get from database
        last_login=datetime.utcnow()   # Would get from database
    )

@router.get("/sessions", response_model=List[SessionInfo])
async def get_user_sessions(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get all active sessions for current user"""
    try:
        sessions = await oidc_auth_service.get_user_sessions(current_user.user_id)
        
        return [
            SessionInfo(
                session_id=session.session_id,
                device_id=session.device_id,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                created_at=session.created_at,
                last_activity=session.last_activity,
                expires_at=session.expires_at,
                is_active=session.is_active
            )
            for session in sessions
        ]

    except Exception as e:
        logger.error(f"Get sessions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sessions"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Revoke a specific session"""
    try:
        # Check if user owns this session
        sessions = await oidc_auth_service.get_user_sessions(current_user.user_id)
        user_session_ids = [s.session_id for s in sessions]
        
        if session_id not in user_session_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        success = await oidc_auth_service.revoke_session(session_id)
        
        if success:
            return {"message": "Session revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revoke session error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke session"
        )

@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    db: MongoDBSchema = Depends(lambda: MongoDBSchema())
):
    """Request password reset (send email)"""
    try:
        # Check if user exists
        user = await db.users.find_one({"email": request.email})
        if not user:
            # Don't reveal if user exists
            return {"message": "If the email exists, a reset link has been sent"}

        # Generate reset token (in production, use proper token generation)
        reset_token = f"reset_{user['user_id']}_{int(datetime.utcnow().timestamp())}"
        
        # Store reset token (in production, use proper storage with expiry)
        await db.password_reset_tokens.insert_one({
            "user_id": user["user_id"],
            "email": request.email,
            "token": reset_token,
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "used": False,
            "created_at": datetime.utcnow()
        })

        # In production, send email with reset link
        logger.info(f"Password reset requested for {request.email}, token: {reset_token}")

        return {"message": "If the email exists, a reset link has been sent"}

    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: MongoDBSchema = Depends(lambda: MongoDBSchema())
):
    """Confirm password reset with token"""
    try:
        # Find reset token
        reset_record = await db.password_reset_tokens.find_one({
            "token": request.token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })

        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Hash new password
        password_hash = pwd_context.hash(request.new_password)

        # Update user password
        await db.users.update_one(
            {"user_id": reset_record["user_id"]},
            {"$set": {"password_hash": password_hash}}
        )

        # Mark token as used
        await db.password_reset_tokens.update_one(
            {"token": request.token},
            {"$set": {"used": True, "used_at": datetime.utcnow()}}
        )

        # Revoke all user sessions
        await oidc_auth_service.revoke_user_sessions(reset_record["user_id"])

        return {"message": "Password reset successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset confirm error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: TokenValidationResult = Depends(get_current_user),
    db: MongoDBSchema = Depends(lambda: MongoDBSchema())
):
    """Change password for authenticated user"""
    try:
        # Get user
        user = await db.users.find_one({"user_id": current_user.user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not pwd_context.verify(request.current_password, user.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash new password
        password_hash = pwd_context.hash(request.new_password)

        # Update password
        await db.users.update_one(
            {"user_id": current_user.user_id},
            {"$set": {"password_hash": password_hash}}
        )

        # Revoke all user sessions except current
        await oidc_auth_service.revoke_user_sessions(current_user.user_id)

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

@router.get("/health")
async def auth_health_check():
    """Health check for authentication service"""
    return await oidc_auth_service.health_check()