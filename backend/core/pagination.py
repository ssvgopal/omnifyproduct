"""
Pagination Support for API Endpoints
Provides consistent pagination across all list endpoints
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Number of items per page")
    
    @classmethod
    def from_query(
        cls,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        """Create pagination params from query parameters"""
        return cls(page=page, page_size=page_size)
    
    @property
    def skip(self) -> int:
        """Calculate skip value for database queries"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Get limit value for database queries"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response
        
        Args:
            items: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Number of items per page
            
        Returns:
            PaginatedResponse instance
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


async def paginate_query(
    query_func,
    pagination: PaginationParams,
    *args,
    **kwargs
) -> PaginatedResponse[Dict[str, Any]]:
    """
    Paginate a database query
    
    Args:
        query_func: Async function that returns a cursor or list
        pagination: Pagination parameters
        *args: Positional arguments for query_func
        **kwargs: Keyword arguments for query_func
        
    Returns:
        PaginatedResponse with results
    """
    # Get total count (if query_func supports it)
    # For now, we'll execute the query and count results
    # In production, you might want a separate count query
    
    # Execute query with pagination
    cursor = await query_func(*args, **kwargs)
    
    # Get total count
    if hasattr(cursor, 'count'):
        total = await cursor.count()
    else:
        # If it's already a list, count it
        if isinstance(cursor, list):
            total = len(cursor)
            items = cursor[pagination.skip:pagination.skip + pagination.limit]
        else:
            # Assume it's a cursor
            items = await cursor.skip(pagination.skip).limit(pagination.limit).to_list(length=pagination.limit)
            # Count total (this is inefficient, but works)
            total_cursor = await query_func(*args, **kwargs)
            if hasattr(total_cursor, 'count'):
                total = await total_cursor.count()
            else:
                total = len(await total_cursor.to_list(length=None))
    
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )

