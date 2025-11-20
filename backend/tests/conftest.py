"""
Pytest configuration and fixtures for all tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
import os

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32-bytes-long!!"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_db() -> AsyncMock:
    """Mock MongoDB database client"""
    db = AsyncMock(spec=AsyncIOMotorClient)
    db.admin = AsyncMock()
    db.admin.command = AsyncMock(return_value={"ok": 1})
    return db


@pytest.fixture
async def mock_redis() -> AsyncMock:
    """Mock Redis client"""
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def mock_user() -> dict:
    """Mock user data"""
    return {
        "user_id": "user_123",
        "email": "test@example.com",
        "organization_id": "org_123",
        "role": "admin",
        "permissions": ["read:campaigns", "write:campaigns"]
    }


@pytest.fixture
def mock_organization() -> dict:
    """Mock organization data"""
    return {
        "organization_id": "org_123",
        "name": "Test Organization",
        "plan": "enterprise",
        "status": "active"
    }


@pytest.fixture
def test_client() -> TestClient:
    """FastAPI test client"""
    from agentkit_server import app
    return TestClient(app)


@pytest.fixture
def auth_headers(mock_user: dict) -> dict:
    """Generate auth headers for testing"""
    # In a real test, you'd generate a JWT token
    # For now, return mock headers
    return {
        "Authorization": "Bearer test-token",
        "X-User-Id": mock_user["user_id"],
        "X-Organization-Id": mock_user["organization_id"]
    }


@pytest.fixture
async def mock_campaign() -> dict:
    """Mock campaign data"""
    return {
        "campaign_id": "campaign_123",
        "name": "Test Campaign",
        "organization_id": "org_123",
        "platform": "google_ads",
        "status": "active",
        "budget": 1000.0,
        "created_at": "2025-01-01T00:00:00Z"
    }


@pytest.fixture
async def mock_integration() -> dict:
    """Mock integration data"""
    return {
        "integration_id": "integration_123",
        "platform": "google_ads",
        "organization_id": "org_123",
        "status": "connected",
        "credentials": {
            "encrypted": True
        }
    }

