"""
YouTube Ads API Integration
Production-ready YouTube advertising platform integration
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
class YouTubeCampaign:
    """YouTube campaign data structure"""
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
class YouTubeAd:
    """YouTube ad data structure"""
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

class YouTubeAdsClient:
    """YouTube Ads API client with production-ready implementation"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.access_token = credentials.get("access_token")
        self.refresh_token = credentials.get("refresh_token")
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
        self.customer_id = credentials.get("customer_id")
        self.api_version = "v14"
        self.base_url = f"https://googleads.googleapis.com/{self.api_version}"
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "developer-token": credentials.get("developer_token", ""),
                "User-Agent": "OmnifyProduct/2.0.0"
            }
        )
    
    async def authenticate(self) -> bool:
        """Authenticate with YouTube Ads API"""
        try:
            # Test authentication by getting customer info
            url = f"/customers/{self.customer_id}"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"YouTube Ads authentication error: {e}")
            return False
    
    async def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with httpx.AsyncClient() as token_client:
                response = await token_client.post(token_url, data=data)
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data["access_token"]
                
                # Update client headers
                self.client.headers["Authorization"] = f"Bearer {self.access_token}"
                
                logger.info("YouTube Ads access token refreshed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error refreshing YouTube Ads access token: {e}")
            return False
    
    async def get_campaigns(self, customer_id: Optional[str] = None) -> List[YouTubeCampaign]:
        """Get YouTube campaigns"""
        try:
            customer = customer_id or self.customer_id
            url = f"/customers/{customer}/campaigns:search"
            
            query = """
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign_budget.amount_micros,
                campaign.start_date,
                campaign.end_date,
                campaign.create_time,
                campaign.update_time
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            """
            
            payload = {
                "query": query,
                "page_size": 1000
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            campaigns = []
            
            for campaign_data in data.get("results", []):
                campaign_info = campaign_data.get("campaign", {})
                budget_info = campaign_data.get("campaignBudget", {})
                
                campaign = YouTubeCampaign(
                    campaign_id=str(campaign_info.get("id")),
                    name=campaign_info.get("name"),
                    status=campaign_info.get("status"),
                    objective=campaign_info.get("advertisingChannelType"),
                    budget=budget_info.get("amountMicros", 0) / 1000000,  # Convert from micros
                    daily_budget=None,  # YouTube doesn't have daily budget in this query
                    start_date=datetime.strptime(campaign_info.get("startDate", "20000101"), "%Y%m%d"),
                    end_date=datetime.strptime(campaign_info.get("endDate", "20301231"), "%Y%m%d") if campaign_info.get("endDate") else None,
                    target_audience={},
                    created_at=datetime.fromisoformat(campaign_info.get("createTime", "").replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(campaign_info.get("updateTime", "").replace("Z", "+00:00"))
                )
                campaigns.append(campaign)
            
            logger.info(f"Retrieved {len(campaigns)} YouTube campaigns", extra={
                "customer_id": customer,
                "campaign_count": len(campaigns)
            })
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Error getting YouTube campaigns: {e}")
            return []
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create YouTube campaign"""
        try:
            customer_id = campaign_data.get("customer_id", self.customer_id)
            url = f"/customers/{customer_id}/campaigns:mutate"
            
            # Prepare campaign operations
            operations = [
                {
                    "create": {
                        "name": campaign_data["name"],
                        "advertisingChannelType": campaign_data.get("objective", "VIDEO"),
                        "status": campaign_data.get("status", "PAUSED"),
                        "campaignBudget": f"customers/{customer_id}/campaignBudgets/{campaign_data.get('budget_id', 'new')}",
                        "startDate": campaign_data.get("start_date", datetime.utcnow().strftime("%Y%m%d")),
                        "endDate": campaign_data.get("end_date", (datetime.utcnow() + timedelta(days=30)).strftime("%Y%m%d"))
                    }
                }
            ]
            
            payload = {
                "operations": operations
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            campaign_id = result.get("results", [{}])[0].get("resourceName", "").split("/")[-1]
            
            logger.info(f"Created YouTube campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "name": campaign_data["name"],
                "objective": campaign_data.get("objective")
            })
            
            return campaign_id if campaign_id else None
            
        except Exception as e:
            logger.error(f"Error creating YouTube campaign: {e}")
            return None
    
    async def get_ads(self, campaign_id: str) -> List[YouTubeAd]:
        """Get YouTube ads for campaign"""
        try:
            url = f"/customers/{self.customer_id}/adGroupAds:search"
            
            query = f"""
            SELECT 
                ad_group_ad.ad.id,
                ad_group_ad.ad.name,
                ad_group_ad.status,
                ad_group_ad.ad.type,
                ad_group_ad.create_time,
                ad_group_ad.update_time
            FROM ad_group_ad
            WHERE campaign.id = {campaign_id}
            AND ad_group_ad.status != 'REMOVED'
            """
            
            payload = {
                "query": query,
                "page_size": 1000
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            ads = []
            
            for ad_data in data.get("results", []):
                ad_info = ad_data.get("adGroupAd", {})
                ad_details = ad_info.get("ad", {})
                
                ad = YouTubeAd(
                    ad_id=str(ad_details.get("id")),
                    campaign_id=campaign_id,
                    name=ad_details.get("name"),
                    status=ad_info.get("status"),
                    format=ad_details.get("type"),
                    creative={},
                    targeting={},
                    bid_strategy="",
                    created_at=datetime.fromisoformat(ad_info.get("createTime", "").replace("Z", "+00:00")),
                    updated_at=datetime.fromisoformat(ad_info.get("updateTime", "").replace("Z", "+00:00"))
                )
                ads.append(ad)
            
            logger.info(f"Retrieved {len(ads)} YouTube ads for campaign {campaign_id}", extra={
                "campaign_id": campaign_id,
                "ad_count": len(ads)
            })
            
            return ads
            
        except Exception as e:
            logger.error(f"Error getting YouTube ads: {e}")
            return []
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create YouTube ad"""
        try:
            customer_id = ad_data.get("customer_id", self.customer_id)
            url = f"/customers/{customer_id}/adGroupAds:mutate"
            
            # Prepare ad operations
            operations = [
                {
                    "create": {
                        "adGroup": f"customers/{customer_id}/adGroups/{ad_data.get('ad_group_id')}",
                        "ad": {
                            "name": ad_data["name"],
                            "type": ad_data.get("format", "VIDEO_RESPONSIVE_AD"),
                            "finalUrls": [ad_data.get("landing_page_url", "")]
                        },
                        "status": ad_data.get("status", "PAUSED")
                    }
                }
            ]
            
            payload = {
                "operations": operations
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            ad_id = result.get("results", [{}])[0].get("resourceName", "").split("/")[-1]
            
            logger.info(f"Created YouTube ad {ad_id}", extra={
                "ad_id": ad_id,
                "campaign_id": ad_data.get("campaign_id"),
                "name": ad_data["name"]
            })
            
            return ad_id if ad_id else None
            
        except Exception as e:
            logger.error(f"Error creating YouTube ad: {e}")
            return None
    
    async def get_campaign_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get YouTube campaign insights"""
        try:
            url = f"/customers/{self.customer_id}/googleAds:searchStream"
            
            query = f"""
            SELECT 
                campaign.id,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.video_views,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE campaign.id = {campaign_id}
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            payload = {
                "query": query
            }
            
            response = await self.client.post(url, json=payload)
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
                "video_views": 0,
                "ctr": 0,
                "cpc": 0
            }
            
            # Extract metrics from response
            if data.get("results"):
                metrics = data["results"][0].get("metrics", {})
                insights.update({
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "spend": metrics.get("costMicros", 0) / 1000000,  # Convert from micros
                    "conversions": metrics.get("conversions", 0),
                    "video_views": metrics.get("videoViews", 0),
                    "ctr": metrics.get("ctr", 0),
                    "cpc": metrics.get("averageCpc", 0) / 1000000  # Convert from micros
                })
            
            logger.info(f"Retrieved YouTube campaign insights for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "impressions": insights["impressions"],
                "clicks": insights["clicks"],
                "spend": insights["spend"]
            })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting YouTube campaign insights: {e}")
            return {}
    
    async def update_campaign_budget(self, campaign_id: str, budget: float) -> bool:
        """Update YouTube campaign budget"""
        try:
            customer_id = self.customer_id
            url = f"/customers/{customer_id}/campaignBudgets:mutate"
            
            # First get the campaign budget ID
            budget_query_url = f"/customers/{customer_id}/campaignBudgets:search"
            budget_query = f"""
            SELECT campaign_budget.id
            FROM campaign_budget
            WHERE campaign.id = {campaign_id}
            """
            
            budget_response = await self.client.post(budget_query_url, json={"query": budget_query})
            budget_response.raise_for_status()
            
            budget_data = budget_response.json()
            if not budget_data.get("results"):
                logger.error(f"No budget found for campaign {campaign_id}")
                return False
            
            budget_id = budget_data["results"][0]["campaignBudget"]["id"]
            
            # Update the budget
            operations = [
                {
                    "update": {
                        "resourceName": f"customers/{customer_id}/campaignBudgets/{budget_id}",
                        "amountMicros": int(budget * 1000000)  # Convert to micros
                    }
                }
            ]
            
            payload = {
                "operations": operations
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Updated YouTube campaign budget for {campaign_id}", extra={
                "campaign_id": campaign_id,
                "new_budget": budget
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating YouTube campaign budget: {e}")
            return False
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause YouTube campaign"""
        try:
            customer_id = self.customer_id
            url = f"/customers/{customer_id}/campaigns:mutate"
            
            operations = [
                {
                    "update": {
                        "resourceName": f"customers/{customer_id}/campaigns/{campaign_id}",
                        "status": "PAUSED"
                    }
                }
            ]
            
            payload = {
                "operations": operations
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Paused YouTube campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error pausing YouTube campaign: {e}")
            return False
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume YouTube campaign"""
        try:
            customer_id = self.customer_id
            url = f"/customers/{customer_id}/campaigns:mutate"
            
            operations = [
                {
                    "update": {
                        "resourceName": f"customers/{customer_id}/campaigns/{campaign_id}",
                        "status": "ENABLED"
                    }
                }
            ]
            
            payload = {
                "operations": operations
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Resumed YouTube campaign {campaign_id}", extra={
                "campaign_id": campaign_id
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error resuming YouTube campaign: {e}")
            return False
    
    async def get_customer_info(self) -> Dict[str, Any]:
        """Get YouTube Ads customer information"""
        try:
            url = f"/customers/{self.customer_id}"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            customer_info = {
                "customer_id": data.get("id"),
                "name": data.get("descriptiveName"),
                "status": data.get("status"),
                "currency": data.get("currencyCode"),
                "timezone": data.get("timeZone"),
                "created_at": data.get("createTime"),
                "updated_at": data.get("updateTime")
            }
            
            logger.info(f"Retrieved YouTube customer info for {self.customer_id}", extra={
                "customer_id": self.customer_id,
                "name": customer_info["name"]
            })
            
            return customer_info
            
        except Exception as e:
            logger.error(f"Error getting YouTube customer info: {e}")
            return {}
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class YouTubeAdsAdapter:
    """YouTube Ads adapter for platform integrations manager"""
    
    def __init__(self):
        self.client = None
        self.credentials = None
    
    async def initialize(self, credentials: Dict[str, Any]):
        """Initialize YouTube Ads client"""
        self.credentials = credentials
        self.client = YouTubeAdsClient(credentials)
        
        # Test authentication
        is_authenticated = await self.client.authenticate()
        if not is_authenticated:
            raise ValueError("YouTube Ads authentication failed")
        
        logger.info("YouTube Ads adapter initialized successfully")
    
    async def get_campaigns(self, customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get campaigns"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        campaigns = await self.client.get_campaigns(customer_id)
        return [campaign.__dict__ for campaign in campaigns]
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Create campaign"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.create_campaign(campaign_data)
    
    async def get_ads(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get ads for campaign"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        ads = await self.client.get_ads(campaign_id)
        return [ad.__dict__ for ad in ads]
    
    async def create_ad(self, ad_data: Dict[str, Any]) -> Optional[str]:
        """Create ad"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.create_ad(ad_data)
    
    async def get_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get campaign insights"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.get_campaign_insights(campaign_id, start_date, end_date)
    
    async def update_budget(self, campaign_id: str, budget: float) -> bool:
        """Update campaign budget"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.update_campaign_budget(campaign_id, budget)
    
    async def pause_campaign(self, campaign_id: str) -> bool:
        """Pause campaign"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.pause_campaign(campaign_id)
    
    async def resume_campaign(self, campaign_id: str) -> bool:
        """Resume campaign"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.resume_campaign(campaign_id)
    
    async def get_customer_info(self) -> Dict[str, Any]:
        """Get customer information"""
        if not self.client:
            raise ValueError("YouTube Ads client not initialized")
        
        return await self.client.get_customer_info()
    
    async def close(self):
        """Close client"""
        if self.client:
            await self.client.close()
