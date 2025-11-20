"""
Email Verification and Password Reset API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr
import os

from core.auth import get_current_user
from services.email_verification_service import EmailVerificationService

router = APIRouter(prefix="/api/auth", tags=["Email Verification"])


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class VerifyEmailRequest(BaseModel):
    token: str


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


def get_email_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> EmailVerificationService:
    """Get email verification service instance"""
    return EmailVerificationService(db)


@router.post("/verify-email/send")
async def send_verification_email(
    current_user: Dict[str, Any] = Depends(get_current_user),
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Send email verification email to current user"""
    try:
        result = await email_service.send_verification_email(
            current_user["user_id"],
            current_user["email"]
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Verify email with token"""
    try:
        is_verified = await email_service.verify_email(request.token)
        if is_verified:
            return {"success": True, "message": "Email verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
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


@router.post("/verify-email/resend")
async def resend_verification_email(
    email: EmailStr,
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Resend verification email"""
    try:
        result = await email_service.resend_verification_email(email)
        return {"success": True, "data": result}
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


@router.post("/password/reset")
async def request_password_reset(
    request: PasswordResetRequest,
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Request password reset"""
    try:
        result = await email_service.send_password_reset_email(request.email)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/password/reset/verify")
async def verify_reset_token(
    token: str,
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Verify password reset token"""
    try:
        result = await email_service.verify_reset_token(token)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    email_service: EmailVerificationService = Depends(get_email_service)
):
    """Confirm password reset with new password"""
    try:
        # Validate password strength
        if len(request.new_password) < 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 12 characters long"
            )
        
        result = await email_service.reset_password(request.token, request.new_password)
        if result:
            return {"success": True, "message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password"
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

