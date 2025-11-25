"""
Database Security Layer
Protects against NoSQL injection and enforces tenant isolation
"""

import logging
from typing import Dict, Any, Optional, List, Union
from motor.motor_asyncio import AsyncIOMotorDatabase
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseSecurityError(Exception):
    """Database security violation"""
    pass


class QueryValidator:
    """Validates and sanitizes MongoDB queries"""
    
    # Dangerous MongoDB operators that should be restricted
    DANGEROUS_OPERATORS = [
        '$where', '$eval', '$function', '$code', '$regex'
    ]
    
    # Allowed operators for user queries
    ALLOWED_OPERATORS = [
        '$eq', '$ne', '$gt', '$gte', '$lt', '$lte',
        '$in', '$nin', '$and', '$or', '$not', '$nor',
        '$exists', '$type', '$mod', '$size', '$all',
        '$elemMatch', '$text', '$search'
    ]
    
    @staticmethod
    def validate_query(query: Dict[str, Any], allow_operators: bool = True) -> Dict[str, Any]:
        """
        Validate and sanitize MongoDB query
        
        Args:
            query: MongoDB query dictionary
            allow_operators: Whether to allow MongoDB operators
            
        Returns:
            Sanitized query dictionary
            
        Raises:
            DatabaseSecurityError: If query contains dangerous patterns
        """
        if not isinstance(query, dict):
            raise DatabaseSecurityError("Query must be a dictionary")
        
        sanitized = {}
        
        for key, value in query.items():
            # Check for dangerous operators
            if key.startswith('$'):
                if not allow_operators:
                    raise DatabaseSecurityError(f"Operators not allowed in query: {key}")
                
                if key in QueryValidator.DANGEROUS_OPERATORS:
                    raise DatabaseSecurityError(f"Dangerous operator not allowed: {key}")
                
                if key not in QueryValidator.ALLOWED_OPERATORS:
                    logger.warning(f"Uncommon operator used: {key}")
            
            # Validate key name
            if not QueryValidator._is_valid_key(key):
                raise DatabaseSecurityError(f"Invalid key name: {key}")
            
            # Recursively validate nested queries
            if isinstance(value, dict):
                sanitized[key] = QueryValidator.validate_query(value, allow_operators=True)
            elif isinstance(value, list):
                sanitized[key] = [
                    QueryValidator.validate_query(item, allow_operators=True) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                # Sanitize value
                sanitized[key] = QueryValidator._sanitize_value(value)
        
        return sanitized
    
    @staticmethod
    def _is_valid_key(key: str) -> bool:
        """Validate key name"""
        # Keys should be alphanumeric with underscores, dots, or dollar signs (for operators)
        if not isinstance(key, str):
            return False
        
        # Allow MongoDB operators (starting with $)
        if key.startswith('$'):
            return True
        
        # Allow field names with dots (for nested fields)
        if '.' in key:
            parts = key.split('.')
            return all(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', part) for part in parts)
        
        # Standard field name
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key))
    
    @staticmethod
    def _sanitize_value(value: Any) -> Any:
        """Sanitize query value"""
        # For strings, check for injection patterns
        if isinstance(value, str):
            # Check for JavaScript code injection
            if any(pattern in value.lower() for pattern in ['javascript:', 'eval(', 'function(', 'script']):
                logger.warning(f"Potentially dangerous value detected: {value[:50]}")
                # Escape or reject
                raise DatabaseSecurityError("Potentially dangerous value detected")
        
        # For other types, return as-is
        return value


