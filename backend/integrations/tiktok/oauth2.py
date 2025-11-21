"""
TikTok Ads OAuth2 Flow Implementation
Handles OAuth2 authorization and token management for TikTok Marketing API
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TikTokAdsOAuth2:
    """TikTok Ads OAuth2 flow handler"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: Optional[list] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes or [
            "ads.manage",
            "ads.read"
        ]
        
        self.auth_url = "https://ads.tiktok.com/marketing_api/auth"
        self.token_url = "https://ads.tiktok.com/open_api/v1.3/oauth2/access_token/"
        self.revoke_url = "https://ads.tiktok.com/open_api/v1.3/oauth2/revoke/"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "app_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": ",".join(self.scopes),
            "state": state or ""
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "app_id": self.client_id,
                    "secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "auth_code": auth_code or code
                }
                
                async with session.post(self.token_url, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {error_text}")
                        raise Exception(f"Token exchange failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    if token_data.get("code") != 0:
                        error_msg = token_data.get("message", "Unknown error")
                        logger.error(f"TikTok API error: {error_msg}")
                        raise Exception(f"TikTok API error: {error_msg}")
                    
                    data_response = token_data.get("data", {})
                    expires_in = data_response.get("expires_in", 86400)  # Default 24 hours
                    
                    return {
                        "access_token": data_response.get("access_token"),
                        "refresh_token": data_response.get("refresh_token"),
                        "expires_in": expires_in,
                        "token_type": "Bearer",
                        "scope": ",".join(self.scopes),
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in)
                    }
                    
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "app_id": self.client_id,
                    "secret": self.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token
                }
                
                async with session.post(self.token_url, json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {error_text}")
                        raise Exception(f"Token refresh failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    if token_data.get("code") != 0:
                        error_msg = token_data.get("message", "Unknown error")
                        logger.error(f"TikTok API error: {error_msg}")
                        raise Exception(f"TikTok API error: {error_msg}")
                    
                    data_response = token_data.get("data", {})
                    expires_in = data_response.get("expires_in", 86400)
                    
                    return {
                        "access_token": data_response.get("access_token"),
                        "refresh_token": data_response.get("refresh_token", refresh_token),
                        "expires_in": expires_in,
                        "token_type": "Bearer",
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in)
                    }
                    
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise
    
    async def revoke_token(self, access_token: str) -> bool:
        """Revoke access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "app_id": self.client_id,
                    "secret": self.client_secret,
                    "access_token": access_token
                }
                
                async with session.post(self.revoke_url, json=data) as response:
                    if response.status != 200:
                        return False
                    
                    result = await response.json()
                    return result.get("code") == 0
                    
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

