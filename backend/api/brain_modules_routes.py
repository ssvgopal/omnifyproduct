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

