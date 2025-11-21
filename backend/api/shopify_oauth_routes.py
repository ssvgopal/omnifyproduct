"""
Shopify OAuth2 API Routes
Uses the OAuth implementation from integrations/shopify/client.py
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import logging

from core.auth import get_current_user
from integrations.shopify.client import shopify_integration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/shopify", tags=["Shopify OAuth"])


class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None
    shop: Optional[str] = None  # shop_domain


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


@router.get("/oauth/authorize")
async def get_authorization_url(
    shop_domain: str = Query(..., description="Shop domain (e.g., 'mystore' for mystore.myshopify.com)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get OAuth2 authorization URL"""
    try:
        state = secrets.token_urlsafe(32)
        
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "shopify",
            "shop_domain": shop_domain,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        auth_url = shopify_integration.get_oauth_url(shop_domain, state)
        
        return {
            "success": True,
            "data": {
                "authorization_url": auth_url,
                "state": state,
                "shop_domain": shop_domain
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
        
        if not request.shop or not request.shop.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shop domain is required"
            )
        
        # Verify state
        state_doc = await db.oauth_states.find_one({
            "user_id": current_user["user_id"],
            "state": request.state,
            "platform": "shopify",
            "shop_domain": request.shop,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not state_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state"
            )
        
        await db.oauth_states.delete_one({"_id": state_doc["_id"]})
        
        # Exchange code for tokens
        try:
            tokens = await shopify_integration.exchange_code_for_tokens(request.shop, request.code)
        except Exception as e:
            logger.error(f"Shopify token exchange failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code for tokens: {str(e)}"
            )
        
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to exchange code for tokens"
            )
        
        # Validate token response
        if not tokens.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid token response from Shopify"
            )
        
        from core.encryption import encrypt_secret
        
        integration_doc = {
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "shopify",
            "shop_domain": request.shop,
            "access_token": encrypt_secret(tokens["access_token"]),
            "shop_id": tokens.get("shop_id"),
            "shop_name": tokens.get("shop_name"),
            "shop_email": tokens.get("shop_email"),
            "shop_currency": tokens.get("shop_currency"),
            "shop_timezone": tokens.get("shop_timezone"),
            "expires_at": tokens.get("expires_at"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.integrations.update_one(
            {
                "user_id": current_user["user_id"],
                "organization_id": current_user["organization_id"],
                "platform": "shopify",
                "shop_domain": request.shop
            },
            {"$set": integration_doc},
            upsert=True
        )
        
        return {
            "success": True,
            "data": {
                "platform": "shopify",
                "shop_domain": request.shop,
                "shop_name": tokens.get("shop_name"),
                "connected": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Shopify OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/oauth/disconnect")
async def disconnect(
    shop_domain: str = Query(..., description="Shop domain to disconnect"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Disconnect Shopify integration"""
    try:
        result = await db.integrations.delete_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "platform": "shopify",
            "shop_domain": shop_domain
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

