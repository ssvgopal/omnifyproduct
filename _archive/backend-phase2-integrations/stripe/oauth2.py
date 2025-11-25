"""
Stripe OAuth2 Flow Implementation
Handles OAuth2 authorization and token management for Stripe Connect
"""

import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StripeOAuth2:
    """Stripe OAuth2 flow handler (for Stripe Connect)"""
    
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
            "read_write"
        ]
        
        self.auth_url = "https://connect.stripe.com/oauth/authorize"
        self.token_url = "https://connect.stripe.com/oauth/token"
        self.deauthorize_url = "https://connect.stripe.com/oauth/deauthorize"
    
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
                    "client_secret": self.client_secret
                }
                
                async with session.post(self.token_url, data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Token exchange failed: {error_text}")
                        raise Exception(f"Token exchange failed: {error_text}")
                    
                    token_data = await response.json()
                    
                    return {
                        "access_token": token_data.get("access_token"),
                        "refresh_token": token_data.get("refresh_token"),
                        "stripe_publishable_key": token_data.get("stripe_publishable_key"),
                        "stripe_user_id": token_data.get("stripe_user_id"),
                        "scope": token_data.get("scope"),
                        "livemode": token_data.get("livemode", False),
                        "token_type": "Bearer",
                        "expires_at": None  # Stripe Connect tokens don't expire
                    }
                    
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            raise
    
    async def deauthorize(self, stripe_user_id: str) -> bool:
        """Deauthorize Stripe Connect account"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "client_id": self.client_id,
                    "stripe_user_id": stripe_user_id
                }
                
                async with session.post(self.deauthorize_url, data=data) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error deauthorizing Stripe account: {e}")
            return False

