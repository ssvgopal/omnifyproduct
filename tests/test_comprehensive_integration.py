"""
Comprehensive Integration Tests for OmnifyProduct
Tests all API endpoints, workflows, and business logic
"""

import pytest
import asyncio
from httpx import AsyncClient
from typing import Dict, Any

# Import our application and services
from agentkit_server import app
from services.auth_service import AuthService
from services.agentkit_service import AgentKitService
from services.validation_service import ValidationService
from models.agentkit_models import (
    AgentConfig, WorkflowDefinition, AgentExecutionRequest
)


class TestHealthEndpoints:
    """Test health check and system information endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    @pytest.mark.asyncio
    async def test_api_info(self, client: AsyncClient):
        """Test API information endpoint"""
        response = await client.get("/api/info")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "OmnifyProduct API"
        assert data["version"] == "2.0.0"


class TestOrganizationSetup:
    """Test organization management and setup"""

    @pytest.mark.asyncio
    async def test_create_organization(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test organization creation"""
        org_data = {
            "name": "Test Organization",
            "subscription_tier": "enterprise"
        }

        response = await client.post("/api/organizations", json=org_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["organization_id"] is not None
        assert data["name"] == "Test Organization"


class TestAgentManagement:
    """Test AgentKit agent lifecycle management"""

    @pytest.mark.asyncio
    async def test_create_agent(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test agent creation"""
        agent_config = {
            "name": "Test Creative Agent",
            "agent_type": "creative_intelligence",
            "description": "Test agent for creative analysis",
            "organization_id": test_organization["organization_id"],
            "config": {
                "platforms": ["google_ads", "meta_ads"],
                "analysis_types": ["aida", "brand_compliance"]
            }
        }

        response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["agent_id"] is not None
        assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_list_agents(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test listing agents for an organization"""
        response = await client.get(
            f"/api/agentkit/agents?organization_id={test_organization['organization_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_execute_agent(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test agent execution"""
        # First create an agent
        agent_config = {
            "name": "Test Execution Agent",
            "agent_type": "creative_intelligence",
            "description": "Agent for testing execution",
            "organization_id": test_organization["organization_id"],
            "config": {"platforms": ["google_ads"]}
        }

        # Create agent
        create_response = await client.post("/api/agentkit/agents", json=agent_config, headers=auth_headers)
        assert create_response.status_code == 200
        agent_id = create_response.json()["agent_id"]

        # Execute agent
        execution_request = {
            "input_data": {
                "asset_url": "https://example.com/test-creative.jpg",
                "analysis_type": "aida"
            },
            "context": {
                "user_id": "test_user_123",
                "session_id": "test_session_789"
            }
        }

        response = await client.post(
            f"/api/agentkit/agents/{agent_id}/execute",
            json=execution_request,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["execution_id"] is not None
        assert data["status"] in ["completed", "in_progress"]


class TestWorkflowManagement:
    """Test workflow orchestration and execution"""

    @pytest.mark.asyncio
    async def test_create_workflow(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test workflow creation"""
        workflow_data = {
            "name": "Test Campaign Workflow",
            "description": "Test workflow for campaign creation",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "creative_analysis",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"asset_url": "campaign_creative_url"},
                    "output_mapping": {"aida_scores": "campaign_aida_scores"}
                },
                {
                    "step_id": "campaign_creation",
                    "agent_type": "marketing_automation",
                    "depends_on": ["creative_analysis"],
                    "input_mapping": {"config": "campaign_config"},
                    "output_mapping": {"campaign_ids": "deployment_results"}
                }
            ]
        }

        response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["workflow_id"] is not None
        assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_execute_workflow(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test workflow execution"""
        # Create a simple workflow first
        workflow_data = {
            "name": "Simple Test Workflow",
            "description": "Simple workflow for testing",
            "organization_id": test_organization["organization_id"],
            "steps": [
                {
                    "step_id": "analysis",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {"asset_url": "test_asset_url"},
                    "output_mapping": {"result": "analysis_result"}
                }
            ]
        }

        # Create workflow
        create_response = await client.post("/api/agentkit/workflows", json=workflow_data, headers=auth_headers)
        assert create_response.status_code == 200
        workflow_id = create_response.json()["workflow_id"]

        # Execute workflow
        execution_data = {
            "input_data": {
                "test_asset_url": "https://example.com/test.jpg",
                "campaign_config": {"name": "Test Campaign"}
            }
        }

        response = await client.post(
            f"/api/agentkit/workflows/{workflow_id}/execute",
            json=execution_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["execution_id"] is not None
        assert data["status"] in ["completed", "in_progress"]


class TestComplianceAndAudit:
    """Test compliance checking and audit logging"""

    @pytest.mark.asyncio
    async def test_run_compliance_check(self, client: AsyncClient, auth_headers: Dict[str, str], test_organization: Dict[str, Any]):
        """Test SOC 2 compliance checking"""
        compliance_data = {
            "check_type": "soc2",
            "organization_id": test_organization["organization_id"]
        }

        response = await client.post("/api/agentkit/compliance/check", json=compliance_data, headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["check_id"] is not None
        assert data["organization_id"] == test_organization["organization_id"]


class TestErrorHandling:
    """Test error handling and validation"""

    @pytest.mark.asyncio
    async def test_validation_errors(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test input validation error handling"""
        # Test invalid agent type
        invalid_data = {
            "name": "Test Agent",
            "agent_type": "invalid_type",  # Invalid agent type
            "config": {}
        }

        response = await client.post("/api/agentkit/agents", json=invalid_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_authentication_errors(self, client: AsyncClient):
        """Test authentication error handling"""
        response = await client.get("/api/agentkit/agents", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_not_found_errors(self, client: AsyncClient, auth_headers: Dict[str, str]):
        """Test 404 error handling"""
        response = await client.get("/api/agentkit/agents/non_existent_agent", headers=auth_headers)
        assert response.status_code == 404


class TestValidationService:
    """Test the validation service directly"""

    def test_email_validation(self):
        """Test email validation"""
        from services.validation_service import ValidationService

        # Valid email
        result = ValidationService.validate_email("test@example.com")
        assert result == "test@example.com"

        # Invalid email
        with pytest.raises(Exception):
            ValidationService.validate_email("invalid-email")

    def test_phone_validation(self):
        """Test phone validation"""
        from services.validation_service import ValidationService

        # Valid US phone
        result = ValidationService.validate_phone("(555) 123-4567", "us")
        assert result == "+15551234567"

        # Invalid phone
        with pytest.raises(Exception):
            ValidationService.validate_phone("invalid", "us")
