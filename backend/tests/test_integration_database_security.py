"""
Integration tests for database security
Tests actual database operations with security enforcement
"""

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from core.database_security import SecureDatabaseClient, DatabaseSecurityError


@pytest.mark.asyncio
@pytest.fixture
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_omnify_security
    yield db
    await client.drop_database("test_omnify_security")
    client.close()


@pytest.mark.asyncio
class TestDatabaseSecurityIntegration:
    """Integration tests for database security"""
    
    async def test_tenant_isolation_enforced(self, test_db):
        """Test that tenant isolation is enforced in queries"""
        secure_db = SecureDatabaseClient(test_db)
        
        # Insert documents for different tenants
        await secure_db.insert_one_secure(
            "test_collection",
            {"name": "doc1", "value": 100},
            "org_123"
        )
        
        await secure_db.insert_one_secure(
            "test_collection",
            {"name": "doc2", "value": 200},
            "org_456"
        )
        
        # Try to query org_123's documents as org_456
        result = await secure_db.find_one_secure(
            "test_collection",
            {"name": "doc1"},
            "org_456"
        )
        
        # Should not find the document (tenant isolation)
        assert result is None
        
        # Query as correct tenant
        result = await secure_db.find_one_secure(
            "test_collection",
            {"name": "doc1"},
            "org_123"
        )
        
        assert result is not None
        assert result["name"] == "doc1"
    
    async def test_no_sql_injection_prevention(self, test_db):
        """Test that NoSQL injection is prevented"""
        secure_db = SecureDatabaseClient(test_db)
        
        # Attempt NoSQL injection
        malicious_query = {
            "$where": "this.name == 'test'"
        }
        
        with pytest.raises(DatabaseSecurityError):
            await secure_db.find_one_secure(
                "test_collection",
                malicious_query,
                "org_123"
            )
    
    async def test_organization_id_required(self, test_db):
        """Test that organization_id is required"""
        secure_db = SecureDatabaseClient(test_db)
        
        with pytest.raises(DatabaseSecurityError):
            await secure_db.find_one_secure(
                "test_collection",
                {"name": "test"},
                None  # Missing organization_id
            )
    
    async def test_cannot_change_organization_id(self, test_db):
        """Test that organization_id cannot be changed in updates"""
        secure_db = SecureDatabaseClient(test_db)
        
        # Insert document
        await secure_db.insert_one_secure(
            "test_collection",
            {"name": "doc1", "value": 100},
            "org_123"
        )
        
        # Try to change organization_id
        update = {"$set": {"organization_id": "org_456"}}
        
        with pytest.raises(DatabaseSecurityError):
            await secure_db.update_one_secure(
                "test_collection",
                {"name": "doc1"},
                update,
                "org_123"
            )

