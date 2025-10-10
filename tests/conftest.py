"""
Test configuration and fixtures for OmnifyProduct
Comprehensive test infrastructure with proper mocking and fixtures
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import Dict, Any, AsyncGenerator
from httpx import AsyncClient
import mongomock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Test configuration
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("MONGO_URL", "mongomock://localhost")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("AGENTKIT_API_KEY", "test-agentkit-key")

# Import after environment setup
from agentkit_server import app
from services.auth_service import AuthService
from database.mongodb_schema import MongoDBSchema


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Create a test database with mongomock for isolated testing."""
    # Use mongomock for testing instead of real MongoDB
    client = AsyncIOMotorClient("mongomock://localhost")
    database = client.test_omnifyproduct

    # Initialize schema in test database
    schema = MongoDBSchema()
    schema.db = database

    # Create collections and indexes for testing
    collections = [
        "users", "organizations", "agentkit_agents", "agentkit_executions",
        "agentkit_workflows", "agentkit_workflow_executions", "audit_logs"
    ]

    for collection in collections:
        await database.create_collection(collection)

    # Set up indexes
    await database.agentkit_executions.create_index([("execution_id", 1)], unique=True)
    await database.agentkit_executions.create_index([("agent_id", 1)])
    await database.agentkit_executions.create_index([("organization_id", 1)])
    await database.users.create_index([("email", 1)], unique=True)
    await database.organizations.create_index([("organization_id", 1)], unique=True)

    yield database

    # Cleanup
    await client.drop_database("test_omnifyproduct")


@pytest_asyncio.fixture
async def test_user(test_db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """Create a test user for authentication testing."""
    user_data = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "organization_id": "test_org_456",
        "is_active": True,
        "created_at": "2024-01-15T10:00:00Z"
    }

    await test_db.users.insert_one(user_data)
    return user_data


@pytest_asyncio.fixture
async def test_organization(test_db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """Create a test organization."""
    org_data = {
        "organization_id": "test_org_456",
        "name": "Test Organization",
        "subscription_tier": "enterprise",
        "is_active": True,
        "created_at": "2024-01-15T10:00:00Z"
    }

    await test_db.organizations.insert_one(org_data)
    return org_data


@pytest_asyncio.fixture
async def auth_service(test_db: AsyncIOMotorDatabase) -> AuthService:
    """Create AuthService instance for testing."""
    return AuthService(db=test_db)


@pytest_asyncio.fixture
async def auth_headers(test_user: Dict[str, Any], auth_service: AuthService) -> Dict[str, str]:
    """Generate authentication headers for testing."""
    token = await auth_service.generate_token(
        user_id=test_user["user_id"],
        organization_id=test_user["organization_id"]
    )

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


@pytest_asyncio.fixture
async def client(test_db: AsyncIOMotorDatabase) -> AsyncGenerator[AsyncClient, None]:
    """Create HTTP client for testing API endpoints."""
    # Override the database dependency for testing
    async def override_get_db():
        return test_db

    app.dependency_overrides[app.dependency_overrides.__self__.get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_agent_config() -> Dict[str, Any]:
    """Sample agent configuration for testing."""
    return {
        "name": "Test Creative Agent",
        "agent_type": "creative_intelligence",
        "description": "Test agent for creative analysis",
        "config": {
            "platforms": ["google_ads", "meta_ads"],
            "analysis_types": ["aida", "brand_compliance"]
        }
    }


@pytest.fixture
def sample_workflow_definition() -> Dict[str, Any]:
    """Sample workflow definition for testing."""
    return {
        "name": "Test Campaign Workflow",
        "description": "Test workflow for campaign creation",
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
        ],
        "config": {
            "execution_mode": "sequential",
            "timeout_seconds": 300
        }
    }


@pytest.fixture
def sample_execution_request() -> Dict[str, Any]:
    """Sample agent execution request for testing."""
    return {
        "input_data": {
            "asset_url": "https://example.com/test-creative.jpg",
            "analysis_type": "aida"
        },
        "context": {
            "user_id": "test_user_123",
            "session_id": "test_session_789"
        }
    }


# Test data fixtures for different scenarios
@pytest.fixture
def test_creative_agent_data() -> Dict[str, Any]:
    """Test data for creative intelligence agent."""
    return {
        "agent_id": "test_creative_agent",
        "organization_id": "test_org_456",
        "name": "Creative Intelligence Agent",
        "agent_type": "creative_intelligence",
        "description": "Analyzes creative assets for AIDA optimization",
        "config": {
            "platforms": ["google_ads", "meta_ads", "linkedin_ads"],
            "analysis_types": ["aida", "brand_compliance", "performance_prediction"],
            "auto_optimize": True
        },
        "is_active": True
    }


@pytest.fixture
def test_marketing_agent_data() -> Dict[str, Any]:
    """Test data for marketing automation agent."""
    return {
        "agent_id": "test_marketing_agent",
        "organization_id": "test_org_456",
        "name": "Marketing Automation Agent",
        "agent_type": "marketing_automation",
        "description": "Automates campaign creation and deployment",
        "config": {
            "platforms": ["google_ads", "meta_ads"],
            "budget_management": True,
            "auto_optimization": True
        },
        "is_active": True
    }


@pytest.fixture
def test_workflow_execution_data() -> Dict[str, Any]:
    """Test data for workflow execution."""
    return {
        "execution_id": "test_workflow_exec_123",
        "workflow_id": "test_campaign_workflow",
        "organization_id": "test_org_456",
        "user_id": "test_user_123",
        "status": "completed",
        "input_data": {
            "campaign_creative_url": "https://example.com/creative.jpg",
            "campaign_config": {
                "name": "Test Campaign",
                "objective": "conversions",
                "budget_daily": 100.00
            }
        },
        "output_data": {
            "campaign_aida_scores": {"attention": 0.75, "interest": 0.70},
            "deployment_results": {"google_ads_campaign_id": "gads_123"}
        },
        "started_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:30:15Z"
    }
