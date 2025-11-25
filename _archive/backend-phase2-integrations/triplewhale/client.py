"""
TripleWhale API Integration
Attribution and analytics platform for DTC brands ($5M-$150M Shopify brands)

Features:
- Multi-touch attribution
- Cross-channel analytics (Meta, Google, TikTok, etc.)
- Shopify revenue tracking
- Creative performance analytics
- ROAS/CLV calculations
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TripleWhaleConfig:
    """Configuration for TripleWhale API"""
    api_key: str
    base_url: str = "https://api.triplewhale.com/v1"
    timeout: int = 30

class TripleWhaleClient:
    """
    TripleWhale API Client
    Integrates with TripleWhale attribution and analytics platform
    """
    
    def __init__(self, config: TripleWhaleConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
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
        """Make HTTP request to TripleWhale API"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, json=data, params=params) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    logger.error(f"TripleWhale API error: {response.status} - {response_data}")
                    raise Exception(f"TripleWhale API error: {response.status} - {response_data}")
                
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"TripleWhale API request failed: {e}")
            raise Exception(f"TripleWhale API request failed: {e}")
    
    # ========== ATTRIBUTION METHODS ==========
    
    async def get_attribution_data(
        self,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get multi-touch attribution data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            channel: Optional channel filter (meta, google, tiktok, etc.)
            campaign_id: Optional campaign ID filter
        
        Returns:
            Attribution data with touchpoints, conversions, revenue
        """
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if channel:
                params["channel"] = channel
            if campaign_id:
                params["campaign_id"] = campaign_id
            
            response = await self._make_request("GET", "/attribution", params=params)
            
            logger.info(f"Retrieved TripleWhale attribution data: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale attribution data: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get attribution data - {str(e)}")
    
    async def get_revenue_data(
        self,
        start_date: str,
        end_date: str,
        breakdown: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get revenue data from Shopify integration
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            breakdown: Optional breakdown (channel, campaign, creative, etc.)
        
        Returns:
            Revenue data with ROAS, CLV, LTV metrics
        """
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if breakdown:
                params["breakdown"] = breakdown
            
            response = await self._make_request("GET", "/revenue", params=params)
            
            logger.info(f"Retrieved TripleWhale revenue data: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale revenue data: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get revenue data - {str(e)}")
    
    async def get_roas_data(
        self,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get ROAS (Return on Ad Spend) data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            channel: Optional channel filter
        
        Returns:
            ROAS data by channel, campaign, creative
        """
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if channel:
                params["channel"] = channel
            
            response = await self._make_request("GET", "/roas", params=params)
            
            logger.info(f"Retrieved TripleWhale ROAS data: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale ROAS data: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get ROAS data - {str(e)}")
    
    # ========== CREATIVE PERFORMANCE METHODS ==========
    
    async def get_creative_performance(
        self,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get creative performance data (for ORACLE module - fatigue prediction)
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            channel: Optional channel filter
        
        Returns:
            Creative performance data with impressions, clicks, conversions, revenue
        """
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            if channel:
                params["channel"] = channel
            
            response = await self._make_request("GET", "/creatives/performance", params=params)
            
            logger.info(f"Retrieved TripleWhale creative performance: {start_date} to {end_date}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale creative performance: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get creative performance - {str(e)}")
    
    async def get_creative_details(self, creative_id: str) -> Dict[str, Any]:
        """
        Get detailed creative information
        
        Args:
            creative_id: Creative ID
        
        Returns:
            Creative details (asset URL, dimensions, type, etc.)
        """
        try:
            response = await self._make_request("GET", f"/creatives/{creative_id}")
            
            logger.info(f"Retrieved TripleWhale creative details: {creative_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale creative details: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get creative details - {str(e)}")
    
    # ========== CAMPAIGN METHODS ==========
    
    async def get_campaigns(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        channel: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get campaign data across all channels
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            channel: Optional channel filter
        
        Returns:
            Campaign data with performance metrics
        """
        try:
            params = {}
            
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if channel:
                params["channel"] = channel
            
            response = await self._make_request("GET", "/campaigns", params=params)
            
            logger.info("Retrieved TripleWhale campaigns")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale campaigns: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get campaigns - {str(e)}")
    
    async def get_campaign_performance(
        self,
        campaign_id: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get performance data for a specific campaign
        
        Args:
            campaign_id: Campaign ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Campaign performance metrics
        """
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            response = await self._make_request("GET", f"/campaigns/{campaign_id}/performance", params=params)
            
            logger.info(f"Retrieved TripleWhale campaign performance: {campaign_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale campaign performance: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get campaign performance - {str(e)}")
    
    # ========== SHOPIFY INTEGRATION METHODS ==========
    
    async def get_shopify_connection_status(self) -> Dict[str, Any]:
        """
        Get Shopify connection status
        
        Returns:
            Connection status and shop information
        """
        try:
            response = await self._make_request("GET", "/shopify/status")
            
            logger.info("Retrieved TripleWhale Shopify connection status")
            return response
            
        except Exception as e:
            logger.error(f"Failed to get TripleWhale Shopify status: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to get Shopify status - {str(e)}")
    
    async def sync_shopify_data(self) -> Dict[str, Any]:
        """
        Trigger Shopify data sync
        
        Returns:
            Sync status and results
        """
        try:
            response = await self._make_request("POST", "/shopify/sync")
            
            logger.info("Triggered TripleWhale Shopify data sync")
            return response
            
        except Exception as e:
            logger.error(f"Failed to sync TripleWhale Shopify data: {e}", exc_info=True)
            raise RuntimeError(f"TripleWhale API error: Failed to sync Shopify data - {str(e)}")

class TripleWhaleAdapter:
    """TripleWhale adapter with unified interface for Omnify"""
    
    def __init__(self):
        self.client: Optional[TripleWhaleClient] = None
        self.config: Optional[TripleWhaleConfig] = None
        
    async def initialize(self, config: Dict[Any, Any]):
        """Initialize TripleWhale adapter with configuration"""
        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("TripleWhale API key is required")
        
        self.config = TripleWhaleConfig(
            api_key=api_key,
            base_url=config.get('base_url', 'https://api.triplewhale.com/v1'),
            timeout=config.get('timeout', 30)
        )
        
        logger.info("TripleWhale adapter initialized")
        
    async def get_attribution(
        self,
        organization_id: str,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Get attribution data for MEMORY module"""
        if not self.config:
            raise RuntimeError("TripleWhale adapter not initialized")
        
        async with TripleWhaleClient(self.config) as client:
            try:
                response = await client.get_attribution_data(start_date, end_date, channel)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'triplewhale',
                    'organization_id': organization_id,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to get TripleWhale attribution: {e}", exc_info=True)
                raise RuntimeError(f"TripleWhale API error: Failed to get attribution - {str(e)}")
    
    async def get_revenue_metrics(
        self,
        organization_id: str,
        start_date: str,
        end_date: str,
        breakdown: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Get revenue metrics for MEMORY module (ROAS, CLV, LTV)"""
        if not self.config:
            raise RuntimeError("TripleWhale adapter not initialized")
        
        async with TripleWhaleClient(self.config) as client:
            try:
                response = await client.get_revenue_data(start_date, end_date, breakdown)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'triplewhale',
                    'organization_id': organization_id,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to get TripleWhale revenue metrics: {e}", exc_info=True)
                raise RuntimeError(f"TripleWhale API error: Failed to get revenue metrics - {str(e)}")
    
    async def get_creative_performance(
        self,
        organization_id: str,
        start_date: str,
        end_date: str,
        channel: Optional[str] = None
    ) -> Dict[Any, Any]:
        """Get creative performance for ORACLE module (fatigue prediction)"""
        if not self.config:
            raise RuntimeError("TripleWhale adapter not initialized")
        
        async with TripleWhaleClient(self.config) as client:
            try:
                response = await client.get_creative_performance(start_date, end_date, channel)
                
                return {
                    'status': 'success',
                    'data': response,
                    'platform': 'triplewhale',
                    'organization_id': organization_id,
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                }
                
            except Exception as e:
                logger.error(f"Failed to get TripleWhale creative performance: {e}", exc_info=True)
                raise RuntimeError(f"TripleWhale API error: Failed to get creative performance - {str(e)}")
    
    async def test_connection(self, organization_id: str, account_id: str = "default") -> Dict[str, Any]:
        """Test TripleWhale connection"""
        if not self.config:
            return {"status": "not_configured", "error": "TripleWhale adapter not initialized"}
        
        try:
            async with TripleWhaleClient(self.config) as client:
                # Test with a simple API call
                await client.get_shopify_connection_status()
                
                return {
                    "status": "connected",
                    "platform": "triplewhale",
                    "organization_id": organization_id
                }
        except Exception as e:
            logger.error(f"TripleWhale connection test failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "platform": "triplewhale"
            }

# Global instance
triplewhale_adapter = TripleWhaleAdapter()

