"""
Filtering and Sorting Support for API Endpoints
Provides consistent filtering and sorting across all list endpoints
"""

from typing import Optional, List, Dict, Any, Callable
from pydantic import BaseModel, Field
from fastapi import Query
from enum import Enum


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class FilterParams(BaseModel):
    """Filter parameters"""
    # Common filters
    search: Optional[str] = Field(None, description="Search term")
    status: Optional[str] = Field(None, description="Filter by status")
    created_from: Optional[str] = Field(None, description="Filter by creation date from (ISO format)")
    created_to: Optional[str] = Field(None, description="Filter by creation date to (ISO format)")
    
    # Custom filters (key-value pairs)
    custom_filters: Dict[str, Any] = Field(default_factory=dict, description="Custom filter parameters")
    
    @classmethod
    def from_query(
        cls,
        search: Optional[str] = Query(None, description="Search term"),
        status: Optional[str] = Query(None, description="Filter by status"),
        created_from: Optional[str] = Query(None, description="Created from date"),
        created_to: Optional[str] = Query(None, description="Created to date"),
        **kwargs
    ):
        """Create filter params from query parameters"""
        # Extract custom filters from kwargs
        custom_filters = {k: v for k, v in kwargs.items() if k not in ['search', 'status', 'created_from', 'created_to']}
        
        return cls(
            search=search,
            status=status,
            created_from=created_from,
            created_to=created_to,
            custom_filters=custom_filters
        )


class SortParams(BaseModel):
    """Sort parameters"""
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")
    
    @classmethod
    def from_query(
        cls,
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: SortOrder = Query(SortOrder.DESC, description="Sort order")
    ):
        """Create sort params from query parameters"""
        return cls(sort_by=sort_by, sort_order=sort_order)
    
    def to_mongo_sort(self) -> List[tuple]:
        """
        Convert to MongoDB sort format
        
        Returns:
            List of (field, direction) tuples
        """
        if not self.sort_by:
            return []
        
        direction = 1 if self.sort_order == SortOrder.ASC else -1
        return [(self.sort_by, direction)]


def build_filter_query(
    filters: FilterParams,
    allowed_fields: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Build MongoDB filter query from filter parameters
    
    Args:
        filters: Filter parameters
        allowed_fields: List of allowed filter fields (for security)
        
    Returns:
        MongoDB query dictionary
    """
    query: Dict[str, Any] = {}
    
    # Status filter
    if filters.status:
        if allowed_fields is None or "status" in allowed_fields:
            query["status"] = filters.status
    
    # Date range filter
    if filters.created_from or filters.created_to:
        if allowed_fields is None or "created_at" in allowed_fields:
            date_filter: Dict[str, Any] = {}
            if filters.created_from:
                date_filter["$gte"] = filters.created_from
            if filters.created_to:
                date_filter["$lte"] = filters.created_to
            if date_filter:
                query["created_at"] = date_filter
    
    # Search filter (text search)
    if filters.search:
        if allowed_fields is None or "search" in allowed_fields:
            # Use text search if available, otherwise regex
            query["$or"] = [
                {"name": {"$regex": filters.search, "$options": "i"}},
                {"description": {"$regex": filters.search, "$options": "i"}}
            ]
    
    # Custom filters
    if filters.custom_filters:
        for key, value in filters.custom_filters.items():
            if allowed_fields is None or key in allowed_fields:
                query[key] = value
    
    return query

