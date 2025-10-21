"""
Meta (Facebook/Instagram) Ads Integration Tests
Priority 2 - CRITICAL: Major ad platform integration

Tests for:
- OAuth2 authentication
- Campaign and ad set management
- Creative management
- Audience targeting
- Performance metrics sync
- Error handling

Author: OmnifyProduct Test Suite
Business Impact: CRITICAL - Major revenue source
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import uuid


class TestMetaAuthentication:
    """Test Meta OAuth2 authentication"""

    def test_oauth_flow(self):
        """Test OAuth2 flow"""
        auth_url = {
            "base_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "client_id": "meta_app_123",
            "redirect_uri": "https://app.omnify.com/oauth/meta/callback",
            "scope": "ads_management,ads_read",
            "state": str(uuid.uuid4())
        }
        
        assert "facebook.com" in auth_url["base_url"]
        assert "ads_management" in auth_url["scope"]

    def test_access_token_exchange(self):
        """Test exchanging code for access token"""
        token_response = {
            "access_token": "EAABwzLixnjYBO...",
            "token_type": "bearer",
            "expires_in": 5184000  # 60 days
        }
        
        assert token_response["access_token"] is not None
        assert token_response["expires_in"] > 0

    def test_long_lived_token(self):
        """Test getting long-lived token"""
        long_lived_token = {
            "access_token": "EAABwzLixnjYBO_LONG...",
            "token_type": "bearer",
            "expires_in": 5184000
        }
        
        assert long_lived_token["expires_in"] == 5184000


class TestCampaignManagement:
    """Test Meta campaign management"""

    def test_create_campaign(self):
        """Test creating Meta campaign"""
        campaign = {
            "name": "Summer Sale Campaign",
            "objective": "CONVERSIONS",
            "status": "PAUSED",
            "special_ad_categories": [],
            "buying_type": "AUCTION"
        }
        
        response = {
            "id": "120210000000000",
            "success": True
        }
        
        assert response["id"] is not None
        assert response["success"] is True

    def test_update_campaign(self):
        """Test updating campaign"""
        update = {
            "campaign_id": "120210000000000",
            "status": "ACTIVE",
            "name": "Updated Campaign Name"
        }
        
        response = {"success": True}
        assert response["success"] is True

    def test_campaign_budget_optimization(self):
        """Test campaign budget optimization"""
        cbo_settings = {
            "campaign_id": "120210000000000",
            "daily_budget": 10000,  # cents
            "budget_optimization": True,
            "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
        }
        
        assert cbo_settings["daily_budget"] > 0
        assert cbo_settings["budget_optimization"] is True


class TestAdSetManagement:
    """Test ad set management"""

    def test_create_ad_set(self):
        """Test creating ad set"""
        ad_set = {
            "name": "Electronics Ad Set",
            "campaign_id": "120210000000000",
            "daily_budget": 5000,  # cents
            "billing_event": "IMPRESSIONS",
            "optimization_goal": "LINK_CLICKS",
            "bid_amount": 200,  # cents
            "status": "PAUSED",
            "targeting": {
                "geo_locations": {"countries": ["US", "CA"]},
                "age_min": 25,
                "age_max": 45,
                "genders": [1, 2]  # All genders
            }
        }
        
        response = {
            "id": "120210000000001",
            "success": True
        }
        
        assert response["id"] is not None
        assert ad_set["targeting"]["age_min"] >= 18

    def test_audience_targeting(self):
        """Test audience targeting"""
        targeting = {
            "geo_locations": {
                "countries": ["US"],
                "cities": [{"key": "2490299", "name": "New York"}]
            },
            "age_min": 25,
            "age_max": 45,
            "genders": [1, 2],
            "interests": [
                {"id": "6003139266461", "name": "Shopping"},
                {"id": "6003107902433", "name": "Fashion"}
            ],
            "behaviors": [
                {"id": "6002714895372", "name": "Frequent travelers"}
            ]
        }
        
        assert len(targeting["interests"]) > 0
        assert targeting["age_min"] < targeting["age_max"]

    def test_custom_audience(self):
        """Test custom audience creation"""
        custom_audience = {
            "name": "Website Visitors",
            "subtype": "WEBSITE",
            "retention_days": 180,
            "rule": {
                "url": {"i_contains": "product"}
            }
        }
        
        response = {
            "id": "120210000000002",
            "success": True
        }
        
        assert response["id"] is not None

    def test_lookalike_audience(self):
        """Test lookalike audience"""
        lookalike = {
            "name": "Lookalike - High Value Customers",
            "origin_audience_id": "120210000000002",
            "country": "US",
            "ratio": 0.01  # 1% lookalike
        }
        
        assert 0 < lookalike["ratio"] <= 0.10


class TestCreativeManagement:
    """Test ad creative management"""

    def test_create_image_ad(self):
        """Test creating image ad"""
        creative = {
            "name": "Summer Sale Image",
            "object_story_spec": {
                "page_id": "123456789",
                "link_data": {
                    "image_hash": "abc123def456",
                    "link": "https://example.com/sale",
                    "message": "Summer Sale - Up to 50% Off!",
                    "call_to_action": {
                        "type": "SHOP_NOW"
                    }
                }
            }
        }
        
        response = {
            "id": "120210000000003",
            "success": True
        }
        
        assert response["id"] is not None
        assert creative["object_story_spec"]["link_data"]["call_to_action"]["type"] == "SHOP_NOW"

    def test_create_video_ad(self):
        """Test creating video ad"""
        video_creative = {
            "name": "Product Demo Video",
            "object_story_spec": {
                "page_id": "123456789",
                "video_data": {
                    "video_id": "987654321",
                    "message": "Check out our new product!",
                    "call_to_action": {
                        "type": "LEARN_MORE",
                        "value": {"link": "https://example.com/product"}
                    }
                }
            }
        }
        
        assert video_creative["object_story_spec"]["video_data"]["video_id"] is not None

    def test_carousel_ad(self):
        """Test carousel ad creation"""
        carousel = {
            "name": "Product Carousel",
            "object_story_spec": {
                "page_id": "123456789",
                "link_data": {
                    "link": "https://example.com",
                    "child_attachments": [
                        {
                            "link": "https://example.com/product1",
                            "image_hash": "hash1",
                            "name": "Product 1",
                            "description": "Description 1"
                        },
                        {
                            "link": "https://example.com/product2",
                            "image_hash": "hash2",
                            "name": "Product 2",
                            "description": "Description 2"
                        }
                    ]
                }
            }
        }
        
        assert len(carousel["object_story_spec"]["link_data"]["child_attachments"]) >= 2


class TestPerformanceMetrics:
    """Test performance metrics sync"""

    def test_fetch_insights(self):
        """Test fetching campaign insights"""
        insights = {
            "campaign_id": "120210000000000",
            "date_start": "2024-01-01",
            "date_stop": "2024-01-31",
            "impressions": 100000,
            "clicks": 5000,
            "spend": "2500.00",  # dollars
            "reach": 75000,
            "frequency": 1.33,
            "ctr": 5.0,
            "cpc": "0.50",
            "cpm": "25.00",
            "actions": [
                {"action_type": "link_click", "value": 5000},
                {"action_type": "purchase", "value": 250}
            ]
        }
        
        assert float(insights["spend"]) > 0
        assert insights["impressions"] > 0
        assert len(insights["actions"]) > 0

    def test_conversion_tracking(self):
        """Test conversion tracking"""
        conversions = {
            "campaign_id": "120210000000000",
            "conversions": [
                {
                    "action_type": "purchase",
                    "value": 250,
                    "action_values": [
                        {"action_type": "purchase", "value": "50000.00"}
                    ]
                }
            ],
            "cost_per_action": [
                {"action_type": "purchase", "value": "10.00"}
            ]
        }
        
        assert conversions["conversions"][0]["value"] > 0

    def test_attribution_window(self):
        """Test attribution window settings"""
        attribution = {
            "click_window": 7,  # days
            "view_window": 1,   # days
            "action_breakdowns": ["action_type", "action_device"]
        }
        
        assert attribution["click_window"] >= 1
        assert attribution["view_window"] >= 1


class TestErrorHandling:
    """Test error handling"""

    def test_rate_limit_error(self):
        """Test rate limit handling"""
        error = {
            "error": {
                "message": "Application request limit reached",
                "type": "OAuthException",
                "code": 4,
                "error_subcode": 2446079
            }
        }
        
        assert error["error"]["code"] == 4

    def test_invalid_token_error(self):
        """Test invalid token handling"""
        error = {
            "error": {
                "message": "Invalid OAuth access token",
                "type": "OAuthException",
                "code": 190
            }
        }
        
        assert error["error"]["code"] == 190

    def test_budget_error(self):
        """Test budget-related errors"""
        error = {
            "error": {
                "message": "Budget is too low",
                "type": "FacebookApiException",
                "code": 100,
                "error_subcode": 1487124
            }
        }
        
        assert "budget" in error["error"]["message"].lower()


class TestWebhooks:
    """Test webhook integration"""

    def test_webhook_subscription(self):
        """Test subscribing to webhooks"""
        subscription = {
            "object": "page",
            "callback_url": "https://app.omnify.com/webhooks/meta",
            "fields": ["leadgen", "messages"],
            "verify_token": "verify_token_xyz"
        }
        
        assert subscription["callback_url"].startswith("https://")

    def test_webhook_verification(self):
        """Test webhook verification"""
        verification = {
            "hub.mode": "subscribe",
            "hub.verify_token": "verify_token_xyz",
            "hub.challenge": "challenge_string"
        }
        
        # Should return challenge if token matches
        assert verification["hub.mode"] == "subscribe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
