"""
Additional Integrations System
Comprehensive integrations for more platforms, CRM systems, and analytics tools
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import aiohttp
import requests
# Phase 1 deprecated - MongoDB archived (MVP uses Supabase)
# from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import redis
import hashlib
import hmac
import base64
from urllib.parse import urlencode, parse_qs
import xml.etree.ElementTree as ET
import csv
import io

logger = logging.getLogger(__name__)

class IntegrationType(str, Enum):
    """Integration types"""
    CRM = "crm"
    EMAIL_MARKETING = "email_marketing"
    SOCIAL_MEDIA = "social_media"
    ECOMMERCE = "ecommerce"
    ANALYTICS = "analytics"
    PAYMENT = "payment"
    COMMUNICATION = "communication"
    PROJECT_MANAGEMENT = "project_management"
    CUSTOMER_SUPPORT = "customer_support"
    MARKETING_AUTOMATION = "marketing_automation"

class IntegrationStatus(str, Enum):
    """Integration status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"
    CONFIGURING = "configuring"

class PlatformType(str, Enum):
    """Platform types"""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    MAILCHIMP = "mailchimp"
    CONSTANT_CONTACT = "constant_contact"
    DRUPAL = "drupal"
    WORDPRESS = "wordpress"
    MAGENTO = "magento"
    WOOCOMMERCE = "woocommerce"
    BIGCOMMERCE = "bigcommerce"
    SQUARE = "square"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    TWILIO = "twilio"
    SLACK = "slack"
    MICROSOFT_TEAMS = "microsoft_teams"
    ZENDESK = "zendesk"
    FRESHWORKS = "freshworks"
    ASANA = "asana"
    TRELLO = "trello"
    MONDAY = "monday"
    ZAPIER = "zapier"
    IFTTT = "ifttt"
    GOOGLE_ANALYTICS = "google_analytics"
    MIXPANEL = "mixpanel"
    AMPLITUDE = "amplitude"
    HOTJAR = "hotjar"
    CUSTOM = "custom"

@dataclass
class IntegrationConfig:
    """Integration configuration"""
    integration_id: str
    platform_type: PlatformType
    integration_type: IntegrationType
    name: str
    description: str
    status: IntegrationStatus
    credentials: Dict[str, Any]
    settings: Dict[str, Any]
    webhook_url: Optional[str]
    api_endpoints: List[str]
    rate_limits: Dict[str, int]
    created_at: datetime
    updated_at: datetime
    last_sync: Optional[datetime]

@dataclass
class SyncResult:
    """Sync operation result"""
    sync_id: str
    integration_id: str
    operation: str
    status: str
    records_processed: int
    records_successful: int
    records_failed: int
    errors: List[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[float]

class SalesforceIntegration:
    """Salesforce CRM integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.base_url = credentials.get("instance_url")
        self.access_token = credentials.get("access_token")
        self.api_version = "v58.0"
    
    async def authenticate(self) -> bool:
        """Authenticate with Salesforce"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = await self._make_request("GET", f"/services/data/{self.api_version}/sobjects/")
            return response is not None
            
        except Exception as e:
            logger.error(f"Salesforce authentication error: {e}")
            return False
    
    async def get_contacts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get contacts from Salesforce"""
        try:
            query = f"SELECT Id, FirstName, LastName, Email, Phone FROM Contact LIMIT {limit}"
            response = await self._make_request("GET", f"/services/data/{self.api_version}/query/?q={query}")
            
            if response and "records" in response:
                return response["records"]
            return []
            
        except Exception as e:
            logger.error(f"Error getting Salesforce contacts: {e}")
            return []
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create contact in Salesforce"""
        try:
            response = await self._make_request(
                "POST", 
                f"/services/data/{self.api_version}/sobjects/Contact/",
                data=contact_data
            )
            
            if response and "id" in response:
                return response["id"]
            return None
            
        except Exception as e:
            logger.error(f"Error creating Salesforce contact: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to Salesforce"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"Salesforce API request error: {e}")
            return None

class HubSpotIntegration:
    """HubSpot CRM integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.api_key = credentials.get("api_key")
        self.base_url = "https://api.hubapi.com"
    
    async def authenticate(self) -> bool:
        """Authenticate with HubSpot"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self._make_request("GET", "/crm/v3/objects/contacts")
            return response is not None
            
        except Exception as e:
            logger.error(f"HubSpot authentication error: {e}")
            return False
    
    async def get_contacts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get contacts (Phase 2 - HubSpot archived)"""
        try:
            params = {"limit": limit}
            response = await self._make_request("GET", "/crm/v3/objects/contacts", params=params)
            
            if response and "results" in response:
                return response["results"]
            return []
            
        except Exception as e:
            logger.error(f"Error getting HubSpot contacts: {e}")
            return []
    
    async def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create contact in HubSpot"""
        try:
            response = await self._make_request(
                "POST", 
                "/crm/v3/objects/contacts",
                data=contact_data
            )
            
            if response and "id" in response:
                return response["id"]
            return None
            
        except Exception as e:
            logger.error(f"Error creating HubSpot contact: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to HubSpot"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers, params=params) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"HubSpot API request error: {e}")
            return None

