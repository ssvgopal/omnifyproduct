"""
Stripe OAuth2 API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import logging

from core.auth import get_current_user
from integrations.stripe.oauth2 import StripeOAuth2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/stripe", tags=["Stripe OAuth"])


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
    """Get OAuth2 authorization URL (for Stripe Connect)"""
    try:
        import os
        client_id = os.environ.get("STRIPE_CONNECT_CLIENT_ID")
        client_secret = os.environ.get("STRIPE_SECRET_KEY")
        redirect_uri = os.environ.get("STRIPE_REDIRECT_URI", "https://app.omnify.com/integrations/stripe/callback")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe OAuth2 not configured"
            )
        
        state = secrets.token_urlsafe(32)
        
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "stripe",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        oauth2 = StripeOAuth2(client_id, client_secret, redirect_uri)
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
            "platform": "stripe",
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
        client_id = os.environ.get("STRIPE_CONNECT_CLIENT_ID")
        client_secret = os.environ.get("STRIPE_SECRET_KEY")
        redirect_uri = os.environ.get("STRIPE_REDIRECT_URI", "https://app.omnify.com/integrations/stripe/callback")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe OAuth2 not configured"
            )
        
        # Exchange code for tokens
        oauth2 = StripeOAuth2(client_id, client_secret, redirect_uri)
        try:
            tokens = await oauth2.exchange_code_for_tokens(request.code)
        except Exception as e:
            logger.error(f"Stripe token exchange failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code for tokens: {str(e)}"
            )
        
        # Validate token response
        if not tokens or not tokens.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid token response from Stripe"
            )
        
        from core.encryption import encrypt_secret
        
        integration_doc = {
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "stripe",
            "access_token": encrypt_secret(tokens["access_token"]),
            "stripe_user_id": tokens.get("stripe_user_id"),
            "stripe_publishable_key": tokens.get("stripe_publishable_key"),
            "livemode": tokens.get("livemode", False),
            "scope": tokens.get("scope"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.integrations.update_one(
            {
                "user_id": current_user["user_id"],
                "organization_id": current_user["organization_id"],
                "platform": "stripe"
            },
            {"$set": integration_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "data": {
                "platform": "stripe",
                "stripe_user_id": tokens.get("stripe_user_id"),
                "connected": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Stripe OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/oauth/disconnect")
async def disconnect(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Disconnect Stripe integration"""
    try:
        integration = await db.integrations.find_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "stripe"
        })
        
        if integration:
            import os
            client_id = os.environ.get("STRIPE_CONNECT_CLIENT_ID")
            client_secret = os.environ.get("STRIPE_SECRET_KEY")
            redirect_uri = os.environ.get("STRIPE_REDIRECT_URI", "https://app.omnify.com/integrations/stripe/callback")
            
            oauth2 = StripeOAuth2(client_id, client_secret, redirect_uri)
            stripe_user_id = integration.get("stripe_user_id")
            
            if stripe_user_id:
                await oauth2.deauthorize(stripe_user_id)
        
        result = await db.integrations.delete_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "stripe"
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

