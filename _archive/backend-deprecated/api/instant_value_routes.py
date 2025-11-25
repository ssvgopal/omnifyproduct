"""
Instant Value Delivery System API Routes
Delivers immediate ROI and performance improvements
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.services.instant_value_delivery_system import (
    get_instant_value_system,
    InstantValueDeliverySystem,
    PlatformType,
    OptimizationType
)
from backend.services.auth_service import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/api/instant-value", tags=["instant-value"])

class InstantValueStartRequest(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    target_platforms: Optional[List[str]] = Field(None, description="Platforms to optimize")

class PlatformOptimizationRequest(BaseModel):
    platform: str = Field(..., description="Platform to optimize")
    campaign_ids: Optional[List[str]] = Field(None, description="Specific campaigns to optimize")

@router.post("/start")
async def start_instant_value_session(
    request: InstantValueStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Start an instant value delivery session"""
    try:
        # Convert platform strings to enums
        target_platforms = None
        if request.target_platforms:
            try:
                target_platforms = [PlatformType(p) for p in request.target_platforms]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid platform: {str(e)}")
        
        result = await system.start_instant_value_session(
            client_id=current_user.id,
            organization_id=request.organization_id,
            target_platforms=target_platforms
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track session start
        background_tasks.add_task(track_instant_value_start, current_user.id, request.organization_id)
        
        return {
            "success": True,
            "message": "Instant value session started successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session start failed: {str(e)}")

@router.post("/optimize/{session_id}")
async def execute_platform_optimization(
    session_id: str,
    request: PlatformOptimizationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Execute optimization for a specific platform"""
    try:
        # Convert platform string to enum
        try:
            platform = PlatformType(request.platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {request.platform}")
        
        result = await system.execute_platform_optimization(
            session_id=session_id,
            platform=platform,
            campaign_ids=request.campaign_ids
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track optimization execution
        background_tasks.add_task(
            track_optimization_execution, 
            session_id, 
            request.platform, 
            result["optimizations_completed"]
        )
        
        return {
            "success": True,
            "message": f"Optimization completed for {request.platform}",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization execution failed: {str(e)}")

@router.get("/progress/{session_id}")
async def get_session_progress(
    session_id: str,
    current_user: User = Depends(get_current_user),
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Get real-time progress of instant value session"""
    try:
        result = await system.get_session_progress(session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Progress retrieval failed: {str(e)}")

@router.post("/complete/{session_id}")
async def complete_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Complete the instant value session and generate final report"""
    try:
        result = await system.complete_session(session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track session completion
        background_tasks.add_task(track_session_completion, session_id, current_user.id)
        
        return {
            "success": True,
            "message": "Instant value session completed successfully",
            "data": result["final_report"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session completion failed: {str(e)}")

@router.get("/platforms")
async def get_supported_platforms():
    """Get list of supported platforms for instant optimization"""
    try:
        platforms = []
        for platform in PlatformType:
            platforms.append({
                "value": platform.value,
                "label": platform.value.replace("_", " ").title(),
                "description": get_platform_description(platform)
            })
        
        return {
            "success": True,
            "platforms": platforms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Platforms retrieval failed: {str(e)}")

@router.get("/optimization-types")
async def get_optimization_types():
    """Get list of available optimization types"""
    try:
        optimization_types = []
        for opt_type in OptimizationType:
            optimization_types.append({
                "value": opt_type.value,
                "label": opt_type.value.replace("_", " ").title(),
                "description": get_optimization_description(opt_type)
            })
        
        return {
            "success": True,
            "optimization_types": optimization_types
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization types retrieval failed: {str(e)}")

@router.get("/value-targets")
async def get_value_targets(
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Get value targets for different optimization types"""
    try:
        targets = {}
        for opt_type, target_metrics in system.value_targets.items():
            targets[opt_type.value] = {
                "label": opt_type.value.replace("_", " ").title(),
                "targets": target_metrics
            }
        
        return {
            "success": True,
            "value_targets": targets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Value targets retrieval failed: {str(e)}")

@router.get("/platform-strategies")
async def get_platform_strategies(
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Get optimization strategies for each platform"""
    try:
        strategies = {}
        for platform, strategy in system.platform_strategies.items():
            strategies[platform.value] = {
                "label": platform.value.replace("_", " ").title(),
                "primary_optimizations": [opt.value for opt in strategy["primary_optimizations"]],
                "quick_wins": strategy["quick_wins"],
                "expected_improvements": strategy["expected_improvements"],
                "optimization_time": strategy["optimization_time"]
            }
        
        return {
            "success": True,
            "platform_strategies": strategies
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Platform strategies retrieval failed: {str(e)}")

@router.get("/demo-results")
async def get_demo_results():
    """Get demo optimization results for demonstration purposes"""
    try:
        demo_results = {
            "google_ads": {
                "optimizations_completed": 4,
                "total_value_added": 185.50,
                "improvements": {
                    "roas": 18.5,
                    "cpc": -22.3,
                    "ctr": 14.2,
                    "conversion_rate": 12.8
                },
                "results": [
                    {
                        "type": "bid_optimization",
                        "campaign_id": "campaign_google_ads_1",
                        "improvement_percentage": {"roas": 15.2, "cpc": -18.5},
                        "estimated_value_added": 45.30,
                        "confidence_score": 0.87
                    },
                    {
                        "type": "keyword_optimization",
                        "campaign_id": "campaign_google_ads_2",
                        "improvement_percentage": {"ctr": 12.8, "cpc": -15.2},
                        "estimated_value_added": 38.90,
                        "confidence_score": 0.82
                    }
                ]
            },
            "meta_ads": {
                "optimizations_completed": 3,
                "total_value_added": 142.75,
                "improvements": {
                    "ctr": 28.5,
                    "engagement_rate": 42.1,
                    "cpc": -19.8,
                    "reach": 35.2
                },
                "results": [
                    {
                        "type": "creative_rotation",
                        "campaign_id": "campaign_meta_ads_1",
                        "improvement_percentage": {"ctr": 25.5, "engagement_rate": 38.2},
                        "estimated_value_added": 52.40,
                        "confidence_score": 0.78
                    }
                ]
            },
            "linkedin_ads": {
                "optimizations_completed": 2,
                "total_value_added": 98.25,
                "improvements": {
                    "ctr": 16.8,
                    "conversion_rate": 22.5,
                    "cpc": -14.2
                },
                "results": [
                    {
                        "type": "audience_expansion",
                        "campaign_id": "campaign_linkedin_ads_1",
                        "improvement_percentage": {"ctr": 18.2, "conversion_rate": 20.8},
                        "estimated_value_added": 48.75,
                        "confidence_score": 0.85
                    }
                ]
            }
        }
        
        return {
            "success": True,
            "demo_results": demo_results,
            "total_value_added": sum(platform["total_value_added"] for platform in demo_results.values()),
            "total_optimizations": sum(platform["optimizations_completed"] for platform in demo_results.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo results retrieval failed: {str(e)}")

@router.get("/health")
async def instant_value_health(
    system: InstantValueDeliverySystem = Depends(get_instant_value_system)
):
    """Health check for instant value delivery system"""
    try:
        return {
            "status": "healthy",
            "system_initialized": system is not None,
            "active_sessions": len(system.active_sessions),
            "supported_platforms": len(PlatformType),
            "optimization_types": len(OptimizationType),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Helper functions
def get_platform_description(platform: PlatformType) -> str:
    """Get description for platform"""
    descriptions = {
        PlatformType.GOOGLE_ADS: "Search and display advertising platform",
        PlatformType.META_ADS: "Social media advertising (Facebook/Instagram)",
        PlatformType.LINKEDIN_ADS: "Professional network advertising",
        PlatformType.TIKTOK_ADS: "Short-form video advertising platform",
        PlatformType.SHOPIFY: "E-commerce platform integration",
        PlatformType.GOHIGHLEVEL: "CRM and marketing automation platform"
    }
    return descriptions.get(platform, "Marketing platform")

def get_optimization_description(opt_type: OptimizationType) -> str:
    """Get description for optimization type"""
    descriptions = {
        OptimizationType.BID_OPTIMIZATION: "Optimize bid strategies for better performance",
        OptimizationType.AUDIENCE_EXPANSION: "Expand and refine target audiences",
        OptimizationType.CREATIVE_ROTATION: "Optimize creative assets and rotation",
        OptimizationType.BUDGET_REALLOCATION: "Reallocate budget for maximum efficiency",
        OptimizationType.KEYWORD_OPTIMIZATION: "Optimize keyword targeting and bids",
        OptimizationType.SCHEDULE_OPTIMIZATION: "Optimize ad scheduling and timing",
        OptimizationType.GEOGRAPHIC_OPTIMIZATION: "Optimize geographic targeting",
        OptimizationType.DEVICE_OPTIMIZATION: "Optimize device-specific targeting"
    }
    return descriptions.get(opt_type, "Campaign optimization")

# Background task functions
async def track_instant_value_start(user_id: str, organization_id: str):
    """Track instant value session start"""
    # Implementation would log to analytics service
    pass

async def track_optimization_execution(session_id: str, platform: str, optimizations_count: int):
    """Track optimization execution"""
    # Implementation would log to analytics service
    pass

async def track_session_completion(session_id: str, user_id: str):
    """Track session completion"""
    # Implementation would log to analytics service
    pass
