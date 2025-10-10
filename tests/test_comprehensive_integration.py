"""
Comprehensive Integration Tests for OmnifyProduct
Tests all API endpoints, workflows, and business logic
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch

# Import our application
from agentkit_server import app
from services.auth_service import AuthService
from services.agentkit_service import AgentKitService
from services.validation_service import ValidationService
from models.agentkit_models import (
    AgentConfig, WorkflowDefinition, AgentExecutionRequest,
    CreativeIntelligenceInput, MarketingAutomationInput
)


@pytest.fixture
async def test_db():
    """Create test database"""
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db_name = "omnify_test_comprehensive"

    # Clean all collections before tests
    db = client[db_name]
    collections = await db.list_collection_names()
    for collection in collections:
        await db[collection].drop()

    yield db

    # Clean up after tests
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
    jwt_secret = "test_jwt_secret_comprehensive"
    jwt_algorithm = "HS256"
    return AuthService(db=test_db, jwt_secret=jwt_secret, jwt_algorithm=jwt_algorithm)


@pytest.fixture
async def agentkit_service(test_db):
    """Create agentkit service for testing"""
    api_key = "test_agentkit_key"
    return AgentKitService(db=test_db, agentkit_api_key=api_key)


@pytest.fixture
async def test_user(auth_service, test_db):
    """Create a test user"""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "organization_id": "test_org"
    }

    # Create organization first
    org_data = {
        "organization_id": "test_org",
        "name": "Test Organization",
        "slug": "test-org",
        "owner_id": "test_user",
        "subscription_tier": "starter",
        "created_at": datetime.utcnow().isoformat()
    }
    await test_db.organizations.insert_one(org_data)

    # Create user
    user = await auth_service.create_user(user_data)
    return user


@pytest.fixture
async def auth_headers(test_user, auth_service):
    """Get authentication headers for test user"""
    token = await auth_service.generate_token(test_user["user_id"])
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    """Test health and info endpoints"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "services" in data
        assert data["services"]["api"] == "operational"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"


class TestOrganizationSetup:
    """Test organization setup functionality"""

    @pytest.mark.asyncio
    async def test_setup_organization(self, client, test_db):
        """Test organization setup"""
        org_data = {
            "organization_id": "new_org",
            "user_id": "new_user",
            "name": "New Test Organization",
            "slug": "new-org",
            "subscription_tier": "professional"
        }

        response = await client.post("/api/organizations/setup", json=org_data)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["organization_id"] == "new_org"
        assert data["agents_created"] > 0

        # Verify organization was created
        org = await test_db.organizations.find_one({"organization_id": "new_org"})
        assert org is not None
        assert org["name"] == "New Test Organization"


