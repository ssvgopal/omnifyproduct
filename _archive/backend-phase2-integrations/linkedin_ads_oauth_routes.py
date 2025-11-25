"""
LinkedIn Ads OAuth2 API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import logging

from core.auth import get_current_user
from integrations.linkedin.oauth2 import LinkedInAdsOAuth2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/linkedin-ads", tags=["LinkedIn Ads OAuth"])


class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


@router.get("/oauth/authorize")
async def get_authorization_url(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get OAuth2 authorization URL"""
    try:
        import os
        client_id = os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
        redirect_uri = os.environ.get("LINKEDIN_REDIRECT_URI", "https://app.omnify.com/integrations/linkedin-ads/callback")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LinkedIn Ads OAuth2 not configured"
            )
        
        state = secrets.token_urlsafe(32)
        
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "linkedin_ads",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        oauth2 = LinkedInAdsOAuth2(client_id, client_secret, redirect_uri)
        auth_url = oauth2.get_authorization_url(state=state)
        
        return {
            "success": True,
            "data": {
                "authorization_url": auth_url,
                "state": state
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oauth/callback")
async def handle_oauth_callback(
    request: OAuthCallbackRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Handle OAuth2 callback"""
    try:
        # Validate required fields
        if not request.code or not request.code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        
        if not request.state or not request.state.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State parameter is required"
            )
        
        # Verify state
        state_doc = await db.oauth_states.find_one({
            "user_id": current_user["user_id"],
            "state": request.state,
            "platform": "linkedin_ads",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not state_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state"
            )
        
        await db.oauth_states.delete_one({"_id": state_doc["_id"]})
        
        # Get OAuth configuration
        import os
        client_id = os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
        redirect_uri = os.environ.get("LINKEDIN_REDIRECT_URI", "https://app.omnify.com/integrations/linkedin-ads/callback")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LinkedIn Ads OAuth2 not configured"
            )
        
        # Exchange code for tokens
        oauth2 = LinkedInAdsOAuth2(client_id, client_secret, redirect_uri)
        try:
            tokens = await oauth2.exchange_code_for_tokens(request.code)
        except Exception as e:
            logger.error(f"LinkedIn Ads token exchange failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code for tokens: {str(e)}"
            )
        
        # Validate token response
        if not tokens or not tokens.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid token response from LinkedIn Ads"
            )
        
        from core.encryption import encrypt_secret
        
        integration_doc = {
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "linkedin_ads",
            "access_token": encrypt_secret(tokens["access_token"]),
            "token_type": tokens.get("token_type", "Bearer"),
            "expires_at": tokens.get("expires_at"),
            "scope": tokens.get("scope"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.integrations.update_one(
            {
                "user_id": current_user["user_id"],
                "organization_id": current_user["organization_id"],
                "platform": "linkedin_ads"
            },
            {"$set": integration_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "data": {
                "platform": "linkedin_ads",
                "connected": True
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oauth/refresh")
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token"""
    try:
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "linkedin_ads"
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LinkedIn Ads integration not found"
            )
        
        from core.encryption import decrypt_secret
        access_token = decrypt_secret(integration["access_token"])
        
        import os
        client_id = os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET")
        redirect_uri = os.environ.get("LINKEDIN_REDIRECT_URI", "https://app.omnify.com/integrations/linkedin-ads/callback")
        
        oauth2 = LinkedInAdsOAuth2(client_id, client_secret, redirect_uri)
        
        # LinkedIn doesn't provide refresh tokens in the same way, so we'll need to re-authenticate
        # For now, return the existing token if it's still valid
        if integration.get("expires_at") and datetime.utcnow() < integration["expires_at"]:
            return {
                "success": True,
                "data": {
                    "access_token": "***",
                    "expires_at": integration["expires_at"]
                }
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired, please re-authenticate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oauth/disconnect")
async def disconnect(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Disconnect LinkedIn Ads integration"""
    try:
        result = await db.integrations.delete_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "linkedin_ads"
        })
        
        return {
            "success": True,
            "data": {
                "disconnected": result.deleted_count > 0
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

