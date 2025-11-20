"""
Tests for Campaign Management API Routes
"""

import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch


class TestCampaignRoutes:
    """Test campaign management endpoints"""
    
    def test_create_campaign_success(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test successful campaign creation"""
        mock_db.campaigns.insert_one = AsyncMock(return_value=MagicMock(inserted_id="campaign_123"))
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.post(
                "/api/campaigns",
                json={
                    "name": mock_campaign["name"],
                    "platform": mock_campaign["platform"],
                    "budget": mock_campaign["budget"]
                },
                headers=auth_headers
            )
            assert response.status_code in [200, 201]
            assert "campaign_id" in response.json()
    
    def test_get_campaign(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test get campaign by ID"""
        mock_db.campaigns.find_one = AsyncMock(return_value=mock_campaign)
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.get(
                f"/api/campaigns/{mock_campaign['campaign_id']}",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["campaign_id"] == mock_campaign["campaign_id"]
    
    def test_list_campaigns(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test list campaigns"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[mock_campaign])
        mock_db.campaigns.find = AsyncMock(return_value=mock_cursor)
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.get(
                "/api/campaigns",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert isinstance(response.json(), list)
    
    def test_update_campaign(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test update campaign"""
        mock_db.campaigns.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.put(
                f"/api/campaigns/{mock_campaign['campaign_id']}",
                json={"name": "Updated Campaign Name"},
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
    
    def test_delete_campaign(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test delete campaign"""
        mock_db.campaigns.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.delete(
                f"/api/campaigns/{mock_campaign['campaign_id']}",
                headers=auth_headers
            )
            assert response.status_code in [200, 204]
    
    def test_get_campaign_performance(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test get campaign performance metrics"""
        mock_db.campaigns.find_one = AsyncMock(return_value=mock_campaign)
        
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            response = test_client.get(
                f"/api/campaigns/{mock_campaign['campaign_id']}/performance",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK

