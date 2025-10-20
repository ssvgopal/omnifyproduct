"""
Additional Platform Integrations System
Production-grade integrations with Facebook Ads, Twitter Ads, Pinterest, Snapchat, Reddit, and Quora
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import hashlib
import hmac
import base64

logger = logging.getLogger(__name__)

class PlatformType(str, Enum):
    """Additional platform types"""
    FACEBOOK_ADS = "facebook_ads"
    TWITTER_ADS = "twitter_ads"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    REDDIT = "reddit"
    QUORA = "quora"

class CampaignObjective(str, Enum):
    """Campaign objectives for different platforms"""
    AWARENESS = "awareness"
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    LEADS = "leads"
    SALES = "sales"
    APP_INSTALLS = "app_installs"
    VIDEO_VIEWS = "video_views"
    REACH = "reach"
    BRAND_AWARENESS = "brand_awareness"

@dataclass
class PlatformCredentials:
    """Platform credentials structure"""
    platform: PlatformType
    access_token: str
    refresh_token: Optional[str]
    client_id: str
    client_secret: str
    account_id: str
    expires_at: Optional[datetime]
    additional_config: Dict[str, Any]

@dataclass
class CampaignData:
    """Campaign data structure"""
    campaign_id: str
    platform: PlatformType
    name: str
    objective: CampaignObjective
    budget: float
    daily_budget: Optional[float]
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    targeting: Dict[str, Any]
    creative: Dict[str, Any]
    metrics: Dict[str, Any]

class FacebookAdsClient:
    """Facebook Ads API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://graph.facebook.com/v18.0"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Facebook Ads campaign"""
        try:
            url = f"{self.base_url}/act_{self.credentials.account_id}/campaigns"
            
            payload = {
                "name": campaign_data["name"],
                "objective": campaign_data["objective"],
                "status": campaign_data.get("status", "PAUSED"),
                "special_ad_categories": campaign_data.get("special_ad_categories", []),
                "access_token": self.credentials.access_token
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Facebook Ads campaign: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Facebook Ads API error: {error_text}")
                    raise Exception(f"Facebook Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Facebook Ads campaign: {e}")
            raise
    
    async def create_ad_set(self, campaign_id: str, ad_set_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Facebook Ads ad set"""
        try:
            url = f"{self.base_url}/act_{self.credentials.account_id}/adsets"
            
            payload = {
                "name": ad_set_data["name"],
                "campaign_id": campaign_id,
                "daily_budget": ad_set_data.get("daily_budget", 1000),
                "billing_event": "IMPRESSIONS",
                "optimization_goal": ad_set_data.get("optimization_goal", "REACH"),
                "targeting": json.dumps(ad_set_data.get("targeting", {})),
                "access_token": self.credentials.access_token
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Facebook Ads ad set: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Facebook Ads API error: {error_text}")
                    raise Exception(f"Facebook Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Facebook Ads ad set: {e}")
            raise
    
    async def create_ad(self, ad_set_id: str, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Facebook Ads ad"""
        try:
            url = f"{self.base_url}/act_{self.credentials.account_id}/ads"
            
            payload = {
                "name": ad_data["name"],
                "adset_id": ad_set_id,
                "creative": json.dumps(ad_data.get("creative", {})),
                "status": ad_data.get("status", "PAUSED"),
                "access_token": self.credentials.access_token
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Facebook Ads ad: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Facebook Ads API error: {error_text}")
                    raise Exception(f"Facebook Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Facebook Ads ad: {e}")
            raise
    
    async def get_campaign_insights(self, campaign_id: str, date_range: str = "last_30_days") -> Dict[str, Any]:
        """Get Facebook Ads campaign insights"""
        try:
            url = f"{self.base_url}/{campaign_id}/insights"
            
            params = {
                "date_preset": date_range,
                "fields": "impressions,clicks,spend,reach,frequency,cpm,cpc,cpp,cost_per_conversion,conversions",
                "access_token": self.credentials.access_token
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Facebook Ads insights for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Facebook Ads API error: {error_text}")
                    raise Exception(f"Facebook Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Facebook Ads insights: {e}")
            raise

class TwitterAdsClient:
    """Twitter Ads API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://ads-api.twitter.com/12"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Twitter Ads campaign"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/campaigns"
            
            payload = {
                "name": campaign_data["name"],
                "funding_instrument_id": campaign_data["funding_instrument_id"],
                "currency": campaign_data.get("currency", "USD"),
                "daily_budget_amount_local_micro": int(campaign_data.get("daily_budget", 1000) * 1000000),
                "total_budget_amount_local_micro": int(campaign_data.get("total_budget", 10000) * 1000000),
                "entity_status": campaign_data.get("status", "PAUSED"),
                "objective": campaign_data.get("objective", "WEBSITE_CLICKS")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Twitter Ads campaign: {result['data']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter Ads API error: {error_text}")
                    raise Exception(f"Twitter Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Twitter Ads campaign: {e}")
            raise
    
    async def create_ad_group(self, campaign_id: str, ad_group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Twitter Ads ad group"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/ad_groups"
            
            payload = {
                "name": ad_group_data["name"],
                "campaign_id": campaign_id,
                "currency": ad_group_data.get("currency", "USD"),
                "bid_amount_local_micro": int(ad_group_data.get("bid_amount", 1.0) * 1000000),
                "entity_status": ad_group_data.get("status", "PAUSED"),
                "targeting_criteria": ad_group_data.get("targeting", {})
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Twitter Ads ad group: {result['data']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter Ads API error: {error_text}")
                    raise Exception(f"Twitter Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Twitter Ads ad group: {e}")
            raise
    
    async def create_promoted_tweet(self, ad_group_id: str, tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Twitter Ads promoted tweet"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/promoted_tweets"
            
            payload = {
                "line_item_id": ad_group_id,
                "tweet_id": tweet_data["tweet_id"],
                "entity_status": tweet_data.get("status", "PAUSED")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Twitter Ads promoted tweet: {result['data']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter Ads API error: {error_text}")
                    raise Exception(f"Twitter Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Twitter Ads promoted tweet: {e}")
            raise
    
    async def get_campaign_stats(self, campaign_id: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """Get Twitter Ads campaign statistics"""
        try:
            url = f"{self.base_url}/stats/accounts/{self.credentials.account_id}"
            
            params = {
                "entity": "CAMPAIGN",
                "entity_ids": campaign_id,
                "start_time": start_time,
                "end_time": end_time,
                "granularity": "DAY",
                "metric_groups": "ENGAGEMENT,BILLING,VIDEO"
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Twitter Ads stats for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter Ads API error: {error_text}")
                    raise Exception(f"Twitter Ads API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Twitter Ads stats: {e}")
            raise

class PinterestClient:
    """Pinterest API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://api.pinterest.com/v5"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Pinterest campaign"""
        try:
            url = f"{self.base_url}/ad_accounts/{self.credentials.account_id}/campaigns"
            
            payload = {
                "name": campaign_data["name"],
                "status": campaign_data.get("status", "PAUSED"),
                "budget_in_micro_currency": int(campaign_data.get("budget", 1000) * 1000000),
                "budget_type": campaign_data.get("budget_type", "DAILY"),
                "objective_type": campaign_data.get("objective", "AWARENESS")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Pinterest campaign: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {error_text}")
                    raise Exception(f"Pinterest API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Pinterest campaign: {e}")
            raise
    
    async def create_ad_group(self, campaign_id: str, ad_group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Pinterest ad group"""
        try:
            url = f"{self.base_url}/ad_accounts/{self.credentials.account_id}/ad_groups"
            
            payload = {
                "name": ad_group_data["name"],
                "campaign_id": campaign_id,
                "status": ad_group_data.get("status", "PAUSED"),
                "budget_in_micro_currency": int(ad_group_data.get("budget", 100) * 1000000),
                "bid_in_micro_currency": int(ad_group_data.get("bid", 1.0) * 1000000)
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Pinterest ad group: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {error_text}")
                    raise Exception(f"Pinterest API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Pinterest ad group: {e}")
            raise
    
    async def create_pin_promotion(self, ad_group_id: str, pin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Pinterest pin promotion"""
        try:
            url = f"{self.base_url}/ad_accounts/{self.credentials.account_id}/ads"
            
            payload = {
                "ad_group_id": ad_group_id,
                "pin_id": pin_data["pin_id"],
                "status": pin_data.get("status", "PAUSED")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Pinterest pin promotion: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {error_text}")
                    raise Exception(f"Pinterest API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Pinterest pin promotion: {e}")
            raise
    
    async def get_campaign_analytics(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Pinterest campaign analytics"""
        try:
            url = f"{self.base_url}/ad_accounts/{self.credentials.account_id}/campaigns/{campaign_id}/analytics"
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "granularity": "DAY",
                "metrics": "IMPRESSION,CLICKTHROUGH,SPEND_IN_DOLLAR,CTR,CPC_IN_MICRO_DOLLAR"
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Pinterest analytics for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {error_text}")
                    raise Exception(f"Pinterest API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Pinterest analytics: {e}")
            raise

class SnapchatClient:
    """Snapchat Ads API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://adsapi.snapchat.com/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Snapchat campaign"""
        try:
            url = f"{self.base_url}/organizations/{self.credentials.account_id}/campaigns"
            
            payload = {
                "campaign": {
                    "name": campaign_data["name"],
                    "status": campaign_data.get("status", "PAUSED"),
                    "daily_budget_micro": int(campaign_data.get("daily_budget", 1000) * 1000000),
                    "objective": campaign_data.get("objective", "AWARENESS")
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Snapchat campaign: {result['campaign']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Snapchat API error: {error_text}")
                    raise Exception(f"Snapchat API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Snapchat campaign: {e}")
            raise
    
    async def create_ad_squad(self, campaign_id: str, ad_squad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Snapchat ad squad"""
        try:
            url = f"{self.base_url}/organizations/{self.credentials.account_id}/adsquads"
            
            payload = {
                "adsquad": {
                    "name": ad_squad_data["name"],
                    "campaign_id": campaign_id,
                    "status": ad_squad_data.get("status", "PAUSED"),
                    "bid_micro": int(ad_squad_data.get("bid", 1.0) * 1000000),
                    "targeting": ad_squad_data.get("targeting", {})
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Snapchat ad squad: {result['adsquad']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Snapchat API error: {error_text}")
                    raise Exception(f"Snapchat API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Snapchat ad squad: {e}")
            raise
    
    async def create_ad(self, ad_squad_id: str, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Snapchat ad"""
        try:
            url = f"{self.base_url}/organizations/{self.credentials.account_id}/ads"
            
            payload = {
                "ad": {
                    "name": ad_data["name"],
                    "adsquad_id": ad_squad_id,
                    "status": ad_data.get("status", "PAUSED"),
                    "creative_id": ad_data["creative_id"]
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Snapchat ad: {result['ad']['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Snapchat API error: {error_text}")
                    raise Exception(f"Snapchat API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Snapchat ad: {e}")
            raise
    
    async def get_campaign_stats(self, campaign_id: str, start_time: str, end_time: str) -> Dict[str, Any]:
        """Get Snapchat campaign statistics"""
        try:
            url = f"{self.base_url}/organizations/{self.credentials.account_id}/stats"
            
            params = {
                "campaign_id": campaign_id,
                "start_time": start_time,
                "end_time": end_time,
                "granularity": "DAY"
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Snapchat stats for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Snapchat API error: {error_text}")
                    raise Exception(f"Snapchat API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Snapchat stats: {e}")
            raise

class RedditClient:
    """Reddit Ads API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://ads.reddit.com/api/v2.0"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Reddit campaign"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/campaigns"
            
            payload = {
                "name": campaign_data["name"],
                "status": campaign_data.get("status", "PAUSED"),
                "daily_budget": campaign_data.get("daily_budget", 1000),
                "objective": campaign_data.get("objective", "AWARENESS")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Reddit campaign: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit API error: {error_text}")
                    raise Exception(f"Reddit API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Reddit campaign: {e}")
            raise
    
    async def create_ad_group(self, campaign_id: str, ad_group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Reddit ad group"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/ad_groups"
            
            payload = {
                "name": ad_group_data["name"],
                "campaign_id": campaign_id,
                "status": ad_group_data.get("status", "PAUSED"),
                "bid": ad_group_data.get("bid", 1.0),
                "targeting": ad_group_data.get("targeting", {})
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Reddit ad group: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit API error: {error_text}")
                    raise Exception(f"Reddit API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Reddit ad group: {e}")
            raise
    
    async def create_ad(self, ad_group_id: str, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Reddit ad"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/ads"
            
            payload = {
                "name": ad_data["name"],
                "ad_group_id": ad_group_id,
                "status": ad_data.get("status", "PAUSED"),
                "creative": ad_data.get("creative", {})
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Reddit ad: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit API error: {error_text}")
                    raise Exception(f"Reddit API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Reddit ad: {e}")
            raise
    
    async def get_campaign_metrics(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Reddit campaign metrics"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/campaigns/{campaign_id}/metrics"
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "granularity": "day"
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Reddit metrics for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit API error: {error_text}")
                    raise Exception(f"Reddit API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Reddit metrics: {e}")
            raise

class QuoraClient:
    """Quora Ads API client"""
    
    def __init__(self, credentials: PlatformCredentials):
        self.credentials = credentials
        self.base_url = "https://api.quora.com/ads/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Quora campaign"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/campaigns"
            
            payload = {
                "name": campaign_data["name"],
                "status": campaign_data.get("status", "PAUSED"),
                "daily_budget": campaign_data.get("daily_budget", 1000),
                "objective": campaign_data.get("objective", "CONVERSIONS")
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Quora campaign: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Quora API error: {error_text}")
                    raise Exception(f"Quora API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Quora campaign: {e}")
            raise
    
    async def create_ad_set(self, campaign_id: str, ad_set_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Quora ad set"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/ad_sets"
            
            payload = {
                "name": ad_set_data["name"],
                "campaign_id": campaign_id,
                "status": ad_set_data.get("status", "PAUSED"),
                "bid": ad_set_data.get("bid", 1.0),
                "targeting": ad_set_data.get("targeting", {})
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Quora ad set: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Quora API error: {error_text}")
                    raise Exception(f"Quora API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Quora ad set: {e}")
            raise
    
    async def create_ad(self, ad_set_id: str, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Quora ad"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/ads"
            
            payload = {
                "name": ad_data["name"],
                "ad_set_id": ad_set_id,
                "status": ad_data.get("status", "PAUSED"),
                "creative": ad_data.get("creative", {})
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Created Quora ad: {result['id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Quora API error: {error_text}")
                    raise Exception(f"Quora API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error creating Quora ad: {e}")
            raise
    
    async def get_campaign_insights(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Quora campaign insights"""
        try:
            url = f"{self.base_url}/accounts/{self.credentials.account_id}/campaigns/{campaign_id}/insights"
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "granularity": "day"
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.access_token}"
            }
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Retrieved Quora insights for campaign {campaign_id}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Quora API error: {error_text}")
                    raise Exception(f"Quora API error: {response.status}")
        
        except Exception as e:
            logger.error(f"Error getting Quora insights: {e}")
            raise

class AdditionalPlatformIntegrationsService:
    """Main service for additional platform integrations"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.platform_clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize platform clients"""
        self.platform_clients = {
            PlatformType.FACEBOOK_ADS: FacebookAdsClient,
            PlatformType.TWITTER_ADS: TwitterAdsClient,
            PlatformType.PINTEREST: PinterestClient,
            PlatformType.SNAPCHAT: SnapchatClient,
            PlatformType.REDDIT: RedditClient,
            PlatformType.QUORA: QuoraClient
        }
    
    async def create_campaign(self, platform: PlatformType, campaign_data: Dict[str, Any], credentials: PlatformCredentials) -> Dict[str, Any]:
        """Create campaign on specified platform"""
        try:
            client_class = self.platform_clients.get(platform)
            if not client_class:
                raise ValueError(f"Unsupported platform: {platform}")
            
            async with client_class(credentials) as client:
                result = await client.create_campaign(campaign_data)
                
                # Save campaign to database
                campaign_doc = {
                    "campaign_id": result.get("id") or result.get("data", {}).get("id"),
                    "platform": platform.value,
                    "name": campaign_data["name"],
                    "objective": campaign_data.get("objective", "AWARENESS"),
                    "budget": campaign_data.get("budget", 1000),
                    "daily_budget": campaign_data.get("daily_budget"),
                    "status": campaign_data.get("status", "PAUSED"),
                    "targeting": campaign_data.get("targeting", {}),
                    "creative": campaign_data.get("creative", {}),
                    "created_at": datetime.utcnow().isoformat(),
                    "credentials_account_id": credentials.account_id
                }
                
                await self.db.additional_platform_campaigns.insert_one(campaign_doc)
                
                logger.info(f"Created {platform.value} campaign: {campaign_doc['campaign_id']}")
                return result
        
        except Exception as e:
            logger.error(f"Error creating {platform.value} campaign: {e}")
            raise
    
    async def get_campaign_metrics(self, platform: PlatformType, campaign_id: str, credentials: PlatformCredentials, date_range: str = "last_30_days") -> Dict[str, Any]:
        """Get campaign metrics from specified platform"""
        try:
            client_class = self.platform_clients.get(platform)
            if not client_class:
                raise ValueError(f"Unsupported platform: {platform}")
            
            async with client_class(credentials) as client:
                if platform == PlatformType.FACEBOOK_ADS:
                    result = await client.get_campaign_insights(campaign_id, date_range)
                elif platform == PlatformType.TWITTER_ADS:
                    start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
                    end_time = datetime.utcnow().isoformat()
                    result = await client.get_campaign_stats(campaign_id, start_time, end_time)
                elif platform == PlatformType.PINTEREST:
                    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = datetime.utcnow().strftime("%Y-%m-%d")
                    result = await client.get_campaign_analytics(campaign_id, start_date, end_date)
                elif platform == PlatformType.SNAPCHAT:
                    start_time = (datetime.utcnow() - timedelta(days=30)).isoformat()
                    end_time = datetime.utcnow().isoformat()
                    result = await client.get_campaign_stats(campaign_id, start_time, end_time)
                elif platform == PlatformType.REDDIT:
                    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = datetime.utcnow().strftime("%Y-%m-%d")
                    result = await client.get_campaign_metrics(campaign_id, start_date, end_date)
                elif platform == PlatformType.QUORA:
                    start_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = datetime.utcnow().strftime("%Y-%m-%d")
                    result = await client.get_campaign_insights(campaign_id, start_date, end_date)
                
                # Save metrics to database
                metrics_doc = {
                    "campaign_id": campaign_id,
                    "platform": platform.value,
                    "metrics": result,
                    "date_range": date_range,
                    "retrieved_at": datetime.utcnow().isoformat()
                }
                
                await self.db.additional_platform_metrics.insert_one(metrics_doc)
                
                logger.info(f"Retrieved {platform.value} metrics for campaign {campaign_id}")
                return result
        
        except Exception as e:
            logger.error(f"Error getting {platform.value} metrics: {e}")
            raise
    
    async def get_platform_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get comprehensive platform dashboard"""
        try:
            # Get all campaigns across platforms
            campaigns = await self.db.additional_platform_campaigns.find({
                "credentials_account_id": organization_id
            }).to_list(length=None)
            
            # Get platform statistics
            platform_stats = {}
            for platform in PlatformType:
                platform_campaigns = [c for c in campaigns if c["platform"] == platform.value]
                platform_stats[platform.value] = {
                    "total_campaigns": len(platform_campaigns),
                    "active_campaigns": len([c for c in platform_campaigns if c["status"] == "ACTIVE"]),
                    "total_budget": sum(c.get("budget", 0) for c in platform_campaigns),
                    "total_daily_budget": sum(c.get("daily_budget", 0) for c in platform_campaigns if c.get("daily_budget"))
                }
            
            # Get recent metrics
            recent_metrics = await self.db.additional_platform_metrics.find({
                "retrieved_at": {"$gte": (datetime.utcnow() - timedelta(days=7)).isoformat()}
            }).sort("retrieved_at", -1).limit(50).to_list(length=None)
            
            return {
                "organization_id": organization_id,
                "platform_statistics": platform_stats,
                "total_campaigns": len(campaigns),
                "active_campaigns": len([c for c in campaigns if c["status"] == "ACTIVE"]),
                "total_budget": sum(c.get("budget", 0) for c in campaigns),
                "recent_metrics": recent_metrics,
                "supported_platforms": [platform.value for platform in PlatformType],
                "generated_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error getting platform dashboard: {e}")
            raise

# Global instance
additional_platform_integrations_service = None

def get_additional_platform_integrations_service(db: AsyncIOMotorClient) -> AdditionalPlatformIntegrationsService:
    """Get additional platform integrations service instance"""
    global additional_platform_integrations_service
    if additional_platform_integrations_service is None:
        additional_platform_integrations_service = AdditionalPlatformIntegrationsService(db)
    return additional_platform_integrations_service
