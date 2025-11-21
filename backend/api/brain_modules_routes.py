"""
Brain Modules API Routes
ORACLE, EYES, VOICE integration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from core.auth import get_current_user
from services.oracle_predictive_service import OraclePredictiveService
from services.eyes_creative_service import EyesCreativeService
from services.voice_automation_service import VoiceAutomationService
from services.curiosity_market_service import CuriosityMarketService
from services.memory_client_service import MemoryClientService
from services.reflexes_performance_service import ReflexesPerformanceService
from services.face_experience_service import FaceExperienceService

router = APIRouter(prefix="/api/brain", tags=["Brain Modules"])


class FatiguePredictionRequest(BaseModel):
    creative_id: str
    campaign_id: str
    performance_history: List[Dict[str, Any]]


class LTVForecastRequest(BaseModel):
    customer_id: str
    customer_data: Dict[str, Any]
    days: int = 90


class AIDAAnalysisRequest(BaseModel):
    creative_id: str
    creative_content: Dict[str, Any]


class CreativePredictionRequest(BaseModel):
    creative_id: str
    creative_content: Dict[str, Any]
    historical_data: Optional[List[Dict[str, Any]]] = None


class BudgetOptimizationRequest(BaseModel):
    campaign_id: str
    platform: str
    performance_data: Dict[str, Any]


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    from agentkit_server import db
    return db


def get_oracle_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> OraclePredictiveService:
    """Get ORACLE service instance"""
    return OraclePredictiveService(db)


def get_eyes_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> EyesCreativeService:
    """Get EYES service instance"""
    return EyesCreativeService(db)


def get_voice_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> VoiceAutomationService:
    """Get VOICE service instance"""
    return VoiceAutomationService(db)


def get_curiosity_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> CuriosityMarketService:
    """Get CURIOSITY service instance"""
    return CuriosityMarketService(db)


def get_memory_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> MemoryClientService:
    """Get MEMORY service instance"""
    return MemoryClientService(db)


def get_reflexes_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ReflexesPerformanceService:
    """Get REFLEXES service instance"""
    return ReflexesPerformanceService(db)


def get_face_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> FaceExperienceService:
    """Get FACE service instance"""
    return FaceExperienceService(db)


# ========== ORACLE (Predictive Intelligence) Routes ==========

@router.post("/oracle/predict-fatigue")
async def predict_creative_fatigue(
    request: FatiguePredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    oracle_service: OraclePredictiveService = Depends(get_oracle_service)
):
    """Predict creative fatigue"""
    try:
        prediction = await oracle_service.predict_creative_fatigue(
            request.creative_id,
            request.campaign_id,
            request.performance_history
        )
        
        return {
            "success": True,
            "data": {
                "creative_id": prediction.creative_id,
                "campaign_id": prediction.campaign_id,
                "days_until_fatigue": prediction.days_until_fatigue,
                "confidence": prediction.confidence,
                "current_performance": prediction.current_performance,
                "predicted_performance": prediction.predicted_performance,
                "recommendation": prediction.recommendation,
                "urgency": prediction.urgency
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oracle/forecast-ltv")
async def forecast_ltv(
    request: LTVForecastRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    oracle_service: OraclePredictiveService = Depends(get_oracle_service)
):
    """Forecast customer lifetime value"""
    try:
        forecast = await oracle_service.forecast_ltv(
            request.customer_id,
            request.customer_data,
            request.days
        )
        
        return {
            "success": True,
            "data": {
                "customer_id": forecast.customer_id,
                "forecasted_ltv": forecast.forecasted_ltv,
                "confidence_interval": forecast.confidence_interval,
                "days_forecast": forecast.days_forecast,
                "factors": forecast.factors,
                "risk_score": forecast.risk_score
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/oracle/detect-anomalies")
async def detect_anomalies(
    campaign_id: str,
    performance_data: List[Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user),
    oracle_service: OraclePredictiveService = Depends(get_oracle_service)
):
    """Detect performance anomalies"""
    try:
        anomalies = await oracle_service.detect_performance_anomalies(
            campaign_id,
            performance_data
        )
        
        return {
            "success": True,
            "data": {
                "campaign_id": campaign_id,
                "anomalies": anomalies,
                "count": len(anomalies)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== EYES (Creative Intelligence) Routes ==========

@router.post("/eyes/analyze-aida")
async def analyze_aida(
    request: AIDAAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    eyes_service: EyesCreativeService = Depends(get_eyes_service)
):
    """Perform AIDA analysis on creative"""
    try:
        analysis = await eyes_service.analyze_aida(
            request.creative_id,
            request.creative_content
        )
        
        return {
            "success": True,
            "data": {
                "creative_id": analysis.creative_id,
                "attention_score": analysis.attention_score,
                "interest_score": analysis.interest_score,
                "desire_score": analysis.desire_score,
                "action_score": analysis.action_score,
                "overall_score": analysis.overall_score,
                "strengths": analysis.strengths,
                "weaknesses": analysis.weaknesses,
                "recommendations": analysis.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/eyes/predict-performance")
async def predict_creative_performance(
    request: CreativePredictionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    eyes_service: EyesCreativeService = Depends(get_eyes_service)
):
    """Predict creative performance"""
    try:
        prediction = await eyes_service.predict_creative_performance(
            request.creative_id,
            request.creative_content,
            request.historical_data
        )
        
        return {
            "success": True,
            "data": {
                "creative_id": prediction.creative_id,
                "predicted_ctr": prediction.predicted_ctr,
                "predicted_conversion_rate": prediction.predicted_conversion_rate,
                "predicted_roas": prediction.predicted_roas,
                "confidence": prediction.confidence,
                "factors": prediction.factors,
                "recommendation": prediction.recommendation
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== VOICE (Marketing Automation) Routes ==========

@router.post("/voice/optimize-budget")
async def optimize_campaign_budget(
    request: BudgetOptimizationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    voice_service: VoiceAutomationService = Depends(get_voice_service)
):
    """Automatically optimize campaign budget"""
    try:
        result = await voice_service.optimize_campaign_budget(
            request.campaign_id,
            request.platform,
            request.performance_data
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/voice/reallocate-budget")
async def reallocate_budget(
    organization_id: str,
    total_budget: float,
    current_user: Dict[str, Any] = Depends(get_current_user),
    voice_service: VoiceAutomationService = Depends(get_voice_service)
):
    """Reallocate budget across campaigns"""
    try:
        result = await voice_service.reallocate_budget_across_campaigns(
            organization_id,
            total_budget
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== CURIOSITY (Market Intelligence) Routes ==========

@router.post("/curiosity/analyze-market")
async def analyze_market(
    vertical: str,
    data: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    curiosity_service: CuriosityMarketService = Depends(get_curiosity_service)
):
    """Analyze market for a specific vertical"""
    try:
        analysis = await curiosity_service.analyze_market(vertical, data)
        
        return {
            "success": True,
            "data": {
                "vertical": analysis.vertical,
                "market_size": analysis.market_size,
                "growth_rate": analysis.growth_rate,
                "key_trends": analysis.key_trends,
                "opportunities": analysis.opportunities,
                "competition_level": analysis.competition_level,
                "key_players": analysis.key_players,
                "market_gaps": analysis.market_gaps,
                "predictions": analysis.predictions,
                "investment_areas": analysis.investment_areas,
                "confidence": analysis.confidence
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/curiosity/analyze-competition")
async def analyze_competition(
    vertical: str,
    competitor_data: Optional[List[Dict[str, Any]]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    curiosity_service: CuriosityMarketService = Depends(get_curiosity_service)
):
    """Analyze competitive landscape"""
    try:
        analyses = await curiosity_service.analyze_competition(vertical, competitor_data)
        
        return {
            "success": True,
            "data": [
                {
                    "competitor_name": a.competitor_name,
                    "market_share": a.market_share,
                    "strengths": a.strengths,
                    "weaknesses": a.weaknesses,
                    "positioning": a.positioning,
                    "threat_level": a.threat_level,
                    "recommendations": a.recommendations
                }
                for a in analyses
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/curiosity/identify-trends")
async def identify_trends(
    vertical: str,
    timeframe_days: int = 90,
    current_user: Dict[str, Any] = Depends(get_current_user),
    curiosity_service: CuriosityMarketService = Depends(get_curiosity_service)
):
    """Identify market trends"""
    try:
        trends = await curiosity_service.identify_trends(vertical, timeframe_days)
        
        return {
            "success": True,
            "data": [
                {
                    "trend_name": t.trend_name,
                    "category": t.category,
                    "impact": t.impact,
                    "timeframe": t.timeframe,
                    "opportunities": t.opportunities,
                    "threats": t.threats,
                    "confidence": t.confidence
                }
                for t in trends
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== MEMORY (Client Intelligence) Routes ==========

@router.post("/memory/analyze-behavior")
async def analyze_client_behavior(
    client_id: str,
    behavior_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryClientService = Depends(get_memory_service)
):
    """Analyze client behavior and create profile"""
    try:
        profile = await memory_service.analyze_client_behavior(client_id, behavior_data)
        
        return {
            "success": True,
            "data": {
                "client_id": profile.client_id,
                "engagement_score": profile.engagement_score,
                "success_score": profile.success_score,
                "health_score": profile.health_score,
                "behavior_patterns": profile.behavior_patterns,
                "preferences": profile.preferences,
                "recommendations": profile.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/memory/predict-churn")
async def predict_churn(
    client_id: str,
    client_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryClientService = Depends(get_memory_service)
):
    """Predict client churn"""
    try:
        prediction = await memory_service.predict_churn(client_id, client_data)
        
        return {
            "success": True,
            "data": {
                "client_id": prediction.client_id,
                "churn_probability": prediction.churn_probability,
                "churn_risk_level": prediction.churn_risk_level,
                "days_until_churn": prediction.days_until_churn,
                "factors": prediction.factors,
                "recommendations": prediction.recommendations
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/memory/segment-clients")
async def segment_clients(
    organization_id: str,
    criteria: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    memory_service: MemoryClientService = Depends(get_memory_service)
):
    """Segment clients based on behavior"""
    try:
        segments = await memory_service.segment_clients(organization_id, criteria)
        
        return {
            "success": True,
            "data": [
                {
                    "segment_id": s.segment_id,
                    "segment_name": s.segment_name,
                    "client_count": s.client_count,
                    "characteristics": s.characteristics,
                    "avg_ltv": s.avg_ltv,
                    "churn_risk": s.churn_risk,
                    "engagement_score": s.engagement_score,
                    "recommendations": s.recommendations
                }
                for s in segments
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== REFLEXES (Performance Optimization) Routes ==========

@router.get("/reflexes/metrics")
async def get_system_metrics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reflexes_service: ReflexesPerformanceService = Depends(get_reflexes_service)
):
    """Get current system performance metrics"""
    try:
        metrics = await reflexes_service.get_system_metrics()
        
        return {
            "success": True,
            "data": {
                "cpu_usage": metrics.cpu_usage,
                "memory_usage": metrics.memory_usage,
                "disk_io": metrics.disk_io,
                "network_io": metrics.network_io,
                "response_time": metrics.response_time,
                "throughput": metrics.throughput,
                "error_rate": metrics.error_rate,
                "timestamp": metrics.timestamp.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reflexes/bottlenecks")
async def identify_bottlenecks(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reflexes_service: ReflexesPerformanceService = Depends(get_reflexes_service)
):
    """Identify performance bottlenecks"""
    try:
        bottlenecks = await reflexes_service.identify_bottlenecks()
        
        return {
            "success": True,
            "data": [
                {
                    "component": b.component,
                    "metric": b.metric,
                    "current_value": b.current_value,
                    "threshold": b.threshold,
                    "severity": b.severity,
                    "recommendations": b.recommendations
                }
                for b in bottlenecks
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reflexes/optimizations")
async def get_optimization_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user),
    reflexes_service: ReflexesPerformanceService = Depends(get_reflexes_service)
):
    """Get performance optimization recommendations"""
    try:
        recommendations = await reflexes_service.get_optimization_recommendations()
        
        return {
            "success": True,
            "data": [
                {
                    "action_type": r.action_type,
                    "target": r.target,
                    "current_value": r.current_value,
                    "recommended_value": r.recommended_value,
                    "priority": r.priority,
                    "impact": r.impact,
                    "estimated_improvement": r.estimated_improvement
                }
                for r in recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ========== FACE (Customer Experience) Routes ==========

@router.post("/face/analyze-behavior")
async def analyze_user_behavior(
    user_id: str,
    timeframe_days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user),
    face_service: FaceExperienceService = Depends(get_face_service)
):
    """Analyze user behavior patterns"""
    try:
        behavior = await face_service.analyze_user_behavior(user_id, timeframe_days)
        
        return {
            "success": True,
            "data": {
                "user_id": behavior.user_id,
                "session_count": behavior.session_count,
                "avg_session_duration": behavior.avg_session_duration,
                "features_used": behavior.features_used,
                "common_paths": behavior.common_paths,
                "drop_off_points": behavior.drop_off_points,
                "engagement_score": behavior.engagement_score
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/face/ux-insights")
async def get_ux_insights(
    organization_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    face_service: FaceExperienceService = Depends(get_face_service)
):
    """Get UX insights and recommendations"""
    try:
        insights = await face_service.get_ux_insights(organization_id)
        
        return {
            "success": True,
            "data": [
                {
                    "insight_type": i.insight_type,
                    "component": i.component,
                    "issue": i.issue,
                    "impact": i.impact,
                    "recommendation": i.recommendation,
                    "priority": i.priority
                }
                for i in insights
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/face/personalization")
async def create_personalization_profile(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    face_service: FaceExperienceService = Depends(get_face_service)
):
    """Create personalized experience profile"""
    try:
        profile = await face_service.create_personalization_profile(user_id)
        
        return {
            "success": True,
            "data": {
                "user_id": profile.user_id,
                "preferences": profile.preferences,
                "recommended_features": profile.recommended_features,
                "content_preferences": profile.content_preferences,
                "ui_preferences": profile.ui_preferences
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

