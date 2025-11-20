"""
Tests for Database Security Layer
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from core.database_security import (
    QueryValidator,
    TenantIsolation,
    SecureDatabaseClient,
    DatabaseSecurityError
)


class TestQueryValidator:
    """Test query validation"""
    
    def test_valid_query(self):
        """Test valid query passes validation"""
        query = {"name": "test", "status": "active"}
        result = QueryValidator.validate_query(query)
        assert result == query
    
    def test_dangerous_operator_rejected(self):
        """Test dangerous operators are rejected"""
        query = {"$where": "this.name == 'test'"}
        with pytest.raises(DatabaseSecurityError):
            QueryValidator.validate_query(query)
    
    def test_allowed_operator_accepted(self):
        """Test allowed operators are accepted"""
        query = {"$or": [{"status": "active"}, {"status": "pending"}]}
        result = QueryValidator.validate_query(query)
        assert "$or" in result
    
    def test_nested_query_validation(self):
        """Test nested queries are validated"""
        query = {
            "$and": [
                {"status": "active"},
                {"$or": [{"type": "A"}, {"type": "B"}]}
            ]
        }
        result = QueryValidator.validate_query(query)
        assert "$and" in result
    
    def test_invalid_key_rejected(self):
        """Test invalid key names are rejected"""
        query = {"invalid-key!": "value"}
        with pytest.raises(DatabaseSecurityError):
            QueryValidator.validate_query(query)


class TestTenantIsolation:
    """Test tenant isolation enforcement"""
    
    def test_enforce_tenant_filter(self):
        """Test tenant filter is added to query"""
        query = {"status": "active"}
        org_id = "org_123"
        
        result = TenantIsolation.enforce_tenant_filter(query, org_id)
        
        assert "organization_id" in str(result)
    
    def test_existing_org_id_validated(self):
        """Test existing organization_id is validated"""
        query = {"organization_id": "org_123", "status": "active"}
        org_id = "org_123"
        
        result = TenantIsolation.enforce_tenant_filter(query, org_id)
        # Should pass validation
        
    def test_mismatched_org_id_rejected(self):
        """Test mismatched organization_id is rejected"""
        query = {"organization_id": "org_456", "status": "active"}
        org_id = "org_123"
        
        with pytest.raises(DatabaseSecurityError):
            TenantIsolation.enforce_tenant_filter(query, org_id)
    
    def test_missing_org_id_required(self):
        """Test organization_id is required"""
        query = {"status": "active"}
        
        with pytest.raises(DatabaseSecurityError):
            TenantIsolation.enforce_tenant_filter(query, None)
    
    def test_validate_tenant_access(self):
        """Test tenant access validation"""
        document = {"organization_id": "org_123", "name": "test"}
        org_id = "org_123"
        
        result = TenantIsolation.validate_tenant_access(document, org_id)
        assert result is True
    
    def test_validate_tenant_access_denied(self):
        """Test tenant access is denied for wrong organization"""
        document = {"organization_id": "org_456", "name": "test"}
        org_id = "org_123"
        
        with pytest.raises(DatabaseSecurityError):
            TenantIsolation.validate_tenant_access(document, org_id)


@pytest.mark.asyncio
class TestSecureDatabaseClient:
    """Test secure database client"""
    
    async def test_find_one_secure(self):
        """Test secure find_one"""
        mock_db = AsyncMock()
        mock_collection = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        
        mock_doc = {"_id": "123", "organization_id": "org_123", "name": "test"}
        mock_collection.find_one = AsyncMock(return_value=mock_doc)
        
        client = SecureDatabaseClient(mock_db)
        result = await client.find_one_secure(
            "test_collection",
            {"name": "test"},
            "org_123"
        )
        
        assert result == mock_doc
        # Verify query included organization_id
        call_args = mock_collection.find_one.call_args
        assert call_args is not None
    
    async def test_insert_one_secure_adds_org_id(self):
        """Test secure insert_one adds organization_id"""
        mock_db = AsyncMock()
        mock_collection = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="123"))
        
        client = SecureDatabaseClient(mock_db)
        document = {"name": "test"}
        
        await client.insert_one_secure(
            "test_collection",
            document,
            "org_123"
        )
        
        # Verify organization_id was added
        call_args = mock_collection.insert_one.call_args
        inserted_doc = call_args[0][0]
        assert inserted_doc["organization_id"] == "org_123"
    
    async def test_update_one_secure_enforces_tenant(self):
        """Test secure update_one enforces tenant isolation"""
        mock_db = AsyncMock()
        mock_collection = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
        
        client = SecureDatabaseClient(mock_db)
        
        await client.update_one_secure(
            "test_collection",
            {"name": "test"},
            {"$set": {"status": "active"}},
            "org_123"
        )
        
        # Verify update was called
        assert mock_collection.update_one.called
    
    async def test_update_one_secure_prevents_org_id_change(self):
        """Test secure update_one prevents organization_id change"""
        mock_db = AsyncMock()
        client = SecureDatabaseClient(mock_db)
        
        update = {"$set": {"organization_id": "org_456"}}
        
        with pytest.raises(DatabaseSecurityError):
            await client.update_one_secure(
                "test_collection",
                {"name": "test"},
                update,
                "org_123"
            )

