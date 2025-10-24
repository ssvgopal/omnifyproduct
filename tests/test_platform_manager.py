import pytest
import os
import sys
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock

# Ensure backend directory is in Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Mock the adapter imports to avoid import errors
with patch.dict('sys.modules', {
    'integrations.google_ads.client': MagicMock(),
    'integrations.meta_ads.client': MagicMock(),
    'integrations.gohighlevel.client': MagicMock(),
    'integrations.linkedin.client': MagicMock(),
    'integrations.tiktok.client': MagicMock(),
    'integrations.youtube.client': MagicMock(),
    'integrations.shopify.client': MagicMock(),
    'integrations.stripe.client': MagicMock(),
}):
    from integrations.platform_manager import PlatformIntegrationsManager, Platform


@pytest.fixture
def mock_platform_adapters():
    """Fixture for mocked platform adapters"""
    adapters = {}
    for platform in Platform:
        adapter = AsyncMock()
        adapter.initialize = AsyncMock()
        adapter.test_connection = AsyncMock(return_value={"status": "connected"})
        adapter.create_campaign = AsyncMock(return_value=f"campaign_{platform.value}_123")
        adapter.get_campaign_performance = AsyncMock(return_value={"impressions": 1000, "clicks": 50})
        adapter.create_contact = AsyncMock(return_value=f"contact_{platform.value}_123")
        adapter.sync_contacts_to_omnify = AsyncMock(return_value={"status": "success", "synced_contacts": 10})
        adapters[platform] = adapter
    return adapters


@pytest.fixture
def mock_services():
    """Fixture for mocked external services"""
    services = {
        'secrets_manager': AsyncMock(),
        'tenant_manager': AsyncMock(),
        'rate_limiter': AsyncMock(),
        'cost_guardrails': AsyncMock()
    }
    
    # Mock secrets manager
    services['secrets_manager'].get_secret = AsyncMock(return_value={
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "access_token": "test_access_token"
    })
    services['secrets_manager'].store_secret = AsyncMock()
    
    # Mock tenant manager
    mock_db = AsyncMock()
    mock_db.platform_integrations = AsyncMock()
    mock_db.platform_integrations.insert_one = AsyncMock()
    mock_db.platform_integrations.find_one = AsyncMock()
    mock_db.platform_integrations.update_one = AsyncMock()
    mock_db.audit_logs = AsyncMock()
    mock_db.audit_logs.insert_one = AsyncMock()
    
    services['tenant_manager'].db = mock_db
    services['tenant_manager'].set_tenant_context = MagicMock()
    
    # Create a proper mock tenant manager instance
    mock_tenant_manager_instance = MagicMock()
    mock_tenant_manager_instance.db = mock_db
    mock_tenant_manager_instance.set_tenant_context = MagicMock()
    services['tenant_manager'] = mock_tenant_manager_instance
    
    # Mock rate limiter
    services['rate_limiter'].check_rate_limit = AsyncMock(return_value=(True, {}))
    
    # Mock cost guardrails
    services['cost_guardrails'].record_cost = AsyncMock()
    
    return services


@pytest.fixture
def platform_manager(mock_platform_adapters, mock_services):
    """Fixture for PlatformIntegrationsManager with mocked dependencies"""
    with patch('integrations.platform_manager.GoogleAdsAdapter', return_value=mock_platform_adapters[Platform.GOOGLE_ADS]), \
         patch('integrations.platform_manager.MetaAdsAdapter', return_value=mock_platform_adapters[Platform.META_ADS]), \
         patch('integrations.platform_manager.LinkedInAdsAdapter', return_value=mock_platform_adapters[Platform.LINKEDIN_ADS]), \
         patch('integrations.platform_manager.TikTokAdsAdapter', return_value=mock_platform_adapters[Platform.TIKTOK_ADS]), \
         patch('integrations.platform_manager.YouTubeAdsAdapter', return_value=mock_platform_adapters[Platform.YOUTUBE_ADS]), \
         patch('integrations.platform_manager.GoHighLevelAdapter', return_value=mock_platform_adapters[Platform.GOHIGHLEVEL]), \
         patch('integrations.platform_manager.ShopifyIntegration', return_value=mock_platform_adapters[Platform.SHOPIFY]), \
         patch('integrations.platform_manager.StripeAdapter', return_value=mock_platform_adapters[Platform.STRIPE]), \
         patch('integrations.platform_manager.production_secrets_manager', mock_services['secrets_manager']), \
         patch('services.production_tenant_manager.get_tenant_manager', return_value=mock_services['tenant_manager']), \
         patch('integrations.platform_manager.production_rate_limiter', mock_services['rate_limiter']), \
         patch('integrations.platform_manager.cost_guardrails', mock_services['cost_guardrails']), \
         patch('integrations.platform_manager.logger') as mock_logger:
        
        manager = PlatformIntegrationsManager()
        return manager, mock_services, mock_platform_adapters


