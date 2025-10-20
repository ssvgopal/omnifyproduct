"""
API Routes for Human Expert Intervention System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from services.human_expert_intervention_system import (
    get_human_expert_system,
    HumanExpertInterventionSystem,
    InterventionType,
    InterventionStatus,
    ExpertLevel,
    DecisionComplexity
)
from database.mongodb_schema import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/expert-intervention", tags=["Expert Intervention"])

# Pydantic models
class InterventionRequest(BaseModel):
    """Request for human expert intervention"""
    client_id: str = Field(..., description="Client identifier")
    intervention_type: str = Field(..., description="Type of intervention needed")
    title: str = Field(..., description="Title of the intervention request")
    description: str = Field(..., description="Detailed description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    ai_recommendation: Optional[str] = Field(None, description="AI's recommendation")
    ai_confidence: float = Field(0.5, description="AI's confidence level")
    priority: int = Field(5, description="Priority level (1-10)")
    complexity: str = Field("medium", description="Decision complexity")
    deadline_minutes: Optional[int] = Field(None, description="Deadline in minutes")

class ExpertDecisionSubmission(BaseModel):
    """Expert decision submission"""
    request_id: str = Field(..., description="Intervention request ID")
    expert_id: str = Field(..., description="Expert identifier")
    decision: str = Field(..., description="The decision made")
    reasoning: str = Field(..., description="Reasoning behind decision")
    confidence: float = Field(0.8, description="Expert's confidence")
    alternatives_considered: Optional[List[str]] = Field(None, description="Alternatives considered")
    risk_assessment: Optional[str] = Field(None, description="Risk assessment")
    follow_up_actions: Optional[List[str]] = Field(None, description="Follow-up actions")
    learning_points: Optional[List[str]] = Field(None, description="Learning points for AI")

class EscalationRequest(BaseModel):
    """Request to escalate intervention"""
    request_id: str = Field(..., description="Intervention request ID")
    reason: str = Field(..., description="Reason for escalation")
    escalate_to_level: Optional[str] = Field(None, description="Target expert level")

class ExpertProfileUpdate(BaseModel):
    """Update expert profile"""
    expert_id: str = Field(..., description="Expert identifier")
    name: Optional[str] = Field(None, description="Expert name")
    email: Optional[str] = Field(None, description="Expert email")
    level: Optional[str] = Field(None, description="Expert level")
    specialties: Optional[List[str]] = Field(None, description="Areas of expertise")
    max_load: Optional[int] = Field(None, description="Maximum interventions")
    is_available: Optional[bool] = Field(None, description="Availability status")

# Dependency to get human expert system
async def get_expert_system() -> HumanExpertInterventionSystem:
    """Get human expert intervention system instance"""
    db = await get_database()
    return await get_human_expert_system(db)

@router.post("/request")
async def request_intervention(
    request: InterventionRequest,
    background_tasks: BackgroundTasks,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Request human expert intervention"""
    try:
        # Convert string enums to enum objects
        intervention_type = InterventionType(request.intervention_type)
        complexity = DecisionComplexity(request.complexity)
        
        request_id = await expert_system.request_intervention(
            client_id=request.client_id,
            intervention_type=intervention_type,
            title=request.title,
            description=request.description,
            context=request.context,
            ai_recommendation=request.ai_recommendation,
            ai_confidence=request.ai_confidence,
            priority=request.priority,
            complexity=complexity,
            deadline_minutes=request.deadline_minutes
        )
        
        return {
            "success": True,
            "message": "Intervention request created successfully",
            "request_id": request_id,
            "client_id": request.client_id
        }
        
    except Exception as e:
        logger.error(f"Error requesting intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/decision")