class TenantIsolation:
    """Enforces tenant isolation in database queries"""
    
    @staticmethod
    def enforce_tenant_filter(
        query: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enforce tenant isolation by adding organization_id filter
        
        Args:
            query: Original query
            organization_id: Organization ID to filter by
            user_id: Optional user ID for user-specific queries
            
        Returns:
            Query with tenant isolation enforced
        """
        if not organization_id:
            raise DatabaseSecurityError("organization_id is required for tenant isolation")
        
        # Create tenant filter
        tenant_filter = {"organization_id": organization_id}
        
        # Add user filter if provided
        if user_id:
            tenant_filter["user_id"] = user_id
        
        # Merge with existing query
        # Use $and to ensure tenant filter is always applied
        if "$and" in query:
            query["$and"].append(tenant_filter)
        else:
            # Check if query already has organization_id
            if "organization_id" in query:
                # Ensure it matches
                if query["organization_id"] != organization_id:
                    raise DatabaseSecurityError("Query organization_id does not match user's organization")
            else:
                # Add tenant filter using $and to ensure it's always enforced
                if len(query) > 0:
                    query = {"$and": [query, tenant_filter]}
                else:
                    query = tenant_filter
        
        return query
    
    @staticmethod
    def validate_tenant_access(
        document: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Validate that a document belongs to the specified tenant
        
        Args:
            document: Document to validate
            organization_id: Expected organization ID
            user_id: Optional expected user ID
            
        Returns:
            True if access is allowed
            
        Raises:
            DatabaseSecurityError: If access is denied
        """
        doc_org_id = document.get("organization_id")
        
        if not doc_org_id:
            logger.warning("Document missing organization_id")
            raise DatabaseSecurityError("Document missing organization_id")
        
        if doc_org_id != organization_id:
            logger.warning(f"Tenant isolation violation: document org_id={doc_org_id}, expected={organization_id}")
            raise DatabaseSecurityError("Access denied: document does not belong to your organization")
        
        if user_id and document.get("user_id") != user_id:
            # User-specific documents must match user_id
            if "user_id" in document:
                raise DatabaseSecurityError("Access denied: document does not belong to you")
        
        return True


class SecureDatabaseClient:
    """Secure wrapper around MongoDB database client"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.validator = QueryValidator()
        self.tenant_isolation = TenantIsolation()
    
    async def find_one_secure(
        self,
        collection: str,
        query: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Secure find_one with tenant isolation"""
        # Validate query
        validated_query = self.validator.validate_query(query)
        
        # Enforce tenant isolation
        secure_query = self.tenant_isolation.enforce_tenant_filter(
            validated_query,
            organization_id,
            user_id
        )
        
        # Execute query
        result = await self.db[collection].find_one(secure_query, **kwargs)
        
        # Validate result belongs to tenant
        if result:
            self.tenant_isolation.validate_tenant_access(result, organization_id, user_id)
        
        return result
    
    async def find_secure(
        self,
        collection: str,
        query: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Secure find with tenant isolation"""
        # Validate query
        validated_query = self.validator.validate_query(query)
        
        # Enforce tenant isolation
        secure_query = self.tenant_isolation.enforce_tenant_filter(
            validated_query,
            organization_id,
            user_id
        )
        
        # Execute query
        cursor = self.db[collection].find(secure_query, **kwargs)
        results = await cursor.to_list(length=kwargs.get('limit', 1000))
        
        # Validate all results belong to tenant
        for result in results:
            self.tenant_isolation.validate_tenant_access(result, organization_id, user_id)
        
        return results
    
    async def insert_one_secure(
        self,
        collection: str,
        document: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        session: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """Secure insert_one with tenant isolation"""
        # Ensure document has organization_id
        if "organization_id" not in document:
            document["organization_id"] = organization_id
        
        # Validate organization_id matches
        if document["organization_id"] != organization_id:
            raise DatabaseSecurityError("Document organization_id does not match user's organization")
        
        # Add user_id if provided
        if user_id and "user_id" not in document:
            document["user_id"] = user_id
        
        # Validate document structure
        self.validator.validate_query(document, allow_operators=False)
        
        # Insert (with session if provided for transactions)
        if session:
            result = await self.db[collection].insert_one(document, session=session, **kwargs)
        else:
            result = await self.db[collection].insert_one(document, **kwargs)
        return result
    
    async def update_one_secure(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        session: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """Secure update_one with tenant isolation"""
        # Validate query
        validated_query = self.validator.validate_query(query)
        
        # Enforce tenant isolation in query
        secure_query = self.tenant_isolation.enforce_tenant_filter(
            validated_query,
            organization_id,
            user_id
        )
        
        # Validate update document
        # Prevent removing organization_id
        if "$unset" in update and "organization_id" in update["$unset"]:
            raise DatabaseSecurityError("Cannot remove organization_id")
        
        # Prevent changing organization_id
        if "$set" in update and "organization_id" in update["$set"]:
            if update["$set"]["organization_id"] != organization_id:
                raise DatabaseSecurityError("Cannot change organization_id")
        
        # Execute update (with session if provided for transactions)
        if session:
            result = await self.db[collection].update_one(secure_query, update, session=session, **kwargs)
        else:
            result = await self.db[collection].update_one(secure_query, update, **kwargs)
        return result
    
    async def delete_one_secure(
        self,
        collection: str,
        query: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Secure delete_one with tenant isolation"""
        # Validate query
        validated_query = self.validator.validate_query(query)
        
        # Enforce tenant isolation
        secure_query = self.tenant_isolation.enforce_tenant_filter(
            validated_query,
            organization_id,
            user_id
        )
        
        # Execute delete
        result = await self.db[collection].delete_one(secure_query, **kwargs)
        return result
    
    async def count_documents_secure(
        self,
        collection: str,
        query: Dict[str, Any],
        organization_id: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> int:
        """Secure count_documents with tenant isolation"""
        # Validate query
        validated_query = self.validator.validate_query(query)
        
        # Enforce tenant isolation
        secure_query = self.tenant_isolation.enforce_tenant_filter(
            validated_query,
            organization_id,
            user_id
        )
        
        # Execute count
        result = await self.db[collection].count_documents(secure_query, **kwargs)
        return result

