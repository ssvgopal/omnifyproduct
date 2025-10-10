"""
Comprehensive Test Suite for Omnify Cloud Connect
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
from datetime import datetime, timedelta

# Import our application code
from services.auth_service import AuthService
from services.agentkit_service import AgentKitService
from models.user_models import (
    UserCreate, UserLogin, UserUpdate, PasswordResetRequest,
    Organization, User, UserRole, SubscriptionTier
)
from models.agentkit_models import (
    AgentConfig, AgentExecutionRequest, AgentExecutionResponse,
    WorkflowDefinition, WorkflowExecution, AgentType, AgentStatus
)

# Test database setup
@pytest.fixture
async def test_db():
    """Create test database"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["omnify_test"]

    # Clean up before test
    await db.users.drop()
    await db.organizations.drop()
    await db.subscriptions.drop()
    await db.agentkit_agents.drop()
    await db.agentkit_executions.drop()
    await db.agentkit_workflows.drop()
    await db.audit_logs.drop()

    yield db

    # Clean up after test
    await db.users.drop()
    await db.organizations.drop()
    await db.subscriptions.drop()
    await db.agentkit_agents.drop()
    await db.agentkit_executions.drop()
    await db.agentkit_workflows.drop()
    await db.audit_logs.drop()

    client.close()


@pytest.fixture
def auth_service(test_db):
    """Create auth service for testing"""
    return AuthService(test_db, "test_secret_key")


@pytest.fixture
def agentkit_service(test_db):
    """Create agentkit service for testing"""
    return AgentKitService(test_db, "test_agentkit_key")


