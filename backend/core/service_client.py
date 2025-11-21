"""
Service Client - HTTP client for inter-service communication
Enables services to call each other in microservices mode
Falls back to direct calls in monolith mode
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    """Service types"""
    AUTH = "auth"
    INTEGRATIONS = "integrations"
    AGENTKIT = "agentkit"
    ANALYTICS = "analytics"
    ONBOARDING = "onboarding"
    ML = "ml"
    INFRASTRUCTURE = "infrastructure"


class ServiceClient:
    """Client for calling other services"""
    
    # Service URLs (can be overridden by environment variables)
    SERVICE_URLS = {
        ServiceType.AUTH: os.getenv('AUTH_SERVICE_URL', 'http://auth-service:80'),
        ServiceType.INTEGRATIONS: os.getenv('INTEGRATIONS_SERVICE_URL', 'http://integrations-service:80'),
        ServiceType.AGENTKIT: os.getenv('AGENTKIT_SERVICE_URL', 'http://agentkit-service:80'),
        ServiceType.ANALYTICS: os.getenv('ANALYTICS_SERVICE_URL', 'http://analytics-service:80'),
        ServiceType.ONBOARDING: os.getenv('ONBOARDING_SERVICE_URL', 'http://onboarding-service:80'),
        ServiceType.ML: os.getenv('ML_SERVICE_URL', 'http://ml-service:80'),
        ServiceType.INFRASTRUCTURE: os.getenv('INFRASTRUCTURE_SERVICE_URL', 'http://infrastructure-service:80'),
    }
    
    def __init__(self):
        self.deployment_mode = os.getenv("DEPLOYMENT_MODE", "monolith")
        self.timeout = float(os.getenv("SERVICE_CLIENT_TIMEOUT", "30.0"))
    
    async def call_service(
        self,
        service_type: ServiceType,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call another service
        
        Args:
            service_type: Type of service to call
            endpoint: API endpoint (e.g., '/api/auth/login')
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body data
            headers: Additional headers
            params: Query parameters
        
        Returns:
            Response data as dictionary
        """
        if self.deployment_mode == "monolith":
            # In monolith mode, services are in the same process
            # For now, we'll still use HTTP calls (can be optimized later)
            logger.debug(f"Monolith mode: calling {service_type.value} via HTTP")
        
        base_url = self.SERVICE_URLS.get(service_type)
        if not base_url:
            raise ValueError(f"Service {service_type.value} not found in service registry")
        
        url = f"{base_url.rstrip('/')}{endpoint}"
        
        # Add default headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Omnify-ServiceClient/1.0",
        }
        if headers:
            request_headers.update(headers)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    headers=request_headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {service_type.value}: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error calling {service_type.value}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling {service_type.value}: {str(e)}")
            raise
    
    async def call_auth_service(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Convenience method to call auth service"""
        return await self.call_service(ServiceType.AUTH, endpoint, method, data, headers)
    
    async def call_integrations_service(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Convenience method to call integrations service"""
        return await self.call_service(ServiceType.INTEGRATIONS, endpoint, method, data, headers)
    
    async def health_check(self, service_type: ServiceType) -> Dict[str, Any]:
        """Check health of a service"""
        try:
            return await self.call_service(service_type, "/health", method="GET")
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": service_type.value,
                "error": str(e)
            }


# Global service client instance
_service_client = None

def get_service_client() -> ServiceClient:
    """Get global service client instance"""
    global _service_client
    if _service_client is None:
        _service_client = ServiceClient()
    return _service_client

