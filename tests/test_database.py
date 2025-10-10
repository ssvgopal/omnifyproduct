"""
Database Schema and Operations Tests
"""

import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os

from database.mongodb_schema import MongoDBSchema
from models.user_models import Organization, User, Subscription, SubscriptionTier
from models.agentkit_models import AgentConfig, AgentExecution, WorkflowDefinition, AgentType


@pytest.fixture
async def test_db():
    """Create test database"""
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(mongo_url)
    db = client["omnify_test_db"]

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
async def schema_manager(test_db):
    """Create schema manager"""
    return MongoDBSchema(test_db)


class TestMongoDBSchema:
    """Test MongoDB schema initialization"""

    @pytest.mark.asyncio
    async def test_initialize_schema(self, schema_manager):
        """Test schema initialization creates all collections"""
        await schema_manager.initialize_schema()

        # Check that all expected collections exist
        collections = await schema_manager.db.list_collection_names()

        expected_collections = [
            "users", "organizations", "subscriptions",
            "campaigns", "clients", "analytics", "assets",
            "audit_logs", "agentkit_agents", "agentkit_executions",
            "agentkit_workflows", "agentkit_workflow_executions"
        ]

        for collection in expected_collections:
            assert collection in collections, f"Collection {collection} not found"

    @pytest.mark.asyncio
    async def test_user_collection_creation(self, schema_manager):
        """Test user collection creation with indexes"""
        await schema_manager._create_users_collection()

        # Check collection exists
        collections = await schema_manager.db.list_collection_names()
        assert "users" in collections

        # Check indexes
        indexes = await schema_manager.db.users.index_information()
        index_names = list(indexes.keys())

        assert "user_id_1" in index_names  # Unique index on user_id
        assert "email_1" in index_names    # Unique index on email
        assert "organization_id_1" in index_names  # Index on organization_id

    @pytest.mark.asyncio
    async def test_organization_collection_creation(self, schema_manager):
        """Test organization collection creation with indexes"""
        await schema_manager._create_organizations_collection()

        collections = await schema_manager.db.list_collection_names()
        assert "organizations" in collections

        indexes = await schema_manager.db.organizations.index_information()
        index_names = list(indexes.keys())

        assert "organization_id_1" in index_names  # Unique index
        assert "slug_1" in index_names            # Unique index on slug

    @pytest.mark.asyncio
    async def test_agentkit_collections_creation(self, schema_manager):
        """Test AgentKit collections creation"""
        await schema_manager._create_agentkit_collections()

        collections = await schema_manager.db.list_collection_names()

        expected_agentkit_collections = [
            "agentkit_agents", "agentkit_executions",
            "agentkit_workflows", "agentkit_workflow_executions"
        ]

        for collection in expected_agentkit_collections:
            assert collection in collections

        # Check agentkit_agents indexes
        agent_indexes = await schema_manager.db.agentkit_agents.index_information()
        agent_index_names = list(agent_indexes.keys())

        assert "agent_id_1" in agent_index_names
        assert "organization_id_1" in agent_index_names
        assert "type_1" in agent_index_names

        # Check agentkit_executions indexes
        execution_indexes = await schema_manager.db.agentkit_executions.index_information()
        execution_index_names = list(execution_indexes.keys())

        assert "execution_id_1" in execution_index_names
        assert "agent_id_1" in execution_index_names
        assert "organization_id_1" in execution_index_names

    @pytest.mark.asyncio
    async def test_audit_logs_collection_creation(self, schema_manager):
        """Test audit logs collection with TTL index"""
        await schema_manager._create_audit_logs_collection()

        collections = await schema_manager.db.list_collection_names()
        assert "audit_logs" in collections

        # Check TTL index (7 years = 220752000 seconds)
        indexes = await schema_manager.db.audit_logs.index_information()
        ttl_index = None
        for index_name, index_info in indexes.items():
            if "timestamp" in index_info.get("key", []):
                ttl_index = index_info
                break

        assert ttl_index is not None
        assert "expireAfterSeconds" in ttl_index
        assert ttl_index["expireAfterSeconds"] == 220752000  # 7 years

    @pytest.mark.asyncio
    async def test_create_default_data(self, schema_manager):
        """Test creation of default AgentKit agents"""
        org_id = "test_org_123"
        user_id = "test_user_456"

        default_agents = await schema_manager.create_default_data(org_id, user_id)

        assert len(default_agents) == 4  # Should create 4 default agents

        # Check agents in database
        agents = await schema_manager.db.agentkit_agents.find({"organization_id": org_id}).to_list(None)
        assert len(agents) == 4

        # Check agent types
        agent_types = [agent["type"] for agent in agents]
        expected_types = ["creative_intelligence", "marketing_automation", "client_management", "analytics"]

        for expected_type in expected_types:
            assert expected_type in agent_types

        # Verify agent configurations
        for agent in agents:
            assert "agent_id" in agent
            assert "name" in agent
            assert "type" in agent
            assert "capabilities" in agent
            assert "configuration" in agent
            assert agent["organization_id"] == org_id
            assert agent["created_by"] == user_id


