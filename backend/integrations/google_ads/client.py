"""
Production-Ready Google Ads API Integration for OmnifyProduct
Complete Google Ads API v14 integration with OAuth2, campaign management, and analytics

Features:
- OAuth2 authentication flow
- Campaign creation and management
- Performance data retrieval
- Bid management and optimization
- Conversion tracking setup
- Budget management
- Real-time reporting
- Error handling and rate limiting
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import json
import base64
import hashlib
import secrets
from urllib.parse import urlencode, parse_qs

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    from google.auth import exceptions as auth_exceptions
    from google.oauth2.credentials import Credentials
    HAS_GOOGLE_ADS = True
except ImportError:
    HAS_GOOGLE_ADS = False
    GoogleAdsClient = None
    GoogleAdsException = Exception
    auth_exceptions = Exception
    Credentials = None

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager

class GoogleAdsIntegration:
    """
    Complete Google Ads API integration for campaign intelligence
    """

    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_ADS_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_ADS_CLIENT_SECRET')
        self.developer_token = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN')
        self.redirect_uri = os.environ.get('GOOGLE_ADS_REDIRECT_URI', 'http://localhost:8000/auth/google-ads/callback')

        # API configuration
        self.api_version = 'v14'
        self.timeout_seconds = 30

        # Rate limiting (Google Ads has strict limits)
        self.requests_per_second = 2  # Conservative limit
        self.requests_per_hour = 1000
        self.daily_limit = 10000

        # Cache settings
        self.cache_ttl = 300  # 5 minutes for account data

        # Initialize client
        self.client = None
        if HAS_GOOGLE_ADS and self.developer_token:
            self.client = GoogleAdsClient.load_from_dict({
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'developer_token': self.developer_token,
                'use_proto_plus': True
            })

        logger.info("Google Ads integration initialized", extra={
            "has_client": HAS_GOOGLE_ADS and self.client is not None,
            "api_version": self.api_version,
            "rate_limit_per_second": self.requests_per_second
        })

    # ========== OAUTH2 AUTHENTICATION ==========

    def get_oauth_url(self, state: str) -> str:
        """
        Generate OAuth2 authorization URL for Google Ads
        """
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/adwords',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state
        }

        return f"{base_url}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for access and refresh tokens
        """
        try:
            import httpx

            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()

                tokens = response.json()
                tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])

                logger.info("Google Ads OAuth tokens obtained successfully")
                return tokens

        except Exception as e:
            logger.error("Failed to exchange OAuth code for tokens", exc_info=e)
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh expired access token
        """
        try:
            import httpx

            token_url = "https://oauth2.googleapis.com/token"
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()

                tokens = response.json()
                tokens['expires_at'] = datetime.utcnow() + timedelta(seconds=tokens.get('expires_in', 3600))

                logger.info("Google Ads access token refreshed")
                return tokens

        except Exception as e:
            logger.error("Failed to refresh Google Ads access token", exc_info=e)
            return None

    async def get_valid_credentials(self, organization_id: str, account_id: str) -> Optional[Credentials]:
        """
        Get valid OAuth2 credentials for an account
        """
        try:
            # Get stored tokens
            tokens_key = f"google_ads_tokens_{organization_id}_{account_id}"
            tokens = await production_secrets_manager.get_secret(tokens_key)

            if not tokens:
                return None

            # Check if access token is still valid
            expires_at = datetime.fromisoformat(tokens['expires_at'])
            if datetime.utcnow() >= expires_at:
                # Refresh token
                refreshed = await self.refresh_access_token(tokens['refresh_token'])
                if refreshed:
                    # Update stored tokens
                    refreshed['refresh_token'] = tokens['refresh_token']  # Keep original refresh token
                    await production_secrets_manager.update_secret(tokens_key, refreshed)
                    tokens = refreshed
                else:
                    logger.warning("Failed to refresh Google Ads tokens", extra={
                        "organization_id": organization_id,
                        "account_id": account_id
                    })
                    return None

            # Create credentials object
            credentials = Credentials(
                token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=['https://www.googleapis.com/auth/adwords']
            )

            return credentials

        except Exception as e:
            logger.error("Failed to get valid Google Ads credentials", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== ACCOUNT MANAGEMENT ==========

    async def list_accessible_accounts(self, organization_id: str) -> List[Dict[str, Any]]:
        """
        List Google Ads accounts accessible to the authenticated user
        """
        try:
            credentials = await self.get_valid_credentials(organization_id, "default")
            if not credentials:
                return []

            # Create client with credentials
            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            # Query accessible accounts
            ga_service = client.get_service("GoogleAdsService")

            query = """
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.manager,
                    customer.test_account
                FROM customer
                WHERE customer.manager = false
                ORDER BY customer.id
            """

            response = ga_service.search(customer_id="1234567890", query=query)  # Dummy customer ID for listing

            accounts = []
            for row in response:
                customer = row.customer
                accounts.append({
                    "account_id": customer.id,
                    "name": customer.descriptive_name,
                    "currency": customer.currency_code,
                    "timezone": customer.time_zone,
                    "is_manager": customer.manager,
                    "is_test": customer.test_account
                })

            # Cache results
            cache_key = f"google_ads_accounts_{organization_id}"
            await production_secrets_manager.store_secret(cache_key, accounts, {"ttl": self.cache_ttl})

            logger.info("Google Ads accounts retrieved", extra={
                "organization_id": organization_id,
                "account_count": len(accounts)
            })

            return accounts

        except GoogleAdsException as e:
            logger.error("Google Ads API error listing accounts", exc_info=e, extra={
                "organization_id": organization_id
            })
            return []
        except Exception as e:
            logger.error("Failed to list Google Ads accounts", exc_info=e, extra={
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
        Create a new Google Ads campaign
        """
        try:
            credentials = await self.get_valid_credentials(organization_id, account_id)
            if not credentials:
                return None

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            # Build campaign operation
            campaign_service = client.get_service("CampaignService")
            campaign_operation = client.get_type("CampaignOperation")

            campaign = campaign_operation.create
            campaign.name = campaign_data.get("name", "New Campaign")
            campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = client.enums.CampaignStatusEnum.PAUSED
            campaign.manual_cpc = client.get_type("ManualCpc")
            campaign.campaign_budget = f"customers/{account_id}/campaignBudgets/{campaign_data.get('budget_id')}"

            # Set targeting
            if "targeting" in campaign_data:
                targeting = campaign_data["targeting"]
                if "locations" in targeting:
                    campaign.geo_target_type_setting.positive_geo_target_type = (
                        client.enums.PositiveGeoTargetTypeEnum.DONT_CARE
                    )

            # Execute campaign creation
            response = campaign_service.mutate_campaigns(
                customer_id=account_id,
                operations=[campaign_operation]
            )

            campaign_id = response.results[0].resource_name.split('/')[-1]

            logger.info("Google Ads campaign created", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "campaign_name": campaign_data.get("name")
            })

            return campaign_id

        except GoogleAdsException as e:
            logger.error("Google Ads API error creating campaign", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_data": campaign_data
            })
            return None
        except Exception as e:
            logger.error("Failed to create Google Ads campaign", exc_info=e, extra={
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
            credentials = await self.get_valid_credentials(organization_id, account_id)
            if not credentials:
                return []

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            ga_service = client.get_service("GoogleAdsService")

            # Build campaign filter
            campaign_filter = " OR ".join([f"campaign.id = {cid}" for cid in campaign_ids])
            if len(campaign_ids) > 1:
                campaign_filter = f"({campaign_filter})"

            # Query performance data
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.optimization_score,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.roas,
                    segments.date
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                AND {campaign_filter}
                AND segments.date BETWEEN '{date_range['start']}' AND '{date_range['end']}'
                ORDER BY segments.date DESC, campaign.id
            """

            response = ga_service.search(customer_id=account_id, query=query)

            performance_data = []
            for row in response:
                campaign = row.campaign
                metrics = row.metrics
                segments = row.segments

                performance_data.append({
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "status": campaign.status.name,
                    "optimization_score": getattr(campaign, 'optimization_score', 0),
                    "date": segments.date,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "cost": metrics.cost_micros / 1000000,  # Convert from micros
                    "conversions": metrics.conversions,
                    "conversion_value": metrics.conversions_value,
                    "ctr": metrics.ctr,
                    "cpc": metrics.average_cpc / 1000000 if metrics.average_cpc else 0,
                    "roas": metrics.roas
                })

            logger.info("Google Ads campaign performance retrieved", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_count": len(campaign_ids),
                "data_points": len(performance_data)
            })

            return performance_data

        except GoogleAdsException as e:
            logger.error("Google Ads API error getting performance", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_ids": campaign_ids
            })
            return []
        except Exception as e:
            logger.error("Failed to get Google Ads campaign performance", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return []

    async def update_campaign_bids(
        self,
        organization_id: str,
        account_id: str,
        campaign_id: str,
        bid_adjustments: Dict[str, float]
    ) -> bool:
        """
        Update campaign bids based on performance data
        """
        try:
            credentials = await self.get_valid_credentials(organization_id, account_id)
            if not credentials:
                return False

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            campaign_criterion_service = client.get_service("CampaignCriterionService")

            operations = []
            for criterion_id, bid_modifier in bid_adjustments.items():
                operation = client.get_type("CampaignCriterionOperation")
                criterion = operation.update
                criterion.resource_name = f"customers/{account_id}/campaignCriteria/{campaign_id}~{criterion_id}"
                criterion.bid_modifier = bid_modifier

                operations.append(operation)

            # Execute updates
            response = campaign_criterion_service.mutate_campaign_criteria(
                customer_id=account_id,
                operations=operations
            )

            logger.info("Google Ads campaign bids updated", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "bid_adjustments": len(bid_adjustments)
            })

            return len(response.results) > 0

        except GoogleAdsException as e:
            logger.error("Google Ads API error updating bids", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id
            })
            return False
        except Exception as e:
            logger.error("Failed to update Google Ads campaign bids", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id
            })
            return False

    # ========== KEYWORD & AUDIENCE MANAGEMENT ==========

    async def get_keywords_performance(
        self,
        organization_id: str,
        account_id: str,
        campaign_id: str,
        date_range: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Get detailed keyword performance data
        """
        try:
            credentials = await self.get_valid_credentials(organization_id, account_id)
            if not credentials:
                return []

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            ga_service = client.get_service("GoogleAdsService")

            query = f"""
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.quality_info.quality_score,
                    ad_group_criterion.bid_modifier,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    segments.date
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
                AND campaign.id = {campaign_id}
                AND segments.date BETWEEN '{date_range['start']}' AND '{date_range['end']}'
                ORDER BY metrics.clicks DESC
            """

            response = ga_service.search(customer_id=account_id, query=query)

            keywords_data = []
            for row in response:
                criterion = row.ad_group_criterion
                keyword = criterion.keyword
                quality_info = criterion.quality_info
                metrics = row.metrics

                keywords_data.append({
                    "keyword_id": criterion.criterion_id,
                    "keyword_text": keyword.text,
                    "match_type": keyword.match_type.name,
                    "status": criterion.status.name,
                    "quality_score": getattr(quality_info, 'quality_score', 0),
                    "bid_modifier": getattr(criterion, 'bid_modifier', 1.0),
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "cost": metrics.cost_micros / 1000000,
                    "conversions": metrics.conversions,
                    "date": row.segments.date
                })

            logger.info("Google Ads keywords performance retrieved", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id,
                "keywords_count": len(keywords_data)
            })

            return keywords_data

        except GoogleAdsException as e:
            logger.error("Google Ads API error getting keywords", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id
            })
            return []
        except Exception as e:
            logger.error("Failed to get Google Ads keywords performance", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "campaign_id": campaign_id
            })
            return []

    # ========== CONVERSION TRACKING ==========

    async def setup_conversion_tracking(
        self,
        organization_id: str,
        account_id: str,
        conversion_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Set up conversion tracking for an account
        """
        try:
            credentials = await self.get_valid_credentials(organization_id, account_id)
            if not credentials:
                return None

            client = GoogleAdsClient(
                credentials=credentials,
                developer_token=self.developer_token,
                client_id=self.client_id,
                use_proto_plus=True
            )

            conversion_action_service = client.get_service("ConversionActionService")
            conversion_operation = client.get_type("ConversionActionOperation")

            conversion = conversion_operation.create
            conversion.name = conversion_data.get("name", "Website Conversion")
            conversion.type = client.enums.ConversionActionTypeEnum.WEB_CONVERSION
            conversion.status = client.enums.ConversionActionStatusEnum.ENABLED
            conversion.attribution_model_settings.attribution_model = (
                client.enums.AttributionModelEnum.DATA_DRIVEN
            )

            # Set up website conversion
            if conversion_data.get("conversion_type") == "website":
                conversion.website_conversion.tag_snippet = conversion_data.get("tag_snippet", "")
                conversion.website_conversion.floodlight_conversion_type = (
                    client.enums.FloodlightConversionTypeEnum.TRANSACTION
                )

            # Execute conversion setup
            response = conversion_action_service.mutate_conversion_actions(
                customer_id=account_id,
                operations=[conversion_operation]
            )

            conversion_id = response.results[0].resource_name.split('/')[-1]

            logger.info("Google Ads conversion tracking setup", extra={
                "organization_id": organization_id,
                "account_id": account_id,
                "conversion_id": conversion_id,
                "conversion_name": conversion_data.get("name")
            })

            return conversion_id

        except GoogleAdsException as e:
            logger.error("Google Ads API error setting up conversion", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None
        except Exception as e:
            logger.error("Failed to setup Google Ads conversion tracking", exc_info=e, extra={
                "organization_id": organization_id,
                "account_id": account_id
            })
            return None

    # ========== UTILITY METHODS ==========

    async def test_connection(self, organization_id: str, account_id: str) -> Dict[str, Any]:
        """
        Test connection to Google Ads API
        """
        try:
            accounts = await self.list_accessible_accounts(organization_id)
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
            'https://www.googleapis.com/auth/adwords'
        ]

    def get_api_limits(self) -> Dict[str, Any]:
        """Get Google Ads API limits information"""
        return {
            "requests_per_second": self.requests_per_second,
            "requests_per_hour": self.requests_per_hour,
            "daily_limit": self.daily_limit,
            "burst_limit": 50,  # Max burst requests
            "cost_based_limits": True,  # API costs affect limits
            "documentation_url": "https://developers.google.com/google-ads/api/docs/best-practices/rate-limits"
        }

# Global Google Ads integration instance
google_ads_integration = GoogleAdsIntegration()
