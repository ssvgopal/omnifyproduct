"""
Klaviyo API Integration
Lifecycle Marketing and Retention platform for DTC brands

Features:
- Email/SMS marketing campaigns
- Customer segmentation
- Lifecycle automation flows
- Analytics and reporting
- Shopify customer sync
"""

import asyncio
import json
import logging
import os
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class KlaviyoConfig:
    """Configuration for Klaviyo API"""
    api_key: str
    base_url: str = "https://a.klaviyo.com/api"
    timeout: int = 30

class KlaviyoClient:
    """
    Klaviyo API Client
    Integrates with Klaviyo lifecycle marketing platform
    Note: Klaviyo uses API keys, not OAuth2
    """
    
    def __init__(self, config: KlaviyoConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        # Klaviyo uses API key in Authorization header
        api_key_encoded = base64.b64encode(f"{config.api_key}:".encode()).decode()
        self.headers = {
            "Authorization": f"Klaviyo-API-Key {config.api_key}",
            "revision": "2024-02-15",  # API version
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to Klaviyo API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"Klaviyo API error: {response.status} - {response_data}")
                    raise Exception(f"Klaviyo API error: {response.status} - {response_data}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"Klaviyo API request failed: {e}")
            raise Exception(f"Klaviyo API request failed: {e}")
    
    # ========== LIST/SEGMENT MANAGEMENT METHODS ==========
    
    async def create_list(self, list_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a list in Klaviyo
        
        Args:
            list_data: List information (name, etc.)
        
        Returns:
            Created list data
        """
        try:
            data = {
                "data": {
                    "type": "list",
                    "attributes": {
                        "name": list_data.get("name", "New List")
                    }
                }
            }
            
            response = await self._make_request("POST", "/lists", data=data)
            
            logger.info(f"Created Klaviyo list: {response.get('data', {}).get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Klaviyo list: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to create list - {str(e)}")
    
    async def get_lists(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get all lists from Klaviyo
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List of lists
        """
        try:
            params = {"page[size]": limit}
            
            response = await self._make_request("GET", "/lists", params=params)
            
            logger.info(f"Retrieved Klaviyo lists: {len(response.get('data', []))} results")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get Klaviyo lists: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to get lists - {str(e)}")
    
    async def create_segment(self, segment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a segment in Klaviyo
        
        Args:
            segment_data: Segment configuration
        
        Returns:
            Created segment data
        """
        try:
            data = {
                "data": {
                    "type": "segment",
                    "attributes": {
                        "name": segment_data.get("name", "New Segment"),
                        "included": segment_data.get("included", []),
                        "filter": segment_data.get("filter", {})
                    }
                }
            }
            
            response = await self._make_request("POST", "/segments", data=data)
            
            logger.info(f"Created Klaviyo segment: {response.get('data', {}).get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Klaviyo segment: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to create segment - {str(e)}")
    
    # ========== PROFILE/CONTACT MANAGEMENT METHODS ==========
    
    async def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a profile in Klaviyo
        
        Args:
            profile_data: Profile information (email, first_name, last_name, etc.)
        
        Returns:
            Profile data
        """
        try:
            data = {
                "data": {
                    "type": "profile",
                    "attributes": {
                        "email": profile_data.get("email"),
                        "first_name": profile_data.get("first_name"),
                        "last_name": profile_data.get("last_name"),
                        "phone_number": profile_data.get("phone_number"),
                        "properties": profile_data.get("properties", {})
                    }
                }
            }
            
            response = await self._make_request("POST", "/profiles", data=data)
            
            logger.info(f"Created/updated Klaviyo profile: {profile_data.get('email')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Klaviyo profile: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to create profile - {str(e)}")
    
    async def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get a profile from Klaviyo
        
        Args:
            profile_id: Klaviyo profile ID or email
        
        Returns:
            Profile data
        """
        try:
            # Klaviyo allows lookup by email or ID
            if "@" in profile_id:
                params = {"filter": f"equals(email,'{profile_id}')"}
                response = await self._make_request("GET", "/profiles", params=params)
            else:
                response = await self._make_request("GET", f"/profiles/{profile_id}")
            
            logger.info(f"Retrieved Klaviyo profile: {profile_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get Klaviyo profile: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to get profile - {str(e)}")
    
    # ========== CAMPAIGN METHODS ==========
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an email/SMS campaign
        
        Args:
            campaign_data: Campaign configuration
        
        Returns:
            Created campaign data
        """
        try:
            data = {
                "data": {
                    "type": "campaign",
                    "attributes": {
                        "name": campaign_data.get("name", "New Campaign"),
                        "status": campaign_data.get("status", "draft"),
                        "audience": {
                            "included": campaign_data.get("audience", [])
                        },
                        "send_options": campaign_data.get("send_options", {}),
                        "tracking_options": campaign_data.get("tracking_options", {})
                    }
                }
            }
            
            response = await self._make_request("POST", "/campaigns", data=data)
            
            logger.info(f"Created Klaviyo campaign: {response.get('data', {}).get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Klaviyo campaign: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to create campaign - {str(e)}")
    
    async def get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get a campaign from Klaviyo
        
        Args:
            campaign_id: Klaviyo campaign ID
        
        Returns:
            Campaign data
        """
        try:
            response = await self._make_request("GET", f"/campaigns/{campaign_id}")
            
            logger.info(f"Retrieved Klaviyo campaign: {campaign_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get Klaviyo campaign: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to get campaign - {str(e)}")
    
    # ========== FLOW AUTOMATION METHODS ==========
    
    async def create_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a flow (automation) in Klaviyo
        
        Args:
            flow_data: Flow configuration
        
        Returns:
            Created flow data
        """
        try:
            data = {
                "data": {
                    "type": "flow",
                    "attributes": {
                        "name": flow_data.get("name", "New Flow"),
                        "status": flow_data.get("status", "draft"),
                        "trigger": flow_data.get("trigger", {}),
                        "actions": flow_data.get("actions", [])
                    }
                }
            }
            
            response = await self._make_request("POST", "/flows", data=data)
            
            logger.info(f"Created Klaviyo flow: {response.get('data', {}).get('id')}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create Klaviyo flow: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to create flow - {str(e)}")
    
    async def trigger_flow(self, flow_id: str, profile_id: str) -> Dict[str, Any]:
        """
        Trigger a flow for a profile
        
        Args:
            flow_id: Klaviyo flow ID
            profile_id: Profile ID to trigger flow for
        
        Returns:
            Trigger result
        """
        try:
            data = {
                "data": {
                    "type": "flow-action",
                    "attributes": {
                        "flow_id": flow_id,
                        "profile_id": profile_id
                    }
                }
            }
            
            response = await self._make_request("POST", "/flow-actions", data=data)
            
            logger.info(f"Triggered Klaviyo flow {flow_id} for profile {profile_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to trigger Klaviyo flow: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to trigger flow - {str(e)}")
    
    # ========== ANALYTICS METHODS ==========
    
    async def get_analytics(
        self,
        start_date: str,
        end_date: str,
        metric_type: str = "email"
    ) -> Dict[str, Any]:
        """
        Get analytics data from Klaviyo
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            metric_type: Metric type (email, sms, etc.)
        
        Returns:
            Analytics data
        """
        try:
            params = {
                "filter": f"greater-or-equal(created,{start_date}),less-or-equal(created,{end_date})",
                "metric_type": metric_type
            }
            
            response = await self._make_request("GET", "/metrics", params=params)
            
            logger.info(f"Retrieved Klaviyo analytics: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get Klaviyo analytics: {e}", exc_info=True)
            raise RuntimeError(f"Klaviyo API error: Failed to get analytics - {str(e)}")

class KlaviyoAdapter:
    """Klaviyo adapter with unified interface for Omnify"""
    
    def __init__(self):
        self.client: Optional[KlaviyoClient] = None
        self.config: Optional[KlaviyoConfig] = None
        
    async def initialize(self, config: Dict[Any, Any]):
        """Initialize Klaviyo adapter with configuration"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("Klaviyo API key is required")
        
        self.config = KlaviyoConfig(
            api_key=api_key,
            base_url=config.get('base_url', 'https://a.klaviyo.com/api'),
            timeout=config.get('timeout', 30)
        )
        
        logger.info("Klaviyo adapter initialized")
        
    async def create_campaign(
        self,
        organization_id: str,
        campaign_data: Dict[Any, Any]
    ) -> Dict[Any, Any]:
        """Create an email/SMS campaign in Klaviyo"""
        if not self.config:
            raise RuntimeError("Klaviyo adapter not initialized")
        
        async with KlaviyoClient(self.config) as client:
            try:
                response = await client.create_campaign(campaign_data)
                
                return {
                    'status': 'success',
                    'campaign_id': response.get('data', {}).get('id'),
                    'data': response,
                    'platform': 'klaviyo',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to create Klaviyo campaign: {e}", exc_info=True)
                raise RuntimeError(f"Klaviyo API error: Failed to create campaign - {str(e)}")
    
    async def create_flow(
        self,
        organization_id: str,
        flow_data: Dict[Any, Any]
    ) -> Dict[Any, Any]:
        """Create a lifecycle automation flow in Klaviyo"""
        if not self.config:
            raise RuntimeError("Klaviyo adapter not initialized")
        
        async with KlaviyoClient(self.config) as client:
            try:
                response = await client.create_flow(flow_data)
                
                return {
                    'status': 'success',
                    'flow_id': response.get('data', {}).get('id'),
                    'data': response,
                    'platform': 'klaviyo',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to create Klaviyo flow: {e}", exc_info=True)
                raise RuntimeError(f"Klaviyo API error: Failed to create flow - {str(e)}")
    
    async def trigger_flow(
        self,
        organization_id: str,
        flow_id: str,
        profile_id: str
    ) -> Dict[Any, Any]:
        """Trigger a flow for a profile"""
        if not self.config:
            raise RuntimeError("Klaviyo adapter not initialized")
        
        async with KlaviyoClient(self.config) as client:
            try:
                response = await client.trigger_flow(flow_id, profile_id)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'klaviyo',
                    'organization_id': organization_id
                }
                
            except Exception as e:
                logger.error(f"Failed to trigger Klaviyo flow: {e}", exc_info=True)
                raise RuntimeError(f"Klaviyo API error: Failed to trigger flow - {str(e)}")
    
    async def get_analytics(
        self,
        organization_id: str,
        start_date: str,
        end_date: str,
        metric_type: str = "email"
    ) -> Dict[Any, Any]:
        """Get analytics data from Klaviyo"""
        if not self.config:
            raise RuntimeError("Klaviyo adapter not initialized")
        
        async with KlaviyoClient(self.config) as client:
            try:
                response = await client.get_analytics(start_date, end_date, metric_type)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'klaviyo',
                    'organization_id': organization_id,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to get Klaviyo analytics: {e}", exc_info=True)
                raise RuntimeError(f"Klaviyo API error: Failed to get analytics - {str(e)}")
    
    async def test_connection(self, organization_id: str, account_id: str = "default") -> Dict[str, Any]:
        """Test Klaviyo connection"""
        if not self.config:
            return {"status": "not_configured", "error": "Klaviyo adapter not initialized"}
        
        try:
            async with KlaviyoClient(self.config) as client:
                # Test with a simple API call
                await client.get_lists(limit=1)
                
                return {
                    "status": "connected",
                    "platform": "klaviyo",
                    "organization_id": organization_id
                }
        except Exception as e:
            logger.error(f"Klaviyo connection test failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "platform": "klaviyo"
            }

# Global instance
klaviyo_adapter = KlaviyoAdapter()

