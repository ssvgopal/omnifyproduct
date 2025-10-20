"""
Customer-Facing Orchestration Dashboard API Routes
Shows customers the magical orchestration of their marketing campaigns
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.services.customer_orchestration_dashboard import (
    get_orchestration_dashboard,
    CustomerFacingOrchestrationDashboard,
    OrchestrationEvent,
    AgentType
)
from backend.services.auth_service import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/api/orchestration", tags=["orchestration"])

class OrchestrationStartRequest(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    campaign_ids: Optional[List[str]] = Field(None, description="Campaign IDs to orchestrate")

@router.post("/start")
async def start_orchestration_session(
    request: OrchestrationStartRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    dashboard: CustomerFacingOrchestrationDashboard = Depends(get_orchestration_dashboard)
):
    """Start an orchestration session"""
    try:
        result = await dashboard.start_orchestration_session(
            client_id=current_user.id,
            organization_id=request.organization_id,
            campaign_ids=request.campaign_ids
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track orchestration start
        background_tasks.add_task(track_orchestration_start, current_user.id, request.organization_id)
        
        return {
            "success": True,
            "message": "Orchestration session started successfully",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration start failed: {str(e)}")

@router.get("/feed/{session_id}")
async def get_orchestration_feed(
    session_id: str,
    current_user: User = Depends(get_current_user),
    dashboard: CustomerFacingOrchestrationDashboard = Depends(get_orchestration_dashboard)
):
    """Get real-time orchestration feed"""
    try:
        result = await dashboard.get_orchestration_feed(session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration feed retrieval failed: {str(e)}")

@router.get("/agents/{session_id}")
async def get_agent_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
    dashboard: CustomerFacingOrchestrationDashboard = Depends(get_orchestration_dashboard)
):
    """Get status of all agents"""
    try:
        result = await dashboard.get_agent_status(session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")

@router.get("/agents")
async def get_available_agents():
    """Get list of available AI agents"""
    try:
        agents = []
        for agent_type in AgentType:
            agents.append({
                "type": agent_type.value,
                "name": agent_type.value.replace("_", " ").title(),
                "description": get_agent_description(agent_type)
            })
        
        return {
            "success": True,
            "agents": agents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agents retrieval failed: {str(e)}")

@router.get("/events")
async def get_event_types():
    """Get list of orchestration event types"""
    try:
        events = []
        for event_type in OrchestrationEvent:
            events.append({
                "type": event_type.value,
                "name": event_type.value.replace("_", " ").title(),
                "description": get_event_description(event_type)
            })
        
        return {
            "success": True,
            "events": events
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event types retrieval failed: {str(e)}")

@router.get("/demo-feed")
async def get_demo_orchestration_feed():
    """Get demo orchestration feed for demonstration purposes"""
    try:
        demo_feed = {
            "session_id": "demo_session_123",
            "events": [
                {
                    "event_id": "event_001",
                    "event_type": "campaign_launch",
                    "agent": {
                        "type": "campaign_manager",
                        "name": "Campaign Manager AI",
                        "avatar": "🎯",
                        "color": "blue"
                    },
                    "campaign_id": "campaign_google_ads_1",
                    "platform": "Google Ads",
                    "status": "completed",
                    "title": "Launching New Campaign",
                    "description": "Setting up and launching a new marketing campaign",
                    "customer_message": "🚀 Your new campaign is being launched! Our AI is setting up everything for optimal performance.",
                    "impact_score": 0.9,
                    "confidence_score": 0.87,
                    "estimated_duration": 15,
                    "actual_duration": 14,
                    "start_time": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
                    "end_time": (datetime.utcnow() - timedelta(minutes=6)).isoformat(),
                    "results": {
                        "success": True,
                        "metrics_improved": [
                            {"metric": "Campaign Setup", "improvement": "100% Complete"},
                            {"metric": "Targeting", "improvement": "Optimized"}
                        ],
                        "value_added": 0.0,
                        "recommendations": ["Monitor initial performance", "Adjust bids based on results"]
                    }
                },
                {
                    "event_id": "event_002",
                    "event_type": "budget_optimization",
                    "agent": {
                        "type": "budget_optimizer",
                        "name": "Budget Optimizer AI",
                        "avatar": "💰",
                        "color": "yellow"
                    },
                    "campaign_id": "campaign_meta_ads_1",
                    "platform": "Meta Ads",
                    "status": "in_progress",
                    "title": "Optimizing Budget Allocation",
                    "description": "Reallocating budget to high-performing campaigns",
                    "customer_message": "💰 Smart move! We're reallocating your budget to the highest-performing campaigns.",
                    "impact_score": 0.8,
                    "confidence_score": 0.92,
                    "estimated_duration": 8,
                    "actual_duration": None,
                    "start_time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "end_time": None,
                    "results": {}
                },
                {
                    "event_id": "event_003",
                    "event_type": "creative_rotation",
                    "agent": {
                        "type": "creative_specialist",
                        "name": "Creative Specialist AI",
                        "avatar": "🎨",
                        "color": "purple"
                    },
                    "campaign_id": "campaign_linkedin_ads_1",
                    "platform": "LinkedIn Ads",
                    "status": "planned",
                    "title": "Rotating Creative Assets",
                    "description": "Testing new creative variations for better performance",
                    "customer_message": "🎨 Fresh creative assets are being tested! We're finding what resonates best with your audience.",
                    "impact_score": 0.7,
                    "confidence_score": 0.85,
                    "estimated_duration": 12,
                    "actual_duration": None,
                    "start_time": datetime.utcnow().isoformat(),
                    "end_time": None,
                    "results": {}
                },
                {
                    "event_id": "event_004",
                    "event_type": "audience_refinement",
                    "agent": {
                        "type": "audience_expert",
                        "name": "Audience Expert AI",
                        "avatar": "👥",
                        "color": "pink"
                    },
                    "campaign_id": "campaign_google_ads_2",
                    "platform": "Google Ads",
                    "status": "completed",
                    "title": "Refining Target Audience",
                    "description": "Analyzing and optimizing audience targeting",
                    "customer_message": "👥 Audience targeting is being refined! We're finding your most valuable customers.",
                    "impact_score": 0.8,
                    "confidence_score": 0.89,
                    "estimated_duration": 10,
                    "actual_duration": 9,
                    "start_time": (datetime.utcnow() - timedelta(minutes=25)).isoformat(),
                    "end_time": (datetime.utcnow() - timedelta(minutes=16)).isoformat(),
                    "results": {
                        "success": True,
                        "metrics_improved": [
                            {"metric": "Conversion Rate", "improvement": "+18.5%"},
                            {"metric": "Audience Reach", "improvement": "+32.1%"}
                        ],
                        "value_added": 85.50,
                        "recommendations": ["Expand lookalike audiences", "Refine targeting parameters"]
                    }
                },
                {
                    "event_id": "event_005",
                    "event_type": "performance_monitoring",
                    "agent": {
                        "type": "performance_monitor",
                        "name": "Performance Monitor AI",
                        "avatar": "📈",
                        "color": "red"
                    },
                    "campaign_id": "campaign_meta_ads_2",
                    "platform": "Meta Ads",
                    "status": "in_progress",
                    "title": "Monitoring Performance",
                    "description": "Analyzing campaign performance metrics",
                    "customer_message": "📊 Performance monitoring active! Our AI is watching your campaigns 24/7.",
                    "impact_score": 0.5,
                    "confidence_score": 0.95,
                    "estimated_duration": 5,
                    "actual_duration": None,
                    "start_time": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                    "end_time": None,
                    "results": {}
                }
            ],
            "active_agents": [
                {
                    "type": "campaign_manager",
                    "name": "Campaign Manager AI",
                    "avatar": "🎯",
                    "color": "blue",
                    "specialty": "Campaign Strategy & Execution",
                    "description": "Oversees all campaign activities and ensures optimal performance",
                    "capabilities": ["Strategy Planning", "Performance Monitoring", "Budget Management"]
                },
                {
                    "type": "budget_optimizer",
                    "name": "Budget Optimizer AI",
                    "avatar": "💰",
                    "color": "yellow",
                    "specialty": "Budget Allocation",
                    "description": "Optimizes budget allocation across campaigns and platforms",
                    "capabilities": ["Budget Allocation", "Cost Optimization", "ROI Maximization"]
                },
                {
                    "type": "creative_specialist",
                    "name": "Creative Specialist AI",
                    "avatar": "🎨",
                    "color": "purple",
                    "specialty": "Creative Optimization",
                    "description": "Continuously optimizes creative assets for maximum engagement",
                    "capabilities": ["Creative Testing", "Asset Optimization", "Brand Consistency"]
                },
                {
                    "type": "audience_expert",
                    "name": "Audience Expert AI",
                    "avatar": "👥",
                    "color": "pink",
                    "specialty": "Audience Targeting",
                    "description": "Refines and expands audience targeting for better reach",
                    "capabilities": ["Audience Analysis", "Lookalike Creation", "Segmentation"]
                },
                {
                    "type": "performance_monitor",
                    "name": "Performance Monitor AI",
                    "avatar": "📈",
                    "color": "red",
                    "specialty": "Real-time Monitoring",
                    "description": "Monitors campaign performance 24/7 and alerts on anomalies",
                    "capabilities": ["Real-time Monitoring", "Anomaly Detection", "Alert Management"]
                }
            ],
            "session_stats": {
                "total_events": 5,
                "completed_events": 2,
                "active_events": 2,
                "session_duration": 1800  # 30 minutes
            }
        }
        
        return {
            "success": True,
            "data": demo_feed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo feed retrieval failed: {str(e)}")

@router.get("/health")
async def orchestration_health(
    dashboard: CustomerFacingOrchestrationDashboard = Depends(get_orchestration_dashboard)
):
    """Health check for orchestration dashboard"""
    try:
        return {
            "status": "healthy",
            "dashboard_initialized": dashboard is not None,
            "active_sessions": len(dashboard.active_sessions),
            "available_agents": len(AgentType),
            "event_types": len(OrchestrationEvent),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Helper functions
def get_agent_description(agent_type: AgentType) -> str:
    """Get description for agent type"""
    descriptions = {
        AgentType.CAMPAIGN_MANAGER: "Manages campaign strategy and execution",
        AgentType.CREATIVE_SPECIALIST: "Optimizes creative assets and content",
        AgentType.DATA_ANALYST: "Analyzes performance data and trends",
        AgentType.BUDGET_OPTIMIZER: "Optimizes budget allocation and ROI",
        AgentType.AUDIENCE_EXPERT: "Refines audience targeting and segmentation",
        AgentType.PERFORMANCE_MONITOR: "Monitors campaign performance in real-time",
        AgentType.COMPETITOR_TRACKER: "Tracks competitor activities and strategies",
        AgentType.MARKET_RESEARCHER: "Researches market trends and opportunities"
    }
    return descriptions.get(agent_type, "AI agent for marketing optimization")

def get_event_description(event_type: OrchestrationEvent) -> str:
    """Get description for event type"""
    descriptions = {
        OrchestrationEvent.CAMPAIGN_LAUNCH: "Launching new marketing campaigns",
        OrchestrationEvent.BUDGET_OPTIMIZATION: "Optimizing budget allocation",
        OrchestrationEvent.CREATIVE_ROTATION: "Rotating and testing creative assets",
        OrchestrationEvent.AUDIENCE_REFINEMENT: "Refining target audience targeting",
        OrchestrationEvent.BID_ADJUSTMENT: "Adjusting bid strategies",
        OrchestrationEvent.PERFORMANCE_MONITORING: "Monitoring campaign performance",
        OrchestrationEvent.ANOMALY_DETECTION: "Detecting performance anomalies",
        OrchestrationEvent.COMPETITOR_ANALYSIS: "Analyzing competitor activities",
        OrchestrationEvent.MARKET_TREND_ANALYSIS: "Analyzing market trends",
        OrchestrationEvent.CUSTOMER_JOURNEY_OPTIMIZATION: "Optimizing customer journey"
    }
    return descriptions.get(event_type, "Marketing optimization activity")

# Background task functions
async def track_orchestration_start(user_id: str, organization_id: str):
    """Track orchestration session start"""
    # Implementation would log to analytics service
    pass
