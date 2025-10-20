"""
Proactive Intelligence Engine API Routes
Hybrid AI with human expert oversight endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.services.proactive_intelligence_engine import (
    get_proactive_intelligence_engine,
    ProactiveIntelligenceEngine,
    ClientPreferenceLevel,
    DecisionCriticality,
    ActionType,
    ProactiveAction,
    ExpertIntervention
)
from backend.services.auth_service import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/api/proactive-intelligence", tags=["proactive-intelligence"])

class ClientPreferenceUpdate(BaseModel):
    preference_level: ClientPreferenceLevel
    risk_tolerance: float = Field(..., ge=0.0, le=1.0)
    learning_rate: float = Field(..., ge=0.0, le=1.0)
    expert_preferences: Dict[str, Any] = {}

class ExpertDecision(BaseModel):
    action_id: str
    expert_id: str
    decision: str = Field(..., regex="^(approved|rejected|modified)$")
    reasoning: str
    modifications: Optional[Dict[str, Any]] = None

class ActionExecutionRequest(BaseModel):
    action_id: str
    execute_immediately: bool = False
    expert_override: Optional[ExpertDecision] = None

@router.post("/client/{client_id}/analyze-preferences")
async def analyze_client_preferences(
    client_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Analyze and learn client preferences for adaptive intelligence"""
    try:
        profile = await engine.analyze_client_preferences(client_id)
        
        # Store analysis in background
        background_tasks.add_task(store_preference_analysis, client_id, profile)
        
        return {
            "success": True,
            "client_id": client_id,
            "profile": {
                "preference_level": profile.preference_level.value,
                "risk_tolerance": profile.risk_tolerance,
                "learning_rate": profile.learning_rate,
                "last_updated": profile.last_updated.isoformat()
            },
            "message": "Client preferences analyzed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preference analysis failed: {str(e)}")

@router.put("/client/{client_id}/preferences")
async def update_client_preferences(
    client_id: str,
    preferences: ClientPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Update client preferences for adaptive intelligence"""
    try:
        # Update client profile
        if client_id in engine.client_profiles:
            profile = engine.client_profiles[client_id]
            profile.preference_level = preferences.preference_level
            profile.risk_tolerance = preferences.risk_tolerance
            profile.learning_rate = preferences.learning_rate
            profile.expert_preferences.update(preferences.expert_preferences)
            profile.last_updated = datetime.utcnow()
            
            await engine._save_client_profile(profile)
        
        return {
            "success": True,
            "client_id": client_id,
            "message": "Client preferences updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preference update failed: {str(e)}")

@router.post("/client/{client_id}/generate-actions")
async def generate_proactive_actions(
    client_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Generate proactive actions based on client preferences and data"""
    try:
        actions = await engine.generate_proactive_actions(client_id)
        
        # Process actions in background
        background_tasks.add_task(process_generated_actions, client_id, actions)
        
        return {
            "success": True,
            "client_id": client_id,
            "actions_generated": len(actions),
            "actions": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "priority": action.priority,
                    "confidence": action.confidence,
                    "expected_impact": action.expected_impact,
                    "risk_level": action.risk_level,
                    "requires_human_approval": action.requires_human_approval,
                    "human_expert_required": action.human_expert_required,
                    "reasoning": action.reasoning,
                    "created_at": action.created_at.isoformat(),
                    "expires_at": action.expires_at.isoformat() if action.expires_at else None
                }
                for action in actions
            ],
            "message": f"Generated {len(actions)} proactive actions"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action generation failed: {str(e)}")