class MailChimpIntegration:
    """MailChimp email marketing integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.api_key = credentials.get("api_key")
        self.server_prefix = credentials.get("server_prefix", "us1")
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
    
    async def authenticate(self) -> bool:
        """Authenticate with MailChimp"""
        try:
            response = await self._make_request("GET", "/")
            return response is not None
            
        except Exception as e:
            logger.error(f"MailChimp authentication error: {e}")
            return False
    
    async def get_lists(self) -> List[Dict[str, Any]]:
        """Get email lists from MailChimp"""
        try:
            response = await self._make_request("GET", "/lists")
            
            if response and "lists" in response:
                return response["lists"]
            return []
            
        except Exception as e:
            logger.error(f"Error getting MailChimp lists: {e}")
            return []
    
    async def add_subscriber(self, list_id: str, subscriber_data: Dict[str, Any]) -> bool:
        """Add subscriber to MailChimp list"""
        try:
            response = await self._make_request(
                "POST", 
                f"/lists/{list_id}/members",
                data=subscriber_data
            )
            
            return response is not None
            
        except Exception as e:
            logger.error(f"Error adding MailChimp subscriber: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to MailChimp"""
        try:
            url = f"{self.base_url}{endpoint}"
            auth = ("anystring", self.api_key)
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, auth=auth) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, auth=auth, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"MailChimp API request error: {e}")
            return None

class WordPressIntegration:
    """WordPress CMS integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.base_url = credentials.get("base_url")
        self.username = credentials.get("username")
        self.password = credentials.get("password")
    
    async def authenticate(self) -> bool:
        """Authenticate with WordPress"""
        try:
            response = await self._make_request("GET", "/wp-json/wp/v2/users/me")
            return response is not None
            
        except Exception as e:
            logger.error(f"WordPress authentication error: {e}")
            return False
    
    async def get_posts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get posts from WordPress"""
        try:
            params = {"per_page": limit}
            response = await self._make_request("GET", "/wp-json/wp/v2/posts", params=params)
            
            if isinstance(response, list):
                return response
            return []
            
        except Exception as e:
            logger.error(f"Error getting WordPress posts: {e}")
            return []
    
    async def create_post(self, post_data: Dict[str, Any]) -> Optional[int]:
        """Create post in WordPress"""
        try:
            response = await self._make_request(
                "POST", 
                "/wp-json/wp/v2/posts",
                data=post_data
            )
            
            if response and "id" in response:
                return response["id"]
            return None
            
        except Exception as e:
            logger.error(f"Error creating WordPress post: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to WordPress"""
        try:
            url = f"{self.base_url}{endpoint}"
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, auth=auth, params=params) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, auth=auth, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"WordPress API request error: {e}")
            return None

class WooCommerceIntegration:
    """WooCommerce e-commerce integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.base_url = credentials.get("base_url")
        self.consumer_key = credentials.get("consumer_key")
        self.consumer_secret = credentials.get("consumer_secret")
    
    async def authenticate(self) -> bool:
        """Authenticate with WooCommerce"""
        try:
            response = await self._make_request("GET", "/wp-json/wc/v3/products")
            return response is not None
            
        except Exception as e:
            logger.error(f"WooCommerce authentication error: {e}")
            return False
    
    async def get_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products from WooCommerce"""
        try:
            params = {"per_page": limit}
            response = await self._make_request("GET", "/wp-json/wc/v3/products", params=params)
            
            if isinstance(response, list):
                return response
            return []
            
        except Exception as e:
            logger.error(f"Error getting WooCommerce products: {e}")
            return []
    
    async def create_order(self, order_data: Dict[str, Any]) -> Optional[int]:
        """Create order in WooCommerce"""
        try:
            response = await self._make_request(
                "POST", 
                "/wp-json/wc/v3/orders",
                data=order_data
            )
            
            if response and "id" in response:
                return response["id"]
            return None
            
        except Exception as e:
            logger.error(f"Error creating WooCommerce order: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to WooCommerce"""
        try:
            url = f"{self.base_url}{endpoint}"
            auth = aiohttp.BasicAuth(self.consumer_key, self.consumer_secret)
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, auth=auth, params=params) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, auth=auth, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"WooCommerce API request error: {e}")
            return None

