"""
Google Ads OAuth2 API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

from core.auth import get_current_user
from integrations.google_ads.oauth2 import GoogleAdsOAuth2

router = APIRouter(prefix="/api/integrations/google-ads", tags=["Google Ads OAuth"])


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
        # Get Google Ads OAuth2 config from environment or database
        import os
        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        redirect_uri = os.environ.get("GOOGLE_ADS_REDIRECT_URI", "https://app.omnify.com/integrations/google-ads/callback")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google Ads OAuth2 not configured"
            )
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in database for verification
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "google_ads",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        oauth2 = GoogleAdsOAuth2(client_id, client_secret, redirect_uri)
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
    """Handle OAuth2 callback and store tokens"""
    try:
        from datetime import datetime, timedelta
        
        # Verify state
        state_doc = await db.oauth_states.find_one({
            "user_id": current_user["user_id"],
            "state": request.state,
            "platform": "google_ads",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not state_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state"
            )
        
        # Delete used state
        await db.oauth_states.delete_one({"_id": state_doc["_id"]})
        
        # Exchange code for tokens
        import os
        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        redirect_uri = os.environ.get("GOOGLE_ADS_REDIRECT_URI", "https://app.omnify.com/integrations/google-ads/callback")
        
        oauth2 = GoogleAdsOAuth2(client_id, client_secret, redirect_uri)
        tokens = await oauth2.exchange_code_for_tokens(request.code)
        
        # Store tokens in database (encrypted)
        from core.encryption import encrypt_secret
        
        integration_doc = {
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "google_ads",
            "access_token": encrypt_secret(tokens["access_token"]),
            "refresh_token": encrypt_secret(tokens["refresh_token"]),
            "token_type": tokens["token_type"],
            "expires_at": tokens["expires_at"],
            "scope": tokens.get("scope"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Upsert integration
        await db.integrations.update_one(
            {
                "user_id": current_user["user_id"],
                "organization_id": current_user["organization_id"],
                "platform": "google_ads"
            },
            {"$set": integration_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Google Ads integration connected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oauth/refresh")
async def refresh_tokens(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Refresh access token"""
    try:
        from datetime import datetime
        from core.encryption import decrypt_secret, encrypt_secret
        
        # Get integration
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "google_ads",
            "is_active": True
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Google Ads integration not found"
            )
        
        # Decrypt refresh token
        refresh_token = decrypt_secret(integration["refresh_token"])
        
        # Refresh token
        import os
        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        redirect_uri = os.environ.get("GOOGLE_ADS_REDIRECT_URI", "https://app.omnify.com/integrations/google-ads/callback")
        
        oauth2 = GoogleAdsOAuth2(client_id, client_secret, redirect_uri)
        new_tokens = await oauth2.refresh_access_token(refresh_token)
        
        # Update tokens
        await db.integrations.update_one(
            {"_id": integration["_id"]},
            {
                "$set": {
                    "access_token": encrypt_secret(new_tokens["access_token"]),
                    "expires_at": new_tokens["expires_at"],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Tokens refreshed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/oauth/disconnect")
async def disconnect_integration(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Disconnect Google Ads integration"""
    try:
        from datetime import datetime
        from core.encryption import decrypt_secret
        
        # Get integration
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "google_ads",
            "is_active": True
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Google Ads integration not found"
            )
        
        # Revoke tokens
        import os
        client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")
        redirect_uri = os.environ.get("GOOGLE_ADS_REDIRECT_URI", "https://app.omnify.com/integrations/google-ads/callback")
        
        oauth2 = GoogleAdsOAuth2(client_id, client_secret, redirect_uri)
        
        # Revoke access token
        access_token = decrypt_secret(integration["access_token"])
        await oauth2.revoke_token(access_token)
        
        # Revoke refresh token
        refresh_token = decrypt_secret(integration["refresh_token"])
        await oauth2.revoke_token(refresh_token)
        
        # Mark as inactive
        await db.integrations.update_one(
            {"_id": integration["_id"]},
            {
                "$set": {
                    "is_active": False,
                    "disconnected_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Google Ads integration disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

