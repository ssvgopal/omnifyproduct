import pytest
import os
import sys
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
def platform_manager_simple(mock_platform_adapters):
    """Simplified fixture for PlatformIntegrationsManager"""
    with patch('integrations.platform_manager.GoogleAdsAdapter', return_value=mock_platform_adapters[Platform.GOOGLE_ADS]), \
         patch('integrations.platform_manager.MetaAdsAdapter', return_value=mock_platform_adapters[Platform.META_ADS]), \
         patch('integrations.platform_manager.LinkedInAdsAdapter', return_value=mock_platform_adapters[Platform.LINKEDIN_ADS]), \
         patch('integrations.platform_manager.TikTokAdsAdapter', return_value=mock_platform_adapters[Platform.TIKTOK_ADS]), \
         patch('integrations.platform_manager.YouTubeAdsAdapter', return_value=mock_platform_adapters[Platform.YOUTUBE_ADS]), \
         patch('integrations.platform_manager.GoHighLevelAdapter', return_value=mock_platform_adapters[Platform.GOHIGHLEVEL]), \
         patch('integrations.platform_manager.ShopifyIntegration', return_value=mock_platform_adapters[Platform.SHOPIFY]), \
         patch('integrations.platform_manager.StripeAdapter', return_value=mock_platform_adapters[Platform.STRIPE]), \
         patch('integrations.platform_manager.logger'):
        
        manager = PlatformIntegrationsManager()
        return manager, mock_platform_adapters


