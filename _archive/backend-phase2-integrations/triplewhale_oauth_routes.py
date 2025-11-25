"""
TripleWhale OAuth2 API Routes
Note: TripleWhale primarily uses API keys, but supports OAuth for partner integrations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import logging

from core.auth import get_current_user
from integrations.triplewhale.oauth2 import triplewhale_oauth2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/integrations/triplewhale", tags=["TripleWhale OAuth"])


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
    """Get OAuth2 authorization URL (for partner integrations)"""
    try:
        # Validate OAuth configuration
        if not triplewhale_oauth2.client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TripleWhale OAuth2 not configured. Set TRIPLEWHALE_CLIENT_ID environment variable."
            )
        
        state = secrets.token_urlsafe(32)
        
        await db.oauth_states.insert_one({
            "user_id": current_user["user_id"],
            "organization_id": current_user["organization_id"],
            "state": state,
            "platform": "triplewhale",
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        })
        
        auth_url = triplewhale_oauth2.get_authorization_url(state=state)
        
        return {
            "success": True,
            "data": {
                "authorization_url": auth_url,
                "state": state
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate TripleWhale OAuth URL: {e}", exc_info=True)
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
        state_record = await db.oauth_states.find_one({
            "state": request.state,
            "user_id": current_user["user_id"],
            "platform": "triplewhale"
        })
        
        if not state_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        if state_record["expires_at"] < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State parameter expired"
            )
        
        # Exchange code for tokens
        try:
            tokens = await triplewhale_oauth2.exchange_code_for_tokens(request.code)
        except Exception as e:
            logger.error(f"Token exchange failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code for tokens: {str(e)}"
            )
        
        # Validate token response
        if not tokens or not tokens.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid token response from TripleWhale"
            )
        
        # Store tokens
        organization_id = current_user["organization_id"]
        from services.production_secrets_manager import production_secrets_manager
        await production_secrets_manager.store_secret(
            f"platform_creds_{organization_id}_triplewhale",
            {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token"),
                "expires_at": datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
            }
        )
        
        # Create integration record
        integration_record = {
            "integration_id": f"{organization_id}_triplewhale",
            "organization_id": organization_id,
            "platform": "triplewhale",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.platform_integrations.insert_one(integration_record)
        
        # Delete used state
        await db.oauth_states.delete_one({"_id": state_record["_id"]})
        
        logger.info(f"TripleWhale OAuth connected for organization {organization_id}")
        
        return {
            "success": True,
            "data": {
                "integration_id": integration_record["integration_id"],
                "platform": "triplewhale",
                "status": "connected"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to handle TripleWhale OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle OAuth callback: {str(e)}"
        )


@router.post("/oauth/refresh")
async def refresh_access_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Refresh TripleWhale access token"""
    try:
        organization_id = current_user["organization_id"]
        
        from services.production_secrets_manager import production_secrets_manager
        credentials = await production_secrets_manager.get_secret(
            f"platform_creds_{organization_id}_triplewhale"
        )
        
        if not credentials or not credentials.get("refresh_token"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token available"
            )
        
        tokens = await triplewhale_oauth2.refresh_access_token(credentials["refresh_token"])
        
        # Update stored tokens
        await production_secrets_manager.store_secret(
            f"platform_creds_{organization_id}_triplewhale",
            {
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token", credentials["refresh_token"]),
                "expires_at": datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
            }
        )
        
        return {
            "success": True,
            "data": {
                "access_token": tokens["access_token"],
                "expires_at": datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3600))
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh TripleWhale token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        )

