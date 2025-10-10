"""
Integration Tests for Omnify Cloud Connect API
"""

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os

# Import our application
from agentkit_server import app, get_db
from services.auth_service import AuthService
from models.user_models import UserCreate, UserLogin


@pytest.fixture
async def test_db():
    """Create test database"""
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client["omnify_test_integration"]

    # Clean all collections
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()

    yield db

    # Clean up
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()

    client.close()


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def auth_service(test_db):
    """Create auth service for testing"""
    jwt_secret = "test_jwt_secret_integration"
    return AuthService(test_db, jwt_secret)


@pytest.fixture
async def test_user(auth_service):
    """Create a test user and return user data with token"""
    user_data = UserCreate(
        email="test@example.com",
        password="test_password_123",
        full_name="Test User",
        organization_name="Test Organization"
    )

    user = await auth_service.create_user(user_data)
    org = await auth_service.get_organization(user.organization_id)
    token = await auth_service.create_user_token(user, org)

    return {
        "user": user,
        "organization": org,
        "token": token
    }


class TestAuthAPI:
    """Test authentication API endpoints"""

    @pytest.mark.asyncio
    async def test_register_endpoint(self, client, test_db):
        """Test user registration endpoint"""
        user_data = {
            "email": "register@example.com",
            "password": "register_password_123",
            "full_name": "Register User",
            "organization_name": "Register Org"
        }

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert "organization" in data
        assert data["user"]["email"] == "register@example.com"
        assert data["user"]["full_name"] == "Register User"
        assert data["organization"]["name"] == "Register Org"

    @pytest.mark.asyncio
    async def test_login_endpoint(self, client, test_user):
        """Test user login endpoint"""
        login_data = {
            "email": "test@example.com",
            "password": "test_password_123"
        }

        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert "organization" in data
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        login_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }

        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_refresh_token(self, client, test_user):
        """Test token refresh endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.post("/api/auth/refresh", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert "organization" in data

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, test_user):
        """Test get current user endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/auth/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "owner"

    @pytest.mark.asyncio
    async def test_update_current_user(self, client, test_user):
        """Test update current user endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        update_data = {
            "full_name": "Updated Test User",
            "preferences": {"theme": "dark"}
        }

        response = await client.put("/api/auth/me", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["full_name"] == "Updated Test User"

    @pytest.mark.asyncio
    async def test_verify_token(self, client, test_user):
        """Test token verification endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/auth/verify", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["user_id"] == test_user["user"]["user_id"]
        assert data["organization_id"] == test_user["organization"]["organization_id"]

    @pytest.mark.asyncio
    async def test_verify_invalid_token(self, client):
        """Test token verification with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}

        response = await client.get("/api/auth/verify", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

    @pytest.mark.asyncio
    async def test_get_organization(self, client, test_user):
        """Test get current organization endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/auth/organization", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["organization_id"] == test_user["organization"]["organization_id"]
        assert data["name"] == test_user["organization"]["name"]
        assert data["subscription_tier"] == "starter"

    @pytest.mark.asyncio
    async def test_update_organization(self, client, test_user):
        """Test update organization endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        update_data = {
            "name": "Updated Organization Name",
            "settings": {"theme": "dark"}
        }

        response = await client.put("/api/auth/organization", json=update_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_password_reset_request(self, client, test_user):
        """Test password reset request endpoint"""
        reset_data = {
            "email": "test@example.com"
        }

        response = await client.post("/api/auth/password/reset-request", json=reset_data)

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_get_usage_limits(self, client, test_user):
        """Test get usage limits endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/auth/limits", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "organization_id" in data
        assert "subscription_tier" in data
        assert "limits" in data
        assert "users" in data["limits"]
        assert "campaigns" in data["limits"]


