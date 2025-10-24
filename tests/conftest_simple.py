"""
Simplified Test Configuration for OmniFy Cloud Connect
Minimal setup to get tests running without complex dependencies
"""

import sys
import os
import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Set test environment variables
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("MONGO_URL", "mongomock://localhost")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("AGENTKIT_API_KEY", "test-agentkit-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_database():
    """Mock database for testing"""
    return MagicMock()

@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    return MagicMock()

@pytest.fixture
def mock_agentkit():
    """Mock AgentKit service for testing"""
    mock = AsyncMock()
    mock.create_agent.return_value = {"agent_id": "test-agent-123", "status": "active"}
    mock.execute_workflow.return_value = {"workflow_id": "test-workflow-123", "status": "completed"}
    return mock

@pytest.fixture
def mock_auth_service():
    """Mock authentication service for testing"""
    mock = MagicMock()
    mock.verify_token.return_value = {"user_id": "test-user-123", "email": "test@omnify.com"}
    mock.create_token.return_value = "test-jwt-token"
    return mock

@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "user_id": "test-user-123",
        "email": "test@omnify.com",
        "name": "Test User",
        "organization_id": "test-org-123",
        "role": "admin"
    }

@pytest.fixture
def test_campaign_data():
    """Test campaign data"""
    return {
        "campaign_id": "test-campaign-123",
        "name": "Test Campaign",
        "platform": "google_ads",
        "budget": 1000.0,
        "status": "active",
        "target_audience": "test-audience",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def test_agent_data():
    """Test agent data"""
    return {
        "agent_id": "test-agent-123",
        "name": "Test Agent",
        "type": "marketing_automation",
        "status": "active",
        "workflows": ["test-workflow-123"],
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def test_workflow_data():
    """Test workflow data"""
    return {
        "workflow_id": "test-workflow-123",
        "name": "Test Workflow",
        "steps": [
            {"step_id": "step-1", "action": "create_campaign", "params": {"platform": "google_ads"}},
            {"step_id": "step-2", "action": "optimize_budget", "params": {"target_roas": 3.0}}
        ],
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture
def test_analytics_data():
    """Test analytics data"""
    return {
        "analytics_id": "test-analytics-123",
        "campaign_id": "test-campaign-123",
        "metrics": {
            "impressions": 10000,
            "clicks": 500,
            "conversions": 25,
            "cost": 100.0,
            "roas": 2.5
        },
        "date_range": {
            "start": "2024-01-01",
            "end": "2024-01-31"
        },
        "created_at": "2024-01-01T00:00:00Z"
    }

# Mock external services
@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services"""
    with patch('services.agentkit_service.AgentKitService') as mock_agentkit, \
         patch('services.auth_service.AuthService') as mock_auth, \
         patch('database.mongodb.get_database') as mock_db, \
         patch('services.redis_cache_service.redis_client') as mock_redis:
        
        # Configure mocks
        mock_agentkit.return_value = AsyncMock()
        mock_auth.return_value = MagicMock()
        mock_db.return_value = MagicMock()
        mock_redis.return_value = MagicMock()
        
        yield {
            'agentkit': mock_agentkit,
            'auth': mock_auth,
            'database': mock_db,
            'redis': mock_redis
        }