async def submit_expert_decision(
    decision: ExpertDecisionSubmission,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Submit expert decision for intervention"""
    try:
        decision_id = await expert_system.submit_expert_decision(
            request_id=decision.request_id,
            expert_id=decision.expert_id,
            decision=decision.decision,
            reasoning=decision.reasoning,
            confidence=decision.confidence,
            alternatives_considered=decision.alternatives_considered,
            risk_assessment=decision.risk_assessment,
            follow_up_actions=decision.follow_up_actions,
            learning_points=decision.learning_points
        )
        
        return {
            "success": True,
            "message": "Expert decision submitted successfully",
            "decision_id": decision_id,
            "request_id": decision.request_id
        }
        
    except Exception as e:
        logger.error(f"Error submitting expert decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/escalate")
async def escalate_intervention(
    escalation: EscalationRequest,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Escalate intervention to higher level expert"""
    try:
        escalate_to_level = None
        if escalation.escalate_to_level:
            escalate_to_level = ExpertLevel(escalation.escalate_to_level)
        
        success = await expert_system.escalate_intervention(
            request_id=escalation.request_id,
            reason=escalation.reason,
            escalate_to_level=escalate_to_level
        )
        
        if success:
            return {
                "success": True,
                "message": "Intervention escalated successfully",
                "request_id": escalation.request_id
            }
        else:
            raise HTTPException(status_code=404, detail="Intervention request not found")
        
    except Exception as e:
        logger.error(f"Error escalating intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{request_id}")
async def get_intervention_status(
    request_id: str,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Get status of intervention request"""
    try:
        status = await expert_system.get_intervention_status(request_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Intervention request not found")
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error getting intervention status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expert/{expert_id}/workload")
async def get_expert_workload(
    expert_id: str,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Get expert workload information"""
    try:
        workload = await expert_system.get_expert_workload(expert_id)
        
        if "error" in workload:
            raise HTTPException(status_code=404, detail=workload["error"])
        
        return {
            "success": True,
            "workload": workload
        }
        
    except Exception as e:
        logger.error(f"Error getting expert workload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-interventions")
async def get_active_interventions(
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Get all active interventions"""
    try:
        active_interventions = []
        
        for request_id, intervention in expert_system.active_interventions.items():
            if intervention.status in [InterventionStatus.PENDING, InterventionStatus.IN_PROGRESS]:
                active_interventions.append({
                    "request_id": intervention.request_id,
                    "client_id": intervention.client_id,
                    "title": intervention.title,
                    "status": intervention.status.value,
                    "priority": intervention.priority,
                    "complexity": intervention.complexity.value,
                    "assigned_expert": intervention.assigned_expert,
                    "created_at": intervention.created_at.isoformat(),
                    "deadline": intervention.deadline.isoformat() if intervention.deadline else None
                })
        
        return {
            "success": True,
            "active_interventions": active_interventions,
            "total_count": len(active_interventions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active interventions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/intervention-types")
async def get_intervention_types():
    """Get available intervention types"""
    return {
        "success": True,
        "intervention_types": [
            {
                "value": intervention_type.value,
                "label": intervention_type.value.replace('_', ' ').title(),
                "description": f"Requires {intervention_type.value.replace('_', ' ')} intervention"
            }
            for intervention_type in InterventionType
        ]
    }

@router.get("/expert-levels")
async def get_expert_levels():
    """Get available expert levels"""
    return {
        "success": True,
        "expert_levels": [
            {
                "value": level.value,
                "label": level.value.title(),
                "description": f"{level.value.title()} level expert"
            }
            for level in ExpertLevel
        ]
    }

@router.get("/complexity-levels")
async def get_complexity_levels():
    """Get available complexity levels"""
    return {
        "success": True,
        "complexity_levels": [
            {
                "value": complexity.value,
                "label": complexity.value.title(),
                "description": f"{complexity.value.title()} complexity decision"
            }
            for complexity in DecisionComplexity
        ]
    }

@router.post("/demo-intervention/{client_id}")
async def generate_demo_intervention(
    client_id: str,
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Generate demo intervention request for testing"""
    try:
        request_id = await expert_system.request_intervention(
            client_id=client_id,
            intervention_type=InterventionType.APPROVAL_REQUIRED,
            title="Demo: Budget Reallocation Decision",
            description="AI recommends reallocating 30% of budget from Facebook to TikTok based on performance data. This requires human approval due to high budget impact.",
            context={
                "current_budget": 50000,
                "recommended_reallocation": 15000,
                "platforms": ["facebook", "tiktok"],
                "performance_data": {
                    "facebook_cpa": 45.2,
                    "tiktok_cpa": 32.1,
                    "facebook_roas": 2.1,
                    "tiktok_roas": 3.2
                }
            },
            ai_recommendation="Reallocate $15,000 from Facebook to TikTok to improve ROAS by 52%",
            ai_confidence=0.85,
            priority=7,
            complexity=DecisionComplexity.HIGH,
            deadline_minutes=120
        )
        
        return {
            "success": True,
            "message": "Demo intervention request created",
            "request_id": request_id,
            "client_id": client_id
        }
        
    except Exception as e:
        logger.error(f"Error generating demo intervention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status")
async def get_system_status(
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Get human expert intervention system status"""
    try:
        return {
            "success": True,
            "status": {
                "total_experts": len(expert_system.expert_profiles),
                "active_interventions": len(expert_system.active_interventions),
                "available_workflows": len(expert_system.intervention_workflows),
                "expert_decisions": len(expert_system.expert_decisions),
                "default_sla_minutes": expert_system.default_sla_minutes,
                "escalation_timeout_minutes": expert_system.escalation_timeout_minutes,
                "load_balancing_enabled": expert_system.expert_load_balancing
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    expert_system: HumanExpertInterventionSystem = Depends(get_expert_system)
):
    """Health check for human expert intervention system"""
    try:
        return {
            "success": True,
            "status": "healthy",
            "message": "Human Expert Intervention System is operational",
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
