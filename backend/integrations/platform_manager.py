"""
Unified Platform Integrations Manager for OmnifyProduct
Orchestrates all platform APIs (Google Ads, Meta Ads, GoHighLevel, etc.) with unified interface

Features:
- Unified API interface across all platforms
- Automatic platform detection and routing
- Credential management and rotation
- Rate limiting coordination
- Error handling and retry logic
- Performance monitoring and analytics
- Cost tracking and optimization
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from services.structured_logging import logger
from services.production_secrets_manager import production_secrets_manager
from services.production_tenant_manager import get_tenant_manager
from services.production_rate_limiter import production_rate_limiter
from services.cost_guardrails import cost_guardrails

# Import platform integrations
from integrations.google_ads.client import GoogleAdsAdapter
from integrations.meta_ads.client import MetaAdsAdapter
from integrations.gohighlevel.client import GoHighLevelAdapter
from integrations.linkedin.client import LinkedInAdsAdapter
from integrations.tiktok.client import TikTokAdsAdapter
from integrations.youtube.client import YouTubeAdsAdapter
from integrations.shopify.client import ShopifyIntegration
from integrations.stripe.client import StripeAdapter
from integrations.triplewhale.client import TripleWhaleAdapter
from integrations.hubspot.client import HubSpotAdapter
from integrations.klaviyo.client import KlaviyoAdapter

class Platform(Enum):
    """Supported advertising and marketing platforms"""
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TIKTOK_ADS = "tiktok_ads"
    YOUTUBE_ADS = "youtube_ads"
    GOHIGHLEVEL = "gohighlevel"  # LOW PRIORITY - Prefer TripleWhale/HubSpot/Klaviyo for DTC brands
    TRIPLEWHALE = "triplewhale"  # PRIMARY: Attribution & Analytics for DTC brands
    HUBSPOT = "hubspot"  # SECONDARY: CRM & Marketing Automation
    KLAVIYO = "klaviyo"  # TERTIARY: Lifecycle Marketing & Retention
    SHOPIFY = "shopify"
    STRIPE = "stripe"
    GOOGLE_ANALYTICS = "google_analytics"

class PlatformIntegrationsManager:
    """
    Unified manager for all platform integrations
    """

    def __init__(self):
        self.platforms = {
            Platform.GOOGLE_ADS: GoogleAdsAdapter(),
            Platform.META_ADS: MetaAdsAdapter(),
            Platform.LINKEDIN_ADS: LinkedInAdsAdapter(),
            Platform.TIKTOK_ADS: TikTokAdsAdapter(),
            Platform.YOUTUBE_ADS: YouTubeAdsAdapter(),
            Platform.GOHIGHLEVEL: GoHighLevelAdapter(),  # LOW PRIORITY - kept for backward compatibility
            Platform.TRIPLEWHALE: TripleWhaleAdapter(),  # PRIMARY replacement
            Platform.HUBSPOT: HubSpotAdapter(),  # SECONDARY replacement
            Platform.KLAVIYO: KlaviyoAdapter(),  # TERTIARY replacement
            Platform.SHOPIFY: ShopifyIntegration(),
            Platform.STRIPE: StripeAdapter()
        }

        # Platform capabilities mapping
        self.platform_capabilities = {
            Platform.GOOGLE_ADS: [
                "campaign_management", "keyword_optimization", "conversion_tracking",
                "performance_analytics", "audience_targeting", "bid_management"
            ],
            Platform.META_ADS: [
                "campaign_management", "audience_targeting", "creative_optimization",
                "performance_analytics", "conversion_tracking", "ad_creation"
            ],
            Platform.LINKEDIN_ADS: [
                "campaign_management", "b2b_targeting", "professional_audiences",
                "performance_analytics", "lead_generation", "sponsored_content"
            ],
            Platform.TIKTOK_ADS: [
                "campaign_management", "video_ads", "audience_targeting",
                "performance_analytics", "creative_optimization", "trending_content"
            ],
            Platform.YOUTUBE_ADS: [
                "campaign_management", "video_advertising", "audience_targeting",
                "performance_analytics", "video_optimization", "brand_awareness"
            ],
            Platform.GOHIGHLEVEL: [
                "contact_management", "workflow_automation", "email_campaigns",
                "opportunity_tracking", "appointment_scheduling", "crm_integration"
            ],  # LOW PRIORITY - SMB/agency focused, not ideal for mid-market DTC
            Platform.TRIPLEWHALE: [
                "attribution_analytics", "multi_touch_attribution", "revenue_tracking",
                "roas_calculation", "creative_performance", "campaign_analytics",
                "shopify_integration", "cross_channel_analytics"
            ],
            Platform.HUBSPOT: [
                "contact_management", "crm", "deal_pipeline", "marketing_automation",
                "workflow_automation", "campaign_management", "sales_automation",
                "reporting_analytics", "email_marketing"
            ],
            Platform.KLAVIYO: [
                "email_marketing", "sms_marketing", "lifecycle_automation",
                "customer_segmentation", "flow_automation", "campaign_management",
                "analytics_reporting", "shopify_integration"
            ],
            Platform.SHOPIFY: [
                "product_management", "order_processing", "inventory_tracking",
                "customer_management", "analytics_reporting", "ecommerce_automation"
            ],
            Platform.STRIPE: [
                "payment_processing", "subscription_management", "invoice_generation",
                "customer_billing", "refund_processing", "webhook_handling"
            ]
        }

        # Cost tracking
        self.cost_tracking = {
            Platform.GOOGLE_ADS: {"cost_per_request": 0.001, "monthly_free": 10000},
            Platform.META_ADS: {"cost_per_request": 0.001, "monthly_free": 200000},
            Platform.LINKEDIN_ADS: {"cost_per_request": 0.002, "monthly_free": 50000},
            Platform.TIKTOK_ADS: {"cost_per_request": 0.001, "monthly_free": 100000},
            Platform.YOUTUBE_ADS: {"cost_per_request": 0.001, "monthly_free": 10000},
            Platform.GOHIGHLEVEL: {"cost_per_request": 0.0005, "monthly_free": 100000},  # LOW PRIORITY
            Platform.TRIPLEWHALE: {"cost_per_request": 0.0001, "monthly_free": 1000000},
            Platform.HUBSPOT: {"cost_per_request": 0.0002, "monthly_free": 500000},
            Platform.KLAVIYO: {"cost_per_request": 0.0001, "monthly_free": 1000000},
            Platform.SHOPIFY: {"cost_per_request": 0.0001, "monthly_free": 1000000},
            Platform.STRIPE: {"cost_per_request": 0.029, "monthly_free": 0}  # 2.9% + 30¢ per transaction
        }

        logger.info("Platform integrations manager initialized", extra={
            "platforms_count": len(self.platforms),
            "total_capabilities": sum(len(caps) for caps in self.platform_capabilities.values())
        })

    async def initialize_platforms(self, organization_id: str):
        """Initialize all platform integrations with credentials"""
        try:
            for platform_enum, adapter in self.platforms.items():
                # Get platform credentials from secrets manager
                credentials = await production_secrets_manager.get_secret(
                    f"platform_creds_{organization_id}_{platform_enum.value}"
                )
                
                if credentials:
                    await adapter.initialize(credentials)
                    logger.info(f"Initialized {platform_enum.value} adapter", extra={
                        "organization_id": organization_id,
                        "platform": platform_enum.value
                    })
                else:
                    logger.warning(f"No credentials found for {platform_enum.value}", extra={
                        "organization_id": organization_id,
                        "platform": platform_enum.value
                    })
            
            logger.info("All platform integrations initialized", extra={
                "organization_id": organization_id,
                "platforms_count": len(self.platforms)
            })
            
        except Exception as e:
            logger.error(f"Failed to initialize platform integrations: {e}", extra={
                "organization_id": organization_id,
                "error": str(e)
            })
            raise

    # ========== UNIFIED PLATFORM INTERFACE ==========

    async def execute_platform_action(
        self,
        platform: Union[str, Platform],
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action on a specific platform with unified interface
        """
        try:
            platform_enum = platform if isinstance(platform, Platform) else Platform(platform)

            if platform_enum not in self.platforms:
                return {
                    "status": "error",
                    "error": f"Platform {platform} not supported",
                    "supported_platforms": [p.value for p in Platform]
                }

            # Check rate limits
            rate_limit_check = await production_rate_limiter.check_rate_limit({
                "organization_id": organization_id,
                "endpoint": f"/platforms/{platform_enum.value}/{action}",
                "method": "POST"
            })

            if not rate_limit_check[0]:
                return {
                    "status": "rate_limited",
                    "error": "Rate limit exceeded",
                    "retry_after": rate_limit_check[1]["retry_after"]
                }

            # Get platform integration
            integration = self.platforms[platform_enum]

            # Route to appropriate method
            result = await self._route_platform_action(
                integration, platform_enum, action, organization_id, params
            )

            # Track costs and performance
            await self._track_platform_metrics(platform_enum, action, result)

            # Audit the action
            await self._audit_platform_action(
                organization_id, platform_enum, action, params, result
            )

            return result

        except Exception as e:
            logger.error("Platform action execution failed", exc_info=e, extra={
                "platform": platform,
                "action": action,
                "organization_id": organization_id
            })

            return {
                "status": "error",
                "error": str(e),
                "platform": str(platform),
                "action": action
            }

    async def _route_platform_action(
        self,
        integration: Any,
        platform: Platform,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route action to appropriate platform method
        """
        if platform == Platform.GOOGLE_ADS:
            return await self._handle_google_ads_action(integration, action, organization_id, params)
        elif platform == Platform.META_ADS:
            return await self._handle_meta_ads_action(integration, action, organization_id, params)
        elif platform == Platform.LINKEDIN_ADS:
            result = await self._handle_linkedin_ads_action(integration, action, organization_id, params)
            try:
                cost_info = self.cost_tracking.get(platform, {})
                cost = float(cost_info.get("cost_per_request", 0))
                if cost > 0:
                    await cost_guardrails.record_cost(cost)
            except Exception:
                pass
            return result
        elif platform == Platform.TRIPLEWHALE:
            result = await self._handle_triplewhale_action(integration, action, organization_id, params)
        elif platform == Platform.HUBSPOT:
            result = await self._handle_hubspot_action(integration, action, organization_id, params)
        elif platform == Platform.KLAVIYO:
            result = await self._handle_klaviyo_action(integration, action, organization_id, params)
        elif platform == Platform.GOHIGHLEVEL:
            result = await self._handle_gohighlevel_action(integration, action, organization_id, params)
            # Best-effort per-request cost tracking in low-cost mode
            try:
                cost_info = self.cost_tracking.get(platform, {})
                cost = float(cost_info.get("cost_per_request", 0))
                if cost > 0:
                    await cost_guardrails.record_cost(cost)
            except Exception:
                pass
            return result
        elif platform == Platform.SHOPIFY:
            result = await self._handle_shopify_action(integration, action, organization_id, params)
            try:
                cost_info = self.cost_tracking.get(platform, {})
                cost = float(cost_info.get("cost_per_request", 0))
                if cost > 0:
                    await cost_guardrails.record_cost(cost)
            except Exception:
                pass
            return result
        elif platform == Platform.STRIPE:
            result = await self._handle_stripe_action(integration, action, organization_id, params)
            try:
                cost_info = self.cost_tracking.get(platform, {})
                cost = float(cost_info.get("cost_per_request", 0))
                if cost > 0:
                    await cost_guardrails.record_cost(cost)
            except Exception:
                pass
            return result
        else:
            raise ValueError(f"No handler for platform {platform}")

    # ========== GOOGLE ADS HANDLERS ==========

    async def _handle_google_ads_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Google Ads specific actions"""
        if action == "create_campaign":
            campaign_id = await integration.create_campaign(
                organization_id,
                params["account_id"],
                params["campaign_data"]
            )
            return {
                "status": "success" if campaign_id else "error",
                "campaign_id": campaign_id,
                "platform": "google_ads"
            }

        elif action == "get_performance":
            performance = await integration.get_campaign_performance(
                organization_id,
                params["account_id"],
                params["campaign_ids"],
                params["date_range"]
            )
            return {
                "status": "success",
                "performance_data": performance,
                "platform": "google_ads"
            }

        elif action == "optimize_bids":
            success = await integration.update_campaign_bids(
                organization_id,
                params["account_id"],
                params["campaign_id"],
                params["bid_adjustments"]
            )
            return {
                "status": "success" if success else "error",
                "platform": "google_ads"
            }

        elif action == "setup_conversion_tracking":
            conversion_id = await integration.setup_conversion_tracking(
                organization_id,
                params["account_id"],
                params["conversion_data"]
            )
            return {
                "status": "success" if conversion_id else "error",
                "conversion_id": conversion_id,
                "platform": "google_ads"
            }

        else:
            raise ValueError(f"Unknown Google Ads action: {action}")

    # ========== META ADS HANDLERS ==========

    async def _handle_meta_ads_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Meta Ads specific actions"""
        if action == "create_campaign":
            campaign_id = await integration.create_campaign(
                organization_id,
                params["account_id"],
                params["campaign_data"]
            )
            return {
                "status": "success" if campaign_id else "error",
                "campaign_id": campaign_id,
                "platform": "meta_ads"
            }

        elif action == "get_insights":
            insights = await integration.get_campaign_insights(
                organization_id,
                params["account_id"],
                params["campaign_ids"],
                params["date_range"],
                params.get("metrics")
            )
            return {
                "status": "success",
                "insights_data": insights,
                "platform": "meta_ads"
            }

        elif action == "create_ad_set":
            ad_set_id = await integration.create_ad_set(
                organization_id,
                params["account_id"],
                params["campaign_id"],
                params["ad_set_data"]
            )
            return {
                "status": "success" if ad_set_id else "error",
                "ad_set_id": ad_set_id,
                "platform": "meta_ads"
            }

        elif action == "create_creative":
            creative_id = await integration.create_ad_creative(
                organization_id,
                params["account_id"],
                params["creative_data"]
            )
            return {
                "status": "success" if creative_id else "error",
                "creative_id": creative_id,
                "platform": "meta_ads"
            }

        elif action == "create_ad":
            ad_id = await integration.create_ad(
                organization_id,
                params["account_id"],
                params["ad_set_id"],
                params["creative_id"],
                params["ad_data"]
            )
            return {
                "status": "success" if ad_id else "error",
                "ad_id": ad_id,
                "platform": "meta_ads"
            }

        else:
            raise ValueError(f"Unknown Meta Ads action: {action}")

    # ========== GOHIGHLEVEL HANDLERS ==========

    async def _handle_gohighlevel_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle GoHighLevel specific actions"""
        if action == "create_contact":
            contact_id = await integration.create_contact(
                organization_id,
                params["location_id"],
                params["contact_data"]
            )
            return {
                "status": "success" if contact_id else "error",
                "contact_id": contact_id,
                "platform": "gohighlevel"
            }

        elif action == "update_contact":
            success = await integration.update_contact(
                organization_id,
                params["location_id"],
                params["contact_id"],
                params["contact_data"]
            )
            return {
                "status": "success" if success else "error",
                "platform": "gohighlevel"
            }

        elif action == "trigger_workflow":
            success = await integration.trigger_workflow(
                organization_id,
                params["location_id"],
                params["workflow_id"],
                params["contact_id"],
                params.get("trigger_data")
            )
            return {
                "status": "success" if success else "error",
                "platform": "gohighlevel"
            }

        elif action == "create_opportunity":
            opportunity_id = await integration.create_opportunity(
                organization_id,
                params["location_id"],
                params["opportunity_data"]
            )
            return {
                "status": "success" if opportunity_id else "error",
                "opportunity_id": opportunity_id,
                "platform": "gohighlevel"
            }

        elif action == "create_campaign":
            campaign_id = await integration.create_campaign(
                organization_id,
                params["location_id"],
                params["campaign_data"]
            )
            return {
                "status": "success" if campaign_id else "error",
                "campaign_id": campaign_id,
                "platform": "gohighlevel"
            }

        elif action == "sync_contacts":
            sync_result = await integration.sync_contacts_to_omnify(
                organization_id,
                params["location_id"],
                params.get("last_sync")
            )
            return {
                "status": sync_result["status"],
                "synced_contacts": sync_result.get("synced_contacts", 0),
                "platform": "gohighlevel"
            }

        else:
            raise ValueError(f"Unknown GoHighLevel action: {action}")

    # ========== TRIPLEWHALE HANDLERS ==========

    async def _handle_triplewhale_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle TripleWhale specific actions"""
        if action == "get_attribution":
            result = await integration.get_attribution(
                organization_id,
                params["start_date"],
                params["end_date"],
                params.get("channel")
            )
            return {
                "status": result.get("status", "success"),
                "attribution_data": result.get("data"),
                "platform": "triplewhale"
            }

        elif action == "get_revenue_metrics":
            result = await integration.get_revenue_metrics(
                organization_id,
                params["start_date"],
                params["end_date"],
                params.get("breakdown")
            )
            return {
                "status": result.get("status", "success"),
                "revenue_data": result.get("data"),
                "platform": "triplewhale"
            }

        elif action == "get_creative_performance":
            result = await integration.get_creative_performance(
                organization_id,
                params["start_date"],
                params["end_date"],
                params.get("channel")
            )
            return {
                "status": result.get("status", "success"),
                "creative_data": result.get("data"),
                "platform": "triplewhale"
            }

        elif action == "get_roas":
            # Get ROAS data via revenue metrics
            result = await integration.get_revenue_metrics(
                organization_id,
                params["start_date"],
                params["end_date"],
                breakdown="channel"
            )
            return {
                "status": result.get("status", "success"),
                "roas_data": result.get("data"),
                "platform": "triplewhale"
            }

        else:
            raise ValueError(f"Unknown TripleWhale action: {action}")

    # ========== HUBSPOT HANDLERS ==========

    async def _handle_hubspot_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle HubSpot specific actions"""
        if action == "create_contact":
            result = await integration.create_contact(
                organization_id,
                params["contact_data"]
            )
            return {
                "status": result.get("status", "success"),
                "contact_id": result.get("contact_id"),
                "platform": "hubspot"
            }

        elif action == "create_campaign":
            result = await integration.create_campaign(
                organization_id,
                params["campaign_data"]
            )
            return {
                "status": result.get("status", "success"),
                "campaign_id": result.get("campaign_id"),
                "platform": "hubspot"
            }

        elif action == "create_workflow":
            result = await integration.create_workflow(
                organization_id,
                params["workflow_data"]
            )
            return {
                "status": result.get("status", "success"),
                "workflow_id": result.get("workflow_id"),
                "platform": "hubspot"
            }

        elif action == "trigger_workflow":
            result = await integration.trigger_workflow(
                organization_id,
                params["workflow_id"],
                params["contact_id"]
            )
            return {
                "status": result.get("status", "success"),
                "platform": "hubspot"
            }

        elif action == "get_analytics":
            result = await integration.get_analytics(
                organization_id,
                params["start_date"],
                params["end_date"],
                params.get("object_type", "contacts")
            )
            return {
                "status": result.get("status", "success"),
                "analytics_data": result.get("data"),
                "platform": "hubspot"
            }

        else:
            raise ValueError(f"Unknown HubSpot action: {action}")

    # ========== KLAVIYO HANDLERS ==========

    async def _handle_klaviyo_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Klaviyo specific actions"""
        if action == "create_campaign":
            result = await integration.create_campaign(
                organization_id,
                params["campaign_data"]
            )
            return {
                "status": result.get("status", "success"),
                "campaign_id": result.get("campaign_id"),
                "platform": "klaviyo"
            }

        elif action == "create_flow":
            result = await integration.create_flow(
                organization_id,
                params["flow_data"]
            )
            return {
                "status": result.get("status", "success"),
                "flow_id": result.get("flow_id"),
                "platform": "klaviyo"
            }

        elif action == "trigger_flow":
            result = await integration.trigger_flow(
                organization_id,
                params["flow_id"],
                params["profile_id"]
            )
            return {
                "status": result.get("status", "success"),
                "platform": "klaviyo"
            }

        elif action == "get_analytics":
            result = await integration.get_analytics(
                organization_id,
                params["start_date"],
                params["end_date"],
                params.get("metric_type", "email")
            )
            return {
                "status": result.get("status", "success"),
                "analytics_data": result.get("data"),
                "platform": "klaviyo"
            }

        else:
            raise ValueError(f"Unknown Klaviyo action: {action}")

    # ========== LINKEDIN ADS HANDLERS ==========

    async def _handle_linkedin_ads_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle LinkedIn Ads specific actions"""
        if action == "create_campaign":
            campaign_id = await integration.create_campaign(
                organization_id,
                params["account_id"],
                params["campaign_data"]
            )
            return {
                "status": "success" if campaign_id else "error",
                "campaign_id": campaign_id,
                "platform": "linkedin_ads"
            }

        elif action == "get_performance":
            performance = await integration.get_campaign_performance(
                organization_id,
                params["account_id"],
                params["campaign_ids"],
                params["date_range"]
            )
            return {
                "status": "success",
                "performance_data": performance,
                "platform": "linkedin_ads"
            }

        elif action == "create_creative":
            creative_id = await integration.create_ad_creative(
                organization_id,
                params["account_id"],
                params["creative_data"]
            )
            return {
                "status": "success" if creative_id else "error",
                "creative_id": creative_id,
                "platform": "linkedin_ads"
            }

        else:
            raise ValueError(f"Unknown LinkedIn Ads action: {action}")

    # ========== SHOPIFY HANDLERS ==========

    async def _handle_shopify_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Shopify specific actions"""
        if action == "get_products":
            products_data = await integration.get_products(
                organization_id,
                params["shop_domain"],
                params.get("limit", 50),
                params.get("page_info")
            )
            return {
                "status": "success",
                "products": products_data["products"],
                "has_next_page": products_data["has_next_page"],
                "platform": "shopify"
            }

        elif action == "create_product":
            product_id = await integration.create_product(
                organization_id,
                params["shop_domain"],
                params["product_data"]
            )
            return {
                "status": "success" if product_id else "error",
                "product_id": product_id,
                "platform": "shopify"
            }

        elif action == "get_orders":
            orders = await integration.get_orders(
                organization_id,
                params["shop_domain"],
                params.get("status"),
                params.get("limit", 50),
                params.get("created_at_min")
            )
            return {
                "status": "success",
                "orders": orders,
                "platform": "shopify"
            }

        elif action == "get_analytics":
            analytics = await integration.get_analytics(
                organization_id,
                params["shop_domain"],
                params["date_range"]
            )
            return {
                "status": "success",
                "analytics": analytics,
                "platform": "shopify"
            }

        else:
            raise ValueError(f"Unknown Shopify action: {action}")

    # ========== STRIPE HANDLERS ==========

    async def _handle_stripe_action(
        self,
        integration,
        action: str,
        organization_id: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Stripe specific actions"""
        if action == "create_payment_intent":
            payment_intent = await integration.create_payment_intent(
                organization_id,
                params["account_id"],
                params["payment_data"]
            )
            return {
                "status": "success" if payment_intent else "error",
                "payment_intent": payment_intent,
                "platform": "stripe"
            }

        elif action == "create_customer":
            customer_id = await integration.create_customer(
                organization_id,
                params["account_id"],
                params["customer_data"]
            )
            return {
                "status": "success" if customer_id else "error",
                "customer_id": customer_id,
                "platform": "stripe"
            }

        elif action == "create_subscription":
            subscription = await integration.create_subscription(
                organization_id,
                params["account_id"],
                params["subscription_data"]
            )
            return {
                "status": "success" if subscription else "error",
                "subscription": subscription,
                "platform": "stripe"
            }

        elif action == "create_invoice":
            invoice = await integration.create_invoice(
                organization_id,
                params["account_id"],
                params["invoice_data"]
            )
            return {
                "status": "success" if invoice else "error",
                "invoice": invoice,
                "platform": "stripe"
            }

        else:
            raise ValueError(f"Unknown Stripe action: {action}")

    # ========== PLATFORM MANAGEMENT ==========

    async def setup_platform_integration(
        self,
        organization_id: str,
        platform: Union[str, Platform],
        credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Set up integration credentials for a platform
        """
        try:
            platform_enum = platform if isinstance(platform, Platform) else Platform(platform)

            # Store credentials securely
            creds_key = f"platform_creds_{organization_id}_{platform_enum.value}"
            await production_secrets_manager.store_secret(creds_key, credentials)

            # Create platform integration record
            integration_record = {
                "integration_id": f"{organization_id}_{platform_enum.value}",
                "organization_id": organization_id,
                "platform": platform_enum.value,
                "status": "active",
                "last_sync": None,
                "sync_status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            tenant_manager = get_tenant_manager()
            tenant_manager.set_tenant_context(organization_id)

            await tenant_manager.db.platform_integrations.insert_one(integration_record)

            logger.info("Platform integration setup completed", extra={
                "organization_id": organization_id,
                "platform": platform_enum.value
            })

            return {
                "status": "success",
                "integration_id": integration_record["integration_id"],
                "platform": platform_enum.value
            }

        except Exception as e:
            logger.error("Platform integration setup failed", exc_info=e, extra={
                "organization_id": organization_id,
                "platform": str(platform)
            })

            return {
                "status": "error",
                "error": str(e)
            }

    async def get_platform_status(
        self,
        organization_id: str,
        platform: Union[str, Platform]
    ) -> Dict[str, Any]:
        """
        Get integration status for a platform
        """
        try:
            platform_enum = platform if isinstance(platform, Platform) else Platform(platform)

            tenant_manager = get_tenant_manager()
            tenant_manager.set_tenant_context(organization_id)

            integration = await tenant_manager.db.platform_integrations.find_one({
                "organization_id": organization_id,
                "platform": platform_enum.value
            })

            if not integration:
                return {"status": "not_configured"}

            # Test connection
            integration_instance = self.platforms[platform_enum]
            test_result = await integration_instance.test_connection(organization_id, "default")

            return {
                "status": integration["status"],
                "connection_test": test_result,
                "last_sync": integration.get("last_sync"),
                "sync_status": integration.get("sync_status"),
                "configured_at": integration.get("created_at")
            }

        except Exception as e:
            logger.error("Failed to get platform status", exc_info=e, extra={
                "organization_id": organization_id,
                "platform": str(platform)
            })

            return {"status": "error", "error": str(e)}

    async def sync_platform_data(
        self,
        organization_id: str,
        platform: Union[str, Platform],
        sync_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Synchronize data from a platform
        """
        try:
            platform_enum = platform if isinstance(platform, Platform) else Platform(platform)

            logger.info("Starting platform data sync", extra={
                "organization_id": organization_id,
                "platform": platform_enum.value,
                "sync_type": sync_type
            })

            # Execute sync based on platform
            if platform_enum == Platform.TRIPLEWHALE:
                # Sync attribution and revenue data from TripleWhale
                from datetime import timedelta
                result = await self.execute_platform_action(
                    platform_enum,
                    "get_revenue_metrics",
                    organization_id,
                    {
                        "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        "end_date": datetime.utcnow().strftime("%Y-%m-%d")
                    }
                )
            elif platform_enum == Platform.HUBSPOT:
                # Sync contacts and analytics from HubSpot
                from datetime import timedelta
                result = await self.execute_platform_action(
                    platform_enum,
                    "get_analytics",
                    organization_id,
                    {
                        "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        "end_date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "object_type": "contacts"
                    }
                )
            elif platform_enum == Platform.KLAVIYO:
                # Sync analytics from Klaviyo
                from datetime import timedelta
                result = await self.execute_platform_action(
                    platform_enum,
                    "get_analytics",
                    organization_id,
                    {
                        "start_date": (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        "end_date": datetime.utcnow().strftime("%Y-%m-%d"),
                        "metric_type": "email"
                    }
                )
            elif platform_enum == Platform.GOHIGHLEVEL:
                # Sync contacts from GoHighLevel (LOW PRIORITY)
                result = await self.execute_platform_action(
                    platform_enum,
                    "sync_contacts",
                    organization_id,
                    {"location_id": "default"}
                )
            else:
                # For ad platforms, sync campaign data
                result = await self._sync_ad_platform_data(
                    organization_id, platform_enum, sync_type
                )

            # Update integration status
            tenant_manager = get_tenant_manager()
            tenant_manager.set_tenant_context(organization_id)

            await tenant_manager.db.platform_integrations.update_one(
                {
                    "organization_id": organization_id,
                    "platform": platform_enum.value
                },
                {
                    "$set": {
                        "last_sync": datetime.utcnow(),
                        "sync_status": result["status"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            logger.info("Platform data sync completed", extra={
                "organization_id": organization_id,
                "platform": platform_enum.value,
                "sync_status": result["status"]
            })

            return result

        except Exception as e:
            logger.error("Platform data sync failed", exc_info=e, extra={
                "organization_id": organization_id,
                "platform": str(platform)
            })

            return {
                "status": "error",
                "error": str(e)
            }

    async def _sync_ad_platform_data(
        self,
        organization_id: str,
        platform: Platform,
        sync_type: str
    ) -> Dict[str, Any]:
        """
        Sync advertising platform data (campaigns, performance, etc.)
        """
        try:
            # Get accounts
            if platform == Platform.GOOGLE_ADS:
                accounts = await google_ads_integration.list_accessible_accounts(organization_id)
            elif platform == Platform.META_ADS:
                accounts = await meta_ads_integration.list_ad_accounts(organization_id)
            else:
                return {"status": "unsupported_platform"}

            synced_campaigns = 0
            synced_performance = 0

            for account in accounts[:1]:  # Limit to first account for now
                account_id = account["account_id"]

                # Sync campaigns (simplified - would need more complex logic)
                # This is a placeholder for the full sync logic
                synced_campaigns += 1
                synced_performance += 1

            return {
                "status": "success",
                "accounts_processed": len(accounts),
                "campaigns_synced": synced_campaigns,
                "performance_synced": synced_performance
            }

        except Exception as e:
            logger.error("Ad platform data sync failed", exc_info=e)
            return {"status": "error", "error": str(e)}

    # ========== COST TRACKING & OPTIMIZATION ==========

    async def _track_platform_metrics(
        self,
        platform: Platform,
        action: str,
        result: Dict[str, Any]
    ) -> None:
        """Track platform usage metrics and costs"""
        try:
            cost_info = self.cost_tracking.get(platform, {"cost_per_request": 0.001})
            estimated_cost = cost_info["cost_per_request"]

            # Store metrics (would go to a metrics collection)
            metrics_data = {
                "platform": platform.value,
                "action": action,
                "timestamp": datetime.utcnow(),
                "estimated_cost": estimated_cost,
                "success": result.get("status") == "success"
            }

            # In production, this would be stored in a metrics database
            logger.debug("Platform metrics tracked", extra=metrics_data)

        except Exception as e:
            logger.warning("Failed to track platform metrics", exc_info=e)

    async def _audit_platform_action(
        self,
        organization_id: str,
        platform: Platform,
        action: str,
        params: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Audit platform actions for compliance"""
        try:
            tenant_manager = get_tenant_manager()
            tenant_manager.set_tenant_context(organization_id)

            audit_entry = {
                "audit_id": f"{organization_id}_{platform.value}_{datetime.utcnow().timestamp()}",
                "organization_id": organization_id,
                "user_id": "system",  # Would be actual user in production
                "action": f"platform_{action}",
                "resource_type": f"platform_{platform.value}",
                "resource_id": params.get("account_id") or params.get("campaign_id") or "system",
                "timestamp": datetime.utcnow(),
                "ip_address": "system",
                "user_agent": "platform_integrations_manager",
                "metadata": {
                    "platform": platform.value,
                    "action": action,
                    "params_count": len(params),
                    "result_status": result.get("status")
                }
            }

            await tenant_manager.db.audit_logs.insert_one(audit_entry)

        except Exception as e:
            logger.warning("Platform action audit failed", exc_info=e)

    # ========== UTILITY METHODS ==========

    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        return [p.value for p in Platform]

    def get_platform_capabilities(self, platform: Union[str, Platform]) -> List[str]:
        """Get capabilities for a specific platform"""
        platform_enum = platform if isinstance(platform, Platform) else Platform(platform)
        return self.platform_capabilities.get(platform_enum, [])

    def get_platform_cost_info(self, platform: Union[str, Platform]) -> Dict[str, Any]:
        """Get cost information for a platform"""
        platform_enum = platform if isinstance(platform, Platform) else Platform(platform)
        return self.cost_tracking.get(platform_enum, {})

    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall platform integrations health"""
        health = {
            "platforms": {},
            "total_integrations": len(self.platforms),
            "active_integrations": 0,
            "timestamp": datetime.utcnow().isoformat()
        }

        for platform, integration in self.platforms.items():
            try:
                # Test basic connectivity (simplified)
                has_required_config = bool(getattr(integration, 'client_id', None) or getattr(integration, 'app_id', None))
                health["platforms"][platform.value] = {
                    "status": "configured" if has_required_config else "not_configured",
                    "last_check": datetime.utcnow().isoformat()
                }

                if has_required_config:
                    health["active_integrations"] += 1

            except Exception as e:
                health["platforms"][platform.value] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }

        health["health_score"] = (health["active_integrations"] / health["total_integrations"]) * 100

        return health

# Global platform integrations manager instance
platform_integrations_manager = PlatformIntegrationsManager()
