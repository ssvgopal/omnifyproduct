"""
Real-Time Personalization Engine API Routes
Production-grade API endpoints for dynamic content, audience segmentation, and behavioral targeting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import redis

from services.real_time_personalization_service import (
    get_real_time_personalization_service, RealTimePersonalizationService,
    PersonalizationType, AudienceSegment, ContentType, BehavioralEvent
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class UserProfileRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    demographics: Optional[Dict[str, Any]] = Field({}, description="Demographic data")
    preferences: Optional[Dict[str, Any]] = Field({}, description="User preferences")

class BehavioralEventRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    event_type: str = Field(..., description="Event type")
    properties: Dict[str, Any] = Field(..., description="Event properties")
    session_id: str = Field(..., description="Session identifier")
    page_url: Optional[str] = Field(None, description="Page URL")

class AudienceSegmentRequest(BaseModel):
    name: str = Field(..., description="Segment name")
    segment_type: str = Field(..., description="Segment type")
    criteria: Dict[str, Any] = Field(..., description="Segment criteria")
    description: Optional[str] = Field("", description="Segment description")

class PersonalizationRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    content_type: str = Field(..., description="Content type")
    base_content: Dict[str, Any] = Field(..., description="Base content to personalize")

class UserProfileResponse(BaseModel):
    user_id: str
    demographics: Dict[str, Any]
    behaviors: List[Dict[str, Any]]
    preferences: Dict[str, Any]
    segments: List[str]
    engagement_score: float
    last_updated: str

class AudienceSegmentResponse(BaseModel):
    segment_id: str
    name: str
    segment_type: str
    criteria: Dict[str, Any]
    size: int
    description: str
    created_at: str

class PersonalizedContentResponse(BaseModel):
    content_id: str
    content_type: str
    user_id: str
    segment_id: str
    content_data: Dict[str, Any]
    personalization_rules: List[Dict[str, Any]]
    created_at: str

class PersonalizationDashboardResponse(BaseModel):
    client_id: str
    user_statistics: Dict[str, Any]
    segment_statistics: Dict[str, Any]
    behavioral_statistics: Dict[str, Any]
    personalization_statistics: Dict[str, Any]
    generated_at: str

# Dependency
async def get_personalization_service(db: AsyncIOMotorClient = Depends(get_database)) -> RealTimePersonalizationService:
    # In production, initialize Redis properly
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    return get_real_time_personalization_service(db, redis_client)

# User Profile Management Endpoints
@router.post("/api/personalization/profiles", summary="Create User Profile")
async def create_user_profile(
    request: UserProfileRequest = Body(...),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Create a new user profile for personalization.
    Initializes user data and behavioral tracking.
    """
    try:
        profile_data = {
            "demographics": request.demographics,
            "preferences": request.preferences
        }
        
        profile = await personalization_service.profile_manager.create_user_profile(
            request.user_id, profile_data
        )
        
        return UserProfileResponse(
            user_id=profile.user_id,
            demographics=profile.demographics,
            behaviors=profile.behaviors,
            preferences=profile.preferences,
            segments=profile.segments,
            engagement_score=profile.engagement_score,
            last_updated=profile.last_updated.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user profile"
        )

