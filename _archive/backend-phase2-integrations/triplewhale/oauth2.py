"""
TripleWhale OAuth2 Integration
Note: TripleWhale primarily uses API keys, but supports OAuth for partner integrations
"""

import logging
import os
from typing import Dict, Any, Optional
import aiohttp
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class TripleWhaleOAuth2:
    """OAuth2 handler for TripleWhale (if OAuth is enabled)"""
    
    def __init__(self):
        self.client_id = os.getenv("TRIPLEWHALE_CLIENT_ID", "")
        self.client_secret = os.getenv("TRIPLEWHALE_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("TRIPLEWHALE_REDIRECT_URI", "http://localhost:8000/api/triplewhale/oauth/callback")
        self.base_url = os.getenv("TRIPLEWHALE_BASE_URL", "https://api.triplewhale.com")
        self.auth_url = f"{self.base_url}/oauth/authorize"
        self.token_url = f"{self.base_url}/oauth/token"
    
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
            raise ValueError("TRIPLEWHALE_CLIENT_ID environment variable not set")
        
        default_scopes = ["read:attribution", "read:revenue", "read:creatives", "read:campaigns"]
        scopes = scopes or default_scopes
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": " ".join(scopes)
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        logger.info("Generated TripleWhale OAuth2 authorization URL")
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
            raise ValueError("TRIPLEWHALE_CLIENT_SECRET environment variable not set")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"TripleWhale token exchange failed: {response.status} - {error_text}")
                        raise Exception(f"Token exchange failed: {response.status} - {error_text}")
                    
                    tokens = await response.json()
                    
                    if not tokens.get("access_token"):
                        logger.error("TripleWhale token response missing access_token")
                        raise Exception("Invalid token response: missing access_token")
                    
                    logger.info("Successfully exchanged TripleWhale authorization code for tokens")
                    return tokens
                    
        except aiohttp.ClientError as e:
            logger.error(f"TripleWhale token exchange request failed: {e}", exc_info=True)
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
            raise ValueError("TRIPLEWHALE_CLIENT_SECRET environment variable not set")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"TripleWhale token refresh failed: {response.status} - {error_text}")
                        raise Exception(f"Token refresh failed: {response.status} - {error_text}")
                    
                    tokens = await response.json()
                    
                    if not tokens.get("access_token"):
                        logger.error("TripleWhale token refresh response missing access_token")
                        raise Exception("Invalid token response: missing access_token")
                    
                    logger.info("Successfully refreshed TripleWhale access token")
                    return tokens
                    
        except aiohttp.ClientError as e:
            logger.error(f"TripleWhale token refresh request failed: {e}", exc_info=True)
            raise Exception(f"Token refresh request failed: {str(e)}")

# Global instance
triplewhale_oauth2 = TripleWhaleOAuth2()

