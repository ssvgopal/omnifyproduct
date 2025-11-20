"""
MFA (Multi-Factor Authentication) API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import os

from core.auth import get_current_user
from services.mfa_service import MFAService, MFAMethod
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/mfa", tags=["MFA"])


class TOTPSetupRequest(BaseModel):
    email: EmailStr


class TOTPVerifyRequest(BaseModel):
    code: str


class SMSVerifyRequest(BaseModel):
    phone_number: str


class SMSVerifyCodeRequest(BaseModel):
    session_id: str
    code: str


class EmailVerifyRequest(BaseModel):
    email: EmailStr


class EmailVerifyCodeRequest(BaseModel):
    session_id: str
    code: str


class DisableMFARequest(BaseModel):
    method: str


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


def get_mfa_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> MFAService:
    """Get MFA service instance"""
    encryption_key = os.environ.get('ENCRYPTION_KEY', 'change-me-in-production')
    sms_api_key = os.environ.get('SMS_API_KEY')
    email_service = None  # TODO: Initialize email service
    return MFAService(db, encryption_key, sms_api_key, email_service)


@router.get("/status")
async def get_mfa_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Get MFA status for current user"""
    try:
        status = await mfa_service.get_mfa_status(current_user["user_id"])
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/totp/setup")
async def setup_totp(
    request: TOTPSetupRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Setup TOTP MFA"""
    try:
        result = await mfa_service.setup_totp(current_user["user_id"], request.email)
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


@router.post("/totp/verify")
async def verify_totp(
    request: TOTPVerifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Verify TOTP code"""
    try:
        is_valid = await mfa_service.verify_totp(current_user["user_id"], request.code)
        if is_valid:
            return {"success": True, "message": "TOTP verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code"
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


@router.post("/sms/send")
async def send_sms_code(
    request: SMSVerifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Send SMS verification code"""
    try:
        result = await mfa_service.send_sms_code(current_user["user_id"], request.phone_number)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/sms/verify")
async def verify_sms_code(
    request: SMSVerifyCodeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Verify SMS code"""
    try:
        is_valid = await mfa_service.verify_sms_code(request.session_id, request.code)
        if is_valid:
            return {"success": True, "message": "SMS code verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid SMS code"
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


@router.post("/email/send")
async def send_email_code(
    request: EmailVerifyRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Send email verification code"""
    try:
        result = await mfa_service.send_email_code(current_user["user_id"], request.email)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/email/verify")
async def verify_email_code(
    request: EmailVerifyCodeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Verify email code"""
    try:
        is_valid = await mfa_service.verify_email_code(request.session_id, request.code)
        if is_valid:
            return {"success": True, "message": "Email code verified successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email code"
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


@router.post("/disable")
async def disable_mfa(
    request: DisableMFARequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    mfa_service: MFAService = Depends(get_mfa_service)
):
    """Disable MFA for user"""
    try:
        method = MFAMethod(request.method)
        result = await mfa_service.disable_mfa(current_user["user_id"], method)
        if result:
            return {"success": True, "message": f"MFA method {method.value} disabled successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA method not found"
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

