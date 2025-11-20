"""
Tests for Campaign Management Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from services.campaign_management_service import CampaignManagementService


@pytest.mark.asyncio
class TestCampaignService:
    """Test campaign management service"""
    
    async def test_create_custom_campaign(self, mock_db, mock_user):
        """Test custom campaign creation"""
        service = CampaignManagementService(mock_db)
        
        campaign_config = {
            "name": "Test Campaign",
            "campaign_type": "search",
            "budget": {"daily_budget": 1000.0},
            "targeting": {"locations": ["US"]}
        }
        
        # Mock the campaign builder
        with patch.object(service.campaign_builder, 'create_custom_campaign', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = {
                "campaign_id": "campaign_123",
                "name": "Test Campaign",
                "status": "draft"
            }
            
            result = await service.create_custom_campaign(mock_user["organization_id"], campaign_config)
            
            assert result is not None
            assert "campaign_id" in result
    
    async def test_get_campaign(self, mock_db, mock_campaign):
        """Test get campaign by ID"""
        service = CampaignManagementService(mock_db)
        
        # Mock the campaign builder
        with patch.object(service.campaign_builder, 'get_campaign', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_campaign
            
            result = await service.get_campaign(
                mock_campaign["campaign_id"],
                mock_campaign["organization_id"]
            )
            
            assert result is not None
            assert result["campaign_id"] == mock_campaign["campaign_id"]
    
    async def test_get_client_campaigns(self, mock_db, mock_campaign, mock_user):
        """Test list client campaigns"""
        service = CampaignManagementService(mock_db)
        
        # Mock the campaign builder
        with patch.object(service.campaign_builder, 'get_client_campaigns', new_callable=AsyncMock) as mock_list:
            mock_list.return_value = [mock_campaign]
            
            result = await service.get_client_campaigns(mock_user["organization_id"])
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    async def test_update_campaign(self, mock_db, mock_campaign):
        """Test update campaign"""
        service = CampaignManagementService(mock_db)
        
        # Mock the campaign builder
        with patch.object(service.campaign_builder, 'update_campaign', new_callable=AsyncMock) as mock_update:
            mock_update.return_value = {**mock_campaign, "name": "Updated Name"}
            
            update_data = {"name": "Updated Campaign Name"}
            
            result = await service.update_campaign(
                mock_campaign["campaign_id"],
                mock_campaign["organization_id"],
                update_data
            )
            
            assert result is not None
            assert result["name"] == "Updated Name"

