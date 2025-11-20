"""
Meta Ads OAuth2 API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

from core.auth import get_current_user
from integrations.meta_ads.oauth2 import MetaAdsOAuth2

router = APIRouter(prefix="/api/integrations/meta-ads", tags=["Meta Ads OAuth"])


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
        # Get Meta Ads OAuth2 config from environment
        import os
        app_id = os.environ.get("META_APP_ID")
        app_secret = os.environ.get("META_APP_SECRET")
        redirect_uri = os.environ.get("META_REDIRECT_URI", "https://app.omnify.com/integrations/meta-ads/callback")
        
        if not app_id or not app_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Meta Ads OAuth2 not configured"
            )
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store state in database for verification
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "meta_ads",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        oauth2 = MetaAdsOAuth2(app_id, app_secret, redirect_uri)
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
        # Verify state
        state_doc = await db.oauth_states.find_one({
            "user_id": current_user["user_id"],
            "state": request.state,
            "platform": "meta_ads",
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
        app_id = os.environ.get("META_APP_ID")
        app_secret = os.environ.get("META_APP_SECRET")
        redirect_uri = os.environ.get("META_REDIRECT_URI", "https://app.omnify.com/integrations/meta-ads/callback")
        
        oauth2 = MetaAdsOAuth2(app_id, app_secret, redirect_uri)
        tokens = await oauth2.exchange_code_for_tokens(request.code)
        
        # Debug token to get user info
        token_info = await oauth2.debug_token(tokens["access_token"])
        user_id = token_info.get("data", {}).get("user_id")
        
        # Store tokens in database (encrypted)
        from core.encryption import encrypt_secret
        
        integration_doc = {
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "meta_ads",
            "access_token": encrypt_secret(tokens["access_token"]),
            "token_type": tokens["token_type"],
            "expires_at": tokens["expires_at"],
            "meta_user_id": user_id,
            "token_info": token_info,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Upsert integration
        await db.integrations.update_one(
            {
                "user_id": current_user["user_id"],
                "organization_id": current_user["organization_id"],
                "platform": "meta_ads"
            },
            {"$set": integration_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Meta Ads integration connected successfully"
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
        from core.encryption import decrypt_secret, encrypt_secret
        
        # Get integration
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "meta_ads",
            "is_active": True
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta Ads integration not found"
            )
        
        # Decrypt access token
        access_token = decrypt_secret(integration["access_token"])
        
        # Refresh token
        import os
        app_id = os.environ.get("META_APP_ID")
        app_secret = os.environ.get("META_APP_SECRET")
        redirect_uri = os.environ.get("META_REDIRECT_URI", "https://app.omnify.com/integrations/meta-ads/callback")
        
        oauth2 = MetaAdsOAuth2(app_id, app_secret, redirect_uri)
        new_tokens = await oauth2.refresh_access_token(access_token)
        
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
    """Disconnect Meta Ads integration"""
    try:
        from core.encryption import decrypt_secret
        
        # Get integration
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "meta_ads",
            "is_active": True
        })
        
        if not integration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meta Ads integration not found"
            )
        
        # Revoke token if user_id available
        user_id = integration.get("meta_user_id")
        if user_id:
            import os
            app_id = os.environ.get("META_APP_ID")
            app_secret = os.environ.get("META_APP_SECRET")
            redirect_uri = os.environ.get("META_REDIRECT_URI", "https://app.omnify.com/integrations/meta-ads/callback")
            
            oauth2 = MetaAdsOAuth2(app_id, app_secret, redirect_uri)
            access_token = decrypt_secret(integration["access_token"])
            await oauth2.revoke_token(user_id, access_token)
        
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
            "message": "Meta Ads integration disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

