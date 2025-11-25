"""
API Routes for Critical Decision Hand-Holding System
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from services.critical_decision_hand_holding_system import (
    get_critical_decision_system,
    CriticalDecisionHandHoldingSystem,
    DecisionType,
    DecisionImpact,
    GuidanceLevel,
    DecisionStage
)
from database.mongodb_schema import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/critical-decision", tags=["Critical Decision"])

# Pydantic models
class DecisionGuidanceRequest(BaseModel):
    """Request to start decision guidance"""
    client_id: str = Field(..., description="Client identifier")
    decision_type: str = Field(..., description="Type of decision")
    title: str = Field(..., description="Title of the decision")
    description: str = Field(..., description="Description of the decision")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Context data")
    impact_level: str = Field("medium", description="Impact level of decision")
    guidance_level: Optional[str] = Field(None, description="Level of guidance needed")
    stakeholders: Optional[List[str]] = Field(None, description="List of stakeholders")
    timeline: Optional[str] = Field(None, description="Timeline for decision")
    budget_impact: Optional[float] = Field(None, description="Budget impact amount")

class StepCompletionRequest(BaseModel):
    """Request to complete a guidance step"""
    decision_id: str = Field(..., description="Decision identifier")
    step_id: str = Field(..., description="Step identifier")
    completion_notes: Optional[str] = Field(None, description="Notes about completion")

class DecisionUpdateRequest(BaseModel):
    """Request to update decision context"""
    decision_id: str = Field(..., description="Decision identifier")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Updated context data")
    stakeholders: Optional[List[str]] = Field(None, description="Updated stakeholders")
    timeline: Optional[str] = Field(None, description="Updated timeline")
    budget_impact: Optional[float] = Field(None, description="Updated budget impact")

# Dependency to get critical decision system
async def get_decision_system() -> CriticalDecisionHandHoldingSystem:
    """Get critical decision hand-holding system instance"""
    db = await get_database()
    return await get_critical_decision_system(db)

@router.post("/start-guidance")
async def start_decision_guidance(
    request: DecisionGuidanceRequest,
    background_tasks: BackgroundTasks,
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Start critical decision guidance process"""
    try:
        # Convert string enums to enum objects
        decision_type = DecisionType(request.decision_type)
        impact_level = DecisionImpact(request.impact_level)
        guidance_level = None
        if request.guidance_level:
            guidance_level = GuidanceLevel(request.guidance_level)
        
        # Parse timeline if provided
        timeline = None
        if request.timeline:
            try:
                timeline = datetime.fromisoformat(request.timeline)
            except ValueError:
                timeline = None
        
        decision_id = await decision_system.start_decision_guidance(
            client_id=request.client_id,
            decision_type=decision_type,
            title=request.title,
            description=request.description,
            context_data=request.context_data,
            impact_level=impact_level,
            guidance_level=guidance_level,
            stakeholders=request.stakeholders,
            timeline=timeline,
            budget_impact=request.budget_impact
        )
        
        return {
            "success": True,
            "message": "Decision guidance started successfully",
            "decision_id": decision_id,
            "client_id": request.client_id
        }
        
    except Exception as e:
        logger.error(f"Error starting decision guidance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guidance/{decision_id}")