class TestDatabaseOperations:
    """Test actual database operations"""

    @pytest.mark.asyncio
    async def test_user_crud_operations(self, test_db):
        """Test user CRUD operations"""
        # Create user
        user_data = {
            "user_id": "test_user_crud",
            "email": "crud@example.com",
            "password_hash": "hashed_password",
            "full_name": "CRUD Test User",
            "organization_id": "test_org",
            "role": "member"
        }

        result = await test_db.users.insert_one(user_data)
        assert result.inserted_id is not None

        # Read user
        user = await test_db.users.find_one({"user_id": "test_user_crud"})
        assert user is not None
        assert user["email"] == "crud@example.com"

        # Update user
        update_result = await test_db.users.update_one(
            {"user_id": "test_user_crud"},
            {"$set": {"full_name": "Updated CRUD User"}}
        )
        assert update_result.modified_count == 1

        # Verify update
        updated_user = await test_db.users.find_one({"user_id": "test_user_crud"})
        assert updated_user["full_name"] == "Updated CRUD User"

        # Delete user
        delete_result = await test_db.users.delete_one({"user_id": "test_user_crud"})
        assert delete_result.deleted_count == 1

        # Verify deletion
        deleted_user = await test_db.users.find_one({"user_id": "test_user_crud"})
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_multi_tenant_queries(self, test_db):
        """Test multi-tenant data isolation"""
        # Create users in different organizations
        users_data = [
            {
                "user_id": "user_org1_001",
                "email": "user1@org1.com",
                "organization_id": "org1",
                "role": "member"
            },
            {
                "user_id": "user_org1_002",
                "email": "user2@org1.com",
                "organization_id": "org1",
                "role": "admin"
            },
            {
                "user_id": "user_org2_001",
                "email": "user1@org2.com",
                "organization_id": "org2",
                "role": "member"
            }
        ]

        for user_data in users_data:
            await test_db.users.insert_one(user_data)

        # Query users in org1 only
        org1_users = await test_db.users.find({"organization_id": "org1"}).to_list(None)
        assert len(org1_users) == 2

        user_ids = [user["user_id"] for user in org1_users]
        assert "user_org1_001" in user_ids
        assert "user_org1_002" in user_ids

        # Query users in org2 only
        org2_users = await test_db.users.find({"organization_id": "org2"}).to_list(None)
        assert len(org2_users) == 1
        assert org2_users[0]["user_id"] == "user_org2_001"

    @pytest.mark.asyncio
    async def test_agent_execution_logging(self, test_db):
        """Test agent execution logging"""
        execution_data = {
            "execution_id": "exec_test_001",
            "agent_id": "agent_test_001",
            "organization_id": "org_test",
            "input_data": {"test": "input"},
            "output_data": {"result": "success"},
            "status": "completed",
            "execution_time_seconds": 2.5,
            "timestamp": "2025-10-10T10:00:00Z"
        }

        result = await test_db.agentkit_executions.insert_one(execution_data)
        assert result.inserted_id is not None

        # Query executions by agent
        executions = await test_db.agentkit_executions.find({"agent_id": "agent_test_001"}).to_list(None)
        assert len(executions) == 1
        assert executions[0]["status"] == "completed"

        # Query executions by organization
        org_executions = await test_db.agentkit_executions.find({"organization_id": "org_test"}).to_list(None)
        assert len(org_executions) == 1

    @pytest.mark.asyncio
    async def test_audit_log_operations(self, test_db):
        """Test audit log operations with TTL"""
        audit_entry = {
            "log_id": "audit_test_001",
            "organization_id": "org_test",
            "user_id": "user_test",
            "action": "agent_created",
            "resource_type": "agent",
            "resource_id": "agent_test_001",
            "details": {"agent_name": "Test Agent"},
            "ip_address": "127.0.0.1",
            "user_agent": "Test Client",
            "timestamp": "2025-10-10T10:00:00Z"
        }

        result = await test_db.audit_logs.insert_one(audit_entry)
        assert result.inserted_id is not None

        # Query audit logs
        logs = await test_db.audit_logs.find({"organization_id": "org_test"}).to_list(None)
        assert len(logs) == 1
        assert logs[0]["action"] == "agent_created"

    @pytest.mark.asyncio
    async def test_campaign_operations(self, test_db):
        """Test campaign operations"""
        campaign_data = {
            "campaign_id": "campaign_test_001",
            "organization_id": "org_test",
            "name": "Test Campaign",
            "status": "active",
            "platforms": ["google_ads", "meta_ads"],
            "budget_total": 1000.0,
            "budget_spent": 250.0,
            "created_by": "user_test"
        }

        result = await test_db.campaigns.insert_one(campaign_data)
        assert result.inserted_id is not None

        # Query active campaigns
        active_campaigns = await test_db.campaigns.find({
            "organization_id": "org_test",
            "status": "active"
        }).to_list(None)
        assert len(active_campaigns) == 1

        # Update campaign budget
        update_result = await test_db.campaigns.update_one(
            {"campaign_id": "campaign_test_001"},
            {"$set": {"budget_spent": 500.0}}
        )
        assert update_result.modified_count == 1

    @pytest.mark.asyncio
    async def test_analytics_operations(self, test_db):
        """Test analytics operations"""
        analytics_data = [
            {
                "entry_id": "analytics_test_001",
                "organization_id": "org_test",
                "campaign_id": "campaign_test_001",
                "date": "2025-10-10",
                "platform": "google_ads",
                "metrics": {
                    "impressions": 10000,
                    "clicks": 250,
                    "conversions": 15,
                    "cost": 125.50
                }
            },
            {
                "entry_id": "analytics_test_002",
                "organization_id": "org_test",
                "campaign_id": "campaign_test_001",
                "date": "2025-10-10",
                "platform": "meta_ads",
                "metrics": {
                    "impressions": 8000,
                    "clicks": 200,
                    "conversions": 12,
                    "cost": 98.75
                }
            }
        ]

        for entry in analytics_data:
            await test_db.analytics.insert_one(entry)

        # Query analytics by campaign
        campaign_analytics = await test_db.analytics.find({
            "organization_id": "org_test",
            "campaign_id": "campaign_test_001"
        }).to_list(None)
        assert len(campaign_analytics) == 2

        # Aggregate metrics
        pipeline = [
            {"$match": {"organization_id": "org_test", "campaign_id": "campaign_test_001"}},
            {"$group": {
                "_id": "$platform",
                "total_impressions": {"$sum": "$metrics.impressions"},
                "total_clicks": {"$sum": "$metrics.clicks"},
                "total_conversions": {"$sum": "$metrics.conversions"},
                "total_cost": {"$sum": "$metrics.cost"}
            }}
        ]

        aggregated = await test_db.analytics.aggregate(pipeline).to_list(None)
        assert len(aggregated) == 2

        # Verify aggregation
        google_ads = next(item for item in aggregated if item["_id"] == "google_ads")
        assert google_ads["total_impressions"] == 10000
        assert google_ads["total_clicks"] == 250
        assert google_ads["total_conversions"] == 15

    @pytest.mark.asyncio
    async def test_index_performance(self, test_db):
        """Test index performance with large dataset"""
        # Create large dataset
        users_data = []
        for i in range(100):
            users_data.append({
                "user_id": f"user_perf_{i:03d}",
                "email": f"user{i:03d}@example.com",
                "organization_id": f"org_perf_{(i % 10):02d}",
                "role": "member" if i % 5 != 0 else "admin",
                "full_name": f"Performance User {i}"
            })

        await test_db.users.insert_many(users_data)

        # Create indexes
        await test_db.users.create_index("organization_id")
        await test_db.users.create_index("role")

        # Test indexed queries
        org_users = await test_db.users.find({"organization_id": "org_perf_05"}).to_list(None)
        assert len(org_users) == 10  # Should be 10 users per org

        admin_users = await test_db.users.find({"role": "admin"}).to_list(None)
        assert len(admin_users) == 20  # Every 5th user is admin (100/5 = 20)


if __name__ == "__main__":
    # Run database tests
    pytest.main([__file__, "-v", "--tb=short"])