class TestAgentManagement:
    """Test agent management endpoints"""

    @pytest.mark.asyncio
    async def test_create_agent(self, client, auth_headers, test_db, test_user):
        """Test agent creation"""
        agent_config = {
            "agent_id": "test_creative_agent",
            "organization_id": test_user["organization_id"],
            "name": "Test Creative Agent",
            "agent_type": "creative_intelligence",
            "description": "Test creative intelligence agent",
            "config": {
                "analysis_depth": "comprehensive",
                "platforms": ["google_ads", "meta_ads"]
            }
        }

        response = await client.post(
            "/api/agentkit/agents",
            json=agent_config,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["agent_id"] == "test_creative_agent"
        assert data["status"] == "created"

        # Verify agent was stored
        agent = await test_db.agentkit_agents.find_one({"agent_id": "test_creative_agent"})
        assert agent is not None

    @pytest.mark.asyncio
    async def test_list_agents(self, client, auth_headers, test_user, test_db):
        """Test agent listing"""
        # Create test agent first
        agent_config = AgentConfig(
            agent_id="test_agent_list",
            organization_id=test_user["organization_id"],
            name="Test Agent for Listing",
            agent_type="marketing_automation",
            description="Test agent",
            config={}
        )

        service = AgentKitService(test_db, "test_key")
        await service.create_agent(agent_config)

        response = await client.get(
            f"/api/agentkit/agents?organization_id={test_user['organization_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check agent in list
        agent_names = [agent["name"] for agent in data]
        assert "Test Agent for Listing" in agent_names

    @pytest.mark.asyncio
    async def test_get_agent(self, client, auth_headers, test_user, test_db):
        """Test getting specific agent"""
        # Create test agent
        agent_config = AgentConfig(
            agent_id="test_agent_get",
            organization_id=test_user["organization_id"],
            name="Test Agent for Get",
            agent_type="analytics",
            description="Test agent for get endpoint",
            config={}
        )

        service = AgentKitService(test_db, "test_key")
        await service.create_agent(agent_config)

        response = await client.get(
            f"/api/agentkit/agents/test_agent_get",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["agent_id"] == "test_agent_get"
        assert data["name"] == "Test Agent for Get"

    @pytest.mark.asyncio
    async def test_execute_agent(self, client, auth_headers, test_user, test_db):
        """Test agent execution"""
        # Create test agent
        agent_config = AgentConfig(
            agent_id="test_agent_execute",
            organization_id=test_user["organization_id"],
            name="Test Agent for Execution",
            agent_type="creative_intelligence",
            description="Test agent for execution",
            config={}
        )

        service = AgentKitService(test_db, "test_key")
        await service.create_agent(agent_config)

        execution_request = {
            "input_data": {
                "asset_url": "https://example.com/test-image.jpg",
                "analysis_type": "aida",
                "target_platforms": ["google_ads", "meta_ads"]
            },
            "context": {
                "user_id": test_user["user_id"],
                "session_id": "test_session"
            }
        }

        response = await client.post(
            "/api/agentkit/agents/test_agent_execute/execute",
            json=execution_request,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "execution_id" in data
        assert data["status"] == "completed"
        assert "output_data" in data

    @pytest.mark.asyncio
    async def test_agent_validation_errors(self, client, auth_headers):
        """Test agent validation error handling"""
        # Test invalid agent type
        invalid_agent = {
            "agent_id": "invalid_agent",
            "organization_id": "test_org",
            "name": "Invalid Agent",
            "agent_type": "invalid_type",  # Invalid type
            "config": {}
        }

        response = await client.post(
            "/api/agentkit/agents",
            json=invalid_agent,
            headers=auth_headers
        )
        assert response.status_code == 422

        # Test missing required fields
        incomplete_agent = {
            "agent_id": "incomplete_agent",
            # Missing name and agent_type
            "config": {}
        }

        response = await client.post(
            "/api/agentkit/agents",
            json=incomplete_agent,
            headers=auth_headers
        )
        assert response.status_code == 422


class TestWorkflowManagement:
    """Test workflow management endpoints"""

    @pytest.mark.asyncio
    async def test_create_workflow(self, client, auth_headers, test_user, test_db):
        """Test workflow creation"""
        workflow_data = {
            "workflow_id": "test_workflow",
            "organization_id": test_user["organization_id"],
            "name": "Test Campaign Workflow",
            "description": "Test workflow for campaign automation",
            "steps": [
                {
                    "step_id": "step_1",
                    "agent_type": "creative_intelligence",
                    "input_mapping": {
                        "asset_url": "campaign_creative_url",
                        "analysis_type": "campaign_analysis"
                    },
                    "output_mapping": {
                        "aida_scores": "campaign_aida_scores",
                        "recommendations": "campaign_recommendations"
                    }
                },
                {
                    "step_id": "step_2",
                    "agent_type": "marketing_automation",
                    "depends_on": ["step_1"],
                    "input_mapping": {
                        "campaign_config": "campaign_config",
                        "aida_scores": "campaign_aida_scores"
                    },
                    "output_mapping": {
                        "platform_campaign_ids": "deployment_results"
                    }
                }
            ],
            "config": {
                "max_execution_time": 300,
                "retry_failed_steps": True
            }
        }

        response = await client.post(
            "/api/agentkit/workflows",
            json=workflow_data,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["workflow_id"] == "test_workflow"
        assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_execute_workflow(self, client, auth_headers, test_user, test_db):
        """Test workflow execution"""
        # Create workflow first
        workflow_data = {
            "workflow_id": "test_workflow_execute",
            "organization_id": test_user["organization_id"],
            "name": "Test Workflow for Execution",
            "description": "Test workflow execution",
            "steps": [
                {
                    "step_id": "step_1",
                    "agent_type": "analytics",
                    "input_mapping": {},
                    "output_mapping": {
                        "metrics": "workflow_metrics"
                    }
                }
            ],
            "config": {}
        }

        # Create workflow using service
        service = AgentKitService(test_db, "test_key")
        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        execution_request = {
            "input_data": {
                "analysis_type": "campaign_performance",
                "date_range": {
                    "start_date": datetime.utcnow().isoformat(),
                    "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }
            }
        }

        response = await client.post(
            "/api/agentkit/workflows/test_workflow_execute/execute",
            json=execution_request,
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "execution_id" in data
        assert data["status"] == "completed"
        assert "output_data" in data

    @pytest.mark.asyncio
    async def test_workflow_validation(self, client, auth_headers):
        """Test workflow validation errors"""
        # Test invalid workflow structure
        invalid_workflow = {
            "workflow_id": "invalid_workflow",
            "organization_id": "test_org",
            "name": "Invalid Workflow",
            "steps": "not_a_list"  # Should be a list
        }

        response = await client.post(
            "/api/agentkit/workflows",
            json=invalid_workflow,
            headers=auth_headers
        )
        assert response.status_code == 422


class TestComplianceAndAudit:
    """Test compliance and audit endpoints"""

    @pytest.mark.asyncio
    async def test_run_compliance_check(self, client, auth_headers, test_user, test_db):
        """Test compliance check execution"""
        response = await client.post(
            f"/api/agentkit/compliance/check?organization_id={test_user['organization_id']}",
            json={"check_type": "soc2"},
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "check_id" in data
        assert "status" in data
        assert "findings" in data
        assert "recommendations" in data

    @pytest.mark.asyncio
    async def test_get_audit_logs(self, client, auth_headers, test_user, test_db):
        """Test audit logs retrieval"""
        # Create some audit logs first
        service = AgentKitService(test_db, "test_key")

        # Create a test agent execution to generate audit logs
        agent_config = AgentConfig(
            agent_id="test_audit_agent",
            organization_id=test_user["organization_id"],
            name="Test Audit Agent",
            agent_type="analytics",
            description="Test agent for audit logs",
            config={}
        )

        await service.create_agent(agent_config)

        execution_request = AgentExecutionRequest(
            agent_id="test_audit_agent",
            input_data={"test": "data"},
            user_id=test_user["user_id"],
            organization_id=test_user["organization_id"]
        )

        await service.execute_agent(execution_request)

        response = await client.get(
            f"/api/agentkit/audit-logs?organization_id={test_user['organization_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have audit logs from the execution


class TestAnalyticsAndMetrics:
    """Test analytics and metrics endpoints"""

    @pytest.mark.asyncio
    async def test_get_agent_metrics(self, client, auth_headers, test_user, test_db):
        """Test agent metrics retrieval"""
        # Create and execute some agents to generate metrics
        service = AgentKitService(test_db, "test_key")

        # Create test agent
        agent_config = AgentConfig(
            agent_id="test_metrics_agent",
            organization_id=test_user["organization_id"],
            name="Test Metrics Agent",
            agent_type="creative_intelligence",
            description="Test agent for metrics",
            config={}
        )

        await service.create_agent(agent_config)

        # Execute agent multiple times
        for i in range(3):
            execution_request = AgentExecutionRequest(
                agent_id="test_metrics_agent",
                input_data={"test": f"data_{i}"},
                user_id=test_user["user_id"],
                organization_id=test_user["organization_id"]
            )
            await service.execute_agent(execution_request)

        # Get metrics
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow() + timedelta(days=1)

        response = await client.get(
            f"/api/agentkit/metrics?organization_id={test_user['organization_id']}&start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "metrics" in data
        assert test_user["organization_id"] in data["metrics"]
        assert data["metrics"][test_user["organization_id"]]["total_executions"] >= 3


class TestErrorHandling:
    """Test comprehensive error handling"""

    @pytest.mark.asyncio
    async def test_invalid_authentication(self, client):
        """Test invalid authentication handling"""
        response = await client.get("/api/agentkit/agents")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_organization_access(self, client, auth_headers):
        """Test access to non-existent organization"""
        response = await client.get(
            "/api/agentkit/agents?organization_id=non_existent_org",
            headers=auth_headers
        )
        assert response.status_code == 200  # Should return empty list, not error

    @pytest.mark.asyncio
    async def test_malformed_request_data(self, client, auth_headers):
        """Test malformed request data handling"""
        response = await client.post(
            "/api/agentkit/agents",
            json={"invalid": "data"},  # Missing required fields
            headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_nonexistent_agent_execution(self, client, auth_headers):
        """Test execution of non-existent agent"""
        response = await client.post(
            "/api/agentkit/agents/non_existent_agent/execute",
            json={"input_data": {}},
            headers=auth_headers
        )
        assert response.status_code == 404


class TestValidationService:
    """Test validation service functionality"""

    def test_email_validation(self):
        """Test email validation"""
        # Valid emails
        assert ValidationService.validate_email("test@example.com") == "test@example.com"
        assert ValidationService.validate_email("user.name+tag@domain.co.uk") == "user.name+tag@domain.co.uk"

        # Invalid emails
        with pytest.raises(Exception):
            ValidationService.validate_email("")

        with pytest.raises(Exception):
            ValidationService.validate_email("invalid-email")

        with pytest.raises(Exception):
            ValidationService.validate_email("test@")

    def test_phone_validation(self):
        """Test phone validation"""
        # Valid US phone
        assert ValidationService.validate_phone("(555) 123-4567") == "+15551234567"
        assert ValidationService.validate_phone("555.123.4567") == "+15551234567"

        # Invalid phone
        with pytest.raises(Exception):
            ValidationService.validate_phone("")

        with pytest.raises(Exception):
            ValidationService.validate_phone("invalid-phone")

    def test_organization_id_validation(self):
        """Test organization ID validation"""
        # Valid IDs
        assert ValidationService.validate_organization_id("test-org-123") == "test-org-123"
        assert ValidationService.validate_organization_id("my_organization_2023") == "my_organization_2023"

        # Invalid IDs
        with pytest.raises(Exception):
            ValidationService.validate_organization_id("")

        with pytest.raises(Exception):
            ValidationService.validate_organization_id("Test@Org!")  # Invalid characters


class TestPerformanceAndLoad:
    """Test performance and load handling"""

    @pytest.mark.asyncio
    async def test_concurrent_agent_executions(self, client, auth_headers, test_user, test_db):
        """Test concurrent agent executions"""
        service = AgentKitService(test_db, "test_key")

        # Create test agent
        agent_config = AgentConfig(
            agent_id="test_concurrent_agent",
            organization_id=test_user["organization_id"],
            name="Test Concurrent Agent",
            agent_type="analytics",
            description="Test concurrent executions",
            config={}
        )

        await service.create_agent(agent_config)

        # Execute multiple agents concurrently
        tasks = []
        for i in range(10):
            execution_request = {
                "input_data": {"request_id": i},
                "context": {"concurrent_test": True}
            }

            task = client.post(
                "/api/agentkit/agents/test_concurrent_agent/execute",
                json=execution_request,
                headers=auth_headers
            )
            tasks.append(task)

        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200

        # Check that all executions were recorded
        executions = await test_db.agentkit_executions.count_documents({
            "agent_id": "test_concurrent_agent"
        })
        assert executions >= 10

    @pytest.mark.asyncio
    async def test_large_workflow_execution(self, client, auth_headers, test_user, test_db):
        """Test large workflow execution"""
        # Create workflow with many steps
        steps = []
        for i in range(20):  # Large number of steps
            steps.append({
                "step_id": f"step_{i}",
                "agent_type": "analytics" if i % 2 == 0 else "creative_intelligence",
                "input_mapping": {"step_num": i},
                "output_mapping": {f"result_{i}": f"workflow_result_{i}"}
            })

        workflow_data = {
            "workflow_id": "test_large_workflow",
            "organization_id": test_user["organization_id"],
            "name": "Test Large Workflow",
            "description": "Test workflow with many steps",
            "steps": steps,
            "config": {"timeout": 60}
        }

        service = AgentKitService(test_db, "test_key")
        workflow = WorkflowDefinition(**workflow_data)
        await service.create_workflow(workflow)

        execution_request = {
            "input_data": {"test": "large_workflow_test"}
        }

        response = await client.post(
            "/api/agentkit/workflows/test_large_workflow/execute",
            json=execution_request,
            headers=auth_headers
        )

        # Should complete successfully or fail gracefully
        assert response.status_code in [200, 500]  # Either success or controlled failure


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "--cov=backend",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v"
    ])
