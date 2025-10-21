"""
LinkedIn Ads API Integration
Production-ready LinkedIn advertising platform integration
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
class LinkedInCampaign:
    """LinkedIn campaign data structure"""
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
class LinkedInAd:
    """LinkedIn ad data structure"""
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

class LinkedInAdsClient:
    """LinkedIn Ads API client with production-ready implementation"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.access_token = credentials.get("access_token")
        self.account_id = credentials.get("account_id")
        self.api_version = "v2"
        self.base_url = f"https://api.linkedin.com/{self.api_version}"
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0",
                "User-Agent": "OmnifyProduct/2.0.0"
            }
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn Ads API"""
        try:
            response = await self.client.get("/adAccounts")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LinkedIn Ads authentication error: {e}")
            return False
    
    async def get_campaigns(self, account_id: Optional[str] = None) -> List[LinkedInCampaign]:
        """Get LinkedIn campaigns"""
        try:
            account = account_id or self.account_id
            url = f"/adAccounts/{account}/campaigns"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            campaigns = []
            
            for campaign_data in data.get("elements", []):
                campaign = LinkedInCampaign(
                    campaign_id=campaign_data.get("id"),
                    name=campaign_data.get("name"),
                    status=campaign_data.get("status"),
                    objective=campaign_data.get("objective"),
                    budget=campaign_data.get("budget", {}).get("amount"),
                    daily_budget=campaign_data.get("dailyBudget", {}).get("amount"),
                    start_date=datetime.fromisoformat(campaign_data.get("startDate", "").replace("Z", "+00:00")),
                    end_date=datetime.fromisoformat(campaign_data.get("endDate", "").replace("Z", "+00:00")) if campaign_data.get("endDate") else None,
                    target_audience=campaign_data.get("targetingCriteria", {}),
                    created_at=datetime.fromisoformat(campaign_data.get("created", "").replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(campaign_data.get("lastModified", "").replace("Z", "+00:00"))
                )
                campaigns.append(campaign)
            
            logger.info(f"Retrieved {len(campaigns)} LinkedIn campaigns", extra={
                "account_id": account,
                "campaign_count": len(campaigns)
            })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn campaigns: {e}")
            return []
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create LinkedIn campaign"""
        try:
            account = campaign_data.get("account_id", self.account_id)
            url = f"/adAccounts/{account}/campaigns"
            
            # Prepare campaign payload
            payload = {
                "name": campaign_data["name"],
                "status": campaign_data.get("status", "ACTIVE"),
                "objective": campaign_data["objective"],
                "budget": {
                    "amount": campaign_data["budget"],
                    "currency": campaign_data.get("currency", "USD")
                },
                "targetingCriteria": campaign_data.get("targeting", {}),
                "startDate": campaign_data.get("start_date", datetime.utcnow().isoformat()),
                "endDate": campaign_data.get("end_date")
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            campaign_id = result.get("id")
            
            logger.info(f"Created LinkedIn campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "name": campaign_data["name"],
                "objective": campaign_data["objective"]
            })
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn campaign: {e}")
            return None
    
    async def get_ads(self, campaign_id: str) -> List[LinkedInAd]:
        """Get LinkedIn ads for campaign"""
        try:
            url = f"/campaigns/{campaign_id}/ads"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            ads = []
            
            for ad_data in data.get("elements", []):
                ad = LinkedInAd(
                    ad_id=ad_data.get("id"),
                    campaign_id=campaign_id,
                    name=ad_data.get("name"),
                    status=ad_data.get("status"),
                    format=ad_data.get("format"),
                    creative=ad_data.get("creative", {}),
                    targeting=ad_data.get("targetingCriteria", {}),
                    bid_strategy=ad_data.get("bidStrategy", {}),
                    created_at=datetime.fromisoformat(ad_data.get("created", "").replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(ad_data.get("lastModified", "").replace("Z", "+00:00"))
                )
                ads.append(ad)
            
            logger.info(f"Retrieved {len(ads)} LinkedIn ads for campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "ad_count": len(ads)
            })
            
            return ads
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn ads: {e}")
            return []
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create LinkedIn ad"""
        try:
            campaign_id = ad_data["campaign_id"]
            url = f"/campaigns/{campaign_id}/ads"
            
            # Prepare ad payload
            payload = {
                "name": ad_data["name"],
                "status": ad_data.get("status", "ACTIVE"),
                "format": ad_data["format"],
                "creative": ad_data["creative"],
                "targetingCriteria": ad_data.get("targeting", {}),
                "bidStrategy": ad_data.get("bid_strategy", {})
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            ad_id = result.get("id")
            
            logger.info(f"Created LinkedIn ad {ad_id}", extra={
                "ad_id": ad_id,
                "campaign_id": campaign_id,
                "name": ad_data["name"]
            })
            
            return ad_id
            
        except Exception as e:
            logger.error(f"Error creating LinkedIn ad: {e}")
            return None
    
    async def get_campaign_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get LinkedIn campaign insights"""
        try:
            url = f"/campaigns/{campaign_id}/insights"
            params = {
                "startDate": start_date,
                "endDate": end_date,
                "fields": "impressions,clicks,spend,conversions"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            insights = {
                "campaign_id": campaign_id,
                "start_date": start_date,
                "end_date": end_date,
                "impressions": data.get("impressions", 0),
                "clicks": data.get("clicks", 0),
                "spend": data.get("spend", 0),
                "conversions": data.get("conversions", 0),
                "ctr": data.get("ctr", 0),
                "cpc": data.get("cpc", 0),
                "cpm": data.get("cpm", 0)
            }
            
            logger.info(f"Retrieved LinkedIn campaign insights for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "impressions": insights["impressions"],
                "clicks": insights["clicks"],
                "spend": insights["spend"]
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn campaign insights: {e}")
            return {}
    
    async def update_campaign_budget(self, campaign_id: str, budget: float) -> bool:
        """Update LinkedIn campaign budget"""
        try:
            url = f"/campaigns/{campaign_id}"
            
            payload = {
                "budget": {
                    "amount": budget,
                    "currency": "USD"
                }
            }
            
            response = await self.client.patch(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Updated LinkedIn campaign budget for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "new_budget": budget
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating LinkedIn campaign budget: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause LinkedIn campaign"""
        try:
            url = f"/campaigns/{campaign_id}"
            
            payload = {
                "status": "PAUSED"
            }
            
            response = await self.client.patch(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Paused LinkedIn campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error pausing LinkedIn campaign: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume LinkedIn campaign"""
        try:
            url = f"/campaigns/{campaign_id}"
            
            payload = {
                "status": "ACTIVE"
            }
            
            response = await self.client.patch(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Resumed LinkedIn campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error resuming LinkedIn campaign: {e}")
            return False
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get LinkedIn Ads account information"""
        try:
            url = f"/adAccounts/{self.account_id}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            account_info = {
                "account_id": data.get("id"),
                "name": data.get("name"),
                "status": data.get("status"),
                "currency": data.get("currency"),
                "timezone": data.get("timezone"),
                "created_at": data.get("created"),
                "updated_at": data.get("lastModified")
            }
            
            logger.info(f"Retrieved LinkedIn account info for {self.account_id}", extra={
                "account_id": self.account_id,
                "name": account_info["name"]
            })
            
            return account_info
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn account info: {e}")
            return {}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class LinkedInAdsAdapter:
    """LinkedIn Ads adapter for platform integrations manager"""
    
    def __init__(self):
        self.client = None
        self.credentials = None
    
    async def initialize(self, credentials: Dict[str, Any]):
        """Initialize LinkedIn Ads client"""
        self.credentials = credentials
        self.client = LinkedInAdsClient(credentials)
        
        # Test authentication
        is_authenticated = await self.client.authenticate()
        if not is_authenticated:
            raise ValueError("LinkedIn Ads authentication failed")
        
        logger.info("LinkedIn Ads adapter initialized successfully")
    
    async def get_campaigns(self, account_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaigns"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        campaigns = await self.client.get_campaigns(account_id)
        return [campaign.__dict__ for campaign in campaigns]
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create campaign"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.create_campaign(campaign_data)
    
    async def get_ads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get ads for campaign"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        ads = await self.client.get_ads(campaign_id)
        return [ad.__dict__ for ad in ads]
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create ad"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.create_ad(ad_data)
    
    async def get_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get campaign insights"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.get_campaign_insights(campaign_id, start_date, end_date)
    
    async def update_budget(self, campaign_id: str, budget: float) -> bool:
        """Update campaign budget"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.update_campaign_budget(campaign_id, budget)
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause campaign"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.pause_campaign(campaign_id)
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume campaign"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.resume_campaign(campaign_id)
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.client:
            raise ValueError("LinkedIn Ads client not initialized")
        
        return await self.client.get_account_info()
    
    async def close(self):
        """Close client"""
        if self.client:
            await self.client.close()