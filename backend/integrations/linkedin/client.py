"""
Production-Ready LinkedIn Ads API Integration for OmnifyProduct
Complete LinkedIn Marketing API integration with campaign management and analytics

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
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    httpx = None

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

class LinkedInAdsIntegration:
    """
    Complete LinkedIn Ads API integration for B2B campaigns
    """

    def __init__(self):
        self.client_id = os.environ.get('LINKEDIN_CLIENT_ID')
        self.client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('LINKEDIN_REDIRECT_URI', 'http://localhost:8000/auth/linkedin/callback')

        # API configuration
        self.base_url = 'https://api.linkedin.com'
        self.api_version = 'v2'
        self.timeout_seconds = 30

        # Rate limiting (LinkedIn has strict limits)
        self.requests_per_second = 2  # Conservative limit
        self.requests_per_hour = 1000
        self.daily_limit = 10000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes

        # HTTP client
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout_seconds
            )

        logger.info("LinkedIn Ads integration initialized", extra={
            "has_client": HAS_HTTPX and self.client is not None,
            "base_url": self.base_url,
            "rate_limit_per_second": self.requests_per_second
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for LinkedIn
        """
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'scope': 'r_ads r_ads_reporting r_organization_social'
        }

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access tokens
        """
        try:
            if not self.client:
                return None

            token_url = "/oauth/v2/accessToken"
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

            # Get user info
            access_token = tokens['access_token']
            user_info = await self._get_user_info(access_token)

            tokens.update({
                'user_id': user_info.get('id'),
                'user_name': user_info.get('firstName', '') + ' ' + user_info.get('lastName', '')
            })

            logger.info("LinkedIn OAuth tokens obtained successfully", extra={
                "user_id": user_info.get('id')
            })

            return tokens

        except Exception as e:
            logger.error("Failed to exchange LinkedIn OAuth code for tokens", exc_info=e)
            return None

    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from access token"""
        try:
            if not self.client:
                return {}

            headers = {'Authorization': f'Bearer {access_token}'}
            response = await self.client.get('/v2/people/~', headers=headers)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.warning("Failed to get LinkedIn user info", exc_info=e)
            return {}

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh expired access token
        """
        try:
            if not self.client:
                return None

            token_url = "/oauth/v2/accessToken"
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = await self.client.post(token_url, data=data)
            response.raise_for_status()

            tokens = response.json()
            tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

            logger.info("LinkedIn access token refreshed")
            return tokens

        except Exception as e:
            logger.error("Failed to refresh LinkedIn access token", exc_info=e)
            return None

    async def get_valid_access_token(self, organization_id: str, account_id: str) -> Optional[str]:
        """
        Get valid access token for LinkedIn account
        """
        try:
            # Get stored tokens
            tokens_key = f"linkedin_tokens_{organization_id}_{account_id}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Check if token is still valid (with buffer)
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            buffer_time = timedelta(minutes=5)  # Refresh 5 minutes before expiry

            if datetime.utcnow() >= (expires_at - buffer_time):
                # Refresh token
                refreshed = await self.refresh_access_token(tokens['refresh_token'])
                if refreshed:
                    refreshed['refresh_token'] = tokens['refresh_token']  # Keep original refresh token
                    await production_secrets_manager.update_secret(tokens_key, refreshed)
                    tokens = refreshed
                else:
                    logger.warning("Failed to refresh LinkedIn tokens", extra={
                        "organization_id": organization_id,
                        "account_id": account_id
                    })
                    return None

            return tokens['access_token']

        except Exception as e:
            logger.error("Failed to get valid LinkedIn access token", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== ACCOUNT MANAGEMENT ==========

    async def list_ad_accounts(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List accessible LinkedIn ad accounts
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, "default")
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            # Get ad accounts
            response = await self.client.get('/v2/adAccountsV2', headers=headers)
            response.raise_for_status()

            accounts_data = response.json()
            accounts = accounts_data.get('elements', [])

            ad_accounts = []
            for account in accounts:
                ad_accounts.append({
                    "account_id": account.get('id'),
                    "name": account.get('name'),
                    "currency": account.get('currency'),
                    "timezone": account.get('timezone'),
                    "status": account.get('status'),
                    "type": account.get('type'),
                    "reference": account.get('reference')
                })

            # Cache results
            cache_key = f"linkedin_ad_accounts_{organization_id}"
            await production_secrets_manager.store_secret(cache_key, ad_accounts, {"ttl": self.cache_ttl})

            logger.info("LinkedIn ad accounts retrieved", extra={
                "organization_id": organization_id,
                "account_count": len(ad_accounts)
            })

            return ad_accounts

        except Exception as e:
            logger.error("Failed to list LinkedIn ad accounts", exc_info=e, extra={
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
        Create a new LinkedIn Ads campaign
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format campaign data for LinkedIn API
            campaign_payload = {
                'account': f"urn:li:sponsoredAccount:{account_id}",
                'name': campaign_data.get('name', 'New Campaign'),
                'type': campaign_data.get('type', 'TEXT_AD'),
                'status': campaign_data.get('status', 'PAUSED'),
                'costType': campaign_data.get('cost_type', 'CPC'),
                'dailyBudget': {
                    'amount': campaign_data.get('daily_budget', 100),
                    'currencyCode': campaign_data.get('currency', 'USD')
                },
                'targetingCriteria': campaign_data.get('targeting', {}),
                'objective': campaign_data.get('objective', 'WEBSITE_TRAFFIC')
            }

            response = await self.client.post(
                '/v2/adCampaignsV2',
                headers=headers,
                json=campaign_payload
            )
            response.raise_for_status()

            campaign_result = response.json()
            campaign_id = campaign_result.get('id')

            logger.info("LinkedIn campaign created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "campaign_name": campaign_data.get('name')
            })

            return campaign_id

        except Exception as e:
            logger.error("Failed to create LinkedIn campaign", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    async def get_campaign_performance(
        self,
        organization_id: str,
        account_id: str,
        campaign_ids: List[str],
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Get detailed campaign performance data
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return []

            headers = {'Authorization': f'Bearer {access_token}'}

            # Build campaign filter
            campaign_filter = " OR ".join([f"campaign=={cid}" for cid in campaign_ids])
            if len(campaign_ids) > 1:
                campaign_filter = f"({campaign_filter})"

            # Query performance data
            params = {
                'q': 'analytics',
                'pivot': 'CAMPAIGN',
                'dateRange.start.day': date_range['start'].split('-')[2],
                'dateRange.start.month': date_range['start'].split('-')[1],
                'dateRange.start.year': date_range['start'].split('-')[0],
                'dateRange.end.day': date_range['end'].split('-')[2],
                'dateRange.end.month': date_range['end'].split('-')[1],
                'dateRange.end.year': date_range['end'].split('-')[0],
                'timeGranularity': 'DAILY',
                'fields': 'impressions,clicks,costInLocalCurrency,conversions,externalWebsiteConversions',
                'campaigns[0]': campaign_filter
            }

            response = await self.client.get(
                f'/v2/adAnalyticsV2',
                headers=headers,
                params=params
            )
            response.raise_for_status()

            analytics_data = response.json()
            performance_data = []

            for element in analytics_data.get('elements', []):
                performance_data.append({
                    "campaign_id": element.get('campaign'),
                    "date": element.get('dateRange', {}).get('start'),
                    "impressions": element.get('impressions', 0),
                    "clicks": element.get('clicks', 0),
                    "cost": element.get('costInLocalCurrency', 0),
                    "conversions": element.get('conversions', 0),
                    "external_conversions": element.get('externalWebsiteConversions', 0),
                    "ctr": element.get('clicks', 0) / max(element.get('impressions', 1), 1),
                    "cpc": element.get('costInLocalCurrency', 0) / max(element.get('clicks', 1), 1)
                })

            logger.info("LinkedIn campaign performance retrieved", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_count": len(campaign_ids),
                "data_points": len(performance_data)
            })

            return performance_data

        except Exception as e:
            logger.error("Failed to get LinkedIn campaign performance", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return []

    # ========== CREATIVE MANAGEMENT ==========

    async def create_ad_creative(
        self,
        organization_id: str,
        account_id: str,
        creative_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create an ad creative
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format creative data for LinkedIn API
            creative_payload = {
                'account': f"urn:li:sponsoredAccount:{account_id}",
                'name': creative_data.get('name', 'New Creative'),
                'type': creative_data.get('type', 'TEXT_AD'),
                'status': creative_data.get('status', 'ACTIVE'),
                'text': creative_data.get('text', ''),
                'title': creative_data.get('title', ''),
                'landingPageUrl': creative_data.get('landing_page_url', ''),
                'callToAction': creative_data.get('call_to_action', 'LEARN_MORE')
            }

            # Add image if provided
            if 'image_url' in creative_data:
                creative_payload['image'] = {
                    'url': creative_data['image_url']
                }

            response = await self.client.post(
                '/v2/adCreativesV2',
                headers=headers,
                json=creative_payload
            )
            response.raise_for_status()

            creative_result = response.json()
            creative_id = creative_result.get('id')

            logger.info("LinkedIn creative created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "creative_id": creative_id,
                "creative_name": creative_data.get('name')
            })

            return creative_id

        except Exception as e:
            logger.error("Failed to create LinkedIn creative", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== AUDIENCE MANAGEMENT ==========

    async def create_audience(
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

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format audience data for LinkedIn API
            audience_payload = {
                'account': f"urn:li:sponsoredAccount:{account_id}",
                'name': audience_data.get('name', 'New Audience'),
                'audienceType': audience_data.get('type', 'CUSTOM'),
                'audienceDefinition': audience_data.get('definition', {}),
                'state': audience_data.get('state', 'ACTIVE')
            }

            response = await self.client.post(
                '/v2/adAudiencesV2',
                headers=headers,
                json=audience_payload
            )
            response.raise_for_status()

            audience_result = response.json()
            audience_id = audience_result.get('id')

            logger.info("LinkedIn audience created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "audience_id": audience_id,
                "audience_name": audience_data.get('name')
            })

            return audience_id

        except Exception as e:
            logger.error("Failed to create LinkedIn audience", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== CONVERSION TRACKING ==========

    async def setup_conversion_tracking(
        self,
        organization_id: str,
        account_id: str,
        conversion_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Set up conversion tracking
        """
        try:
            access_token = await self.get_valid_access_token(organization_id, account_id)
            if not access_token:
                return None

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            # Format conversion data for LinkedIn API
            conversion_payload = {
                'account': f"urn:li:sponsoredAccount:{account_id}",
                'name': conversion_data.get('name', 'Website Conversion'),
                'type': conversion_data.get('type', 'WEBSITE_CONVERSION'),
                'postClickAttributionWindowSize': conversion_data.get('attribution_window', 30),
                'viewThroughAttributionWindowSize': conversion_data.get('view_attribution_window', 1),
                'conversionMethod': conversion_data.get('method', 'WEBSITE_PIXEL')
            }

            response = await self.client.post(
                '/v2/adConversionEventsV2',
                headers=headers,
                json=conversion_payload
            )
            response.raise_for_status()

            conversion_result = response.json()
            conversion_id = conversion_result.get('id')

            logger.info("LinkedIn conversion tracking setup", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "conversion_id": conversion_id,
                "conversion_name": conversion_data.get('name')
            })

            return conversion_id

        except Exception as e:
            logger.error("Failed to setup LinkedIn conversion tracking", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, account_id: str) -> Dict[str, Any]:
        """
        Test connection to LinkedIn Ads API
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
            'r_ads',
            'r_ads_reporting',
            'r_organization_social'
        ]

    def get_api_limits(self) -> Dict[str, Any]:
        """Get LinkedIn Ads API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_hour": self.requests_per_hour,
            "daily_limit": self.daily_limit,
            "rate_limit_type": "token_based",
            "burst_allowed": False,
            "cost_based_throttling": True,
            "documentation_url": "https://docs.microsoft.com/en-us/linkedin/marketing/"
        }

    async def get_supported_objectives(self) -> List[str]:
        """Get list of supported campaign objectives"""
        return [
            'WEBSITE_TRAFFIC',
            'WEBSITE_CONVERSIONS',
            'LEAD_GENERATION',
            'BRAND_AWARENESS',
            'VIDEO_VIEWS',
            'ENGAGEMENT',
            'JOB_APPLICANTS',
            'JOB_APPLICATIONS'
        ]

# Global LinkedIn Ads integration instance
linkedin_ads_integration = LinkedInAdsIntegration()