class TestAuthService:
    """Test authentication service"""

    @pytest.mark.asyncio
    async def test_password_hashing(self, auth_service):
        """Test password hashing and verification"""
        password = "test_password_123"

        # Hash password
        hashed = auth_service.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

        # Verify password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong_password", hashed)

    @pytest.mark.asyncio
    async def test_jwt_token_creation(self, auth_service):
        """Test JWT token creation and decoding"""
        payload = {
            "user_id": "user_123",
            "organization_id": "org_456",
            "role": "admin"
        }

        # Create token
        token = auth_service.create_access_token(payload)
        assert isinstance(token, str)
        assert len(token) > 0

        # Decode token
        decoded = auth_service.decode_token(token)
        assert decoded is not None
        assert decoded["user_id"] == "user_123"
        assert decoded["organization_id"] == "org_456"
        assert decoded["role"] == "admin"

    @pytest.mark.asyncio
    async def test_jwt_token_expiration(self, auth_service):
        """Test JWT token expiration"""
        # Create token that expires immediately
        past_time = datetime.utcnow() - timedelta(hours=1)
        payload = {"exp": past_time, "user_id": "test"}

        token = auth_service.create_access_token(payload)

        # Decode should fail for expired token
        decoded = auth_service.decode_token(token)
        assert decoded is None

    @pytest.mark.asyncio
    async def test_user_registration(self, auth_service):
        """Test user registration"""
        user_data = UserCreate(
            email="test@example.com",
            password="test_password_123",
            full_name="Test User",
            organization_name="Test Org"
        )

        # Register user
        user = await auth_service.create_user(user_data)
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.OWNER
        assert user.organization_id.startswith("org_")

        # Check user was created in database
        db_user = await auth_service.db.users.find_one({"user_id": user.user_id})
        assert db_user is not None
        assert db_user["email"] == "test@example.com"

        # Check organization was created
        org = await auth_service.get_organization(user.organization_id)
        assert org is not None
        assert org.name == "Test Org"
        assert org.owner_id == user.user_id

    @pytest.mark.asyncio
    async def test_user_login(self, auth_service):
        """Test user login"""
        # First create a user
        user_data = UserCreate(
            email="login@example.com",
            password="login_password_123",
            full_name="Login User",
            organization_name="Login Org"
        )
        user = await auth_service.create_user(user_data)

        # Test login
        login_data = UserLogin(
            email="login@example.com",
            password="login_password_123"
        )

        authenticated_user = await auth_service.authenticate_user(login_data)
        assert authenticated_user is not None
        assert authenticated_user.user_id == user.user_id

        # Test wrong password
        wrong_login = UserLogin(
            email="login@example.com",
            password="wrong_password"
        )
        assert await auth_service.authenticate_user(wrong_login) is None

    @pytest.mark.asyncio
    async def test_user_update(self, auth_service):
        """Test user update"""
        # Create user
        user_data = UserCreate(
            email="update@example.com",
            password="update_password_123",
            full_name="Update User",
            organization_name="Update Org"
        )
        user = await auth_service.create_user(user_data)

        # Update user
        update_data = UserUpdate(
            full_name="Updated Name",
            preferences={"theme": "dark"}
        )

        success = await auth_service.update_user(user.user_id, update_data)
        assert success

        # Check update in database
        updated_user = await auth_service.get_user_by_id(user.user_id)
        assert updated_user.full_name == "Updated Name"
        assert updated_user.preferences == {"theme": "dark"}

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, auth_service):
        """Test getting user by ID"""
        # Create user
        user_data = UserCreate(
            email="get@example.com",
            password="get_password_123",
            full_name="Get User",
            organization_name="Get Org"
        )
        created_user = await auth_service.create_user(user_data)

        # Get user
        retrieved_user = await auth_service.get_user_by_id(created_user.user_id)
        assert retrieved_user is not None
        assert retrieved_user.user_id == created_user.user_id
        assert retrieved_user.email == "get@example.com"

        # Test non-existent user
        assert await auth_service.get_user_by_id("non_existent") is None

    @pytest.mark.asyncio
    async def test_organization_creation(self, auth_service):
        """Test organization creation"""
        org_data = {
            "name": "Test Organization",
            "slug": "test-org"
        }

        # Create organization manually for testing
        org_id = f"org_{auth_service.generate_reset_token()[:16]}"
        org = Organization(
            organization_id=org_id,
            name=org_data["name"],
            slug=org_data["slug"],
            owner_id="test_owner",
            subscription_tier=SubscriptionTier.STARTER
        )

        await auth_service.db.organizations.insert_one(org.dict())

        # Retrieve and verify
        retrieved_org = await auth_service.get_organization(org_id)
        assert retrieved_org is not None
        assert retrieved_org.name == "Test Organization"
        assert retrieved_org.slug == "test-org"
        assert retrieved_org.subscription_tier == SubscriptionTier.STARTER

    @pytest.mark.asyncio
    async def test_invitation_creation_and_acceptance(self, auth_service):
        """Test user invitation flow"""
        # Create organization first
        org_data = {
            "organization_id": "org_invite_test",
            "name": "Invite Test Org",
            "slug": "invite-test-org",
            "owner_id": "owner_test",
            "subscription_tier": SubscriptionTier.STARTER
        }
        await auth_service.db.organizations.insert_one(org_data)

        # Create invitation
        invitation_data = {
            "email": "invited@example.com",
            "role": UserRole.MEMBER
        }

        invitation = await auth_service.create_invitation(
            "org_invite_test",
            type('MockInvitation', (), invitation_data)(),
            "owner_test"
        )

        assert invitation.email == "invited@example.com"
        assert invitation.role == UserRole.MEMBER
        assert invitation.organization_id == "org_invite_test"
        assert len(invitation.token) > 0

        # Accept invitation
        accept_data = {
            "token": invitation.token,
            "password": "new_password_123",
            "full_name": "Invited User"
        }

        user = await auth_service.accept_invitation(
            type('MockAccept', (), accept_data)()
        )

        assert user.email == "invited@example.com"
        assert user.full_name == "Invited User"
        assert user.organization_id == "org_invite_test"
        assert user.role == UserRole.MEMBER

    @pytest.mark.asyncio
    async def test_password_reset_flow(self, auth_service):
        """Test password reset flow"""
        # Create user
        user_data = UserCreate(
            email="reset@example.com",
            password="reset_password_123",
            full_name="Reset User",
            organization_name="Reset Org"
        )
        user = await auth_service.create_user(user_data)

        # Initiate password reset
        reset_data = PasswordResetRequest(email="reset@example.com")
        reset_token = await auth_service.initiate_password_reset(reset_data)
        assert reset_token is not None  # In real implementation, this would be sent via email

        # Verify reset token was stored
        db_user = await auth_service.db.users.find_one({"user_id": user.user_id})
        assert "reset_token" in db_user
        assert db_user["reset_token"] is not None

        # Reset password
        success = await auth_service.reset_password(reset_token, "new_password_456")
        assert success

        # Verify password was updated
        updated_user = await auth_service.get_user_by_id(user.user_id)
        assert auth_service.verify_password("new_password_456", updated_user.password_hash)
        assert not auth_service.verify_password("reset_password_123", updated_user.password_hash)


