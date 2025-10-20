"""
Magical Customer Onboarding Wizard API Routes
Modern, role-based, gamified onboarding experience
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.services.magical_onboarding_wizard import (
    get_onboarding_wizard,
    MagicalOnboardingWizard,
    OnboardingStep,
    UserRole
)
from backend.services.auth_service import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

class OnboardingStepData(BaseModel):
    step: OnboardingStep
    data: Dict[str, Any]

class OnboardingStartRequest(BaseModel):
    organization_id: str = Field(..., description="Organization ID for onboarding")

class OnboardingCompleteRequest(BaseModel):
    step: OnboardingStep
    data: Dict[str, Any] = Field(default_factory=dict)

class OnboardingSkipRequest(BaseModel):
    step: OnboardingStep
    reason: Optional[str] = None

@router.post("/start")
async def start_onboarding(
    request: OnboardingStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Start the magical onboarding experience"""
    try:
        result = await wizard.start_onboarding(
            user_id=current_user.id,
            organization_id=request.organization_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track onboarding start
        background_tasks.add_task(track_onboarding_start, current_user.id, request.organization_id)
        
        return {
            "success": True,
            "message": "Onboarding started successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding start failed: {str(e)}")

@router.post("/step/complete")
async def complete_onboarding_step(
    request: OnboardingCompleteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Complete an onboarding step"""
    try:
        result = await wizard.complete_step(
            user_id=current_user.id,
            step=request.step,
            step_data=request.data
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track step completion
        background_tasks.add_task(
            track_step_completion, 
            current_user.id, 
            request.step.value, 
            request.data
        )
        
        return {
            "success": True,
            "message": f"Step {request.step.value} completed successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step completion failed: {str(e)}")

@router.post("/step/skip")
async def skip_onboarding_step(
    request: OnboardingSkipRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Skip an onboarding step"""
    try:
        result = await wizard.skip_step(
            user_id=current_user.id,
            step=request.step
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track step skip
        background_tasks.add_task(
            track_step_skip, 
            current_user.id, 
            request.step.value, 
            request.reason
        )
        
        return {
            "success": True,
            "message": f"Step {request.step.value} skipped",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step skip failed: {str(e)}")

@router.get("/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Get current onboarding status"""
    try:
        result = await wizard.get_onboarding_status(current_user.id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "data": result["status"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.post("/complete")
async def complete_onboarding(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Complete the onboarding process"""
    try:
        result = await wizard.complete_onboarding(current_user.id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track onboarding completion
        background_tasks.add_task(track_onboarding_completion, current_user.id)
        
        return {
            "success": True,
            "message": "Onboarding completed successfully! Welcome to OmniFy!",
            "data": result["completion"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding completion failed: {str(e)}")

@router.get("/step/{step_name}")
async def get_step_configuration(
    step_name: str,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Get configuration for a specific onboarding step"""
    try:
        # Validate step name
        try:
            step = OnboardingStep(step_name)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
        
        # Get step configuration
        step_config = wizard.step_configs[step]
        
        return {
            "success": True,
            "step": step_name,
            "config": step_config
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step configuration retrieval failed: {str(e)}")

@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Get all available achievements"""
    try:
        return {
            "success": True,
            "achievements": wizard.achievements
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Achievements retrieval failed: {str(e)}")

@router.get("/roles")
async def get_user_roles():
    """Get all available user roles"""
    try:
        roles = []
        for role in UserRole:
            roles.append({
                "value": role.value,
                "label": role.value.replace("_", " ").title()
            })
        
        return {
            "success": True,
            "roles": roles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roles retrieval failed: {str(e)}")

@router.get("/demo-data/{step_name}")
async def get_demo_data(
    step_name: str,
    current_user: User = Depends(get_current_user),
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Get demo data for onboarding steps"""
    try:
        # Validate step name
        try:
            step = OnboardingStep(step_name)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid step name: {step_name}")
        
        demo_data = {}
        
        if step == OnboardingStep.COMPANY_INFO:
            demo_data = {
                "company_name": "Acme Marketing Co.",
                "industry": "Technology",
                "company_size": "51-200 employees",
                "monthly_marketing_budget": "$10,000 - $25,000"
            }
        
        elif step == OnboardingStep.PLATFORM_CONNECTION:
            demo_data = {
                "connected_platforms": ["google_ads", "meta_ads"],
                "connection_status": {
                    "google_ads": {"connected": True, "account_name": "Acme Marketing"},
                    "meta_ads": {"connected": True, "account_name": "Acme Marketing"}
                }
            }
        
        elif step == OnboardingStep.BRAND_SETUP:
            demo_data = {
                "brand_assets": {
                    "logo": "https://example.com/logo.png",
                    "brand_colors": ["#3B82F6", "#10B981", "#F59E0B"],
                    "brand_fonts": ["Inter", "Roboto"],
                    "brand_voice": "Professional, innovative, trustworthy"
                }
            }
        
        elif step == OnboardingStep.FIRST_CAMPAIGN:
            demo_data = {
                "campaign_type": "awareness",
                "campaign_data": {
                    "name": "Brand Awareness Campaign",
                    "objective": "Brand Awareness",
                    "target_audience": "Tech-savvy millennials",
                    "budget": "$5,000",
                    "platforms": ["Meta Ads", "Google Ads"],
                    "duration": "30 days"
                }
            }
        
        return {
            "success": True,
            "step": step_name,
            "demo_data": demo_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo data retrieval failed: {str(e)}")

@router.get("/health")
async def onboarding_health(
    wizard: MagicalOnboardingWizard = Depends(get_onboarding_wizard)
):
    """Health check for onboarding wizard"""
    try:
        return {
            "status": "healthy",
            "wizard_initialized": wizard is not None,
            "active_sessions": len(wizard.active_sessions),
            "total_steps": len(OnboardingStep),
            "total_achievements": len(wizard.achievements),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Background task functions
async def track_onboarding_start(user_id: str, organization_id: str):
    """Track onboarding start event"""
    # Implementation would log to analytics service
    pass

async def track_step_completion(user_id: str, step_name: str, step_data: Dict[str, Any]):
    """Track step completion event"""
    # Implementation would log to analytics service
    pass

async def track_step_skip(user_id: str, step_name: str, reason: Optional[str]):
    """Track step skip event"""
    # Implementation would log to analytics service
    pass

async def track_onboarding_completion(user_id: str):
    """Track onboarding completion event"""
    # Implementation would log to analytics service
    pass
