"""
API Routes for Adaptive Client Learning System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from services.adaptive_client_learning_system import (
    get_adaptive_learning_system, 
    AdaptiveClientLearningSystem,
    ClientPersonalityType,
    LearningStyle,
    CommunicationPreference
)
from database.mongodb_schema import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/adaptive-learning", tags=["Adaptive Learning"])

# Pydantic models
class InteractionData(BaseModel):
    """Data for tracking client interaction"""
    client_id: str = Field(..., description="Client identifier")
    interaction_type: str = Field(..., description="Type of interaction")
    action_taken: Optional[str] = Field(None, description="Action taken by client")
    outcome: Optional[str] = Field(None, description="Outcome of interaction")
    data_request: Optional[bool] = Field(False, description="Whether data was requested")
    followed_recommendation: Optional[bool] = Field(None, description="Whether recommendation was followed")
    successful_adaptation: Optional[bool] = Field(None, description="Whether adaptation was successful")
    adaptation_attempt: Optional[bool] = Field(False, description="Whether adaptation was attempted")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class RecommendationRequest(BaseModel):
    """Request for adaptive recommendation"""
    client_id: str = Field(..., description="Client identifier")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for recommendation")
    recommendation_type: Optional[str] = Field(None, description="Specific type of recommendation needed")

class LearningInsightsRequest(BaseModel):
    """Request for learning insights"""
    client_id: str = Field(..., description="Client identifier")
    include_recommendations: bool = Field(True, description="Include personalized recommendations")

class ProfileUpdateRequest(BaseModel):
    """Request to update client profile"""
    client_id: str = Field(..., description="Client identifier")
    personality_type: Optional[str] = Field(None, description="Personality type override")
    learning_style: Optional[str] = Field(None, description="Learning style override")
    communication_preference: Optional[str] = Field(None, description="Communication preference override")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom preferences")

# Dependency to get adaptive learning system
async def get_learning_system() -> AdaptiveClientLearningSystem:
    """Get adaptive learning system instance"""
    db = await get_database()
    return await get_adaptive_learning_system(db)

@router.post("/track-interaction")
async def track_interaction(
    interaction_data: InteractionData,
    background_tasks: BackgroundTasks,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Track client interaction for learning"""
    try:
        # Convert to dict for tracking
        interaction_dict = interaction_data.dict()
        
        # Track interaction in background
        background_tasks.add_task(
            learning_system.track_client_interaction,
            interaction_data.client_id,
            interaction_dict
        )
        
        return {
            "success": True,
            "message": "Interaction tracked successfully",
            "client_id": interaction_data.client_id,
            "interaction_type": interaction_data.interaction_type
        }
        
    except Exception as e:
        logger.error(f"Error tracking interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{client_id}")