class TestAgentKitService:
    """Test AgentKit service"""

    @pytest.mark.asyncio
    async def test_agent_creation(self, agentkit_service):
        """Test agent creation"""
        agent_config = AgentConfig(
            agent_id="test_agent_001",
            name="Test Creative Agent",
            type=AgentType.CREATIVE_INTELLIGENCE,
            description="Test agent for creative intelligence",
            capabilities=["content_analysis", "repurposing"],
            configuration={
                "model": "gpt-4",
                "temperature": 0.7
            }
        )

        # Create agent
        created_agent = await agentkit_service.create_agent(agent_config)

        # Verify agent was created
        assert created_agent.agent_id == "test_agent_001"
        assert created_agent.name == "Test Creative Agent"
        assert created_agent.type == AgentType.CREATIVE_INTELLIGENCE
        assert created_agent.status == AgentStatus.ACTIVE

        # Verify in database
        db_agent = await agentkit_service.db.agentkit_agents.find_one({"agent_id": "test_agent_001"})
        assert db_agent is not None
        assert db_agent["name"] == "Test Creative Agent"

    @pytest.mark.asyncio
    async def test_agent_retrieval(self, agentkit_service):
        """Test agent retrieval"""
        # Create agent first
        agent_config = AgentConfig(
            agent_id="retrieve_test_001",
            name="Retrieve Test Agent",
            type=AgentType.MARKETING_AUTOMATION,
            description="Agent for testing retrieval"
        )
        await agentkit_service.create_agent(agent_config)

        # Retrieve agent
        retrieved_agent = await agentkit_service.get_agent("retrieve_test_001")
        assert retrieved_agent is not None
        assert retrieved_agent.agent_id == "retrieve_test_001"
        assert retrieved_agent.name == "Retrieve Test Agent"

        # Test non-existent agent
        assert await agentkit_service.get_agent("non_existent") is None

    @pytest.mark.asyncio
    async def test_agent_update(self, agentkit_service):
        """Test agent update"""
        # Create agent
        agent_config = AgentConfig(
            agent_id="update_test_001",
            name="Update Test Agent",
            type=AgentType.CLIENT_MANAGEMENT,
            description="Agent for testing updates"
        )
        await agentkit_service.create_agent(agent_config)

        # Update agent
        update_data = {
            "name": "Updated Agent Name",
            "description": "Updated description",
            "configuration": {"new_setting": "value"}
        }

        success = await agentkit_service.update_agent("update_test_001", update_data)
        assert success

        # Verify update
        updated_agent = await agentkit_service.get_agent("update_test_001")
        assert updated_agent.name == "Updated Agent Name"
        assert updated_agent.description == "Updated description"
        assert updated_agent.configuration["new_setting"] == "value"

    @pytest.mark.asyncio
    async def test_agent_deletion(self, agentkit_service):
        """Test agent deletion"""
        # Create agent
        agent_config = AgentConfig(
            agent_id="delete_test_001",
            name="Delete Test Agent",
            type=AgentType.ANALYTICS
        )
        await agentkit_service.create_agent(agent_config)

        # Delete agent
        success = await agentkit_service.delete_agent("delete_test_001")
        assert success

        # Verify deletion
        assert await agentkit_service.get_agent("delete_test_001") is None

    @pytest.mark.asyncio
    async def test_list_agents(self, agentkit_service):
        """Test listing agents"""
        # Create multiple agents
        agents_data = [
            {"agent_id": "list_test_001", "name": "Agent 1", "type": AgentType.CREATIVE_INTELLIGENCE},
            {"agent_id": "list_test_002", "name": "Agent 2", "type": AgentType.MARKETING_AUTOMATION},
            {"agent_id": "list_test_003", "name": "Agent 3", "type": AgentType.CLIENT_MANAGEMENT}
        ]

        for agent_data in agents_data:
            agent_config = AgentConfig(**agent_data)
            await agentkit_service.create_agent(agent_config)

        # List agents
        agents = await agentkit_service.list_agents()
        agent_ids = [agent.agent_id for agent in agents]

        assert "list_test_001" in agent_ids
        assert "list_test_002" in agent_ids
        assert "list_test_003" in agent_ids
        assert len(agents) >= 3  # May include default agents

    @pytest.mark.asyncio
    async def test_workflow_creation_and_execution(self, agentkit_service):
        """Test workflow creation and execution"""
        workflow_def = WorkflowDefinition(
            workflow_id="workflow_test_001",
            name="Test Workflow",
            description="Workflow for testing",
            steps=[
                {
                    "step_id": "step_1",
                    "agent_id": "test_agent_001",
                    "action": "analyze",
                    "parameters": {"input": "test"}
                }
            ],
            triggers=["manual"],
            organization_id="org_test"
        )

        # Create workflow
        created_workflow = await agentkit_service.create_workflow(workflow_def)
        assert created_workflow.workflow_id == "workflow_test_001"
        assert created_workflow.name == "Test Workflow"

        # Execute workflow
        execution = await agentkit_service.execute_workflow("workflow_test_001", {})
        assert execution.workflow_id == "workflow_test_001"
        assert execution.status == "completed"  # Mock execution completes immediately

    @pytest.mark.asyncio
    async def test_compliance_checking(self, agentkit_service):
        """Test compliance checking"""
        # This would test SOC 2 compliance checks
        # For now, test the framework is in place
        result = await agentkit_service.run_compliance_check("soc2")
        assert "status" in result
        assert "findings" in result
        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_audit_logging(self, agentkit_service):
        """Test audit logging"""
        # Create an agent to trigger audit logging
        agent_config = AgentConfig(
            agent_id="audit_test_001",
            name="Audit Test Agent",
            type=AgentType.CREATIVE_INTELLIGENCE
        )

        # Create agent (should trigger audit log)
        await agentkit_service.create_agent(agent_config)

        # Check audit logs
        logs = await agentkit_service.get_audit_logs("org_test", limit=10)
        assert isinstance(logs, list)
        # Should contain the agent creation log

    @pytest.mark.asyncio
    async def test_agent_metrics(self, agentkit_service):
        """Test agent metrics calculation"""
        # Create and execute an agent to generate metrics
        agent_config = AgentConfig(
            agent_id="metrics_test_001",
            name="Metrics Test Agent",
            type=AgentType.ANALYTICS
        )
        await agentkit_service.create_agent(agent_config)

        # Execute agent
        execution_request = AgentExecutionRequest(
            agent_id="metrics_test_001",
            input_data={"test": "data"},
            organization_id="org_test"
        )
        await agentkit_service.execute_agent("metrics_test_001", execution_request)

        # Get metrics
        metrics = await agentkit_service.get_agent_metrics("org_test", days=30)
        assert "org_test" in metrics
        assert "metrics_test_001" in metrics["org_test"]
        assert "total_executions" in metrics["org_test"]["metrics_test_001"]


# Integration tests will be added in separate files
class TestIntegrationBase:
    """Base class for integration tests"""

    @pytest.fixture
    async def client(self):
        """Create test client"""
        # This will be implemented when we have the FastAPI app
        pass

    @pytest.fixture
    async def authenticated_client(self, client):
        """Create authenticated test client"""
        # This will be implemented when we have authentication
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