@router.get("/api/personalization/profiles/{user_id}", response_model=UserProfileResponse, summary="Get User Profile")
async def get_user_profile(
    user_id: str,
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get user profile with behavioral data and preferences.
    Returns comprehensive user profile for personalization.
    """
    try:
        profile = await personalization_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserProfileResponse(
            user_id=profile.user_id,
            demographics=profile.demographics,
            behaviors=profile.behaviors,
            preferences=profile.preferences,
            segments=profile.segments,
            engagement_score=profile.engagement_score,
            last_updated=profile.last_updated.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@router.put("/api/personalization/profiles/{user_id}", response_model=UserProfileResponse, summary="Update User Profile")
async def update_user_profile(
    user_id: str,
    request: UserProfileRequest = Body(...),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Update user profile with new data.
    Merges new data with existing profile information.
    """
    try:
        updates = {
            "demographics": request.demographics,
            "preferences": request.preferences
        }
        
        profile = await personalization_service.profile_manager.update_user_profile(
            user_id, updates
        )
        
        return UserProfileResponse(
            user_id=profile.user_id,
            demographics=profile.demographics,
            behaviors=profile.behaviors,
            preferences=profile.preferences,
            segments=profile.segments,
            engagement_score=profile.engagement_score,
            last_updated=profile.last_updated.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

# Behavioral Event Tracking Endpoints
@router.post("/api/personalization/events", summary="Track Behavioral Event")
async def track_behavioral_event(
    request: BehavioralEventRequest = Body(...),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Track a behavioral event for personalization.
    Records user behavior for real-time personalization.
    """
    try:
        event_type = BehavioralEvent(request.event_type)
        
        await personalization_service.track_user_event(
            request.user_id,
            event_type,
            request.properties,
            request.session_id,
            request.page_url
        )
        
        return {
            "user_id": request.user_id,
            "event_type": request.event_type,
            "tracked_at": datetime.utcnow().isoformat(),
            "status": "tracked"
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type: {request.event_type}"
        )
    except Exception as e:
        logger.error(f"Error tracking behavioral event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track behavioral event"
        )

@router.get("/api/personalization/events/{user_id}", summary="Get User Events")
async def get_user_events(
    user_id: str,
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    days: int = Query(30, description="Number of days to look back"),
    limit: int = Query(100, description="Maximum number of events to return"),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get behavioral events for a user.
    Returns event history with filtering options.
    """
    try:
        # Build query
        query = {"user_id": user_id}
        
        if event_type:
            query["event_type"] = event_type
        
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query["timestamp"] = {"$gte": cutoff_date.isoformat()}
        
        # Get events
        events = await personalization_service.db.behavioral_events.find(query).sort("timestamp", -1).limit(limit).to_list(length=None)
        
        return {
            "user_id": user_id,
            "events": events,
            "total_count": len(events),
            "query_period_days": days
        }
        
    except Exception as e:
        logger.error(f"Error getting user events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user events"
        )

# Audience Segmentation Endpoints
@router.post("/api/personalization/segments", response_model=AudienceSegmentResponse, summary="Create Audience Segment")
async def create_audience_segment(
    request: AudienceSegmentRequest = Body(...),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Create a new audience segment.
    Defines criteria and populates segment with matching users.
    """
    try:
        segment_data = {
            "name": request.name,
            "segment_type": request.segment_type,
            "criteria": request.criteria,
            "description": request.description
        }
        
        segment_id = await personalization_service.create_audience_segment(segment_data)
        
        # Get created segment
        segment_doc = await personalization_service.db.audience_segments.find_one({"segment_id": segment_id})
        
        return AudienceSegmentResponse(
            segment_id=segment_doc["segment_id"],
            name=segment_doc["name"],
            segment_type=segment_doc["segment_type"],
            criteria=segment_doc["criteria"],
            size=segment_doc["size"],
            description=segment_doc["description"],
            created_at=segment_doc["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Error creating audience segment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audience segment"
        )

@router.get("/api/personalization/segments", response_model=List[AudienceSegmentResponse], summary="List Audience Segments")
async def list_audience_segments(
    segment_type: Optional[str] = Query(None, description="Filter by segment type"),
    active_only: bool = Query(True, description="Show only active segments"),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    List audience segments with filtering options.
    Returns segment definitions and metadata.
    """
    try:
        # Build query
        query = {}
        if segment_type:
            query["segment_type"] = segment_type
        if active_only:
            query["active"] = True
        
        # Get segments
        segments = await personalization_service.db.audience_segments.find(query).sort("created_at", -1).to_list(length=None)
        
        segment_responses = []
        for segment in segments:
            segment_responses.append(AudienceSegmentResponse(
                segment_id=segment["segment_id"],
                name=segment["name"],
                segment_type=segment["segment_type"],
                criteria=segment["criteria"],
                size=segment["size"],
                description=segment["description"],
                created_at=segment["created_at"]
            ))
        
        return segment_responses
        
    except Exception as e:
        logger.error(f"Error listing audience segments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list audience segments"
        )

@router.get("/api/personalization/segments/{segment_id}/users", summary="Get Segment Users")
async def get_segment_users(
    segment_id: str,
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get users in an audience segment.
    Returns list of user IDs in the segment.
    """
    try:
        users = await personalization_service.segmentation_engine.get_segment_users(segment_id)
        
        return {
            "segment_id": segment_id,
            "users": users,
            "total_count": len(users)
        }
        
    except Exception as e:
        logger.error(f"Error getting segment users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get segment users"
        )

@router.get("/api/personalization/segments/{segment_id}/performance", summary="Get Segment Performance")
async def get_segment_performance(
    segment_id: str,
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get performance metrics for an audience segment.
    Returns behavioral analysis and engagement metrics.
    """
    try:
        performance = await personalization_service.segmentation_engine.analyze_segment_performance(segment_id)
        
        return {
            "segment_id": segment_id,
            "performance": performance,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting segment performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get segment performance"
        )

# Content Personalization Endpoints
@router.post("/api/personalization/content", response_model=PersonalizedContentResponse, summary="Personalize Content")
async def personalize_content(
    request: PersonalizationRequest = Body(...),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Personalize content for a specific user.
    Returns personalized content based on user profile and segments.
    """
    try:
        content_type = ContentType(request.content_type)
        
        personalized = await personalization_service.personalize_for_user(
            request.user_id,
            content_type,
            request.base_content
        )
        
        return PersonalizedContentResponse(
            content_id=personalized.content_id,
            content_type=personalized.content_type.value,
            user_id=personalized.user_id,
            segment_id=personalized.segment_id,
            content_data=personalized.content_data,
            personalization_rules=personalized.personalization_rules,
            created_at=personalized.created_at.isoformat()
        )
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {request.content_type}"
        )
    except Exception as e:
        logger.error(f"Error personalizing content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to personalize content"
        )

@router.get("/api/personalization/content/{user_id}", summary="Get Personalized Content")
async def get_personalized_content(
    user_id: str,
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    limit: int = Query(50, description="Maximum number of content items"),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get personalized content for a user.
    Returns content history with personalization details.
    """
    try:
        # Build query
        query = {"user_id": user_id}
        if content_type:
            query["content_type"] = content_type
        
        # Get personalized content
        content_items = await personalization_service.db.personalized_content.find(query).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return {
            "user_id": user_id,
            "content_items": content_items,
            "total_count": len(content_items)
        }
        
    except Exception as e:
        logger.error(f"Error getting personalized content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get personalized content"
        )

# Personalization Rules Management
@router.post("/api/personalization/rules", summary="Create Personalization Rule")
async def create_personalization_rule(
    segment_id: str = Body(..., description="Target segment ID"),
    content_type: str = Body(..., description="Content type"),
    personalization: Dict[str, Any] = Body(..., description="Personalization data"),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Create a personalization rule for a segment.
    Defines how content should be personalized for segment members.
    """
    try:
        rule_doc = {
            "rule_id": str(uuid.uuid4()),
            "segment_id": segment_id,
            "content_type": content_type,
            "personalization": personalization,
            "active": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await personalization_service.db.personalization_rules.insert_one(rule_doc)
        
        return {
            "rule_id": rule_doc["rule_id"],
            "segment_id": segment_id,
            "content_type": content_type,
            "created_at": rule_doc["created_at"],
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Error creating personalization rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create personalization rule"
        )

@router.get("/api/personalization/rules", summary="List Personalization Rules")
async def list_personalization_rules(
    segment_id: Optional[str] = Query(None, description="Filter by segment ID"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    List personalization rules with filtering options.
    Returns rule definitions and configurations.
    """
    try:
        # Build query
        query = {"active": True}
        if segment_id:
            query["segment_id"] = segment_id
        if content_type:
            query["content_type"] = content_type
        
        # Get rules
        rules = await personalization_service.db.personalization_rules.find(query).to_list(length=None)
        
        return {
            "rules": rules,
            "total_count": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Error listing personalization rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list personalization rules"
        )

# Dashboard Endpoint
@router.get("/api/personalization/dashboard/{client_id}", response_model=PersonalizationDashboardResponse, summary="Get Personalization Dashboard")
async def get_personalization_dashboard(
    client_id: str,
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Get comprehensive personalization dashboard.
    Returns user statistics, segment data, and personalization metrics.
    """
    try:
        dashboard = await personalization_service.get_personalization_dashboard(client_id)
        
        return PersonalizationDashboardResponse(
            client_id=dashboard["client_id"],
            user_statistics=dashboard["user_statistics"],
            segment_statistics=dashboard["segment_statistics"],
            behavioral_statistics=dashboard["behavioral_statistics"],
            personalization_statistics=dashboard["personalization_statistics"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting personalization dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get personalization dashboard"
        )

# Real-Time Personalization Health Check
@router.get("/api/personalization/health", summary="Personalization System Health Check")
async def personalization_health_check(
    personalization_service: RealTimePersonalizationService = Depends(get_personalization_service)
):
    """
    Check the health of the personalization system.
    Returns system status and capabilities.
    """
    try:
        # Check database connection
        await personalization_service.db.admin.command('ping')
        
        # Check Redis connection
        try:
            await personalization_service.redis.ping()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"
        
        # Get system statistics
        stats = {
            "total_users": await personalization_service.db.user_profiles.count_documents({}),
            "active_users": await personalization_service.db.user_profiles.count_documents({
                "last_updated": {"$gte": (datetime.utcnow() - timedelta(days=30)).isoformat()}
            }),
            "total_segments": await personalization_service.db.audience_segments.count_documents({}),
            "active_segments": await personalization_service.db.audience_segments.count_documents({"active": True}),
            "total_events": await personalization_service.db.behavioral_events.count_documents({}),
            "total_personalized_content": await personalization_service.db.personalized_content.count_documents({})
        }
        
        all_healthy = redis_status == "healthy"
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": {
                "database": "healthy",
                "redis": redis_status,
                "profile_manager": "healthy",
                "segmentation_engine": "healthy",
                "content_engine": "healthy"
            },
            "statistics": stats,
            "capabilities": {
                "user_profiling": True,
                "behavioral_tracking": True,
                "audience_segmentation": True,
                "content_personalization": True,
                "real_time_updates": True,
                "engagement_scoring": True,
                "preference_learning": True,
                "dynamic_content": True
            },
            "supported_personalization_types": [pt.value for pt in PersonalizationType],
            "supported_audience_segments": [as.value for as in AudienceSegment],
            "supported_content_types": [ct.value for ct in ContentType],
            "supported_behavioral_events": [be.value for be in BehavioralEvent],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking personalization health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
