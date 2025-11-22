"""
Service-to-Service Authentication
Generates and validates JWT tokens for inter-service communication
"""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceRole(str, Enum):
    """Service roles for service-to-service authentication"""
    AUTH = "auth"
    INTEGRATIONS = "integrations"
    AGENTKIT = "agentkit"
    ANALYTICS = "analytics"
    ONBOARDING = "onboarding"
    ML = "ml"
    INFRASTRUCTURE = "infrastructure"


class ServiceAuth:
    """Service-to-service authentication using JWT tokens"""
    
    def __init__(self):
        self.secret = os.getenv("SERVICE_JWT_SECRET", os.getenv("JWT_SECRET_KEY", ""))
        self.algorithm = os.getenv("SERVICE_JWT_ALGORITHM", "HS256")
        self.token_expiry = timedelta(hours=1)  # Short-lived service tokens
        
        if not self.secret:
            logger.warning("SERVICE_JWT_SECRET not set, service-to-service auth disabled")
    
    def generate_service_token(self, service_name: str, target_service: Optional[str] = None) -> str:
        """
        Generate JWT token for service-to-service communication
        
        Args:
            service_name: Name of the calling service
            target_service: Optional target service name (for scoped tokens)
        
        Returns:
            JWT token string
        """
        if not self.secret:
            return ""  # Auth disabled
        
        payload = {
            "service": service_name,
            "type": "service",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.token_expiry,
        }
        
        if target_service:
            payload["target_service"] = target_service
        
        try:
            token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating service token: {e}")
            return ""
    
    def verify_service_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify service-to-service JWT token
        
        Args:
            token: JWT token to verify
        
        Returns:
            Decoded payload if valid, None otherwise
        """
        if not self.secret:
            return None  # Auth disabled
        
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            
            # Verify it's a service token
            if payload.get("type") != "service":
                logger.warning("Token is not a service token")
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Service token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid service token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying service token: {e}")
            return None
    
    def get_service_name(self) -> str:
        """Get current service name from environment"""
        return os.getenv("SERVICE_NAME", "unknown")


# Global instance
_service_auth = None

def get_service_auth() -> ServiceAuth:
    """Get global service auth instance"""
    global _service_auth
    if _service_auth is None:
        _service_auth = ServiceAuth()
    return _service_auth

