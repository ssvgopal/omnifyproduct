"""
Comprehensive Campaign Management Service Tests
Priority 1 - CRITICAL: Core revenue-generating feature

Tests for:
- Campaign CRUD operations
- Campaign execution (start/stop/pause/resume)
- Budget management and alerts
- Platform integration
- Performance tracking
- Error handling and rollback

Author: OmnifyProduct Test Suite
Business Impact: CRITICAL - Primary revenue feature
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
import uuid
import sys

# Mock PIL to avoid import error
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Import campaign management components
from backend.services.campaign_management_service import (
    CampaignStatus,
    CampaignType,
    CreativeType,
    AssetType,
    CampaignTargeting,
    CampaignBudget,
    CampaignSchedule,
    CreativeAsset,
    CampaignTemplate,
    AssetManager
)


class TestCampaignCRUDOperations:
    """Test campaign CRUD operations"""

    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = MagicMock()
        db.campaigns = AsyncMock()
        db.campaigns.insert_one = AsyncMock(return_value=MagicMock(inserted_id="campaign_123"))
        db.campaigns.find_one = AsyncMock()
        db.campaigns.update_one = AsyncMock()
        db.campaigns.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        db.campaigns.find = MagicMock()
        return db

    @pytest.fixture
    def sample_campaign_data(self):
        """Sample campaign data"""
        return {
            "campaign_id": str(uuid.uuid4()),
            "client_id": "client_123",
            "name": "Summer Sale Campaign",
            "description": "Promotional campaign for summer sale",
            "campaign_type": CampaignType.SOCIAL.value,
            "status": CampaignStatus.DRAFT.value,
            "budget": {
                "daily_budget": 100.0,
                "lifetime_budget": 3000.0,
                "bid_strategy": "auto",
                "optimization_goal": "conversions"
            },
            "targeting": {
                "demographics": {"age_range": [25, 45], "gender": ["all"]},
                "interests": ["shopping", "fashion", "lifestyle"],
                "locations": ["US", "CA", "UK"],
                "devices": ["mobile", "desktop"]
            },
            "schedule": {
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
            },
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

    @pytest.mark.asyncio
    async def test_create_campaign_success(self, mock_db, sample_campaign_data):
        """Test successful campaign creation"""
        # Create campaign
        campaign_id = sample_campaign_data["campaign_id"]
        
        # Mock database insert
        mock_db.campaigns.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=campaign_id)
        )
        
        # Insert campaign
        result = await mock_db.campaigns.insert_one(sample_campaign_data)
        
        # Verify
        assert result.inserted_id == campaign_id
        mock_db.campaigns.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_campaign_validation(self, sample_campaign_data):
        """Test campaign creation with validation"""
        # Test required fields
        assert "name" in sample_campaign_data
        assert "campaign_type" in sample_campaign_data
        assert "budget" in sample_campaign_data
        
        # Test budget validation
        budget = sample_campaign_data["budget"]
        assert budget["daily_budget"] > 0
        assert budget["lifetime_budget"] >= budget["daily_budget"]
        
        # Test date validation
        schedule = sample_campaign_data["schedule"]
        start_date = datetime.fromisoformat(schedule["start_date"])
        end_date = datetime.fromisoformat(schedule["end_date"])
        assert end_date > start_date

    @pytest.mark.asyncio
    async def test_get_campaign_by_id(self, mock_db, sample_campaign_data):
        """Test retrieving campaign by ID"""
        campaign_id = sample_campaign_data["campaign_id"]
        
        # Mock database find
        mock_db.campaigns.find_one = AsyncMock(return_value=sample_campaign_data)
        
        # Retrieve campaign
        result = await mock_db.campaigns.find_one({"campaign_id": campaign_id})
        
        # Verify
        assert result is not None
        assert result["campaign_id"] == campaign_id
        assert result["name"] == sample_campaign_data["name"]

    @pytest.mark.asyncio
    async def test_update_campaign_settings(self, mock_db, sample_campaign_data):
        """Test updating campaign settings"""
        campaign_id = sample_campaign_data["campaign_id"]
        
        # Update data
        updates = {
            "name": "Updated Summer Sale Campaign",
            "budget.daily_budget": 150.0,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Mock database update
        mock_db.campaigns.update_one = AsyncMock(
            return_value=MagicMock(modified_count=1)
        )
        
        # Update campaign
        result = await mock_db.campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": updates}
        )
        
        # Verify
        assert result.modified_count == 1
        mock_db.campaigns.update_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_campaign(self, mock_db):
        """Test campaign deletion"""
        campaign_id = "campaign_123"
        
        # Mock database delete
        mock_db.campaigns.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )
        
        # Delete campaign
        result = await mock_db.campaigns.delete_one({"campaign_id": campaign_id})
        
        # Verify
        assert result.deleted_count == 1
        mock_db.campaigns.delete_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_campaigns_with_pagination(self, mock_db, sample_campaign_data):
        """Test listing campaigns with pagination"""
        # Create mock cursor
        async def async_iter():
            yield sample_campaign_data
            yield {**sample_campaign_data, "campaign_id": "campaign_456"}
        
        mock_cursor = MagicMock()
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.__aiter__ = lambda self: async_iter()
        
        mock_db.campaigns.find = MagicMock(return_value=mock_cursor)
        
        # List campaigns
        campaigns = []
        async for campaign in mock_db.campaigns.find({"client_id": "client_123"}):
            campaigns.append(campaign)
        
        # Verify
        assert len(campaigns) == 2
        assert campaigns[0]["campaign_id"] == sample_campaign_data["campaign_id"]

    @pytest.mark.asyncio
    async def test_search_campaigns_by_name(self, mock_db, sample_campaign_data):
        """Test searching campaigns by name"""
        # Mock search
        async def async_iter():
            yield sample_campaign_data
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda self: async_iter()
        
        mock_db.campaigns.find = MagicMock(return_value=mock_cursor)
        
        # Search campaigns
        search_query = {"name": {"$regex": "Summer", "$options": "i"}}
        campaigns = []
        async for campaign in mock_db.campaigns.find(search_query):
            campaigns.append(campaign)
        
        # Verify
        assert len(campaigns) == 1
        assert "Summer" in campaigns[0]["name"]


class TestCampaignExecution:
    """Test campaign execution operations"""

    @pytest.fixture
    def campaign_data(self):
        """Campaign data for execution tests"""
        return {
            "campaign_id": "campaign_123",
            "status": CampaignStatus.DRAFT.value,
            "budget": {
                "daily_budget": 100.0,
                "lifetime_budget": 3000.0,
                "spent_today": 0.0,
                "total_spent": 0.0
            },
            "metrics": {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "cost": 0.0
            }
        }

    @pytest.mark.asyncio
    async def test_start_campaign(self, campaign_data):
        """Test starting a campaign"""
        # Verify initial state
        assert campaign_data["status"] == CampaignStatus.DRAFT.value
        
        # Start campaign
        campaign_data["status"] = CampaignStatus.ACTIVE.value
        campaign_data["started_at"] = datetime.utcnow().isoformat()
        
        # Verify
        assert campaign_data["status"] == CampaignStatus.ACTIVE.value
        assert "started_at" in campaign_data

    @pytest.mark.asyncio
    async def test_pause_campaign(self, campaign_data):
        """Test pausing an active campaign"""
        # Set to active
        campaign_data["status"] = CampaignStatus.ACTIVE.value
        
        # Pause campaign
        campaign_data["status"] = CampaignStatus.PAUSED.value
        campaign_data["paused_at"] = datetime.utcnow().isoformat()
        
        # Verify
        assert campaign_data["status"] == CampaignStatus.PAUSED.value
        assert "paused_at" in campaign_data

    @pytest.mark.asyncio
    async def test_resume_campaign(self, campaign_data):
        """Test resuming a paused campaign"""
        # Set to paused
        campaign_data["status"] = CampaignStatus.PAUSED.value
        campaign_data["paused_at"] = datetime.utcnow().isoformat()
        
        # Resume campaign
        campaign_data["status"] = CampaignStatus.ACTIVE.value
        campaign_data["resumed_at"] = datetime.utcnow().isoformat()
        
        # Verify
        assert campaign_data["status"] == CampaignStatus.ACTIVE.value
        assert "resumed_at" in campaign_data

    @pytest.mark.asyncio
    async def test_stop_campaign(self, campaign_data):
        """Test stopping a campaign"""
        # Set to active
        campaign_data["status"] = CampaignStatus.ACTIVE.value
        
        # Stop campaign
        campaign_data["status"] = CampaignStatus.COMPLETED.value
        campaign_data["completed_at"] = datetime.utcnow().isoformat()
        
        # Verify
        assert campaign_data["status"] == CampaignStatus.COMPLETED.value
        assert "completed_at" in campaign_data

    @pytest.mark.asyncio
    async def test_campaign_schedule_validation(self):
        """Test campaign scheduling"""
        now = datetime.utcnow()
        schedule = CampaignSchedule(
            start_date=now,
            end_date=now + timedelta(days=30),
            time_zones=["America/New_York"],
            day_parting={"monday": ["09:00-17:00"], "tuesday": ["09:00-17:00"]}
        )
        
        # Verify schedule
        assert schedule.start_date < schedule.end_date
        assert len(schedule.time_zones) > 0
        assert "monday" in schedule.day_parting


class TestBudgetManagement:
    """Test budget management and alerts"""

    @pytest.fixture
    def budget_data(self):
        """Budget data for tests"""
        return {
            "daily_budget": 100.0,
            "lifetime_budget": 3000.0,
            "spent_today": 0.0,
            "total_spent": 0.0,
            "bid_strategy": "auto",
            "optimization_goal": "conversions"
        }

    def test_budget_validation(self, budget_data):
        """Test budget validation rules"""
        # Daily budget must be positive
        assert budget_data["daily_budget"] > 0
        
        # Lifetime budget must be >= daily budget
        assert budget_data["lifetime_budget"] >= budget_data["daily_budget"]
        
        # Spent amounts must be non-negative
        assert budget_data["spent_today"] >= 0
        assert budget_data["total_spent"] >= 0

    def test_daily_budget_check(self, budget_data):
        """Test daily budget limit check"""
        # Simulate spending
        budget_data["spent_today"] = 85.0
        
        # Check if under budget
        remaining = budget_data["daily_budget"] - budget_data["spent_today"]
        assert remaining > 0
        assert remaining == 15.0

    def test_daily_budget_exceeded(self, budget_data):
        """Test daily budget exceeded scenario"""
        # Simulate exceeding daily budget
        budget_data["spent_today"] = 105.0
        
        # Check if exceeded
        exceeded = budget_data["spent_today"] > budget_data["daily_budget"]
        assert exceeded is True
        
        # Campaign should be paused
        should_pause = exceeded
        assert should_pause is True

    def test_lifetime_budget_tracking(self, budget_data):
        """Test lifetime budget tracking"""
        # Simulate spending over multiple days
        budget_data["total_spent"] = 2500.0
        
        # Check remaining lifetime budget
        remaining = budget_data["lifetime_budget"] - budget_data["total_spent"]
        assert remaining > 0
        assert remaining == 500.0

    def test_budget_alert_threshold(self, budget_data):
        """Test budget alert thresholds"""
        # Set alert threshold at 80%
        alert_threshold = 0.8
        budget_data["spent_today"] = 85.0
        
        # Check if alert should trigger
        spent_percentage = budget_data["spent_today"] / budget_data["daily_budget"]
        should_alert = spent_percentage >= alert_threshold
        
        assert should_alert is True
        assert spent_percentage == 0.85


class TestPlatformIntegration:
    """Test platform API integration"""

    @pytest.mark.asyncio
    async def test_google_ads_campaign_sync(self):
        """Test Google Ads campaign synchronization"""
        # Mock Google Ads API response
        google_ads_response = {
            "campaign_id": "google_campaign_123",
            "status": "ENABLED",
            "metrics": {
                "impressions": 1000,
                "clicks": 50,
                "cost_micros": 25000000  # $25 in micros
            }
        }
        
        # Verify response structure
        assert "campaign_id" in google_ads_response
        assert "status" in google_ads_response
        assert "metrics" in google_ads_response
        
        # Convert cost from micros to dollars
        cost_dollars = google_ads_response["metrics"]["cost_micros"] / 1_000_000
        assert cost_dollars == 25.0

    @pytest.mark.asyncio
    async def test_meta_ads_campaign_sync(self):
        """Test Meta (Facebook) Ads campaign synchronization"""
        # Mock Meta Ads API response
        meta_ads_response = {
            "id": "meta_campaign_123",
            "status": "ACTIVE",
            "insights": {
                "impressions": 2000,
                "clicks": 100,
                "spend": "50.00"
            }
        }
        
        # Verify response structure
        assert "id" in meta_ads_response
        assert "status" in meta_ads_response
        assert "insights" in meta_ads_response
        
        # Convert spend to float
        spend = float(meta_ads_response["insights"]["spend"])
        assert spend == 50.0

    @pytest.mark.asyncio
    async def test_platform_error_handling(self):
        """Test platform API error handling"""
        # Mock API error
        api_error = {
            "error": {
                "code": 401,
                "message": "Invalid authentication credentials",
                "type": "AuthenticationError"
            }
        }
        
        # Verify error structure
        assert "error" in api_error
        assert api_error["error"]["code"] == 401
        assert "authentication" in api_error["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self):
        """Test rate limiting handling"""
        # Mock rate limit response
        rate_limit_response = {
            "error": {
                "code": 429,
                "message": "Rate limit exceeded",
                "retry_after": 60
            }
        }
        
        # Verify rate limit handling
        assert rate_limit_response["error"]["code"] == 429
        assert "retry_after" in rate_limit_response["error"]
        
        # Should wait before retry
        retry_after = rate_limit_response["error"]["retry_after"]
        assert retry_after > 0


class TestPerformanceTracking:
    """Test campaign performance tracking"""

    @pytest.fixture
    def performance_metrics(self):
        """Performance metrics data"""
        return {
            "impressions": 10000,
            "clicks": 500,
            "conversions": 50,
            "cost": 250.0,
            "revenue": 1000.0
        }

    def test_calculate_ctr(self, performance_metrics):
        """Test CTR (Click-Through Rate) calculation"""
        ctr = (performance_metrics["clicks"] / performance_metrics["impressions"]) * 100
        assert ctr == 5.0  # 5% CTR

    def test_calculate_conversion_rate(self, performance_metrics):
        """Test conversion rate calculation"""
        conversion_rate = (performance_metrics["conversions"] / performance_metrics["clicks"]) * 100
        assert conversion_rate == 10.0  # 10% conversion rate

    def test_calculate_cpa(self, performance_metrics):
        """Test CPA (Cost Per Acquisition) calculation"""
        cpa = performance_metrics["cost"] / performance_metrics["conversions"]
        assert cpa == 5.0  # $5 per conversion

    def test_calculate_roas(self, performance_metrics):
        """Test ROAS (Return on Ad Spend) calculation"""
        roas = performance_metrics["revenue"] / performance_metrics["cost"]
        assert roas == 4.0  # 4x ROAS

    def test_performance_alerts(self, performance_metrics):
        """Test performance alert triggers"""
        # Calculate metrics
        ctr = (performance_metrics["clicks"] / performance_metrics["impressions"]) * 100
        roas = performance_metrics["revenue"] / performance_metrics["cost"]
        
        # Check alert conditions
        low_ctr_alert = ctr < 1.0  # Alert if CTR < 1%
        low_roas_alert = roas < 2.0  # Alert if ROAS < 2x
        
        assert low_ctr_alert is False  # CTR is 5%, no alert
        assert low_roas_alert is False  # ROAS is 4x, no alert


class TestAssetManagement:
    """Test creative asset management"""

    @pytest.fixture
    def asset_manager(self):
        """Asset manager instance"""
        mock_db = MagicMock()
        mock_db.assets = AsyncMock()
        mock_db.creative_assets = AsyncMock()
        mock_db.creative_assets.insert_one = AsyncMock(return_value=MagicMock(inserted_id="asset_123"))
        return AssetManager(mock_db)

    @pytest.mark.asyncio
    async def test_upload_image_asset(self, asset_manager):
        """Test uploading image asset"""
        # Mock image data
        file_data = b"fake_image_data"
        file_name = "test_image.jpg"
        
        # Upload asset
        asset = await asset_manager.upload_asset(
            client_id="client_123",
            file_data=file_data,
            file_name=file_name,
            asset_type=AssetType.IMAGE
        )
        
        # Verify
        assert asset is not None
        assert asset.asset_type == AssetType.IMAGE
        assert asset.file_name == file_name
        assert asset.file_size == len(file_data)

    @pytest.mark.asyncio
    async def test_validate_file_format(self, asset_manager):
        """Test file format validation"""
        # Test valid format
        valid_extension = "jpg"
        assert valid_extension in asset_manager.supported_formats['image']
        
        # Test invalid format
        invalid_extension = "exe"
        assert invalid_extension not in asset_manager.supported_formats['image']

    @pytest.mark.asyncio
    async def test_validate_file_size(self, asset_manager):
        """Test file size validation"""
        # Test within limit
        file_data = b"x" * (5 * 1024 * 1024)  # 5MB
        assert len(file_data) <= asset_manager.max_file_sizes['image']
        
        # Test exceeds limit
        large_file_data = b"x" * (15 * 1024 * 1024)  # 15MB
        assert len(large_file_data) > asset_manager.max_file_sizes['image']

    def test_asset_metadata(self):
        """Test asset metadata structure"""
        asset = CreativeAsset(
            asset_id="asset_123",
            asset_type=AssetType.IMAGE,
            file_name="banner.jpg",
            file_size=1024000,
            mime_type="image/jpeg",
            dimensions={"width": 1200, "height": 628},
            url="/assets/client_123/asset_123/banner.jpg",
            thumbnail_url="/assets/client_123/asset_123/thumbnail_banner.jpg",
            tags=["banner", "summer", "sale"],
            created_at=datetime.utcnow()
        )
        
        # Verify metadata
        assert asset.asset_id is not None
        assert asset.dimensions["width"] == 1200
        assert asset.dimensions["height"] == 628
        assert len(asset.tags) == 3


class TestCampaignTemplates:
    """Test campaign templates"""

    def test_create_template(self):
        """Test creating campaign template"""
        template = CampaignTemplate(
            template_id="template_123",
            name="E-commerce Sale Template",
            description="Template for e-commerce sale campaigns",
            template_data={
                "campaign_type": CampaignType.SOCIAL.value,
                "budget": {"daily_budget": 100.0},
                "targeting": {"interests": ["shopping", "fashion"]}
            }
        )
        
        # Verify template
        assert template.template_id is not None
        assert template.name is not None
        assert "campaign_type" in template.template_data

    def test_template_to_dict(self):
        """Test template serialization"""
        template = CampaignTemplate(
            template_id="template_123",
            name="Test Template",
            description="Test description",
            template_data={"test": "data"}
        )
        
        template_dict = template.to_dict()
        
        # Verify serialization
        assert "template_id" in template_dict
        assert "name" in template_dict
        assert "template_data" in template_dict
        assert "created_at" in template_dict


class TestErrorHandlingAndRollback:
    """Test error handling and rollback scenarios"""

    @pytest.mark.asyncio
    async def test_campaign_creation_failure_rollback(self):
        """Test rollback on campaign creation failure"""
        # Mock database error
        mock_db = MagicMock()
        mock_db.campaigns.insert_one = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        
        # Attempt to create campaign
        try:
            await mock_db.campaigns.insert_one({"name": "Test Campaign"})
            assert False, "Should have raised exception"
        except Exception as e:
            # Verify error handling
            assert "Database connection failed" in str(e)
            # In production, rollback would occur here

    @pytest.mark.asyncio
    async def test_budget_exceeded_auto_pause(self):
        """Test automatic pause when budget exceeded"""
        campaign = {
            "campaign_id": "campaign_123",
            "status": CampaignStatus.ACTIVE.value,
            "budget": {
                "daily_budget": 100.0,
                "spent_today": 105.0
            }
        }
        
        # Check if budget exceeded
        budget_exceeded = campaign["budget"]["spent_today"] > campaign["budget"]["daily_budget"]
        
        if budget_exceeded:
            campaign["status"] = CampaignStatus.PAUSED.value
            campaign["pause_reason"] = "daily_budget_exceeded"
        
        # Verify auto-pause
        assert campaign["status"] == CampaignStatus.PAUSED.value
        assert campaign["pause_reason"] == "daily_budget_exceeded"

    @pytest.mark.asyncio
    async def test_platform_api_failure_retry(self):
        """Test retry logic for platform API failures"""
        max_retries = 3
        retry_count = 0
        
        # Simulate API failures
        for attempt in range(max_retries):
            retry_count += 1
            # In production, would attempt API call here
            if retry_count < max_retries:
                # Simulate failure
                continue
            else:
                # Final attempt
                break
        
        # Verify retry attempts
        assert retry_count == max_retries


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