@pytest.fixture
def test_organization_id():
    """Fixture for test organization ID"""
    return "test-org-123"


@pytest.fixture
def test_platform_credentials():
    """Fixture for test platform credentials"""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }


class TestPlatformIntegrationsManager:
    """Tests for the Platform Integrations Manager"""

    # ========== INITIALIZATION TESTS ==========

    def test_manager_initialization(self, platform_manager):
        """Test platform manager initialization"""
        manager, mock_services, mock_adapters = platform_manager
        
        assert len(manager.platforms) == 8
        assert Platform.GOOGLE_ADS in manager.platforms
        assert Platform.META_ADS in manager.platforms
        assert Platform.LINKEDIN_ADS in manager.platforms
        assert Platform.TIKTOK_ADS in manager.platforms
        assert Platform.YOUTUBE_ADS in manager.platforms
        assert Platform.GOHIGHLEVEL in manager.platforms
        assert Platform.SHOPIFY in manager.platforms
        assert Platform.STRIPE in manager.platforms

    def test_platform_capabilities_mapping(self, platform_manager):
        """Test platform capabilities mapping"""
        manager, mock_services, mock_adapters = platform_manager
        
        google_caps = manager.platform_capabilities[Platform.GOOGLE_ADS]
        assert "campaign_management" in google_caps
        assert "keyword_optimization" in google_caps
        assert "conversion_tracking" in google_caps
        
        meta_caps = manager.platform_capabilities[Platform.META_ADS]
        assert "campaign_management" in meta_caps
        assert "audience_targeting" in meta_caps
        assert "creative_optimization" in meta_caps
        
        shopify_caps = manager.platform_capabilities[Platform.SHOPIFY]
        assert "product_management" in shopify_caps
        assert "order_processing" in shopify_caps
        assert "inventory_tracking" in shopify_caps

    def test_cost_tracking_configuration(self, platform_manager):
        """Test cost tracking configuration"""
        manager, mock_services, mock_adapters = platform_manager
        
        google_cost = manager.cost_tracking[Platform.GOOGLE_ADS]
        assert "cost_per_request" in google_cost
        assert "monthly_free" in google_cost
        assert google_cost["cost_per_request"] == 0.001
        
        stripe_cost = manager.cost_tracking[Platform.STRIPE]
        assert stripe_cost["cost_per_request"] == 0.029  # 2.9% + 30¢

    # ========== PLATFORM INITIALIZATION TESTS ==========

    @pytest.mark.asyncio
    async def test_initialize_platforms_success(self, platform_manager, test_organization_id):
        """Test successful platform initialization"""
        manager, mock_services, mock_adapters = platform_manager
        
        await manager.initialize_platforms(test_organization_id)
        
        # Verify secrets manager was called for each platform
        assert mock_services['secrets_manager'].get_secret.call_count == 8
        
        # Verify adapters were initialized
        for adapter in mock_adapters.values():
            adapter.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_platforms_with_missing_credentials(self, platform_manager, test_organization_id):
        """Test platform initialization with missing credentials"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock missing credentials for some platforms
        mock_services['secrets_manager'].get_secret.side_effect = [
            None,  # Google Ads - no credentials
            {"client_id": "test"},  # Meta Ads - has credentials
            None,  # LinkedIn Ads - no credentials
            {"client_id": "test"},  # TikTok Ads - has credentials
            None,  # YouTube Ads - no credentials
            {"client_id": "test"},  # GoHighLevel - has credentials
            None,  # Shopify - no credentials
            {"client_id": "test"}   # Stripe - has credentials
        ]
        
        await manager.initialize_platforms(test_organization_id)
        
        # Verify only platforms with credentials were initialized
        assert mock_adapters[Platform.GOOGLE_ADS].initialize.call_count == 0
        assert mock_adapters[Platform.META_ADS].initialize.call_count == 1
        assert mock_adapters[Platform.LINKEDIN_ADS].initialize.call_count == 0
        assert mock_adapters[Platform.TIKTOK_ADS].initialize.call_count == 1
        assert mock_adapters[Platform.YOUTUBE_ADS].initialize.call_count == 0
        assert mock_adapters[Platform.GOHIGHLEVEL].initialize.call_count == 1
        assert mock_adapters[Platform.SHOPIFY].initialize.call_count == 0
        assert mock_adapters[Platform.STRIPE].initialize.call_count == 1

    @pytest.mark.asyncio
    async def test_initialize_platforms_failure(self, platform_manager, test_organization_id):
        """Test platform initialization failure handling"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock adapter initialization failure
        mock_adapters[Platform.GOOGLE_ADS].initialize.side_effect = Exception("Initialization failed")
        
        with pytest.raises(Exception) as exc_info:
            await manager.initialize_platforms(test_organization_id)
        
        assert "Initialization failed" in str(exc_info.value)

    # ========== PLATFORM ACTION EXECUTION TESTS ==========

    @pytest.mark.asyncio
    async def test_execute_platform_action_success(self, platform_manager, test_organization_id):
        """Test successful platform action execution"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Ensure rate limiter allows the request
        mock_services['rate_limiter'].check_rate_limit.return_value = (True, {})
        
        # Mock successful campaign creation
        mock_adapters[Platform.GOOGLE_ADS].create_campaign.return_value = "campaign_123"
        
        result = await manager.execute_platform_action(
            Platform.GOOGLE_ADS,
            "create_campaign",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_data": {"name": "Test Campaign", "budget": 1000}
            }
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == "campaign_123"
        assert result["platform"] == "google_ads"
        
        # Verify rate limiter was checked
        mock_services['rate_limiter'].check_rate_limit.assert_called_once()
        
        # Verify cost tracking was called
        mock_services['cost_guardrails'].record_cost.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_platform_action_rate_limited(self, platform_manager, test_organization_id):
        """Test platform action execution when rate limited"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock rate limit exceeded
        mock_services['rate_limiter'].check_rate_limit.return_value = (False, {"retry_after": 60})
        
        result = await manager.execute_platform_action(
            Platform.META_ADS,
            "create_campaign",
            test_organization_id,
            {"account_id": "account_123", "campaign_data": {}}
        )
        
        assert result["status"] == "rate_limited"
        assert result["retry_after"] == 3600

    @pytest.mark.asyncio
    async def test_execute_platform_action_unsupported_platform(self, platform_manager, test_organization_id):
        """Test platform action execution with unsupported platform"""
        manager, mock_services, mock_adapters = platform_manager
        
        result = await manager.execute_platform_action(
            "unsupported_platform",
            "create_campaign",
            test_organization_id,
            {}
        )
        
        assert result["status"] == "error"
        assert "not a valid Platform" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_platform_action_exception(self, platform_manager, test_organization_id):
        """Test platform action execution with exception"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Ensure rate limiter allows the request
        mock_services['rate_limiter'].check_rate_limit.return_value = (True, {})
        
        # Mock adapter method failure
        mock_adapters[Platform.LINKEDIN_ADS].create_campaign.side_effect = Exception("API Error")
        
        result = await manager.execute_platform_action(
            Platform.LINKEDIN_ADS,
            "create_campaign",
            test_organization_id,
            {"account_id": "account_123", "campaign_data": {}}
        )
        
        assert result["status"] == "error"
        assert "API Error" in result["error"]

    # ========== GOOGLE ADS HANDLER TESTS ==========

    @pytest.mark.asyncio
    async def test_handle_google_ads_create_campaign(self, platform_manager, test_organization_id):
        """Test Google Ads campaign creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.GOOGLE_ADS].create_campaign.return_value = "google_campaign_123"
        
        result = await manager._handle_google_ads_action(
            mock_adapters[Platform.GOOGLE_ADS],
            "create_campaign",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_data": {"name": "Google Campaign", "budget": 1000}
            }
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == "google_campaign_123"
        assert result["platform"] == "google_ads"

    @pytest.mark.asyncio
    async def test_handle_google_ads_get_performance(self, platform_manager, test_organization_id):
        """Test Google Ads performance retrieval"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_performance = {"impressions": 5000, "clicks": 250, "conversions": 10}
        mock_adapters[Platform.GOOGLE_ADS].get_campaign_performance.return_value = mock_performance
        
        result = await manager._handle_google_ads_action(
            mock_adapters[Platform.GOOGLE_ADS],
            "get_performance",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_ids": ["campaign_1", "campaign_2"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
            }
        )
        
        assert result["status"] == "success"
        assert result["performance_data"] == mock_performance

    @pytest.mark.asyncio
    async def test_handle_google_ads_optimize_bids(self, platform_manager, test_organization_id):
        """Test Google Ads bid optimization"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.GOOGLE_ADS].update_campaign_bids.return_value = True
        
        result = await manager._handle_google_ads_action(
            mock_adapters[Platform.GOOGLE_ADS],
            "optimize_bids",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_id": "campaign_123",
                "bid_adjustments": {"keyword_1": 1.2, "keyword_2": 0.8}
            }
        )
        
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_google_ads_unknown_action(self, platform_manager, test_organization_id):
        """Test Google Ads unknown action handling"""
        manager, mock_services, mock_adapters = platform_manager
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_google_ads_action(
                mock_adapters[Platform.GOOGLE_ADS],
                "unknown_action",
                test_organization_id,
                {}
            )
        
        assert "Unknown Google Ads action" in str(exc_info.value)

    # ========== META ADS HANDLER TESTS ==========

    @pytest.mark.asyncio
    async def test_handle_meta_ads_create_campaign(self, platform_manager, test_organization_id):
        """Test Meta Ads campaign creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.META_ADS].create_campaign.return_value = "meta_campaign_123"
        
        result = await manager._handle_meta_ads_action(
            mock_adapters[Platform.META_ADS],
            "create_campaign",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_data": {"name": "Meta Campaign", "objective": "CONVERSIONS"}
            }
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == "meta_campaign_123"
        assert result["platform"] == "meta_ads"

    @pytest.mark.asyncio
    async def test_handle_meta_ads_get_insights(self, platform_manager, test_organization_id):
        """Test Meta Ads insights retrieval"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_insights = {"reach": 10000, "impressions": 50000, "clicks": 500}
        mock_adapters[Platform.META_ADS].get_campaign_insights.return_value = mock_insights
        
        result = await manager._handle_meta_ads_action(
            mock_adapters[Platform.META_ADS],
            "get_insights",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_ids": ["campaign_1"],
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
                "metrics": ["reach", "impressions", "clicks"]
            }
        )
        
        assert result["status"] == "success"
        assert result["insights_data"] == mock_insights

    @pytest.mark.asyncio
    async def test_handle_meta_ads_create_ad_set(self, platform_manager, test_organization_id):
        """Test Meta Ads ad set creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.META_ADS].create_ad_set.return_value = "adset_123"
        
        result = await manager._handle_meta_ads_action(
            mock_adapters[Platform.META_ADS],
            "create_ad_set",
            test_organization_id,
            {
                "account_id": "account_123",
                "campaign_id": "campaign_123",
                "ad_set_data": {"name": "Test Ad Set", "budget": 100}
            }
        )
        
        assert result["status"] == "success"
        assert result["ad_set_id"] == "adset_123"

    # ========== GOHIGHLEVEL HANDLER TESTS ==========

    @pytest.mark.asyncio
    async def test_handle_gohighlevel_create_contact(self, platform_manager, test_organization_id):
        """Test GoHighLevel contact creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.GOHIGHLEVEL].create_contact.return_value = "contact_123"
        
        result = await manager._handle_gohighlevel_action(
            mock_adapters[Platform.GOHIGHLEVEL],
            "create_contact",
            test_organization_id,
            {
                "location_id": "location_123",
                "contact_data": {"email": "test@example.com", "name": "Test User"}
            }
        )
        
        assert result["status"] == "success"
        assert result["contact_id"] == "contact_123"
        assert result["platform"] == "gohighlevel"

    @pytest.mark.asyncio
    async def test_handle_gohighlevel_trigger_workflow(self, platform_manager, test_organization_id):
        """Test GoHighLevel workflow triggering"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.GOHIGHLEVEL].trigger_workflow.return_value = True
        
        result = await manager._handle_gohighlevel_action(
            mock_adapters[Platform.GOHIGHLEVEL],
            "trigger_workflow",
            test_organization_id,
            {
                "location_id": "location_123",
                "workflow_id": "workflow_123",
                "contact_id": "contact_123",
                "trigger_data": {"source": "website"}
            }
        )
        
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_handle_gohighlevel_sync_contacts(self, platform_manager, test_organization_id):
        """Test GoHighLevel contact synchronization"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_sync_result = {"status": "success", "synced_contacts": 25}
        mock_adapters[Platform.GOHIGHLEVEL].sync_contacts_to_omnify.return_value = mock_sync_result
        
        result = await manager._handle_gohighlevel_action(
            mock_adapters[Platform.GOHIGHLEVEL],
            "sync_contacts",
            test_organization_id,
            {"location_id": "location_123", "last_sync": "2024-01-01"}
        )
        
        assert result["status"] == "success"
        assert result["synced_contacts"] == 25

    # ========== SHOPIFY HANDLER TESTS ==========

    @pytest.mark.asyncio
    async def test_handle_shopify_get_products(self, platform_manager, test_organization_id):
        """Test Shopify products retrieval"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_products_data = {
            "products": [{"id": "prod_1", "title": "Product 1"}, {"id": "prod_2", "title": "Product 2"}],
            "has_next_page": False
        }
        mock_adapters[Platform.SHOPIFY].get_products.return_value = mock_products_data
        
        result = await manager._handle_shopify_action(
            mock_adapters[Platform.SHOPIFY],
            "get_products",
            test_organization_id,
            {"shop_domain": "test-shop.myshopify.com", "limit": 50}
        )
        
        assert result["status"] == "success"
        assert len(result["products"]) == 2
        assert result["has_next_page"] is False

    @pytest.mark.asyncio
    async def test_handle_shopify_create_product(self, platform_manager, test_organization_id):
        """Test Shopify product creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.SHOPIFY].create_product.return_value = "product_123"
        
        result = await manager._handle_shopify_action(
            mock_adapters[Platform.SHOPIFY],
            "create_product",
            test_organization_id,
            {
                "shop_domain": "test-shop.myshopify.com",
                "product_data": {"title": "New Product", "price": 29.99}
            }
        )
        
        assert result["status"] == "success"
        assert result["product_id"] == "product_123"

    @pytest.mark.asyncio
    async def test_handle_shopify_get_analytics(self, platform_manager, test_organization_id):
        """Test Shopify analytics retrieval"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_analytics = {"total_sales": 10000, "orders": 50, "customers": 25}
        mock_adapters[Platform.SHOPIFY].get_analytics.return_value = mock_analytics
        
        result = await manager._handle_shopify_action(
            mock_adapters[Platform.SHOPIFY],
            "get_analytics",
            test_organization_id,
            {
                "shop_domain": "test-shop.myshopify.com",
                "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
            }
        )
        
        assert result["status"] == "success"
        assert result["analytics"] == mock_analytics

    # ========== STRIPE HANDLER TESTS ==========

    @pytest.mark.asyncio
    async def test_handle_stripe_create_payment_intent(self, platform_manager, test_organization_id):
        """Test Stripe payment intent creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_payment_intent = {"id": "pi_123", "status": "requires_payment_method"}
        mock_adapters[Platform.STRIPE].create_payment_intent.return_value = mock_payment_intent
        
        result = await manager._handle_stripe_action(
            mock_adapters[Platform.STRIPE],
            "create_payment_intent",
            test_organization_id,
            {
                "account_id": "acct_123",
                "payment_data": {"amount": 2000, "currency": "usd"}
            }
        )
        
        assert result["status"] == "success"
        assert result["payment_intent"] == mock_payment_intent

    @pytest.mark.asyncio
    async def test_handle_stripe_create_customer(self, platform_manager, test_organization_id):
        """Test Stripe customer creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_adapters[Platform.STRIPE].create_customer.return_value = "cus_123"
        
        result = await manager._handle_stripe_action(
            mock_adapters[Platform.STRIPE],
            "create_customer",
            test_organization_id,
            {
                "account_id": "acct_123",
                "customer_data": {"email": "customer@example.com", "name": "Customer Name"}
            }
        )
        
        assert result["status"] == "success"
        assert result["customer_id"] == "cus_123"

    @pytest.mark.asyncio
    async def test_handle_stripe_create_subscription(self, platform_manager, test_organization_id):
        """Test Stripe subscription creation"""
        manager, mock_services, mock_adapters = platform_manager
        
        mock_subscription = {"id": "sub_123", "status": "active"}
        mock_adapters[Platform.STRIPE].create_subscription.return_value = mock_subscription
        
        result = await manager._handle_stripe_action(
            mock_adapters[Platform.STRIPE],
            "create_subscription",
            test_organization_id,
            {
                "account_id": "acct_123",
                "subscription_data": {"customer": "cus_123", "price": "price_123"}
            }
        )
        
        assert result["status"] == "success"
        assert result["subscription"] == mock_subscription

    # ========== PLATFORM SETUP TESTS ==========

    @pytest.mark.asyncio
    async def test_setup_platform_integration_success(self, platform_manager, test_organization_id, test_platform_credentials):
        """Test successful platform integration setup"""
        manager, mock_services, mock_adapters = platform_manager
        
        result = await manager.setup_platform_integration(
            test_organization_id,
            Platform.GOOGLE_ADS,
            test_platform_credentials
        )
        
        assert result["status"] == "success"
        assert result["platform"] == "google_ads"
        assert "integration_id" in result
        
        # Verify credentials were stored
        mock_services['secrets_manager'].store_secret.assert_called_once()
        
        # Verify integration record was created
        mock_services['tenant_manager'].db.platform_integrations.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_platform_integration_failure(self, platform_manager, test_organization_id, test_platform_credentials):
        """Test platform integration setup failure"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock database failure
        mock_services['tenant_manager'].db.platform_integrations.insert_one.side_effect = Exception("DB Error")
        
        result = await manager.setup_platform_integration(
            test_organization_id,
            Platform.META_ADS,
            test_platform_credentials
        )
        
        assert result["status"] == "error"
        assert "DB Error" in result["error"]

    @pytest.mark.asyncio
    async def test_get_platform_status_configured(self, platform_manager, test_organization_id):
        """Test getting platform status when configured"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock existing integration
        mock_integration = {
            "organization_id": test_organization_id,
            "platform": "google_ads",
            "status": "active",
            "last_sync": datetime.utcnow(),
            "sync_status": "success",
            "created_at": datetime.utcnow()
        }
        mock_services['tenant_manager'].db.platform_integrations.find_one.return_value = mock_integration
        
        result = await manager.get_platform_status(test_organization_id, Platform.GOOGLE_ADS)
        
        assert result["status"] == "active"
        assert "connection_test" in result
        assert "last_sync" in result

    @pytest.mark.asyncio
    async def test_get_platform_status_not_configured(self, platform_manager, test_organization_id):
        """Test getting platform status when not configured"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock no integration found
        mock_services['tenant_manager'].db.platform_integrations.find_one.return_value = None
        
        result = await manager.get_platform_status(test_organization_id, Platform.SHOPIFY)
        
        assert result["status"] == "not_configured"

    # ========== DATA SYNCHRONIZATION TESTS ==========

    @pytest.mark.asyncio
    async def test_sync_platform_data_gohighlevel(self, platform_manager, test_organization_id):
        """Test GoHighLevel data synchronization"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock successful sync
        mock_sync_result = {"status": "success", "synced_contacts": 15}
        mock_adapters[Platform.GOHIGHLEVEL].sync_contacts_to_omnify.return_value = mock_sync_result
        
        result = await manager.sync_platform_data(test_organization_id, Platform.GOHIGHLEVEL, "full")
        
        assert result["status"] == "success"
        assert result["synced_contacts"] == 15
        
        # Verify integration status was updated
        mock_services['tenant_manager'].db.platform_integrations.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_platform_data_failure(self, platform_manager, test_organization_id):
        """Test platform data synchronization failure"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Mock sync failure
        mock_adapters[Platform.GOHIGHLEVEL].sync_contacts_to_omnify.side_effect = Exception("Sync Error")
        
        result = await manager.sync_platform_data(test_organization_id, Platform.GOHIGHLEVEL, "full")
        
        assert result["status"] == "error"
        assert "Sync Error" in result["error"]

    # ========== UTILITY METHOD TESTS ==========

    def test_get_supported_platforms(self, platform_manager):
        """Test getting supported platforms list"""
        manager, mock_services, mock_adapters = platform_manager
        
        platforms = manager.get_supported_platforms()
        
        assert len(platforms) == 9  # Including GOOGLE_ANALYTICS
        assert "google_ads" in platforms
        assert "meta_ads" in platforms
        assert "linkedin_ads" in platforms
        assert "tiktok_ads" in platforms
        assert "youtube_ads" in platforms
        assert "gohighlevel" in platforms
        assert "shopify" in platforms
        assert "stripe" in platforms

    def test_get_platform_capabilities(self, platform_manager):
        """Test getting platform capabilities"""
        manager, mock_services, mock_adapters = platform_manager
        
        google_caps = manager.get_platform_capabilities(Platform.GOOGLE_ADS)
        assert "campaign_management" in google_caps
        assert "keyword_optimization" in google_caps
        
        meta_caps = manager.get_platform_capabilities("meta_ads")
        assert "campaign_management" in meta_caps
        assert "audience_targeting" in meta_caps

    def test_get_platform_cost_info(self, platform_manager):
        """Test getting platform cost information"""
        manager, mock_services, mock_adapters = platform_manager
        
        google_cost = manager.get_platform_cost_info(Platform.GOOGLE_ADS)
        assert "cost_per_request" in google_cost
        assert "monthly_free" in google_cost
        
        stripe_cost = manager.get_platform_cost_info("stripe")
        assert stripe_cost["cost_per_request"] == 0.029

    @pytest.mark.asyncio
    async def test_get_system_health(self, platform_manager):
        """Test getting system health status"""
        manager, mock_services, mock_adapters = platform_manager
        
        health = await manager.get_system_health()
        
        assert "platforms" in health
        assert "total_integrations" in health
        assert "active_integrations" in health
        assert "health_score" in health
        assert "timestamp" in health
        
        assert health["total_integrations"] == 8
        assert isinstance(health["health_score"], (int, float))

    # ========== COST TRACKING TESTS ==========

    @pytest.mark.asyncio
    async def test_track_platform_metrics(self, platform_manager):
        """Test platform metrics tracking"""
        manager, mock_services, mock_adapters = platform_manager
        
        result = {"status": "success", "campaign_id": "campaign_123"}
        
        # Should not raise exception
        await manager._track_platform_metrics(Platform.GOOGLE_ADS, "create_campaign", result)
        
        # Verify cost guardrails was called
        mock_services['cost_guardrails'].record_cost.assert_called()

    @pytest.mark.asyncio
    async def test_audit_platform_action(self, platform_manager, test_organization_id):
        """Test platform action auditing"""
        manager, mock_services, mock_adapters = platform_manager
        
        params = {"account_id": "account_123", "campaign_data": {"name": "Test"}}
        result = {"status": "success", "campaign_id": "campaign_123"}
        
        # Should not raise exception
        await manager._audit_platform_action(
            test_organization_id,
            Platform.META_ADS,
            "create_campaign",
            params,
            result
        )
        
        # Verify audit log was created
        mock_services['tenant_manager'].db.audit_logs.insert_one.assert_called_once()

    # ========== ERROR HANDLING TESTS ==========

    @pytest.mark.asyncio
    async def test_platform_action_routing_error(self, platform_manager, test_organization_id):
        """Test platform action routing error"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Test with unsupported platform enum
        with pytest.raises(ValueError) as exc_info:
            await manager._route_platform_action(
                mock_adapters[Platform.GOOGLE_ADS],
                Platform.GOOGLE_ANALYTICS,  # Not handled in routing
                "create_campaign",
                test_organization_id,
                {}
            )
        
        assert "No handler for platform" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_platform_enum_conversion(self, platform_manager, test_organization_id):
        """Test platform enum conversion from string"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Test string to enum conversion
        result = await manager.execute_platform_action(
            "google_ads",  # String instead of enum
            "create_campaign",
            test_organization_id,
            {"account_id": "account_123", "campaign_data": {}}
        )
        
        # Should work the same as enum
        assert "status" in result

    # ========== CONCURRENT EXECUTION TESTS ==========

    @pytest.mark.asyncio
    async def test_concurrent_platform_actions(self, platform_manager, test_organization_id):
        """Test concurrent platform action execution"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Ensure rate limiter allows all requests
        mock_services['rate_limiter'].check_rate_limit.return_value = (True, {})
        
        # Mock successful responses
        for adapter in mock_adapters.values():
            adapter.create_campaign.return_value = "campaign_123"
        
        # Execute multiple actions concurrently
        tasks = [
            manager.execute_platform_action(
                Platform.GOOGLE_ADS,
                "create_campaign",
                test_organization_id,
                {"account_id": "account_1", "campaign_data": {}}
            ),
            manager.execute_platform_action(
                Platform.META_ADS,
                "create_campaign",
                test_organization_id,
                {"account_id": "account_2", "campaign_data": {}}
            ),
            manager.execute_platform_action(
                Platform.LINKEDIN_ADS,
                "create_campaign",
                test_organization_id,
                {"account_id": "account_3", "campaign_data": {}}
            )
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert result["status"] == "success"
            assert result["campaign_id"] == "campaign_123"

    # ========== INTEGRATION TESTS ==========

    @pytest.mark.asyncio
    async def test_full_platform_workflow(self, platform_manager, test_organization_id, test_platform_credentials):
        """Test complete platform workflow: setup -> execute -> sync"""
        manager, mock_services, mock_adapters = platform_manager
        
        # 1. Setup platform integration
        setup_result = await manager.setup_platform_integration(
            test_organization_id,
            Platform.GOHIGHLEVEL,
            test_platform_credentials
        )
        assert setup_result["status"] == "success"
        
        # 2. Execute platform action
        mock_adapters[Platform.GOHIGHLEVEL].create_contact.return_value = "contact_123"
        action_result = await manager.execute_platform_action(
            Platform.GOHIGHLEVEL,
            "create_contact",
            test_organization_id,
            {
                "location_id": "location_123",
                "contact_data": {"email": "test@example.com", "name": "Test User"}
            }
        )
        assert action_result["status"] == "success"
        
        # 3. Sync platform data
        mock_adapters[Platform.GOHIGHLEVEL].sync_contacts_to_omnify.return_value = {
            "status": "success", "synced_contacts": 5
        }
        sync_result = await manager.sync_platform_data(test_organization_id, Platform.GOHIGHLEVEL)
        assert sync_result["status"] == "success"
        
        # Verify all steps were executed
        mock_services['secrets_manager'].store_secret.assert_called()
        mock_services['tenant_manager'].db.platform_integrations.insert_one.assert_called()
        mock_services['tenant_manager'].db.platform_integrations.update_one.assert_called()
        mock_services['cost_guardrails'].record_cost.assert_called()

    # ========== PERFORMANCE TESTS ==========

    @pytest.mark.asyncio
    async def test_platform_action_performance(self, platform_manager, test_organization_id):
        """Test platform action execution performance"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Ensure rate limiter allows the request
        mock_services['rate_limiter'].check_rate_limit.return_value = (True, {})
        
        import time
        
        # Mock fast response
        mock_adapters[Platform.SHOPIFY].get_products.return_value = {
            "products": [], "has_next_page": False
        }
        
        start_time = time.time()
        result = await manager.execute_platform_action(
            Platform.SHOPIFY,
            "get_products",
            test_organization_id,
            {"shop_domain": "test-shop.myshopify.com"}
        )
        end_time = time.time()
        
        assert result["status"] == "success"
        assert (end_time - start_time) < 1.0  # Should complete quickly

    # ========== DATA VALIDATION TESTS ==========

    @pytest.mark.asyncio
    async def test_platform_action_parameter_validation(self, platform_manager, test_organization_id):
        """Test platform action parameter validation"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Test with missing required parameters
        result = await manager.execute_platform_action(
            Platform.GOOGLE_ADS,
            "create_campaign",
            test_organization_id,
            {}  # Missing account_id and campaign_data
        )
        
        # Should handle gracefully (adapter will handle validation)
        assert "status" in result

    @pytest.mark.asyncio
    async def test_platform_enum_validation(self, platform_manager, test_organization_id):
        """Test platform enum validation"""
        manager, mock_services, mock_adapters = platform_manager
        
        # Test with invalid platform string
        result = await manager.execute_platform_action(
            "invalid_platform",
            "create_campaign",
            test_organization_id,
            {}
        )
        
        assert result["status"] == "error"
        assert "not a valid Platform" in result["error"]