class TestPlatformIntegrationsManagerSimple:
    """Simplified tests for the Platform Integrations Manager"""

    def test_manager_initialization(self, platform_manager_simple):
        """Test platform manager initialization"""
        manager, mock_adapters = platform_manager_simple
        
        assert len(manager.platforms) == 8
        assert Platform.GOOGLE_ADS in manager.platforms
        assert Platform.META_ADS in manager.platforms
        assert Platform.LINKEDIN_ADS in manager.platforms
        assert Platform.TIKTOK_ADS in manager.platforms
        assert Platform.YOUTUBE_ADS in manager.platforms
        assert Platform.GOHIGHLEVEL in manager.platforms
        assert Platform.SHOPIFY in manager.platforms
        assert Platform.STRIPE in manager.platforms

    def test_platform_capabilities_mapping(self, platform_manager_simple):
        """Test platform capabilities mapping"""
        manager, mock_adapters = platform_manager_simple
        
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

    def test_cost_tracking_configuration(self, platform_manager_simple):
        """Test cost tracking configuration"""
        manager, mock_adapters = platform_manager_simple
        
        google_cost = manager.cost_tracking[Platform.GOOGLE_ADS]
        assert "cost_per_request" in google_cost
        assert "monthly_free" in google_cost
        assert google_cost["cost_per_request"] == 0.001
        
        stripe_cost = manager.cost_tracking[Platform.STRIPE]
        assert stripe_cost["cost_per_request"] == 0.029  # 2.9% + 30¢

    def test_get_supported_platforms(self, platform_manager_simple):
        """Test getting supported platforms list"""
        manager, mock_adapters = platform_manager_simple
        
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

    def test_get_platform_capabilities(self, platform_manager_simple):
        """Test getting platform capabilities"""
        manager, mock_adapters = platform_manager_simple
        
        google_caps = manager.get_platform_capabilities(Platform.GOOGLE_ADS)
        assert "campaign_management" in google_caps
        assert "keyword_optimization" in google_caps
        
        meta_caps = manager.get_platform_capabilities("meta_ads")
        assert "campaign_management" in meta_caps
        assert "audience_targeting" in meta_caps

    def test_get_platform_cost_info(self, platform_manager_simple):
        """Test getting platform cost information"""
        manager, mock_adapters = platform_manager_simple
        
        google_cost = manager.get_platform_cost_info(Platform.GOOGLE_ADS)
        assert "cost_per_request" in google_cost
        assert "monthly_free" in google_cost
        
        stripe_cost = manager.get_platform_cost_info("stripe")
        assert stripe_cost["cost_per_request"] == 0.029

    @pytest.mark.asyncio
    async def test_get_system_health(self, platform_manager_simple):
        """Test getting system health status"""
        manager, mock_adapters = platform_manager_simple
        
        health = await manager.get_system_health()
        
        assert "platforms" in health
        assert "total_integrations" in health
        assert "active_integrations" in health
        assert "health_score" in health
        assert "timestamp" in health
        
        assert health["total_integrations"] == 8
        assert isinstance(health["health_score"], (int, float))

    @pytest.mark.asyncio
    async def test_handle_google_ads_create_campaign(self, platform_manager_simple):
        """Test Google Ads campaign creation"""
        manager, mock_adapters = platform_manager_simple
        
        mock_adapters[Platform.GOOGLE_ADS].create_campaign.return_value = "google_campaign_123"
        
        result = await manager._handle_google_ads_action(
            mock_adapters[Platform.GOOGLE_ADS],
            "create_campaign",
            "test-org-123",
            {
                "account_id": "account_123",
                "campaign_data": {"name": "Google Campaign", "budget": 1000}
            }
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == "google_campaign_123"
        assert result["platform"] == "google_ads"

    @pytest.mark.asyncio
    async def test_handle_meta_ads_create_campaign(self, platform_manager_simple):
        """Test Meta Ads campaign creation"""
        manager, mock_adapters = platform_manager_simple
        
        mock_adapters[Platform.META_ADS].create_campaign.return_value = "meta_campaign_123"
        
        result = await manager._handle_meta_ads_action(
            mock_adapters[Platform.META_ADS],
            "create_campaign",
            "test-org-123",
            {
                "account_id": "account_123",
                "campaign_data": {"name": "Meta Campaign", "objective": "CONVERSIONS"}
            }
        )
        
        assert result["status"] == "success"
        assert result["campaign_id"] == "meta_campaign_123"
        assert result["platform"] == "meta_ads"

    @pytest.mark.asyncio
    async def test_handle_gohighlevel_create_contact(self, platform_manager_simple):
        """Test GoHighLevel contact creation"""
        manager, mock_adapters = platform_manager_simple
        
        mock_adapters[Platform.GOHIGHLEVEL].create_contact.return_value = "contact_123"
        
        result = await manager._handle_gohighlevel_action(
            mock_adapters[Platform.GOHIGHLEVEL],
            "create_contact",
            "test-org-123",
            {
                "location_id": "location_123",
                "contact_data": {"email": "test@example.com", "name": "Test User"}
            }
        )
        
        assert result["status"] == "success"
        assert result["contact_id"] == "contact_123"
        assert result["platform"] == "gohighlevel"

    @pytest.mark.asyncio
    async def test_handle_shopify_get_products(self, platform_manager_simple):
        """Test Shopify products retrieval"""
        manager, mock_adapters = platform_manager_simple
        
        mock_products_data = {
            "products": [{"id": "prod_1", "title": "Product 1"}, {"id": "prod_2", "title": "Product 2"}],
            "has_next_page": False
        }
        mock_adapters[Platform.SHOPIFY].get_products.return_value = mock_products_data
        
        result = await manager._handle_shopify_action(
            mock_adapters[Platform.SHOPIFY],
            "get_products",
            "test-org-123",
            {"shop_domain": "test-shop.myshopify.com", "limit": 50}
        )
        
        assert result["status"] == "success"
        assert len(result["products"]) == 2
        assert result["has_next_page"] is False

    @pytest.mark.asyncio
    async def test_handle_stripe_create_payment_intent(self, platform_manager_simple):
        """Test Stripe payment intent creation"""
        manager, mock_adapters = platform_manager_simple
        
        mock_payment_intent = {"id": "pi_123", "status": "requires_payment_method"}
        mock_adapters[Platform.STRIPE].create_payment_intent.return_value = mock_payment_intent
        
        result = await manager._handle_stripe_action(
            mock_adapters[Platform.STRIPE],
            "create_payment_intent",
            "test-org-123",
            {
                "account_id": "acct_123",
                "payment_data": {"amount": 2000, "currency": "usd"}
            }
        )
        
        assert result["status"] == "success"
        assert result["payment_intent"] == mock_payment_intent

    def test_platform_enum_validation(self, platform_manager_simple):
        """Test platform enum validation"""
        manager, mock_adapters = platform_manager_simple
        
        # Test valid platforms
        assert Platform.GOOGLE_ADS.value == "google_ads"
        assert Platform.META_ADS.value == "meta_ads"
        assert Platform.SHOPIFY.value == "shopify"
        
        # Test invalid platform
        with pytest.raises(ValueError):
            Platform("invalid_platform")

    @pytest.mark.asyncio
    async def test_platform_action_routing_error(self, platform_manager_simple):
        """Test platform action routing error"""
        manager, mock_adapters = platform_manager_simple
        
        # Test with unsupported platform enum
        with pytest.raises(ValueError) as exc_info:
            await manager._route_platform_action(
                mock_adapters[Platform.GOOGLE_ADS],
                Platform.GOOGLE_ANALYTICS,  # Not handled in routing
                "create_campaign",
                "test-org-123",
                {}
            )
        
        assert "No handler for platform" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_google_ads_unknown_action(self, platform_manager_simple):
        """Test Google Ads unknown action handling"""
        manager, mock_adapters = platform_manager_simple
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_google_ads_action(
                mock_adapters[Platform.GOOGLE_ADS],
                "unknown_action",
                "test-org-123",
                {}
            )
        
        assert "Unknown Google Ads action" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_meta_ads_unknown_action(self, platform_manager_simple):
        """Test Meta Ads unknown action handling"""
        manager, mock_adapters = platform_manager_simple
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_meta_ads_action(
                mock_adapters[Platform.META_ADS],
                "unknown_action",
                "test-org-123",
                {}
            )
        
        assert "Unknown Meta Ads action" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_gohighlevel_unknown_action(self, platform_manager_simple):
        """Test GoHighLevel unknown action handling"""
        manager, mock_adapters = platform_manager_simple
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_gohighlevel_action(
                mock_adapters[Platform.GOHIGHLEVEL],
                "unknown_action",
                "test-org-123",
                {}
            )
        
        assert "Unknown GoHighLevel action" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_shopify_unknown_action(self, platform_manager_simple):
        """Test Shopify unknown action handling"""
        manager, mock_adapters = platform_manager_simple
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_shopify_action(
                mock_adapters[Platform.SHOPIFY],
                "unknown_action",
                "test-org-123",
                {}
            )
        
        assert "Unknown Shopify action" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_stripe_unknown_action(self, platform_manager_simple):
        """Test Stripe unknown action handling"""
        manager, mock_adapters = platform_manager_simple
        
        with pytest.raises(ValueError) as exc_info:
            await manager._handle_stripe_action(
                mock_adapters[Platform.STRIPE],
                "unknown_action",
                "test-org-123",
                {}
            )
        
        assert "Unknown Stripe action" in str(exc_info.value)
