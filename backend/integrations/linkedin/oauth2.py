"""
LinkedIn Ads OAuth2 Flow Implementation
Handles OAuth2 authorization and token management for LinkedIn Marketing API
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LinkedInAdsOAuth2:
    """LinkedIn Ads OAuth2 flow handler"""
    
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
            "r_ads",
            "r_ads_reporting",
            "rw_ads"
        ]
        
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.revoke_url = "https://www.linkedin.com/oauth/v2/revoke"
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes)
        }
        
        if state:
            params["state"] = state
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {error_text}")
                        raise Exception(f"Token exchange failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    expires_in = token_data.get("expires_in", 5184000)  # Default 60 days
                    
                    return {
                        "access_token": token_data.get("access_token"),
                        "expires_in": expires_in,
                        "token_type": token_data.get("token_type", "Bearer"),
                        "scope": token_data.get("scope"),
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
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {error_text}")
                        raise Exception(f"Token refresh failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    expires_in = token_data.get("expires_in", 5184000)
                    
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token", refresh_token),
                        "expires_in": expires_in,
                        "token_type": token_data.get("token_type", "Bearer"),
                        "scope": token_data.get("scope"),
                        "expires_at": datetime.utcnow() + timedelta(seconds=expires_in)
                    }
                    
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke access token"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "token": token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                async with session.post(self.revoke_url, data=data) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False

