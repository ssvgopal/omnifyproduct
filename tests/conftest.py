# tests/conftest.py
import pytest
import asyncio
import os
import sys

# Ensure backend directory is in Python path for imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def set_test_environment_variables():
    """Set environment variables for testing."""
    original_env = os.environ.copy()
    
    # Set consistent test environment variables
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["MONGO_URL"] = "mongodb://localhost:27017/testdb"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["JWT_SECRET_KEY"] = "super-secret-test-key"
    os.environ["AGENTKIT_API_KEY"] = "test-agentkit-api-key"
    os.environ["OPENAI_API_KEY"] = "test-openai-api-key"
    os.environ["DB_NAME"] = "testdb"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)