class TwilioIntegration:
    """Twilio communication integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.account_sid = credentials.get("account_sid")
        self.auth_token = credentials.get("auth_token")
        self.phone_number = credentials.get("phone_number")
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
    
    async def authenticate(self) -> bool:
        """Authenticate with Twilio"""
        try:
            response = await self._make_request("GET", ".json")
            return response is not None
            
        except Exception as e:
            logger.error(f"Twilio authentication error: {e}")
            return False
    
    async def send_sms(self, to: str, message: str) -> Optional[str]:
        """Send SMS via Twilio"""
        try:
            data = {
                "To": to,
                "From": self.phone_number,
                "Body": message
            }
            
            response = await self._make_request(
                "POST", 
                "/Messages.json",
                data=data
            )
            
            if response and "sid" in response:
                return response["sid"]
            return None
            
        except Exception as e:
            logger.error(f"Error sending Twilio SMS: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to Twilio"""
        try:
            url = f"{self.base_url}{endpoint}"
            auth = aiohttp.BasicAuth(self.account_sid, self.auth_token)
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, auth=auth) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, auth=auth, data=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"Twilio API request error: {e}")
            return None

class SlackIntegration:
    """Slack communication integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.bot_token = credentials.get("bot_token")
        self.base_url = "https://slack.com/api"
    
    async def authenticate(self) -> bool:
        """Authenticate with Slack"""
        try:
            response = await self._make_request("GET", "/auth.test")
            return response and response.get("ok", False)
            
        except Exception as e:
            logger.error(f"Slack authentication error: {e}")
            return False
    
    async def send_message(self, channel: str, message: str) -> bool:
        """Send message to Slack channel"""
        try:
            data = {
                "channel": channel,
                "text": message
            }
            
            response = await self._make_request(
                "POST", 
                "/chat.postMessage",
                data=data
            )
            
            return response and response.get("ok", False)
            
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to Slack"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Authorization": f"Bearer {self.bot_token}"}
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, headers=headers, data=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"Slack API request error: {e}")
            return None

class GoogleAnalyticsIntegration:
    """Google Analytics integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.access_token = credentials.get("access_token")
        self.property_id = credentials.get("property_id")
        self.base_url = "https://analyticsdata.googleapis.com/v1beta"
    
    async def authenticate(self) -> bool:
        """Authenticate with Google Analytics"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self._make_request("GET", f"/properties/{self.property_id}/metadata")
            return response is not None
            
        except Exception as e:
            logger.error(f"Google Analytics authentication error: {e}")
            return False
    
    async def get_analytics_data(self, start_date: str, end_date: str, metrics: List[str]) -> Optional[Dict[str, Any]]:
        """Get analytics data from Google Analytics"""
        try:
            data = {
                "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                "metrics": [{"name": metric} for metric in metrics]
            }
            
            response = await self._make_request(
                "POST", 
                f"/properties/{self.property_id}:runReport",
                data=data
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting Google Analytics data: {e}")
            return None
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make API request to Google Analytics"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await response.json() if response.status == 200 else None
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json() if response.status in [200, 201] else None
                        
        except Exception as e:
            logger.error(f"Google Analytics API request error: {e}")
            return None

class ZapierIntegration:
    """Zapier automation integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.webhook_url = credentials.get("webhook_url")
        self.api_key = credentials.get("api_key")
    
    async def trigger_webhook(self, data: Dict[str, Any]) -> bool:
        """Trigger Zapier webhook"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, headers=headers, json=data) as response:
                    return response.status in [200, 201]
                    
        except Exception as e:
            logger.error(f"Error triggering Zapier webhook: {e}")
            return False

class AdditionalIntegrationsService:
    """Main service for additional integrations"""
    
    def __init__(self, db=None, redis_client: redis.Redis=None):
        # Phase 1 deprecated - MongoDB archived (MVP uses Supabase)
        self.db = None  # Phase 1: MongoDB archived
        self.redis = redis_client
        self.integrations = {}
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize integration classes"""
        self.integration_classes = {
            PlatformType.SALESFORCE: SalesforceIntegration,
            PlatformType.HUBSPOT: HubSpotIntegration,
            PlatformType.MAILCHIMP: MailChimpIntegration,
            PlatformType.WORDPRESS: WordPressIntegration,
            PlatformType.WOOCOMMERCE: WooCommerceIntegration,
            PlatformType.TWILIO: TwilioIntegration,
            PlatformType.SLACK: SlackIntegration,
            PlatformType.GOOGLE_ANALYTICS: GoogleAnalyticsIntegration,
            PlatformType.ZAPIER: ZapierIntegration
        }
    
    async def create_integration(self, integration_data: Dict[str, Any]) -> str:
        """Create new integration"""
        try:
            integration_id = str(uuid.uuid4())
            
            config = IntegrationConfig(
                integration_id=integration_id,
                platform_type=PlatformType(integration_data["platform_type"]),
                integration_type=IntegrationType(integration_data["integration_type"]),
                name=integration_data["name"],
                description=integration_data.get("description", ""),
                status=IntegrationStatus.PENDING,
                credentials=integration_data["credentials"],
                settings=integration_data.get("settings", {}),
                webhook_url=integration_data.get("webhook_url"),
                api_endpoints=integration_data.get("api_endpoints", []),
                rate_limits=integration_data.get("rate_limits", {}),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_sync=None
            )
            
            config_doc = {
                "integration_id": integration_id,
                "platform_type": config.platform_type.value,
                "integration_type": config.integration_type.value,
                "name": config.name,
                "description": config.description,
                "status": config.status.value,
                "credentials": config.credentials,
                "settings": config.settings,
                "webhook_url": config.webhook_url,
                "api_endpoints": config.api_endpoints,
                "rate_limits": config.rate_limits,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                "last_sync": config.last_sync.isoformat() if config.last_sync else None
            }
            
            await self.db.additional_integrations.insert_one(config_doc)
            
            logger.info(f"Created integration {integration_id}: {config.name}")
            return integration_id
            
        except Exception as e:
            logger.error(f"Error creating integration: {e}")
            raise
    
    async def test_integration(self, integration_id: str) -> Dict[str, Any]:
        """Test integration connection"""
        try:
            # Get integration config
            config_doc = await self.db.additional_integrations.find_one({"integration_id": integration_id})
            if not config_doc:
                raise ValueError(f"Integration {integration_id} not found")
            
            platform_type = PlatformType(config_doc["platform_type"])
            
            # Initialize integration
            if platform_type in self.integration_classes:
                integration = self.integration_classes[platform_type](config_doc["credentials"])
                
                # Test authentication
                is_authenticated = await integration.authenticate()
                
                # Update status
                status = IntegrationStatus.ACTIVE if is_authenticated else IntegrationStatus.ERROR
                await self.db.additional_integrations.update_one(
                    {"integration_id": integration_id},
                    {
                        "$set": {
                            "status": status.value,
                            "updated_at": datetime.utcnow().isoformat()
                        }
                    }
                )
                
                return {
                    "integration_id": integration_id,
                    "platform_type": platform_type.value,
                    "authenticated": is_authenticated,
                    "status": status.value,
                    "tested_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "integration_id": integration_id,
                    "platform_type": platform_type.value,
                    "authenticated": False,
                    "status": IntegrationStatus.ERROR.value,
                    "error": "Unsupported platform type"
                }
                
        except Exception as e:
            logger.error(f"Error testing integration: {e}")
            raise
    
    async def sync_data(self, integration_id: str, operation: str, data: Dict[str, Any] = None) -> SyncResult:
        """Sync data with integration"""
        try:
            sync_id = str(uuid.uuid4())
            started_at = datetime.utcnow()
            
            # Get integration config
            config_doc = await self.db.additional_integrations.find_one({"integration_id": integration_id})
            if not config_doc:
                raise ValueError(f"Integration {integration_id} not found")
            
            platform_type = PlatformType(config_doc["platform_type"])
            integration = self.integration_classes[platform_type](config_doc["credentials"])
            
            records_processed = 0
            records_successful = 0
            records_failed = 0
            errors = []
            
            # Perform sync operation based on platform and operation
            if platform_type == PlatformType.SALESFORCE:
                if operation == "get_contacts":
                    contacts = await integration.get_contacts()
                    records_processed = len(contacts)
                    records_successful = len(contacts)
                elif operation == "create_contact" and data:
                    contact_id = await integration.create_contact(data)
                    records_processed = 1
                    records_successful = 1 if contact_id else 0
                    records_failed = 1 if not contact_id else 0
            
            elif platform_type == PlatformType.HUBSPOT:
                if operation == "get_contacts":
                    contacts = await integration.get_contacts()
                    records_processed = len(contacts)
                    records_successful = len(contacts)
                elif operation == "create_contact" and data:
                    contact_id = await integration.create_contact(data)
                    records_processed = 1
                    records_successful = 1 if contact_id else 0
                    records_failed = 1 if not contact_id else 0
            
            elif platform_type == PlatformType.MAILCHIMP:
                if operation == "get_lists":
                    lists = await integration.get_lists()
                    records_processed = len(lists)
                    records_successful = len(lists)
                elif operation == "add_subscriber" and data:
                    success = await integration.add_subscriber(data.get("list_id"), data.get("subscriber_data"))
                    records_processed = 1
                    records_successful = 1 if success else 0
                    records_failed = 1 if not success else 0
            
            # Update last sync time
            await self.db.additional_integrations.update_one(
                {"integration_id": integration_id},
                {
                    "$set": {
                        "last_sync": datetime.utcnow().isoformat(),
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            completed_at = datetime.utcnow()
            duration = (completed_at - started_at).total_seconds()
            
            sync_result = SyncResult(
                sync_id=sync_id,
                integration_id=integration_id,
                operation=operation,
                status="completed" if records_failed == 0 else "partial",
                records_processed=records_processed,
                records_successful=records_successful,
                records_failed=records_failed,
                errors=errors,
                started_at=started_at,
                completed_at=completed_at,
                duration=duration
            )
            
            # Store sync result
            sync_doc = {
                "sync_id": sync_id,
                "integration_id": integration_id,
                "operation": operation,
                "status": sync_result.status,
                "records_processed": records_processed,
                "records_successful": records_successful,
                "records_failed": records_failed,
                "errors": errors,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "duration": duration
            }
            
            await self.db.sync_results.insert_one(sync_doc)
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error syncing data: {e}")
            raise
    
    async def get_integrations(self, organization_id: str, platform_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get integrations for organization"""
        try:
            query = {"organization_id": organization_id}
            if platform_type:
                query["platform_type"] = platform_type
            
            integrations = await self.db.additional_integrations.find(query).to_list(length=None)
            return integrations
            
        except Exception as e:
            logger.error(f"Error getting integrations: {e}")
            raise
    
    async def get_integration_dashboard(self, organization_id: str) -> Dict[str, Any]:
        """Get additional integrations dashboard"""
        try:
            # Get integration statistics
            total_integrations = await self.db.additional_integrations.count_documents({"organization_id": organization_id})
            active_integrations = await self.db.additional_integrations.count_documents({
                "organization_id": organization_id,
                "status": IntegrationStatus.ACTIVE.value
            })
            error_integrations = await self.db.additional_integrations.count_documents({
                "organization_id": organization_id,
                "status": IntegrationStatus.ERROR.value
            })
            
            # Get recent integrations
            recent_integrations = await self.db.additional_integrations.find({
                "organization_id": organization_id
            }).sort("created_at", -1).limit(10).to_list(length=None)
            
            # Get sync statistics
            recent_syncs = await self.db.sync_results.find({
                "integration_id": {"$in": [i["integration_id"] for i in recent_integrations]}
            }).sort("started_at", -1).limit(20).to_list(length=None)
            
            # Calculate success rate
            total_syncs = len(recent_syncs)
            successful_syncs = len([s for s in recent_syncs if s["status"] == "completed"])
            sync_success_rate = successful_syncs / total_syncs if total_syncs > 0 else 0
            
            return {
                "organization_id": organization_id,
                "integration_statistics": {
                    "total_integrations": total_integrations,
                    "active_integrations": active_integrations,
                    "error_integrations": error_integrations,
                    "success_rate": active_integrations / total_integrations if total_integrations > 0 else 0
                },
                "sync_statistics": {
                    "total_syncs": total_syncs,
                    "successful_syncs": successful_syncs,
                    "sync_success_rate": sync_success_rate
                },
                "recent_integrations": recent_integrations,
                "recent_syncs": recent_syncs,
                "supported_platforms": [pt.value for pt in PlatformType],
                "supported_integration_types": [it.value for it in IntegrationType],
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting integration dashboard: {e}")
            raise

# Global instance
additional_integrations_service = None

def get_additional_integrations_service(db=None, redis_client: redis.Redis=None) -> AdditionalIntegrationsService:
    # Phase 1 deprecated - MongoDB archived (MVP uses Supabase)
    """Get additional integrations service instance"""
    global additional_integrations_service
    if additional_integrations_service is None:
        additional_integrations_service = AdditionalIntegrationsService(db, redis_client)
    return additional_integrations_service