@router.get("/client/{client_id}/actions")
async def get_client_actions(
    client_id: str,
    status: str = Query("active", description="Filter by action status"),
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Get proactive actions for a client"""
    try:
        if status == "active":
            actions = [
                action for action in engine.active_actions.values()
                if action.client_id == client_id
            ]
        else:
            # This would query historical actions from database
            actions = []
        
        return {
            "success": True,
            "client_id": client_id,
            "status": status,
            "actions": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "campaign_id": action.campaign_id,
                    "priority": action.priority,
                    "confidence": action.confidence,
                    "expected_impact": action.expected_impact,
                    "risk_level": action.risk_level,
                    "requires_human_approval": action.requires_human_approval,
                    "human_expert_required": action.human_expert_required,
                    "reasoning": action.reasoning,
                    "created_at": action.created_at.isoformat(),
                    "expires_at": action.expires_at.isoformat() if action.expires_at else None
                }
                for action in actions
            ],
            "total_actions": len(actions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action retrieval failed: {str(e)}")

@router.post("/action/{action_id}/execute")
async def execute_proactive_action(
    action_id: str,
    request: ActionExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Execute a proactive action with optional expert intervention"""
    try:
        # Create expert intervention if provided
        expert_intervention = None
        if request.expert_override:
            expert_intervention = ExpertIntervention(
                intervention_id=f"intervention_{action_id}_{datetime.utcnow().timestamp()}",
                action_id=action_id,
                expert_id=request.expert_override.expert_id,
                decision=request.expert_override.decision,
                reasoning=request.expert_override.reasoning,
                modifications=request.expert_override.modifications
            )
        
        # Execute action
        result = await engine.execute_action(action_id, expert_intervention)
        
        # Log execution in background
        background_tasks.add_task(log_action_execution, action_id, result, current_user.id)
        
        return {
            "success": True,
            "action_id": action_id,
            "execution_result": result,
            "message": "Action executed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")

@router.post("/action/{action_id}/expert-decision")
async def submit_expert_decision(
    action_id: str,
    decision: ExpertDecision,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Submit expert decision for a proactive action"""
    try:
        expert_intervention = ExpertIntervention(
            intervention_id=f"intervention_{action_id}_{datetime.utcnow().timestamp()}",
            action_id=action_id,
            expert_id=decision.expert_id,
            decision=decision.decision,
            reasoning=decision.reasoning,
            modifications=decision.modifications
        )
        
        # Store expert intervention
        engine.expert_interventions[expert_intervention.intervention_id] = expert_intervention
        
        # Execute action with expert decision
        result = await engine.execute_action(action_id, expert_intervention)
        
        # Log expert decision in background
        background_tasks.add_task(log_expert_decision, expert_intervention, current_user.id)
        
        return {
            "success": True,
            "action_id": action_id,
            "expert_intervention": {
                "intervention_id": expert_intervention.intervention_id,
                "expert_id": expert_intervention.expert_id,
                "decision": expert_intervention.decision,
                "reasoning": expert_intervention.reasoning,
                "created_at": expert_intervention.created_at.isoformat()
            },
            "execution_result": result,
            "message": "Expert decision submitted and action executed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert decision submission failed: {str(e)}")

@router.get("/client/{client_id}/insights")
async def get_client_insights(
    client_id: str,
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Get comprehensive insights for a client"""
    try:
        insights = await engine.get_client_insights(client_id)
        
        return {
            "success": True,
            "client_id": client_id,
            "insights": insights,
            "message": "Client insights retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights retrieval failed: {str(e)}")

@router.get("/client/{client_id}/recommendations")
async def get_client_recommendations(
    client_id: str,
    category: Optional[str] = Query(None, description="Filter recommendations by category"),
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Get personalized recommendations for a client"""
    try:
        profile = engine.client_profiles.get(client_id)
        if not profile:
            profile = await engine.analyze_client_preferences(client_id)
        
        recommendations = await engine._generate_client_recommendations(client_id, profile)
        
        # Filter by category if specified
        if category:
            recommendations = [r for r in recommendations if category.lower() in r.lower()]
        
        return {
            "success": True,
            "client_id": client_id,
            "category": category,
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "message": "Recommendations retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations retrieval failed: {str(e)}")

@router.get("/actions/pending-approval")
async def get_pending_approvals(
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Get all actions pending human approval"""
    try:
        pending_actions = [
            action for action in engine.active_actions.values()
            if action.requires_human_approval
        ]
        
        # Sort by priority and confidence
        pending_actions.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
        
        return {
            "success": True,
            "pending_actions": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "client_id": action.client_id,
                    "campaign_id": action.campaign_id,
                    "priority": action.priority,
                    "confidence": action.confidence,
                    "expected_impact": action.expected_impact,
                    "risk_level": action.risk_level,
                    "reasoning": action.reasoning,
                    "created_at": action.created_at.isoformat(),
                    "expires_at": action.expires_at.isoformat() if action.expires_at else None
                }
                for action in pending_actions
            ],
            "total_pending": len(pending_actions),
            "message": "Pending approvals retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pending approvals retrieval failed: {str(e)}")

@router.get("/actions/expert-required")
async def get_expert_required_actions(
    current_user: User = Depends(get_current_user),
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Get all actions requiring expert intervention"""
    try:
        expert_actions = [
            action for action in engine.active_actions.values()
            if action.human_expert_required
        ]
        
        # Sort by priority and risk level
        expert_actions.sort(key=lambda x: (x.priority, x.risk_level), reverse=True)
        
        return {
            "success": True,
            "expert_required_actions": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "client_id": action.client_id,
                    "campaign_id": action.campaign_id,
                    "priority": action.priority,
                    "confidence": action.confidence,
                    "expected_impact": action.expected_impact,
                    "risk_level": action.risk_level,
                    "reasoning": action.reasoning,
                    "data_evidence": action.data_evidence,
                    "created_at": action.created_at.isoformat(),
                    "expires_at": action.expires_at.isoformat() if action.expires_at else None
                }
                for action in expert_actions
            ],
            "total_expert_required": len(expert_actions),
            "message": "Expert required actions retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Expert required actions retrieval failed: {str(e)}")

@router.get("/health")
async def proactive_intelligence_health(
    engine: ProactiveIntelligenceEngine = Depends(get_proactive_intelligence_engine)
):
    """Health check for proactive intelligence engine"""
    try:
        return {
            "status": "healthy",
            "engine_initialized": engine is not None,
            "client_profiles_loaded": len(engine.client_profiles),
            "active_actions": len(engine.active_actions),
            "expert_interventions": len(engine.expert_interventions),
            "models_trained": {
                "fatigue_predictor": engine.fatigue_predictor is not None,
                "ltv_predictor": engine.ltv_predictor is not None,
                "churn_predictor": engine.churn_predictor is not None,
                "anomaly_detector": engine.anomaly_detector is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Background task functions
async def store_preference_analysis(client_id: str, profile):
    """Store preference analysis in database"""
    # Implementation would save to MongoDB
    pass

async def process_generated_actions(client_id: str, actions: List[ProactiveAction]):
    """Process generated actions in background"""
    # Implementation would handle action processing
    pass

async def log_action_execution(action_id: str, result: Dict[str, Any], user_id: str):
    """Log action execution in database"""
    # Implementation would log to MongoDB
    pass

async def log_expert_decision(intervention: ExpertIntervention, user_id: str):
    """Log expert decision in database"""
    # Implementation would log to MongoDB
    pass
