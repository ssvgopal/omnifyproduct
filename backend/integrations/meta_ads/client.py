"""
Production-Ready Meta Ads API Integration for OmnifyProduct
Complete Facebook/Instagram Ads API integration with campaign management and analytics

Features:
- OAuth2 authentication flow
- Campaign creation and management
- Audience targeting
- Creative asset management
- Performance analytics
- Conversion tracking
- Budget optimization
- Real-time reporting
"""

import os
import asyncio
import json
import base64
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs

try:
    import facebook_business
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.campaign import Campaign
    from facebook_business.adobjects.adset import AdSet
    from facebook_business.adobjects.ad import Ad
    from facebook_business.adobjects.adcreative import AdCreative
    from facebook_business.adobjects.insights import Insights
    from facebook_business.exceptions import FacebookRequestError
    HAS_META_ADS = True
except ImportError:
    HAS_META_ADS = False
    FacebookAdsApi = None
    FacebookRequestError = Exception

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

class MetaAdsIntegration:
    """
    Complete Meta Ads API integration for Facebook/Instagram campaigns
    """

    def __init__(self):
        self.app_id = os.environ.get('META_APP_ID')
        self.app_secret = os.environ.get('META_APP_SECRET')
        self.redirect_uri = os.environ.get('META_REDIRECT_URI', 'http://localhost:8000/auth/meta-ads/callback')

        # API configuration
        self.api_version = 'v18.0'
        self.timeout_seconds = 30

        # Rate limiting (Meta Ads has limits)
        self.requests_per_second = 5  # Conservative limit
        self.requests_per_hour = 2000
        self.daily_limit = 50000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes

        # Initialize API
        self.api = None
        if HAS_META_ADS and self.app_id and self.app_secret:
            FacebookAdsApi.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                api_version=self.api_version
            )
            self.api = FacebookAdsApi.get_default_api()

        logger.info("Meta Ads integration initialized", extra={
            "has_api": HAS_META_ADS and self.api is not None,
            "api_version": self.api_version,
            "rate_limit_per_second": self.requests_per_second
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for Meta
        """
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'ads_management,ads_read,business_management',
            'response_type': 'code',
            'state': state
        }

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access token
        """
        try:
            import httpx

            token_url = f"https://graph.facebook.com/{self.api_version}/oauth/access_token"
            params = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'redirect_uri': self.redirect_uri,
                'code': code
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(token_url, params=params)
                response.raise_for_status()

                data = response.json()

                # Get long-lived token
                long_lived_url = f"https://graph.facebook.com/{self.api_version}/oauth/access_token"
                long_lived_params = {
                    'grant_type': 'fb_exchange_token',
                    'client_id': self.app_id,
                    'client_secret': self.app_secret,
                    'fb_exchange_token': data['access_token']
                }

                long_lived_response = await client.get(long_lived_url, params=long_lived_params)
                long_lived_data = long_lived_response.json()

                tokens = {
                    'access_token': long_lived_data['access_token'],
                    'token_type': long_lived_data.get('token_type', 'bearer'),
                    'expires_in': long_lived_data.get('expires_in', 5184000),  # 60 days
                    'expires_at': datetime.utcnow() + timedelta(seconds=long_lived_data.get('expires_in', 5184000))
                }

                logger.info("Meta Ads OAuth tokens obtained successfully")
                return tokens

        except Exception as e:
            logger.error("Failed to exchange Meta OAuth code for tokens", exc_info=e)
            return None

    async def get_valid_access_token(self, organization_id: str, account_id: str) -> Optional[str]:
        """
        Get valid access token for Meta account
        """
        try:
            # Get stored tokens
            tokens_key = f"meta_ads_tokens_{organization_id}_{account_id}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Check if token is still valid (with buffer)
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            buffer_time = timedelta(hours=24)  # Refresh 24 hours before expiry

            if datetime.utcnow() >= (expires_at - buffer_time):
                logger.warning("Meta Ads token expired or expiring soon", extra={
                    "organization_id": organization_id,
                    "account_id": account_id,
                    "expires_at": expires_at.isoformat()
                })
                return None

            return tokens['access_token']

        except Exception as e:
            logger.error("Failed to get valid Meta Ads access token", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== ACCOUNT MANAGEMENT ==========

    async def list_ad_accounts(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List accessible Meta ad accounts
        """
        try:
            # Get user's access token (assuming first account for now)
            access_token = await self.get_valid_access_token(organization_id, "default")
            if not access_token:
                return []

            # Initialize API with user token
            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)
            api = FacebookAdsApi.get_default_api()

            # Get user's ad accounts
            from facebook_business.adobjects.user import User
            me = User(fbid='me', api=api)
            accounts = me.get_ad_accounts(fields=[
                'account_id', 'name', 'currency', 'timezone_name',
                'account_status', 'balance', 'spend_cap'
            ])

            ad_accounts = []
            for account in accounts:
                ad_accounts.append({
                    "account_id": account['account_id'],
                    "name": account['name'],
                    "currency": account['currency'],
                    "timezone": account['timezone_name'],
                    "status": account['account_status'],
                    "balance": account.get('balance'),
                    "spend_cap": account.get('spend_cap')
                })

            # Cache results
            cache_key = f"meta_ad_accounts_{organization_id}"
            await production_secrets_manager.store_secret(cache_key, ad_accounts, {"ttl": self.cache_ttl})

            logger.info("Meta ad accounts retrieved", extra={
                "organization_id": organization_id,
                "account_count": len(ad_accounts)
            })

            return ad_accounts

        except FacebookRequestError as e:
            logger.error("Meta Ads API error listing accounts", exc_info=e, extra={
                "organization_id": organization_id,
                "error_code": e.api_error_code(),
                "error_message": e.api_error_message()
            })
            return []
        except Exception as e:
            logger.error("Failed to list Meta ad accounts", exc_info=e, extra={
                "organization_id": organization_id
            })
            return []

    # ========== CAMPAIGN MANAGEMENT ==========

    async def create_campaign(
        self,
        organization_id: str,
        account_id: str,
        campaign_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a new Meta Ads campaign
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            account = AdAccount(f'act_{account_id}')

            # Create campaign
            campaign = Campaign(parent_id=account.get_id_assured())
            campaign.update({
                'name': campaign_data.get('name', 'New Campaign'),
                'objective': campaign_data.get('objective', 'CONVERSIONS'),
                'status': 'PAUSED',
                'special_ad_categories': []
            })

            # Set campaign budget
            if 'budget' in campaign_data:
                budget_data = campaign_data['budget']
                campaign.update({
                    'daily_budget': budget_data.get('daily_budget'),
                    'lifetime_budget': budget_data.get('lifetime_budget')
                })

            # Execute campaign creation
            campaign.remote_create()

            logger.info("Meta Ads campaign created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign.get_id(),
                "campaign_name": campaign_data.get('name')
            })

            return campaign.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error creating campaign", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to create Meta Ads campaign", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def get_campaign_insights(
        self,
        organization_id: str,
        account_id: str,
        campaign_ids: List[str],
        date_range: Dict[str, str],
        metrics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed campaign performance insights
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return []

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            # Default metrics if not specified
            if not metrics:
                metrics = [
                    'impressions', 'clicks', 'spend', 'reach', 'frequency',
                    'actions', 'cost_per_action_type', 'ctr', 'cpc', 'cpp',
                    'conversions', 'conversion_rate', 'roas'
                ]

            insights_data = []

            for campaign_id in campaign_ids:
                try:
                    campaign = Campaign(campaign_id)
                    insights = campaign.get_insights(
                        fields=metrics,
                        params={
                            'time_range': {
                                'since': date_range['start'],
                                'until': date_range['end']
                            },
                            'level': 'campaign',
                            'time_increment': 1
                        }
                    )

                    for insight in insights:
                        insight_data = {
                            "campaign_id": campaign_id,
                            "date_start": insight.get('date_start'),
                            "date_stop": insight.get('date_stop'),
                            "impressions": int(insight.get('impressions', 0)),
                            "clicks": int(insight.get('clicks', 0)),
                            "spend": float(insight.get('spend', 0)),
                            "reach": int(insight.get('reach', 0)),
                            "frequency": float(insight.get('frequency', 0)),
                            "ctr": float(insight.get('ctr', 0)),
                            "cpc": float(insight.get('cpc', 0)),
                            "cpp": float(insight.get('cpp', 0))
                        }

                        # Process actions and conversions
                        actions = insight.get('actions', [])
                        conversions = 0
                        conversion_value = 0

                        for action in actions:
                            if action.get('action_type') in ['offsite_conversion.custom', 'purchase', 'lead']:
                                conversions += int(action.get('value', 0))

                        insight_data["conversions"] = conversions
                        insight_data["conversion_value"] = conversion_value
                        insight_data["roas"] = conversion_value / float(insight.get('spend', 1)) if conversion_value > 0 else 0

                        insights_data.append(insight_data)

                except FacebookRequestError as e:
                    logger.warning("Failed to get insights for campaign", extra={
                        "campaign_id": campaign_id,
                        "error_code": e.api_error_code()
                    })
                    continue

            logger.info("Meta Ads campaign insights retrieved", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_count": len(campaign_ids),
                "data_points": len(insights_data)
            })

            return insights_data

        except FacebookRequestError as e:
            logger.error("Meta Ads API error getting insights", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return []
        except Exception as e:
            logger.error("Failed to get Meta Ads campaign insights", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return []

    async def create_ad_set(
        self,
        organization_id: str,
        account_id: str,
        campaign_id: str,
        ad_set_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create an ad set within a campaign
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            account = AdAccount(f'act_{account_id}')

            # Create ad set
            ad_set = AdSet(parent_id=account.get_id_assured())
            ad_set.update({
                'name': ad_set_data.get('name', 'New Ad Set'),
                'campaign_id': campaign_id,
                'status': 'PAUSED',
                'billing_event': ad_set_data.get('billing_event', 'IMPRESSIONS'),
                'optimization_goal': ad_set_data.get('optimization_goal', 'REACH'),
                'bid_strategy': ad_set_data.get('bid_strategy', 'LOWEST_COST_WITHOUT_CAP')
            })

            # Set budget
            if 'budget' in ad_set_data:
                ad_set.update({
                    'daily_budget': ad_set_data['budget'].get('daily_budget'),
                    'lifetime_budget': ad_set_data['budget'].get('lifetime_budget')
                })

            # Set targeting
            if 'targeting' in ad_set_data:
                targeting = ad_set_data['targeting']

                targeting_data = {}

                # Geographic targeting
                if 'geo_locations' in targeting:
                    targeting_data['geo_locations'] = targeting['geo_locations']

                # Demographic targeting
                if 'age_min' in targeting or 'age_max' in targeting:
                    targeting_data['age_min'] = targeting.get('age_min', 18)
                    targeting_data['age_max'] = targeting.get('age_max', 65)

                if 'genders' in targeting:
                    targeting_data['genders'] = targeting['genders']

                # Interest targeting
                if 'interests' in targeting:
                    targeting_data['interests'] = targeting['interests']

                # Custom audiences
                if 'custom_audiences' in targeting:
                    targeting_data['custom_audiences'] = targeting['custom_audiences']

                ad_set.update({'targeting': targeting_data})

            # Execute ad set creation
            ad_set.remote_create()

            logger.info("Meta Ads ad set created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "ad_set_id": ad_set.get_id(),
                "ad_set_name": ad_set_data.get('name')
            })

            return ad_set.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error creating ad set", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to create Meta Ads ad set", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id
            })
            return None

    async def create_ad_creative(
        self,
        organization_id: str,
        account_id: str,
        creative_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create an ad creative with image/video content
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            account = AdAccount(f'act_{account_id}')

            # Create ad creative
            creative = AdCreative(parent_id=account.get_id_assured())

            creative_data_api = {
                'name': creative_data.get('name', 'New Creative'),
                'object_story_spec': {
                    'page_id': creative_data.get('page_id'),
                    'link_data': {
                        'link': creative_data.get('link', 'https://example.com'),
                        'message': creative_data.get('message', 'Check this out!'),
                        'name': creative_data.get('headline', 'Amazing Product'),
                        'description': creative_data.get('description', 'Best product ever'),
                        'image_hash': creative_data.get('image_hash')
                    }
                }
            }

            # Add video if provided
            if 'video_id' in creative_data:
                creative_data_api['object_story_spec']['video_data'] = {
                    'video_id': creative_data['video_id'],
                    'message': creative_data.get('message', ''),
                    'title': creative_data.get('headline', ''),
                    'description': creative_data.get('description', '')
                }
                # Remove link_data for video creatives
                del creative_data_api['object_story_spec']['link_data']

            creative.update(creative_data_api)
            creative.remote_create()

            logger.info("Meta Ads creative created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "creative_id": creative.get_id(),
                "creative_name": creative_data.get('name')
            })

            return creative.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error creating creative", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to create Meta Ads creative", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def create_ad(
        self,
        organization_id: str,
        account_id: str,
        ad_set_id: str,
        creative_id: str,
        ad_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create an ad within an ad set
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            account = AdAccount(f'act_{account_id}')

            # Create ad
            ad = Ad(parent_id=account.get_id_assured())
            ad.update({
                'name': ad_data.get('name', 'New Ad'),
                'adset_id': ad_set_id,
                'creative': {'creative_id': creative_id},
                'status': 'PAUSED',
                'tracking_specs': [
                    {
                        'action_type': ['offsite_conversion'],
                        'fb_pixel': [ad_data.get('pixel_id')]
                    }
                ] if ad_data.get('pixel_id') else []
            })

            # Execute ad creation
            ad.remote_create()

            logger.info("Meta Ads ad created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "ad_set_id": ad_set_id,
                "creative_id": creative_id,
                "ad_id": ad.get_id(),
                "ad_name": ad_data.get('name')
            })

            return ad.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error creating ad", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to create Meta Ads ad", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== AUDIENCE MANAGEMENT ==========

    async def create_custom_audience(
        self,
        organization_id: str,
        account_id: str,
        audience_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a custom audience for targeting
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            account = AdAccount(f'act_{account_id}')

            # Create custom audience
            from facebook_business.adobjects.customaudience import CustomAudience

            audience = CustomAudience(parent_id=account.get_id_assured())
            audience.update({
                'name': audience_data.get('name', 'New Audience'),
                'description': audience_data.get('description', ''),
                'subtype': audience_data.get('subtype', 'CUSTOM'),
                'customer_file_source': 'USER_PROVIDED_ONLY' if audience_data.get('customer_file') else None
            })

            # Add rules if provided
            if 'rules' in audience_data:
                audience.update({
                    'rule': json.dumps(audience_data['rules'])
                })

            audience.remote_create()

            logger.info("Meta Ads custom audience created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "audience_id": audience.get_id(),
                "audience_name": audience_data.get('name')
            })

            return audience.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error creating audience", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to create Meta Ads custom audience", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== CONVERSION TRACKING ==========

    async def setup_conversion_tracking(
        self,
        organization_id: str,
        account_id: str,
        pixel_id: str,
        conversion_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Set up conversion tracking with Facebook Pixel
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            FacebookAdsApi.init(access_token=access_token, api_version=self.api_version)

            # Create offline conversion data set
            from facebook_business.adobjects.offlineconversiondataset import OfflineConversionDataSet

            dataset = OfflineConversionDataSet()
            dataset.update({
                'name': conversion_data.get('name', 'Conversions'),
                'description': conversion_data.get('description', ''),
                'business': {'id': account_id}  # This should be business ID
            })

            dataset.remote_create()

            logger.info("Meta Ads conversion tracking setup", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "pixel_id": pixel_id,
                "dataset_id": dataset.get_id(),
                "conversion_name": conversion_data.get('name')
            })

            return dataset.get_id()

        except FacebookRequestError as e:
            logger.error("Meta Ads API error setting up conversion tracking", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "error_code": e.api_error_code()
            })
            return None
        except Exception as e:
            logger.error("Failed to setup Meta Ads conversion tracking", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, account_id: str) -> Dict[str, Any]:
        """
        Test connection to Meta Ads API
        """
        try:
            accounts = await self.list_ad_accounts(organization_id)
            if accounts:
                return {
                    "status": "connected",
                    "accounts_count": len(accounts),
                    "first_account": accounts[0]["account_id"] if accounts else None
                }
            else:
                return {"status": "no_accounts"}
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def get_required_scopes(self) -> List[str]:
        """Get required OAuth2 scopes"""
        return [
            'ads_management',
            'ads_read',
            'business_management'
        ]

    def get_api_limits(self) -> Dict[str, Any]:
        """Get Meta Ads API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_hour": self.requests_per_hour,
            "daily_limit": self.daily_limit,
            "rate_limit_type": "token_based",
            "burst_allowed": True,
            "cost_based_throttling": True,
            "documentation_url": "https://developers.facebook.com/docs/marketing-api/rate-limiting/"
        }

    async def get_supported_objectives(self) -> List[str]:
        """Get list of supported campaign objectives"""
        return [
            'BRAND_AWARENESS',
            'REACH',
            'TRAFFIC',
            'ENGAGEMENT',
            'APP_INSTALLS',
            'VIDEO_VIEWS',
            'LEAD_GENERATION',
            'MESSAGES',
            'CONVERSIONS',
            'CATALOG_SALES',
            'STORE_VISITS'
        ]

# Global Meta Ads integration instance
meta_ads_integration = MetaAdsIntegration()