async def get_client_profile(
    client_id: str,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Get client learning profile"""
    try:
        profile = await learning_system.get_client_profile(client_id)
        
        if not profile:
            return {
                "success": False,
                "message": "No profile found for client",
                "client_id": client_id
            }
        
        return {
            "success": True,
            "profile": {
                "client_id": profile.client_id,
                "personality_type": profile.personality_type.value,
                "learning_style": profile.learning_style.value,
                "communication_preference": profile.communication_preference.value,
                "behavior_patterns": {
                    "decision_speed": profile.behavior_patterns.decision_speed,
                    "risk_tolerance": profile.behavior_patterns.risk_tolerance,
                    "data_reliance": profile.behavior_patterns.data_reliance,
                    "collaboration_level": profile.behavior_patterns.collaboration_level,
                    "autonomy_level": profile.behavior_patterns.autonomy_level,
                    "communication_frequency": profile.behavior_patterns.communication_frequency,
                    "detail_preference": profile.behavior_patterns.detail_preference
                },
                "confidence_level": profile.confidence_level,
                "adaptation_rate": profile.adaptation_rate,
                "success_patterns": profile.success_patterns,
                "failure_patterns": profile.failure_patterns,
                "preferences": profile.preferences,
                "last_updated": profile.last_updated.isoformat(),
                "learning_score": profile.learning_score
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting client profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendation")
async def generate_recommendation(
    request: RecommendationRequest,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Generate adaptive recommendation for client"""
    try:
        recommendation = await learning_system.generate_adaptive_recommendation(
            request.client_id,
            request.context
        )
        
        return {
            "success": True,
            "recommendation": {
                "type": recommendation.recommendation_type,
                "content": recommendation.content,
                "presentation_style": recommendation.presentation_style,
                "confidence_level": recommendation.confidence_level,
                "reasoning": recommendation.reasoning,
                "alternatives": recommendation.alternatives,
                "expected_outcome": recommendation.expected_outcome,
                "risk_assessment": recommendation.risk_assessment,
                "follow_up_actions": recommendation.follow_up_actions
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights")
async def get_learning_insights(
    request: LearningInsightsRequest,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Get learning insights for client"""
    try:
        insights = await learning_system.get_learning_insights(request.client_id)
        
        return {
            "success": True,
            "insights": insights
        }
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update-profile")
async def update_profile(
    request: ProfileUpdateRequest,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Update client profile with manual overrides"""
    try:
        # Get existing profile
        profile = await learning_system.get_client_profile(request.client_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Client profile not found")
        
        # Update profile with overrides
        if request.personality_type:
            profile.personality_type = ClientPersonalityType(request.personality_type)
        
        if request.learning_style:
            profile.learning_style = LearningStyle(request.learning_style)
        
        if request.communication_preference:
            profile.communication_preference = CommunicationPreference(request.communication_preference)
        
        if request.preferences:
            profile.preferences.update(request.preferences)
        
        profile.last_updated = datetime.utcnow()
        
        # Save updated profile
        await learning_system._save_client_profile(profile)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "client_id": request.client_id
        }
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/personality-types")
async def get_personality_types():
    """Get available personality types"""
    return {
        "success": True,
        "personality_types": [
            {
                "value": personality.value,
                "label": personality.value.replace('_', ' ').title(),
                "description": f"Client prefers {personality.value} decision-making approach"
            }
            for personality in ClientPersonalityType
        ]
    }

@router.get("/learning-styles")
async def get_learning_styles():
    """Get available learning styles"""
    return {
        "success": True,
        "learning_styles": [
            {
                "value": style.value,
                "label": style.value.replace('_', ' ').title(),
                "description": f"Client prefers {style.value} learning approach"
            }
            for style in LearningStyle
        ]
    }

@router.get("/communication-preferences")
async def get_communication_preferences():
    """Get available communication preferences"""
    return {
        "success": True,
        "communication_preferences": [
            {
                "value": preference.value,
                "label": preference.value.replace('_', ' ').title(),
                "description": f"Client prefers {preference.value} communication style"
            }
            for preference in CommunicationPreference
        ]
    }

@router.get("/demo-interaction/{client_id}")
async def generate_demo_interaction(
    client_id: str,
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Generate demo interaction data for testing"""
    try:
        demo_interactions = [
            {
                "client_id": client_id,
                "interaction_type": "dashboard_view",
                "action_taken": "viewed_analytics",
                "outcome": "success",
                "data_request": True,
                "followed_recommendation": True,
                "metadata": {"page": "analytics", "duration": 120}
            },
            {
                "client_id": client_id,
                "interaction_type": "recommendation_review",
                "action_taken": "accepted_recommendation",
                "outcome": "success",
                "followed_recommendation": True,
                "successful_adaptation": True,
                "metadata": {"recommendation_type": "budget_optimization"}
            },
            {
                "client_id": client_id,
                "interaction_type": "experiment_launch",
                "action_taken": "launched_new_campaign",
                "outcome": "success",
                "followed_recommendation": True,
                "successful_adaptation": True,
                "metadata": {"campaign_type": "creative_test", "risk_level": "medium"}
            },
            {
                "client_id": client_id,
                "interaction_type": "data_analysis",
                "action_taken": "analyzed_performance",
                "outcome": "success",
                "data_request": True,
                "metadata": {"analysis_depth": "detailed", "metrics_count": 15}
            },
            {
                "client_id": client_id,
                "interaction_type": "team_collaboration",
                "action_taken": "shared_insights",
                "outcome": "success",
                "metadata": {"team_size": 3, "collaboration_type": "brainstorming"}
            }
        ]
        
        # Track demo interactions
        for interaction in demo_interactions:
            await learning_system.track_client_interaction(client_id, interaction)
        
        return {
            "success": True,
            "message": f"Generated {len(demo_interactions)} demo interactions",
            "client_id": client_id,
            "interactions": demo_interactions
        }
        
    except Exception as e:
        logger.error(f"Error generating demo interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status")
async def get_system_status(
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Get adaptive learning system status"""
    try:
        return {
            "success": True,
            "status": {
                "total_profiles": len(learning_system.client_profiles),
                "tracking_clients": len(learning_system.behavior_tracking),
                "min_interactions_required": learning_system.min_interactions_for_profile,
                "profile_update_frequency": learning_system.profile_update_frequency,
                "learning_decay_factor": learning_system.learning_decay_factor,
                "available_personality_types": len(ClientPersonalityType),
                "available_learning_styles": len(LearningStyle),
                "available_communication_preferences": len(CommunicationPreference)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    learning_system: AdaptiveClientLearningSystem = Depends(get_learning_system)
):
    """Health check for adaptive learning system"""
    try:
        return {
            "success": True,
            "status": "healthy",
            "message": "Adaptive Client Learning System is operational",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "status": "unhealthy",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
