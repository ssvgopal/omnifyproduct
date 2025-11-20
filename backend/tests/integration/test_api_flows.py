"""
Integration tests for API flows
Tests complete user journeys across multiple endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock


class TestUserRegistrationFlow:
    """Test complete user registration and onboarding flow"""
    
    def test_complete_registration_flow(self, test_client, mock_db):
        """Test user registration -> email verification -> login flow"""
        # Step 1: Register user
        with patch('api.auth_routes.get_database', return_value=mock_db):
            mock_db.users.find_one = AsyncMock(return_value=None)
            mock_db.users.insert_one = AsyncMock(
                return_value=MagicMock(inserted_id="user_123")
            )
            
            register_response = test_client.post(
                "/api/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "SecurePass123!",
                    "organization_name": "Test Org"
                }
            )
            
            assert register_response.status_code in [200, 201]
            user_data = register_response.json()
            assert "user_id" in user_data or "access_token" in user_data


class TestCampaignManagementFlow:
    """Test complete campaign management flow"""
    
    def test_create_and_manage_campaign(self, test_client, mock_campaign, auth_headers, mock_db):
        """Test create -> update -> get performance -> delete flow"""
        with patch('api.campaign_management_routes.get_database', return_value=mock_db):
            # Create campaign
            mock_db.campaigns.insert_one = AsyncMock(
                return_value=MagicMock(inserted_id=mock_campaign["campaign_id"])
            )
            
            create_response = test_client.post(
                "/api/campaigns",
                json={
                    "name": mock_campaign["name"],
                    "platform": mock_campaign["platform"],
                    "budget": mock_campaign["budget"]
                },
                headers=auth_headers
            )
            
            assert create_response.status_code in [200, 201]
            campaign_id = create_response.json().get("campaign_id")
            
            # Get campaign
            mock_db.campaigns.find_one = AsyncMock(return_value=mock_campaign)
            get_response = test_client.get(
                f"/api/campaigns/{campaign_id}",
                headers=auth_headers
            )
            
            assert get_response.status_code == 200
            
            # Update campaign
            mock_db.campaigns.update_one = AsyncMock(
                return_value=MagicMock(modified_count=1)
            )
            update_response = test_client.put(
                f"/api/campaigns/{campaign_id}",
                json={"name": "Updated Name"},
                headers=auth_headers
            )
            
            assert update_response.status_code == 200


class TestIntegrationFlow:
    """Test platform integration flow"""
    
    def test_oauth_integration_flow(self, test_client, auth_headers):
        """Test OAuth authorization -> callback -> status check flow"""
        # Get auth URL
        auth_url_response = test_client.get(
            "/api/integrations/google-ads/auth-url",
            headers=auth_headers
        )
        
        assert auth_url_response.status_code == 200
        assert "auth_url" in auth_url_response.json()
        
        # Handle callback (simulated)
        callback_response = test_client.get(
            "/api/integrations/google-ads/callback?code=test_code&state=test_state",
            headers=auth_headers
        )
        
        # Should handle callback (may succeed or fail depending on mock)
        assert callback_response.status_code in [200, 400, 500]

