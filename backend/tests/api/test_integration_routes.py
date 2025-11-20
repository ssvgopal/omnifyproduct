"""
Tests for Integration API Routes
"""

import pytest
from fastapi import status
from unittest.mock import AsyncMock, patch


class TestIntegrationRoutes:
    """Test integration management endpoints"""
    
    def test_get_integration_auth_url(self, test_client, auth_headers):
        """Test get OAuth authorization URL"""
        response = test_client.get(
            "/api/integrations/google-ads/auth-url",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "auth_url" in response.json()
    
    def test_handle_integration_callback(self, test_client, auth_headers):
        """Test OAuth callback handling"""
        response = test_client.get(
            "/api/integrations/google-ads/callback?code=test_code&state=test_state",
            headers=auth_headers
        )
        # Should return 200 on success or 400 on error
        assert response.status_code in [200, 400]
    
    def test_get_integration_status(self, test_client, mock_integration, auth_headers, mock_db):
        """Test get integration status"""
        mock_db.integrations.find_one = AsyncMock(return_value=mock_integration)
        
        with patch('api.google_ads_oauth_routes.get_database', return_value=mock_db):
            response = test_client.get(
                "/api/integrations/google-ads/status",
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
    
    def test_disconnect_integration(self, test_client, mock_integration, auth_headers, mock_db):
        """Test disconnect integration"""
        mock_db.integrations.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
        
        with patch('api.google_ads_oauth_routes.get_database', return_value=mock_db):
            response = test_client.post(
                "/api/integrations/google-ads/disconnect",
                headers=auth_headers
            )
            assert response.status_code in [200, 204]

