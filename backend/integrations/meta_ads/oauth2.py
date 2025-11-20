"""
Meta Ads OAuth2 Flow Implementation
Handles OAuth2 authorization and token management for Meta Marketing API
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MetaAdsOAuth2:
    """Meta Ads OAuth2 flow handler"""
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        redirect_uri: str,
        scopes: Optional[list] = None
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or [
            "ads_management",
            "ads_read",
            "business_management"
        ]
        
        self.auth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        self.token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
        self.debug_token_url = "https://graph.facebook.com/v18.0/debug_token"
        self.revoke_url = "https://graph.facebook.com/v18.0/{user-id}/permissions"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": ",".join(self.scopes),
            "response_type": "code"
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code
                }
                
                async with session.get(self.token_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {error_text}")
                        raise Exception(f"Token exchange failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    # Meta returns access_token and expires_in
                    access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 5184000)  # Default 60 days
                    
                    # Get long-lived token (60 days)
                    long_lived_token = await self._exchange_for_long_lived_token(access_token)
                    
                    return {
                        "access_token": long_lived_token.get("access_token", access_token),
                        "expires_in": long_lived_token.get("expires_in", expires_in),
                        "token_type": "Bearer",
                        "expires_at": datetime.utcnow() + timedelta(seconds=long_lived_token.get("expires_in", expires_in))
                    }
                    
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    async def _exchange_for_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived token (60 days)"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "grant_type": "fb_exchange_token",
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "fb_exchange_token": short_lived_token
                }
                
                async with session.get(self.token_url, params=params) as response:
                    if response.status != 200:
                        # If exchange fails, return original token
                        logger.warning("Failed to exchange for long-lived token, using short-lived token")
                        return {
                            "access_token": short_lived_token,
                            "expires_in": 3600  # 1 hour default
                        }
                    
                    return await response.json()
                    
        except Exception as e:
            logger.warning(f"Error exchanging for long-lived token: {e}")
            return {
                "access_token": short_lived_token,
                "expires_in": 3600
            }
    
    async def refresh_access_token(self, access_token: str) -> Dict[str, Any]:
        """Refresh access token (Meta tokens are long-lived, but can be refreshed)"""
        try:
            # For Meta, we can extend the token or get a new long-lived token
            # This is a simplified refresh - in production, check token expiry first
            async with aiohttp.ClientSession() as session:
                params = {
                    "grant_type": "fb_exchange_token",
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "fb_exchange_token": access_token
                }
                
                async with session.get(self.token_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {error_text}")
                        raise Exception(f"Token refresh failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    return {
                        "access_token": token_data.get("access_token"),
                        "expires_in": token_data.get("expires_in", 5184000),
                        "token_type": "Bearer",
                        "expires_at": datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))
                    }
                    
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise
    
    async def debug_token(self, access_token: str) -> Dict[str, Any]:
        """Debug token to get user info and permissions"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "input_token": access_token,
                    "access_token": f"{self.app_id}|{self.app_secret}"
                }
                
                async with session.get(self.debug_token_url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token debug failed: {error_text}")
                        raise Exception(f"Token debug failed: {error_text}")
                    
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error debugging token: {e}")
            raise
    
    async def revoke_token(self, user_id: str, access_token: str) -> bool:
        """Revoke access token"""
        try:
            async with aiohttp.ClientSession() as session:
                url = self.revoke_url.format(user_id=user_id)
                params = {
                    "access_token": access_token
                }
                
                async with session.delete(url, params=params) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