async def get_decision_guidance(
    decision_id: str,
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Get comprehensive guidance for decision"""
    try:
        guidance = await decision_system.get_decision_guidance(decision_id)
        
        if not guidance:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        return {
            "success": True,
            "guidance": guidance
        }
        
    except Exception as e:
        logger.error(f"Error getting decision guidance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete-step")
async def complete_guidance_step(
    request: StepCompletionRequest,
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Complete a guidance step"""
    try:
        success = await decision_system.complete_guidance_step(
            request.decision_id,
            request.step_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Step not found")
        
        return {
            "success": True,
            "message": "Step completed successfully",
            "decision_id": request.decision_id,
            "step_id": request.step_id
        }
        
    except Exception as e:
        logger.error(f"Error completing guidance step: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-decisions/{client_id}")
async def get_active_decisions(
    client_id: str,
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Get active decisions for client"""
    try:
        active_decisions = []
        
        for decision_id, decision in decision_system.active_decisions.items():
            if decision.client_id == client_id:
                steps = decision_system.guidance_steps.get(decision_id, [])
                progress = decision_system._calculate_progress(steps)
                
                active_decisions.append({
                    "decision_id": decision.decision_id,
                    "title": decision.title,
                    "decision_type": decision.decision_type.value,
                    "impact_level": decision.impact_level.value,
                    "guidance_level": decision.guidance_level.value,
                    "current_stage": decision.current_stage.value,
                    "progress": progress,
                    "created_at": decision.created_at.isoformat(),
                    "updated_at": decision.updated_at.isoformat(),
                    "timeline": decision.timeline.isoformat() if decision.timeline else None,
                    "budget_impact": decision.budget_impact,
                    "risk_level": decision.risk_level
                })
        
        return {
            "success": True,
            "active_decisions": active_decisions,
            "total_count": len(active_decisions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active decisions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decision-types")
async def get_decision_types():
    """Get available decision types"""
    return {
        "success": True,
        "decision_types": [
            {
                "value": decision_type.value,
                "label": decision_type.value.replace('_', ' ').title(),
                "description": f"Guidance for {decision_type.value.replace('_', ' ')} decisions"
            }
            for decision_type in DecisionType
        ]
    }

@router.get("/impact-levels")
async def get_impact_levels():
    """Get available impact levels"""
    return {
        "success": True,
        "impact_levels": [
            {
                "value": impact_level.value,
                "label": impact_level.value.title(),
                "description": f"{impact_level.value.title()} impact decision"
            }
            for impact_level in DecisionImpact
        ]
    }

@router.get("/guidance-levels")
async def get_guidance_levels():
    """Get available guidance levels"""
    return {
        "success": True,
        "guidance_levels": [
            {
                "value": guidance_level.value,
                "label": guidance_level.value.replace('_', ' ').title(),
                "description": f"{guidance_level.value.replace('_', ' ')} level guidance"
            }
            for guidance_level in GuidanceLevel
        ]
    }

@router.get("/decision-stages")
async def get_decision_stages():
    """Get available decision stages"""
    return {
        "success": True,
        "decision_stages": [
            {
                "value": stage.value,
                "label": stage.value.title(),
                "description": f"{stage.value.title()} stage of decision making"
            }
            for stage in DecisionStage
        ]
    }

@router.post("/demo-decision/{client_id}")
async def generate_demo_decision(
    client_id: str,
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Generate demo decision guidance for testing"""
    try:
        decision_id = await decision_system.start_decision_guidance(
            client_id=client_id,
            decision_type=DecisionType.BUDGET_ALLOCATION,
            title="Demo: Q4 Budget Reallocation Strategy",
            description="Deciding how to reallocate marketing budget across channels for Q4 to maximize ROI and prepare for holiday season. Current performance shows TikTok outperforming Facebook by 40% in ROAS, but Facebook has higher volume.",
            context_data={
                "current_budget": 100000,
                "q4_target": 150000,
                "channels": ["facebook", "google", "tiktok", "linkedin"],
                "performance_data": {
                    "facebook": {"cpa": 45, "roas": 2.1, "spend": 40000, "volume": "high"},
                    "google": {"cpa": 38, "roas": 2.8, "spend": 35000, "volume": "medium"},
                    "tiktok": {"cpa": 32, "roas": 3.2, "spend": 15000, "volume": "low"},
                    "linkedin": {"cpa": 55, "roas": 1.8, "spend": 10000, "volume": "low"}
                },
                "seasonal_factors": {
                    "holiday_season": True,
                    "competitor_activity": "high",
                    "audience_behavior": "increased_purchasing"
                }
            },
            impact_level=DecisionImpact.HIGH,
            guidance_level=GuidanceLevel.INTERACTIVE,
            stakeholders=["CMO", "Marketing Director", "Finance Team"],
            timeline=datetime.utcnow() + timedelta(days=14),
            budget_impact=50000
        )
        
        return {
            "success": True,
            "message": "Demo decision guidance created",
            "decision_id": decision_id,
            "client_id": client_id
        }
        
    except Exception as e:
        logger.error(f"Error generating demo decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-status")
async def get_system_status(
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Get critical decision hand-holding system status"""
    try:
        return {
            "success": True,
            "status": {
                "active_decisions": len(decision_system.active_decisions),
                "decision_templates": len(decision_system.decision_templates),
                "guidance_templates": len(decision_system.guidance_templates),
                "total_guidance_steps": sum(len(steps) for steps in decision_system.guidance_steps.values()),
                "total_recommendations": sum(len(recs) for recs in decision_system.decision_recommendations.values()),
                "default_guidance_level": decision_system.default_guidance_level.value,
                "max_guidance_steps": decision_system.max_guidance_steps,
                "expert_threshold_impact": decision_system.expert_threshold_impact.value
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    decision_system: CriticalDecisionHandHoldingSystem = Depends(get_decision_system)
):
    """Health check for critical decision hand-holding system"""
    try:
        return {
            "success": True,
            "status": "healthy",
            "message": "Critical Decision Hand-Holding System is operational",
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
