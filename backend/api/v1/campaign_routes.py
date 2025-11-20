"""
Versioned Campaign Management API Routes (v1)
Example of versioned API with pagination, filtering, and sorting
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime

from core.api_versioning import create_versioned_router
from core.pagination import PaginationParams, PaginatedResponse
from core.filtering import FilterParams, SortParams, build_filter_query
from services.campaign_management_service import CampaignManagementService, get_campaign_management_service
from core.auth import get_current_user
from motor.motor_asyncio import AsyncIOMotorClient

def get_database() -> AsyncIOMotorClient:
    """Get database instance"""
    from agentkit_server import db
    return db

# Create versioned router
router = create_versioned_router("v1")


@router.get("/campaigns", response_model=PaginatedResponse)
async def list_campaigns(
    pagination: PaginationParams = Depends(PaginationParams.from_query),
    filters: FilterParams = Depends(FilterParams.from_query),
    sort: SortParams = Depends(SortParams.from_query),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_database),
    campaign_service: CampaignManagementService = Depends(get_campaign_management_service)
):
    """
    List campaigns with pagination, filtering, and sorting
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - search: Search term
    - status: Filter by status
    - created_from: Created from date (ISO format)
    - created_to: Created to date (ISO format)
    - sort_by: Field to sort by
    - sort_order: Sort order (asc/desc)
    """
    try:
        organization_id = current_user.get("organization_id")
        
        # Build filter query
        filter_query = build_filter_query(
            filters,
            allowed_fields=["status", "created_at", "platform", "name"]
        )
        
        # Add organization filter
        filter_query["organization_id"] = organization_id
        
        # Get campaigns with pagination
        cursor = db.campaigns.find(filter_query)
        
        # Apply sorting
        if sort.sort_by:
            sort_list = sort.to_mongo_sort()
            cursor = cursor.sort(sort_list)
        
        # Get total count
        total = await db.campaigns.count_documents(filter_query)
        
        # Apply pagination
        items = await cursor.skip(pagination.skip).limit(pagination.limit).to_list(length=pagination.limit)
        
        # Create paginated response
        return PaginatedResponse.create(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}"
        )


@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user),
    campaign_service: CampaignManagementService = Depends(get_campaign_management_service)
):
    """Get campaign by ID"""
    try:
        organization_id = current_user.get("organization_id")
        campaign = await campaign_service.get_campaign(campaign_id, organization_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return campaign
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )

