"""
Predictive Intelligence Dashboard API Routes
Shows customers future predictions, trends, and opportunities
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from backend.services.predictive_intelligence_dashboard import (
    get_predictive_dashboard,
    PredictiveIntelligenceDashboard,
    PredictionType,
    PredictionConfidence,
    TrendDirection
)
from backend.services.auth_service import get_current_user
from backend.models.user_models import User

router = APIRouter(prefix="/api/predictive", tags=["predictive"])

class PredictionRequest(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    prediction_types: Optional[List[str]] = Field(None, description="Types of predictions to generate")

class TrendAnalysisRequest(BaseModel):
    organization_id: str = Field(..., description="Organization ID")
    metrics: Optional[List[str]] = Field(None, description="Metrics to analyze")

@router.post("/predictions")
async def generate_predictions(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    dashboard: PredictiveIntelligenceDashboard = Depends(get_predictive_dashboard)
):
    """Generate predictions for a client"""
    try:
        # Convert prediction type strings to enums
        prediction_types = None
        if request.prediction_types:
            try:
                prediction_types = [PredictionType(pt) for pt in request.prediction_types]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid prediction type: {str(e)}")
        
        result = await dashboard.generate_predictions(
            client_id=current_user.id,
            organization_id=request.organization_id,
            prediction_types=prediction_types
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track prediction generation
        background_tasks.add_task(track_prediction_generation, current_user.id, len(result["predictions"]))
        
        return {
            "success": True,
            "message": f"Generated {len(result['predictions'])} predictions",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction generation failed: {str(e)}")

@router.post("/trends")
async def analyze_trends(
    request: TrendAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    dashboard: PredictiveIntelligenceDashboard = Depends(get_predictive_dashboard)
):
    """Analyze trends for client metrics"""
    try:
        result = await dashboard.analyze_trends(
            client_id=current_user.id,
            organization_id=request.organization_id,
            metrics=request.metrics
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track trend analysis
        background_tasks.add_task(track_trend_analysis, current_user.id, len(result["trend_analyses"]))
        
        return {
            "success": True,
            "message": f"Analyzed {len(result['trend_analyses'])} trends",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

@router.post("/opportunities")
async def generate_opportunity_alerts(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    dashboard: PredictiveIntelligenceDashboard = Depends(get_predictive_dashboard)
):
    """Generate opportunity alerts for a client"""
    try:
        result = await dashboard.generate_opportunity_alerts(
            client_id=current_user.id,
            organization_id=request.organization_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Track opportunity generation
        background_tasks.add_task(track_opportunity_generation, current_user.id, len(result["alerts"]))
        
        return {
            "success": True,
            "message": f"Generated {len(result['alerts'])} opportunity alerts",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Opportunity alert generation failed: {str(e)}")

@router.get("/dashboard")
async def get_prediction_dashboard(
    current_user: User = Depends(get_current_user),
    dashboard: PredictiveIntelligenceDashboard = Depends(get_predictive_dashboard)
):
    """Get comprehensive prediction dashboard data"""
    try:
        result = await dashboard.get_prediction_dashboard(
            client_id=current_user.id,
            organization_id="org_123"  # In real implementation, get from user context
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

@router.get("/prediction-types")
async def get_prediction_types():
    """Get list of available prediction types"""
    try:
        prediction_types = []
        for pred_type in PredictionType:
            prediction_types.append({
                "value": pred_type.value,
                "label": pred_type.value.replace("_", " ").title(),
                "description": get_prediction_description(pred_type)
            })
        
        return {
            "success": True,
            "prediction_types": prediction_types
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction types retrieval failed: {str(e)}")

@router.get("/confidence-levels")
async def get_confidence_levels():
    """Get list of confidence levels"""
    try:
        confidence_levels = []
        for conf_level in PredictionConfidence:
            confidence_levels.append({
                "value": conf_level.value,
                "label": conf_level.value.replace("_", " ").title(),
                "description": get_confidence_description(conf_level)
            })
        
        return {
            "success": True,
            "confidence_levels": confidence_levels
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confidence levels retrieval failed: {str(e)}")

@router.get("/trend-directions")
async def get_trend_directions():
    """Get list of trend directions"""
    try:
        trend_directions = []
        for trend_dir in TrendDirection:
            trend_directions.append({
                "value": trend_dir.value,
                "label": trend_dir.value.title(),
                "description": get_trend_description(trend_dir)
            })
        
        return {
            "success": True,
            "trend_directions": trend_directions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend directions retrieval failed: {str(e)}")

@router.get("/demo-dashboard")
async def get_demo_prediction_dashboard():
    """Get demo prediction dashboard data"""
    try:
        demo_data = {
            "client_id": "demo_client_123",
            "dashboard_metrics": {
                "total_predictions": 8,
                "high_confidence_predictions": 5,
                "rising_trends": 6,
                "total_opportunities": 4,
                "high_value_opportunities": 2,
                "urgent_alerts": 1,
                "average_confidence": 0.82,
                "total_potential_value": 4500.0
            },
            "insights": [
                "You have 5 high-confidence predictions that require immediate attention",
                "6 metrics are predicted to rise, indicating positive momentum",
                "4 metrics show strong trends that should be monitored closely",
                "You have 2 high-value opportunities worth $3,200",
                "1 urgent opportunities require immediate action"
            ],
            "predictions": [
                {
                    "prediction_id": "pred_001",
                    "type": "creative_fatigue",
                    "title": "Creative Fatigue Prediction",
                    "current_value": 75.2,
                    "predicted_value": 68.5,
                    "confidence_score": 0.87,
                    "confidence_level": "high",
                    "trend_direction": "falling",
                    "time_horizon": 14,
                    "impact_score": 0.8,
                    "risk_level": "medium",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "prediction_id": "pred_002",
                    "type": "ltv_forecast",
                    "title": "Customer Lifetime Value Forecast",
                    "current_value": 125.50,
                    "predicted_value": 142.30,
                    "confidence_score": 0.91,
                    "confidence_level": "high",
                    "trend_direction": "rising",
                    "time_horizon": 90,
                    "impact_score": 0.9,
                    "risk_level": "low",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "prediction_id": "pred_003",
                    "type": "churn_risk",
                    "title": "Customer Churn Risk Prediction",
                    "current_value": 12.5,
                    "predicted_value": 8.2,
                    "confidence_score": 0.78,
                    "confidence_level": "medium",
                    "trend_direction": "falling",
                    "time_horizon": 30,
                    "impact_score": 0.95,
                    "risk_level": "high",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "prediction_id": "pred_004",
                    "type": "revenue_forecast",
                    "title": "Revenue Forecast",
                    "current_value": 45000.0,
                    "predicted_value": 52000.0,
                    "confidence_score": 0.85,
                    "confidence_level": "high",
                    "trend_direction": "rising",
                    "time_horizon": 90,
                    "impact_score": 0.95,
                    "risk_level": "low",
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "trend_analyses": [
                {
                    "trend_id": "trend_001",
                    "metric_name": "roas",
                    "current_trend": "rising",
                    "trend_strength": 0.78,
                    "key_insights": [
                        "Return on Ad Spend shows rising trend over the last 7 days",
                        "Trend strength: 78%",
                        "Predicted ROAS will increase by 12.5% in the next 14 days"
                    ],
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "trend_id": "trend_002",
                    "metric_name": "ctr",
                    "current_trend": "stable",
                    "trend_strength": 0.45,
                    "key_insights": [
                        "Click-Through Rate shows stable trend over the last 7 days",
                        "Trend strength: 45%",
                        "Predicted CTR will remain stable in the next 14 days"
                    ],
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "trend_id": "trend_003",
                    "metric_name": "conversion_rate",
                    "current_trend": "rising",
                    "trend_strength": 0.82,
                    "key_insights": [
                        "Conversion Rate shows rising trend over the last 7 days",
                        "Trend strength: 82%",
                        "Predicted Conversion Rate will increase by 8.3% in the next 14 days"
                    ],
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "opportunity_alerts": [
                {
                    "alert_id": "alert_001",
                    "opportunity_type": "budget_reallocation",
                    "title": "Budget Reallocation Opportunity",
                    "potential_value": 1500.0,
                    "confidence_score": 0.82,
                    "urgency_level": "medium",
                    "time_sensitivity": 48,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "alert_id": "alert_002",
                    "opportunity_type": "competitor_gap",
                    "title": "Competitor Gap Opportunity",
                    "potential_value": 2500.0,
                    "confidence_score": 0.89,
                    "urgency_level": "high",
                    "time_sensitivity": 24,
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "alert_id": "alert_003",
                    "opportunity_type": "audience_expansion",
                    "title": "Audience Expansion Opportunity",
                    "potential_value": 800.0,
                    "confidence_score": 0.71,
                    "urgency_level": "low",
                    "time_sensitivity": 72,
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        }
        
        return {
            "success": True,
            "data": demo_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo dashboard retrieval failed: {str(e)}")

@router.get("/health")
async def predictive_health(
    dashboard: PredictiveIntelligenceDashboard = Depends(get_predictive_dashboard)
):
    """Health check for predictive intelligence dashboard"""
    try:
        return {
            "status": "healthy",
            "dashboard_initialized": dashboard is not None,
            "prediction_types": len(PredictionType),
            "confidence_levels": len(PredictionConfidence),
            "trend_directions": len(TrendDirection),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Helper functions
def get_prediction_description(prediction_type: PredictionType) -> str:
    """Get description for prediction type"""
    descriptions = {
        PredictionType.CREATIVE_FATIGUE: "Predicts when creative assets will lose effectiveness",
        PredictionType.LTV_FORECAST: "Forecasts customer lifetime value",
        PredictionType.CHURN_RISK: "Identifies customers at risk of churning",
        PredictionType.BUDGET_OPTIMIZATION: "Predicts optimal budget allocation",
        PredictionType.CAMPAIGN_PERFORMANCE: "Forecasts campaign performance metrics",
        PredictionType.MARKET_TRENDS: "Predicts upcoming market trends",
        PredictionType.COMPETITOR_ACTIVITY: "Predicts competitor marketing activities",
        PredictionType.CUSTOMER_JOURNEY: "Predicts optimal customer journey paths",
        PredictionType.REVENUE_FORECAST: "Forecasts future revenue",
        PredictionType.SEASONAL_PATTERNS: "Predicts seasonal trends and patterns"
    }
    return descriptions.get(prediction_type, "Marketing prediction")

def get_confidence_description(confidence_level: PredictionConfidence) -> str:
    """Get description for confidence level"""
    descriptions = {
        PredictionConfidence.HIGH: "80-100% confidence - Very reliable prediction",
        PredictionConfidence.MEDIUM: "60-79% confidence - Moderately reliable prediction",
        PredictionConfidence.LOW: "40-59% confidence - Low reliability prediction",
        PredictionConfidence.VERY_LOW: "Less than 40% confidence - Very low reliability"
    }
    return descriptions.get(confidence_level, "Prediction confidence level")

def get_trend_description(trend_direction: TrendDirection) -> str:
    """Get description for trend direction"""
    descriptions = {
        TrendDirection.RISING: "Values are increasing over time",
        TrendDirection.FALLING: "Values are decreasing over time",
        TrendDirection.STABLE: "Values remain relatively constant",
        TrendDirection.VOLATILE: "Values show high variability"
    }
    return descriptions.get(trend_direction, "Trend direction")

# Background task functions
async def track_prediction_generation(user_id: str, prediction_count: int):
    """Track prediction generation"""
    # Implementation would log to analytics service
    pass

async def track_trend_analysis(user_id: str, trend_count: int):
    """Track trend analysis"""
    # Implementation would log to analytics service
    pass

async def track_opportunity_generation(user_id: str, opportunity_count: int):
    """Track opportunity generation"""
    # Implementation would log to analytics service
    pass
