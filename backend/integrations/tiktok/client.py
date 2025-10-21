"""
TikTok Ads API Integration
Production-ready TikTok advertising platform integration
"""

import os
import asyncio
import json
import base64
import hashlib
import hmac
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
import httpx
from dataclasses import dataclass

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

@dataclass
class TikTokCampaign:
    """TikTok campaign data structure"""
    campaign_id: str
    name: str
    status: str
    objective: str
    budget: float
    daily_budget: Optional[float]
    start_date: datetime
    end_date: Optional[datetime]
    target_audience: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class TikTokAd:
    """TikTok ad data structure"""
    ad_id: str
    campaign_id: str
    name: str
    status: str
    format: str
    creative: Dict[str, Any]
    targeting: Dict[str, Any]
    bid_strategy: str
    created_at: datetime
    updated_at: datetime

class TikTokAdsClient:
    """TikTok Ads API client with production-ready implementation"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.access_token = credentials.get("access_token")
        self.advertiser_id = credentials.get("advertiser_id")
        self.api_version = "v1.3"
        self.base_url = f"https://business-api.tiktok.com/open_api/{self.api_version}"
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Access-Token": self.access_token,
                "Content-Type": "application/json",
                "User-Agent": "OmnifyProduct/2.0.0"
            }
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok Ads API"""
        try:
            response = await self.client.get(f"/advertiser/info/?advertiser_id={self.advertiser_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"TikTok Ads authentication error: {e}")
            return False
    
    async def get_campaigns(self, advertiser_id: Optional[str] = None) -> List[TikTokCampaign]:
        """Get TikTok campaigns"""
        try:
            advertiser = advertiser_id or self.advertiser_id
            url = f"/campaign/get/"
            
            params = {
                "advertiser_id": advertiser,
                "fields": ["campaign_id", "campaign_name", "status", "objective", "budget", "daily_budget", "start_time", "end_time", "create_time", "modify_time"]
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            campaigns = []
            
            for campaign_data in data.get("data", {}).get("list", []):
                campaign = TikTokCampaign(
                    campaign_id=str(campaign_data.get("campaign_id")),
                    name=campaign_data.get("campaign_name"),
                    status=campaign_data.get("status"),
                    objective=campaign_data.get("objective"),
                    budget=campaign_data.get("budget", 0),
                    daily_budget=campaign_data.get("daily_budget"),
                    start_date=datetime.fromtimestamp(campaign_data.get("start_time", 0)),
                    end_date=datetime.fromtimestamp(campaign_data.get("end_time", 0)) if campaign_data.get("end_time") else None,
                    target_audience={},
                    created_at=datetime.fromtimestamp(campaign_data.get("create_time", 0)),
                    updated_at=datetime.fromtimestamp(campaign_data.get("modify_time", 0))
                )
                campaigns.append(campaign)
            
            logger.info(f"Retrieved {len(campaigns)} TikTok campaigns", extra={
                "advertiser_id": advertiser,
                "campaign_count": len(campaigns)
            })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting TikTok campaigns: {e}")
            return []
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create TikTok campaign"""
        try:
            advertiser_id = campaign_data.get("advertiser_id", self.advertiser_id)
            url = f"/campaign/create/"
            
            # Prepare campaign payload
            payload = {
                "advertiser_id": advertiser_id,
                "campaign_name": campaign_data["name"],
                "objective": campaign_data["objective"],
                "budget": campaign_data["budget"],
                "daily_budget": campaign_data.get("daily_budget"),
                "start_time": int(campaign_data.get("start_date", datetime.utcnow()).timestamp()),
                "end_time": int(campaign_data.get("end_date", datetime.utcnow() + timedelta(days=30)).timestamp()) if campaign_data.get("end_date") else None
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            campaign_id = result.get("data", {}).get("campaign_id")
            
            logger.info(f"Created TikTok campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "name": campaign_data["name"],
                "objective": campaign_data["objective"]
            })
            
            return str(campaign_id) if campaign_id else None
            
        except Exception as e:
            logger.error(f"Error creating TikTok campaign: {e}")
            return None
    
    async def get_ads(self, campaign_id: str) -> List[TikTokAd]:
        """Get TikTok ads for campaign"""
        try:
            url = f"/ad/get/"
            
            params = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "fields": ["ad_id", "ad_name", "status", "ad_format", "create_time", "modify_time"]
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            ads = []
            
            for ad_data in data.get("data", {}).get("list", []):
                ad = TikTokAd(
                    ad_id=str(ad_data.get("ad_id")),
                    campaign_id=campaign_id,
                    name=ad_data.get("ad_name"),
                    status=ad_data.get("status"),
                    format=ad_data.get("ad_format"),
                    creative={},
                    targeting={},
                    bid_strategy="",
                    created_at=datetime.fromtimestamp(ad_data.get("create_time", 0)),
                    updated_at=datetime.fromtimestamp(ad_data.get("modify_time", 0))
                )
                ads.append(ad)
            
            logger.info(f"Retrieved {len(ads)} TikTok ads for campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "ad_count": len(ads)
            })
            
            return ads
            
        except Exception as e:
            logger.error(f"Error getting TikTok ads: {e}")
            return []
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create TikTok ad"""
        try:
            url = f"/ad/create/"
            
            # Prepare ad payload
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": ad_data["campaign_id"],
                "ad_name": ad_data["name"],
                "ad_format": ad_data["format"],
                "placement_type": ad_data.get("placement_type", "AUTOMATIC"),
                "promotion_type": ad_data.get("promotion_type", "WEBSITE"),
                "landing_page_url": ad_data.get("landing_page_url", ""),
                "call_to_action": ad_data.get("call_to_action", "LEARN_MORE")
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            ad_id = result.get("data", {}).get("ad_id")
            
            logger.info(f"Created TikTok ad {ad_id}", extra={
                "ad_id": ad_id,
                "campaign_id": ad_data["campaign_id"],
                "name": ad_data["name"]
            })
            
            return str(ad_id) if ad_id else None
            
        except Exception as e:
            logger.error(f"Error creating TikTok ad: {e}")
            return None
    
    async def get_campaign_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get TikTok campaign insights"""
        try:
            url = f"/report/integrated/get/"
            
            params = {
                "advertiser_id": self.advertiser_id,
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "CAMPAIGN",
                "dimensions": ["campaign_id"],
                "metrics": ["impressions", "clicks", "spend", "conversions"],
                "start_date": start_date,
                "end_date": end_date,
                "filters": [{"field": "campaign_id", "operator": "=", "value": campaign_id}]
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            insights = {
                "campaign_id": campaign_id,
                "start_date": start_date,
                "end_date": end_date,
                "impressions": 0,
                "clicks": 0,
                "spend": 0,
                "conversions": 0,
                "ctr": 0,
                "cpc": 0,
                "cpm": 0
            }
            
            # Extract metrics from response
            if data.get("data", {}).get("list"):
                metrics = data["data"]["list"][0]
                insights.update({
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "spend": metrics.get("spend", 0),
                    "conversions": metrics.get("conversions", 0),
                    "ctr": metrics.get("ctr", 0),
                    "cpc": metrics.get("cpc", 0),
                    "cpm": metrics.get("cpm", 0)
                })
            
            logger.info(f"Retrieved TikTok campaign insights for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "impressions": insights["impressions"],
                "clicks": insights["clicks"],
                "spend": insights["spend"]
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting TikTok campaign insights: {e}")
            return {}
    
    async def update_campaign_budget(self, campaign_id: str, budget: float) -> bool:
        """Update TikTok campaign budget"""
        try:
            url = f"/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "budget": budget
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Updated TikTok campaign budget for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "new_budget": budget
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating TikTok campaign budget: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause TikTok campaign"""
        try:
            url = f"/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "status": "PAUSED"
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Paused TikTok campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error pausing TikTok campaign: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume TikTok campaign"""
        try:
            url = f"/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "status": "ENABLE"
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Resumed TikTok campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error resuming TikTok campaign: {e}")
            return False
    
    async def get_advertiser_info(self) -> Dict[str, Any]:
        """Get TikTok advertiser information"""
        try:
            url = f"/advertiser/info/"
            
            params = {
                "advertiser_id": self.advertiser_id
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            advertiser_info = {
                "advertiser_id": data.get("data", {}).get("advertiser_id"),
                "name": data.get("data", {}).get("name"),
                "status": data.get("data", {}).get("status"),
                "currency": data.get("data", {}).get("currency"),
                "timezone": data.get("data", {}).get("timezone"),
                "created_at": data.get("data", {}).get("create_time"),
                "updated_at": data.get("data", {}).get("modify_time")
            }
            
            logger.info(f"Retrieved TikTok advertiser info for {self.advertiser_id}", extra={
                "advertiser_id": self.advertiser_id,
                "name": advertiser_info["name"]
            })
            
            return advertiser_info
            
        except Exception as e:
            logger.error(f"Error getting TikTok advertiser info: {e}")
            return {}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class TikTokAdsAdapter:
    """TikTok Ads adapter for platform integrations manager"""
    
    def __init__(self):
        self.client = None
        self.credentials = None
    
    async def initialize(self, credentials: Dict[str, Any]):
        """Initialize TikTok Ads client"""
        self.credentials = credentials
        self.client = TikTokAdsClient(credentials)
        
        # Test authentication
        is_authenticated = await self.client.authenticate()
        if not is_authenticated:
            raise ValueError("TikTok Ads authentication failed")
        
        logger.info("TikTok Ads adapter initialized successfully")
    
    async def get_campaigns(self, advertiser_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaigns"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        campaigns = await self.client.get_campaigns(advertiser_id)
        return [campaign.__dict__ for campaign in campaigns]
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create campaign"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.create_campaign(campaign_data)
    
    async def get_ads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get ads for campaign"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        ads = await self.client.get_ads(campaign_id)
        return [ad.__dict__ for ad in ads]
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create ad"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.create_ad(ad_data)
    
    async def get_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get campaign insights"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.get_campaign_insights(campaign_id, start_date, end_date)
    
    async def update_budget(self, campaign_id: str, budget: float) -> bool:
        """Update campaign budget"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.update_campaign_budget(campaign_id, budget)
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause campaign"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.pause_campaign(campaign_id)
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume campaign"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.resume_campaign(campaign_id)
    
    async def get_advertiser_info(self) -> Dict[str, Any]:
        """Get advertiser information"""
        if not self.client:
            raise ValueError("TikTok Ads client not initialized")
        
        return await self.client.get_advertiser_info()
    
    async def close(self):
        """Close client"""
        if self.client:
            await self.client.close()
