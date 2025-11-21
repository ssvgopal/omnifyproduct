"""
HubSpot OAuth2 Integration
Handles OAuth2 authorization and token management for HubSpot API
"""

import logging
import os
from typing import Dict, Any, Optional
import aiohttp
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class HubSpotOAuth2:
    """HubSpot OAuth2 flow handler"""
    
    def __init__(self):
        self.client_id = os.getenv("HUBSPOT_CLIENT_ID", "")
        self.client_secret = os.getenv("HUBSPOT_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("HUBSPOT_REDIRECT_URI", "http://localhost:8000/api/hubspot/oauth/callback")
        self.auth_url = "https://app.hubspot.com/oauth/authorize"
        self.token_url = "https://api.hubapi.com/oauth/v1/token"
    
    def get_authorization_url(self, state: str, scopes: Optional[list] = None) -> str:
        """
        Generate OAuth2 authorization URL
        
        Args:
            state: State parameter for CSRF protection
            scopes: Optional list of scopes to request
        
        Returns:
            Authorization URL
        """
        if not self.client_id:
            raise ValueError("HUBSPOT_CLIENT_ID environment variable not set")
        
        default_scopes = [
            "contacts",
            "content",
            "reports",
            "automation",
            "marketing",
            "sales-email-read",
            "sales-email-write"
        ]
        scopes = scopes or default_scopes
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        logger.info("Generated HubSpot OAuth2 authorization URL")
        return auth_url
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from OAuth callback
        
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        if not self.client_secret:
            raise ValueError("HUBSPOT_CLIENT_SECRET environment variable not set")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"HubSpot token exchange failed: {response.status} - {error_text}")
                        raise Exception(f"Token exchange failed: {response.status} - {error_text}")
                    
                    tokens = await response.json()
                    
                    if not tokens.get("access_token"):
                        logger.error("HubSpot token response missing access_token")
                        raise Exception("Invalid token response: missing access_token")
                    
                    logger.info("Successfully exchanged HubSpot authorization code for tokens")
                    return tokens
                    
        except aiohttp.ClientError as e:
            logger.error(f"HubSpot token exchange request failed: {e}", exc_info=True)
            raise Exception(f"Token exchange request failed: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token from previous token exchange
        
        Returns:
            New token response
        """
        if not self.client_secret:
            raise ValueError("HUBSPOT_CLIENT_SECRET environment variable not set")
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"HubSpot token refresh failed: {response.status} - {error_text}")
                        raise Exception(f"Token refresh failed: {response.status} - {error_text}")
                    
                    tokens = await response.json()
                    
                    if not tokens.get("access_token"):
                        logger.error("HubSpot token refresh response missing access_token")
                        raise Exception("Invalid token response: missing access_token")
                    
                    logger.info("Successfully refreshed HubSpot access token")
                    return tokens
                    
        except aiohttp.ClientError as e:
            logger.error(f"HubSpot token refresh request failed: {e}", exc_info=True)
            raise Exception(f"Token refresh request failed: {str(e)}")

# Global instance
hubspot_oauth2 = HubSpotOAuth2()

