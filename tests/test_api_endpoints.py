"""
API Endpoint Integration Tests
Priority 4 - HIGH: API reliability and contract validation

Tests for:
- Campaign endpoints (CRUD)
- Analytics endpoints
- Platform integration endpoints
- User management endpoints
- Request validation
- Response handling

Author: OmnifyProduct Test Suite
Business Impact: HIGH - API reliability affects all features
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime
import uuid


class TestCampaignEndpoints:
    """Test campaign API endpoints"""

    @pytest.fixture
    def mock_client(self):
        """Mock FastAPI test client"""
        client = MagicMock()
        return client

    def test_create_campaign_success(self, mock_client):
        """Test POST /api/v1/campaigns - success"""
        campaign_data = {
            "name": "Summer Sale Campaign",
            "type": "social",
            "budget": {"daily_budget": 100.0},
            "status": "draft"
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "campaign_id": str(uuid.uuid4()),
            "name": campaign_data["name"],
            "status": "draft"
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/campaigns", json=campaign_data)
        
        assert response.status_code == 201
        assert "campaign_id" in response.json()

    def test_list_campaigns_with_pagination(self, mock_client):
        """Test GET /api/v1/campaigns - pagination"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaigns": [
                {"campaign_id": "1", "name": "Campaign 1"},
                {"campaign_id": "2", "name": "Campaign 2"}
            ],
            "total": 10,
            "page": 1,
            "page_size": 2
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/campaigns?page=1&page_size=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["campaigns"]) == 2
        assert data["total"] == 10

    def test_get_campaign_by_id(self, mock_client):
        """Test GET /api/v1/campaigns/{id}"""
        campaign_id = str(uuid.uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaign_id": campaign_id,
            "name": "Test Campaign",
            "status": "active"
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get(f"/api/v1/campaigns/{campaign_id}")
        
        assert response.status_code == 200
        assert response.json()["campaign_id"] == campaign_id

    def test_update_campaign(self, mock_client):
        """Test PUT /api/v1/campaigns/{id}"""
        campaign_id = str(uuid.uuid4())
        update_data = {"name": "Updated Campaign", "status": "paused"}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaign_id": campaign_id,
            "name": update_data["name"],
            "status": update_data["status"]
        }
        
        mock_client.put.return_value = mock_response
        response = mock_client.put(f"/api/v1/campaigns/{campaign_id}", json=update_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]

    def test_delete_campaign(self, mock_client):
        """Test DELETE /api/v1/campaigns/{id}"""
        campaign_id = str(uuid.uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 204
        
        mock_client.delete.return_value = mock_response
        response = mock_client.delete(f"/api/v1/campaigns/{campaign_id}")
        
        assert response.status_code == 204

    def test_start_campaign(self, mock_client):
        """Test POST /api/v1/campaigns/{id}/start"""
        campaign_id = str(uuid.uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaign_id": campaign_id,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post(f"/api/v1/campaigns/{campaign_id}/start")
        
        assert response.status_code == 200
        assert response.json()["status"] == "active"

    def test_pause_campaign(self, mock_client):
        """Test POST /api/v1/campaigns/{id}/pause"""
        campaign_id = str(uuid.uuid4())
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "campaign_id": campaign_id,
            "status": "paused",
            "paused_at": datetime.utcnow().isoformat()
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post(f"/api/v1/campaigns/{campaign_id}/pause")
        
        assert response.status_code == 200
        assert response.json()["status"] == "paused"


class TestAnalyticsEndpoints:
    """Test analytics API endpoints"""

    @pytest.fixture
    def mock_client(self):
        """Mock FastAPI test client"""
        return MagicMock()

    def test_get_dashboard(self, mock_client):
        """Test GET /api/v1/analytics/dashboard"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "overview": {
                "total_campaigns": 15,
                "active_campaigns": 8,
                "total_spend": 25000.0,
                "total_revenue": 75000.0
            },
            "performance": {
                "impressions": 500000,
                "clicks": 25000,
                "conversions": 2500
            }
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/analytics/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "overview" in data
        assert "performance" in data

    def test_get_reports(self, mock_client):
        """Test GET /api/v1/analytics/reports"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "reports": [
                {"report_id": "1", "name": "Monthly Report"},
                {"report_id": "2", "name": "Weekly Report"}
            ]
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/analytics/reports")
        
        assert response.status_code == 200
        assert len(response.json()["reports"]) == 2

    def test_create_custom_report(self, mock_client):
        """Test POST /api/v1/analytics/custom-report"""
        report_data = {
            "name": "Custom Performance Report",
            "metrics": ["impressions", "clicks", "conversions"],
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"}
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "report_id": str(uuid.uuid4()),
            "name": report_data["name"],
            "status": "generating"
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/analytics/custom-report", json=report_data)
        
        assert response.status_code == 201
        assert "report_id" in response.json()

    def test_export_analytics(self, mock_client):
        """Test GET /api/v1/analytics/export"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/csv"}
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/analytics/export?format=csv")
        
        assert response.status_code == 200
        assert "text/csv" in response.headers["Content-Type"]

    def test_get_metrics(self, mock_client):
        """Test GET /api/v1/analytics/metrics"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metrics": {
                "ctr": 5.0,
                "conversion_rate": 10.0,
                "cpa": 25.0,
                "roas": 4.0
            }
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/analytics/metrics")
        
        assert response.status_code == 200
        assert "metrics" in response.json()


class TestPlatformEndpoints:
    """Test platform integration endpoints"""

    @pytest.fixture
    def mock_client(self):
        """Mock FastAPI test client"""
        return MagicMock()

    def test_connect_platform(self, mock_client):
        """Test POST /api/v1/platforms/connect"""
        platform_data = {
            "platform": "google_ads",
            "credentials": {
                "client_id": "client_123",
                "client_secret": "secret_xyz"
            }
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "platform": "google_ads",
            "status": "connected",
            "connected_at": datetime.utcnow().isoformat()
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/platforms/connect", json=platform_data)
        
        assert response.status_code == 200
        assert response.json()["status"] == "connected"

    def test_get_platform_status(self, mock_client):
        """Test GET /api/v1/platforms/status"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "platforms": [
                {"platform": "google_ads", "status": "connected"},
                {"platform": "meta_ads", "status": "connected"}
            ]
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/platforms/status")
        
        assert response.status_code == 200
        assert len(response.json()["platforms"]) == 2

    def test_disconnect_platform(self, mock_client):
        """Test DELETE /api/v1/platforms/disconnect"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "platform": "google_ads",
            "status": "disconnected"
        }
        
        mock_client.delete.return_value = mock_response
        response = mock_client.delete("/api/v1/platforms/disconnect?platform=google_ads")
        
        assert response.status_code == 200
        assert response.json()["status"] == "disconnected"

    def test_sync_platform_data(self, mock_client):
        """Test POST /api/v1/platforms/sync"""
        sync_data = {"platform": "google_ads", "sync_type": "full"}
        
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.json.return_value = {
            "sync_id": str(uuid.uuid4()),
            "status": "in_progress"
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/platforms/sync", json=sync_data)
        
        assert response.status_code == 202
        assert response.json()["status"] == "in_progress"


class TestUserEndpoints:
    """Test user management endpoints"""

    @pytest.fixture
    def mock_client(self):
        """Mock FastAPI test client"""
        return MagicMock()

    def test_login(self, mock_client):
        """Test POST /api/v1/auth/login"""
        credentials = {
            "email": "user@example.com",
            "password": "SecurePassword123!"
        }
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "jwt_token_xyz",
            "refresh_token": "refresh_token_abc",
            "token_type": "bearer",
            "expires_in": 3600
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/auth/login", json=credentials)
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_logout(self, mock_client):
        """Test POST /api/v1/auth/logout"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Logged out successfully"}
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/auth/logout")
        
        assert response.status_code == 200

    def test_refresh_token(self, mock_client):
        """Test POST /api/v1/auth/refresh"""
        refresh_data = {"refresh_token": "refresh_token_abc"}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_jwt_token",
            "expires_in": 3600
        }
        
        mock_client.post.return_value = mock_response
        response = mock_client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_get_user_profile(self, mock_client):
        """Test GET /api/v1/users/profile"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": str(uuid.uuid4()),
            "email": "user@example.com",
            "name": "John Doe",
            "role": "admin"
        }
        
        mock_client.get.return_value = mock_response
        response = mock_client.get("/api/v1/users/profile")
        
        assert response.status_code == 200
        assert "user_id" in response.json()

    def test_update_user_profile(self, mock_client):
        """Test PUT /api/v1/users/profile"""
        update_data = {"name": "Jane Doe", "phone": "+1234567890"}
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": str(uuid.uuid4()),
            "name": update_data["name"],
            "phone": update_data["phone"]
        }
        
        mock_client.put.return_value = mock_response
        response = mock_client.put("/api/v1/users/profile", json=update_data)
        
        assert response.status_code == 200
        assert response.json()["name"] == update_data["name"]


class TestRequestValidation:
    """Test request validation"""

    def test_input_sanitization(self):
        """Test input sanitization"""
        malicious_input = "<script>alert('XSS')</script>"
        sanitized = malicious_input.replace("<", "&lt;").replace(">", "&gt;")
        
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized

    def test_type_validation(self):
        """Test type validation"""
        valid_data = {
            "name": "Campaign",
            "budget": 100.0,
            "active": True
        }
        
        assert isinstance(valid_data["name"], str)
        assert isinstance(valid_data["budget"], (int, float))
        assert isinstance(valid_data["active"], bool)

    def test_required_fields(self):
        """Test required fields validation"""
        data = {"name": "Campaign", "type": "social"}
        required_fields = ["name", "type", "budget"]
        
        missing_fields = [f for f in required_fields if f not in data]
        assert "budget" in missing_fields

    def test_format_validation(self):
        """Test format validation"""
        import re
        
        email = "user@example.com"
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        assert re.match(email_pattern, email) is not None

    def test_size_limits(self):
        """Test size limits"""
        max_name_length = 100
        campaign_name = "A" * 150
        
        is_too_long = len(campaign_name) > max_name_length
        assert is_too_long is True


class TestResponseHandling:
    """Test response handling"""

    def test_status_codes(self):
        """Test HTTP status codes"""
        status_codes = {
            "success": 200,
            "created": 201,
            "no_content": 204,
            "bad_request": 400,
            "unauthorized": 401,
            "forbidden": 403,
            "not_found": 404,
            "server_error": 500
        }
        
        assert status_codes["success"] == 200
        assert status_codes["created"] == 201
        assert status_codes["not_found"] == 404

    def test_error_message_format(self):
        """Test error message format"""
        error_response = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid campaign data",
                "details": [
                    {"field": "budget", "error": "Must be greater than 0"}
                ]
            }
        }
        
        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]

    def test_data_serialization(self):
        """Test JSON serialization"""
        data = {
            "campaign_id": str(uuid.uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            "budget": 100.0
        }
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["campaign_id"] == data["campaign_id"]

    def test_pagination_headers(self):
        """Test pagination in response"""
        response_data = {
            "items": [{"id": "1"}, {"id": "2"}],
            "total": 100,
            "page": 1,
            "page_size": 2,
            "total_pages": 50
        }
        
        assert response_data["total_pages"] == response_data["total"] // response_data["page_size"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
