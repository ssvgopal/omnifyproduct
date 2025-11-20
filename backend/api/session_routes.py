"""
Session Management API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from core.auth import get_current_user
from services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


class DeviceInfo(BaseModel):
    user_agent: str
    platform: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None


class CreateSessionRequest(BaseModel):
    device_info: DeviceInfo
    remember_me: bool = False


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


def get_session_service(
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> SessionService:
    """Get session service instance"""
    # TODO: Get Redis client if available
    redis_client = None
    return SessionService(db, redis_client)


@router.get("")
async def list_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """List all active sessions for current user"""
    try:
        sessions = await session_service.list_user_sessions(current_user["user_id"])
        return {"success": True, "data": sessions}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Revoke specific session"""
    try:
        result = await session_service.revoke_session(session_id, current_user["user_id"])
        if result:
            return {"success": True, "message": "Session revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/revoke-all")
async def revoke_all_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Revoke all sessions for current user"""
    try:
        count = await session_service.revoke_all_sessions(current_user["user_id"])
        return {
            "success": True,
            "message": f"Revoked {count} session(s)",
            "count": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/device/{device_id}")
async def revoke_device_sessions(
    device_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Revoke all sessions for specific device"""
    try:
        count = await session_service.revoke_device_sessions(
            current_user["user_id"],
            device_id
        )
        return {
            "success": True,
            "message": f"Revoked {count} session(s) for device",
            "count": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/activity")
async def update_activity(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_service: SessionService = Depends(get_session_service)
):
    """Update session activity (called periodically by frontend)"""
    try:
        # Get session ID from token or header
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            # Try to extract from auth token
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                # Session ID might be in token payload
                # For now, skip if not provided
                return {"success": True, "message": "Activity updated"}
        
        await session_service.update_session_activity(session_id)
        return {"success": True, "message": "Activity updated"}
    except Exception as e:
        # Don't fail if session update fails
        logger.warning(f"Error updating session activity: {e}")
        return {"success": True, "message": "Activity updated"}