class TestAgentKitAPI:
    """Test AgentKit API endpoints"""

    @pytest.mark.asyncio
    async def test_create_agent(self, client, test_user):
        """Test create agent endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        agent_data = {
            "agent_id": "api_test_agent_001",
            "name": "API Test Agent",
            "type": "creative_intelligence",
            "description": "Agent created via API test",
            "capabilities": ["content_analysis"],
            "configuration": {"model": "gpt-4"}
        }

        response = await client.post("/api/agentkit/agents", json=agent_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "api_test_agent_001"
        assert data["name"] == "API Test Agent"
        assert data["type"] == "creative_intelligence"

    @pytest.mark.asyncio
    async def test_get_agent(self, client, test_user):
        """Test get agent endpoint"""
        # First create an agent
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        agent_data = {
            "agent_id": "get_test_agent_001",
            "name": "Get Test Agent",
            "type": "marketing_automation",
            "description": "Agent for get test"
        }

        await client.post("/api/agentkit/agents", json=agent_data, headers=headers)

        # Now get the agent
        response = await client.get("/api/agentkit/agents/get_test_agent_001", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "get_test_agent_001"
        assert data["name"] == "Get Test Agent"

    @pytest.mark.asyncio
    async def test_list_agents(self, client, test_user):
        """Test list agents endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/agentkit/agents", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should include default agents created during org setup

    @pytest.mark.asyncio
    async def test_execute_agent(self, client, test_user):
        """Test execute agent endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        # Create an agent first
        agent_data = {
            "agent_id": "execute_test_agent_001",
            "name": "Execute Test Agent",
            "type": "creative_intelligence"
        }

        await client.post("/api/agentkit/agents", json=agent_data, headers=headers)

        # Execute the agent
        execution_data = {
            "input_data": {"test": "data"},
            "organization_id": test_user["organization"]["organization_id"]
        }

        response = await client.post(
            "/api/agentkit/agents/execute_test_agent_001/execute",
            json=execution_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data
        assert "agent_id" in data

    @pytest.mark.asyncio
    async def test_create_workflow(self, client, test_user):
        """Test create workflow endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        workflow_data = {
            "workflow_id": "api_workflow_test_001",
            "name": "API Test Workflow",
            "description": "Workflow created via API test",
            "steps": [
                {
                    "step_id": "step_1",
                    "agent_id": "test_agent",
                    "action": "analyze",
                    "parameters": {"input": "test"}
                }
            ],
            "triggers": ["manual"],
            "organization_id": test_user["organization"]["organization_id"]
        }

        response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "api_workflow_test_001"
        assert data["name"] == "API Test Workflow"

    @pytest.mark.asyncio
    async def test_compliance_check(self, client, test_user):
        """Test compliance check endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.post("/api/agentkit/compliance/check", json={"check_type": "soc2"}, headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "findings" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, client, test_user):
        """Test get audit logs endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/agentkit/audit-logs", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_metrics(self, client, test_user):
        """Test get agent metrics endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        response = await client.get("/api/agentkit/metrics?days=30", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert test_user["organization"]["organization_id"] in data


class TestSpecializedAgents:
    """Test specialized agent endpoints"""

    @pytest.mark.asyncio
    async def test_creative_intelligence_analyze(self, client, test_user):
        """Test creative intelligence analysis endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        analysis_data = {
            "asset_url": "https://example.com/content.jpg",
            "asset_type": "image",
            "analysis_type": "aida",
            "target_platforms": ["google_ads", "meta_ads"]
        }

        response = await client.post(
            "/api/agentkit/creative-intelligence/analyze",
            json=analysis_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_marketing_automation_execute(self, client, test_user):
        """Test marketing automation execution endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        automation_data = {
            "campaign_id": "campaign_test_001",
            "action": "deploy",
            "platforms": ["google_ads"],
            "campaign_config": {
                "name": "Test Campaign",
                "objective": "conversions",
                "budget_daily": 50
            }
        }

        response = await client.post(
            "/api/agentkit/marketing-automation/execute",
            json=automation_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_client_management_execute(self, client, test_user):
        """Test client management execution endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        management_data = {
            "action": "onboard",
            "client_data": {
                "email": "client@example.com",
                "full_name": "Test Client",
                "company": "Test Company"
            }
        }

        response = await client.post(
            "/api/agentkit/client-management/execute",
            json=management_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_analytics_analyze(self, client, test_user):
        """Test analytics analysis endpoint"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}

        analytics_data = {
            "analysis_type": "performance",
            "date_range": {
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            },
            "metrics": ["impressions", "clicks", "conversions"]
        }

        response = await client.post(
            "/api/agentkit/analytics/analyze",
            json=analytics_data,
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "execution_id" in data
        assert "status" in data


class TestHealthAndCore:
    """Test health and core endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "architecture" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_api_info(self, client):
        """Test API info endpoint"""
        response = await client.get("/api/info")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "architecture" in data
        assert "endpoints" in data


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
