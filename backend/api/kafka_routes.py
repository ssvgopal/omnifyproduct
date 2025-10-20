"""
Kafka Event Streaming Management Routes
API endpoints for managing Kafka topics, events, and monitoring
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from services.kafka_eventing import (
    kafka_service, EventType, EventPriority, EventMetadata, EventMessage
)
from services.oidc_auth import get_current_user, TokenValidationResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kafka", tags=["Kafka Event Streaming Management"])

# Request/Response Models
class EventRequest(BaseModel):
    """Request to produce an event"""
    event_type: str
    payload: Dict[str, Any]
    source: str
    organization_id: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: str = "medium"

class EventResponse(BaseModel):
    """Event production response"""
    event_id: str
    status: str
    message: str
    produced_at: str

class TopicStatsResponse(BaseModel):
    """Topic statistics response"""
    topic: str
    partitions: int
    total_lag: int
    partition_stats: List[Dict[str, Any]]
    timestamp: str

class ConsumerGroupResponse(BaseModel):
    """Consumer group response"""
    group_id: str
    topics: List[str]
    active_consumers: int
    status: str

# ========== KAFKA MANAGEMENT ROUTES ==========

@router.get("/health")
async def kafka_health_check():
    """Check Kafka service health"""
    try:
        return await kafka_service.health_check()
    except Exception as e:
        logger.error(f"Kafka health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Kafka health check failed: {str(e)}"
        )

@router.post("/events", response_model=EventResponse)
async def produce_event(
    request: EventRequest,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Produce an event to Kafka"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled. Set ENABLE_KAFKA=true to enable."
            )

        # Validate event type
        try:
            event_type = EventType(request.event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event type: {request.event_type}"
            )

        # Validate priority
        try:
            priority = EventPriority(request.priority)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {request.priority}"
            )

        # Create event metadata
        import uuid
        event_id = str(uuid.uuid4())
        metadata = EventMetadata(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            source=request.source,
            organization_id=request.organization_id,
            user_id=request.user_id or current_user.user_id,
            correlation_id=request.correlation_id,
            priority=priority
        )

        # Produce event
        success = await kafka_service.produce_event(event_type, request.payload, metadata)
        
        if success:
            logger.info("Event produced to Kafka", extra={
                "event_id": event_id,
                "event_type": request.event_type,
                "user_id": current_user.user_id,
                "organization_id": current_user.organization_id
            })

            return EventResponse(
                event_id=event_id,
                status="produced",
                message="Event produced successfully",
                produced_at=datetime.utcnow().isoformat()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to produce event"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to produce event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to produce event: {str(e)}"
        )

@router.get("/topics/{topic}/stats", response_model=TopicStatsResponse)
async def get_topic_stats(
    topic: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get topic statistics"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        stats = await kafka_service.get_topic_stats(topic)
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=stats["error"]
            )

        return TopicStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get topic stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get topic stats: {str(e)}"
        )

@router.get("/consumer-groups", response_model=List[ConsumerGroupResponse])
async def get_consumer_groups(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get consumer group information"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Get consumer group info
        consumer_groups = [
            ConsumerGroupResponse(
                group_id=kafka_service.consumer_group,
                topics=list(kafka_service.consumers.keys()),
                active_consumers=len(kafka_service.consumers),
                status="active" if kafka_service.consumers else "inactive"
            )
        ]

        return consumer_groups

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get consumer groups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get consumer groups: {str(e)}"
        )

@router.post("/topics/create")
async def create_topics(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Create required Kafka topics"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        success = await kafka_service.create_topics()
        
        if success:
            logger.info("Kafka topics created", extra={
                "user_id": current_user.user_id,
                "topics": [
                    kafka_service.topic_integration_sync,
                    kafka_service.topic_model_trained,
                    kafka_service.topic_dlq
                ]
            })

            return {
                "status": "success",
                "message": "Kafka topics created successfully",
                "topics": [
                    kafka_service.topic_integration_sync,
                    kafka_service.topic_model_trained,
                    kafka_service.topic_dlq
                ]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create topics"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create topics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create topics: {str(e)}"
        )

@router.get("/events/types")
async def get_event_types(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get available event types"""
    try:
        event_types = [
            {
                "type": event_type.value,
                "description": event_type.name.replace("_", " ").title(),
                "category": "integration" if "integration" in event_type.value else 
                           "model" if "model" in event_type.value else
                           "workflow" if "workflow" in event_type.value else
                           "system"
            }
            for event_type in EventType
        ]

        return {
            "event_types": event_types,
            "total": len(event_types)
        }

    except Exception as e:
        logger.error(f"Failed to get event types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event types: {str(e)}"
        )

@router.get("/events/priorities")
async def get_event_priorities(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get available event priorities"""
    try:
        priorities = [
            {
                "priority": priority.value,
                "description": priority.name.title(),
                "level": i
            }
            for i, priority in enumerate(EventPriority)
        ]

        return {
            "priorities": priorities,
            "total": len(priorities)
        }

    except Exception as e:
        logger.error(f"Failed to get event priorities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event priorities: {str(e)}"
        )

@router.get("/configuration")
async def get_kafka_configuration(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get Kafka service configuration"""
    try:
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        return {
            "kafka_enabled": kafka_service.enable_kafka,
            "bootstrap_servers": kafka_service.bootstrap_servers,
            "consumer_group": kafka_service.consumer_group,
            "topics": {
                "integration_sync": kafka_service.topic_integration_sync,
                "model_trained": kafka_service.topic_model_trained,
                "dlq": kafka_service.topic_dlq
            },
            "dlq_enabled": kafka_service.dlq_enabled,
            "max_retries": kafka_service.max_retries,
            "active_consumers": len(kafka_service.consumers),
            "producer_connected": kafka_service.producer is not None,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Kafka configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration: {str(e)}"
        )

@router.post("/consumers/{topic}/start")
async def start_consumer(
    topic: str,
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Start a consumer for a topic"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Simple event handler for demonstration
        async def event_handler(event_message: EventMessage):
            logger.info(f"Event processed: {event_message.event_type}", extra={
                "event_id": event_message.event_id,
                "organization_id": event_message.organization_id
            })

        success = await kafka_service.start_consumer(topic, event_handler)
        
        if success:
            logger.info("Consumer started", extra={
                "topic": topic,
                "user_id": current_user.user_id
            })

            return {
                "status": "success",
                "message": f"Consumer started for topic: {topic}",
                "topic": topic
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start consumer"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start consumer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start consumer: {str(e)}"
        )

@router.get("/dlq/stats")
async def get_dlq_stats(
    current_user: TokenValidationResult = Depends(get_current_user)
):
    """Get Dead Letter Queue statistics"""
    try:
        if not kafka_service.enable_kafka:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kafka is not enabled"
            )

        # Check permissions
        if "admin" not in current_user.roles and "manager" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Manager or admin permissions required"
            )

        # Get DLQ topic stats
        dlq_stats = await kafka_service.get_topic_stats(kafka_service.topic_dlq)
        
        return {
            "dlq_topic": kafka_service.topic_dlq,
            "dlq_enabled": kafka_service.dlq_enabled,
            "max_retries": kafka_service.max_retries,
            "topic_stats": dlq_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get DLQ stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get DLQ stats: {str(e)}"
        )
