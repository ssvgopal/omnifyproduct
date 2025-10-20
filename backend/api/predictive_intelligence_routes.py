"""
Predictive Intelligence API Routes
Production-grade API endpoints for predictive analytics, optimization recommendations, and market forecasting
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta
import pandas as pd

from services.predictive_intelligence_service import (
    get_predictive_intelligence_service, PredictiveIntelligenceService,
    PredictionType, OptimizationAction, ConfidenceLevel
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class PredictionRequest(BaseModel):
    prediction_types: List[str] = Field(..., description="Types of predictions to generate")
    features: Dict[str, float] = Field(..., description="Feature values for prediction")
    horizon_days: int = Field(30, description="Prediction horizon in days")

class OptimizationRequest(BaseModel):
    campaign_id: str = Field(..., description="Campaign ID to optimize")
    campaign_data: Dict[str, Any] = Field(..., description="Campaign data for analysis")

class MarketForecastRequest(BaseModel):
    market_segment: str = Field(..., description="Market segment to forecast")
    forecast_period: str = Field("6_months", description="Forecast period")

class PredictionResponse(BaseModel):
    prediction_id: str
    prediction_type: str
    predicted_value: float
    confidence: float
    confidence_level: str
    prediction_horizon: int
    factors: List[str]
    model_used: str
    accuracy_score: float
    created_at: str
    valid_until: str

class OptimizationRecommendationResponse(BaseModel):
    recommendation_id: str
    action: str
    target_campaign_id: str
    expected_impact: float
    confidence: float
    reasoning: str
    implementation_steps: List[str]
    risk_level: str
    priority: str
    created_at: str

class MarketForecastResponse(BaseModel):
    forecast_id: str
    market_segment: str
    forecast_period: str
    predicted_growth: float
    confidence: float
    key_drivers: List[str]
    risks: List[str]
    opportunities: List[str]
    created_at: str

class PredictiveDashboardResponse(BaseModel):
    client_id: str
    predictions: List[PredictionResponse]
    optimization_recommendations: List[OptimizationRecommendationResponse]
    market_forecast: MarketForecastResponse
    model_performance: Dict[str, Any]
    generated_at: str

# Dependency
async def get_predictive_service(db: AsyncIOMotorClient = Depends(get_database)) -> PredictiveIntelligenceService:
    return get_predictive_intelligence_service(db)

# Prediction Endpoints
@router.post("/api/predictive/predictions", response_model=List[PredictionResponse], summary="Generate Predictions")
async def generate_predictions(
    client_id: str = Query(..., description="Client ID"),
    request: PredictionRequest = Body(...),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Generate predictions for specified types and features.
    Returns predictions with confidence scores and factors.
    """
    try:
        # Convert string prediction types to enums
        prediction_types = [PredictionType(pt) for pt in request.prediction_types]
        
        # Generate predictions
        predictions = await predictive_service.generate_predictions(
            client_id, prediction_types, request.features
        )
        
        return [PredictionResponse(**prediction.__dict__) for prediction in predictions]
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid prediction type: {e}"
        )
    except Exception as e:
        logger.error(f"Error generating predictions for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate predictions"
        )

@router.get("/api/predictive/predictions/{client_id}", response_model=List[PredictionResponse], summary="Get Client Predictions")
async def get_client_predictions(
    client_id: str,
    prediction_type: Optional[str] = Query(None, description="Filter by prediction type"),
    days_ahead: int = Query(30, description="Filter by prediction horizon"),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Get predictions for a specific client.
    Returns historical predictions with filtering options.
    """
    try:
        # Build query
        query = {"client_id": client_id}
        
        if prediction_type:
            query["prediction_type"] = prediction_type
        
        if days_ahead:
            query["prediction_horizon"] = days_ahead
        
        # Get predictions from database
        predictions_docs = await predictive_service.db.predictions.find(query).sort("created_at", -1).limit(50).to_list(length=None)
        
        predictions = []
        for doc in predictions_docs:
            predictions.append(PredictionResponse(
                prediction_id=doc["prediction_id"],
                prediction_type=doc["prediction_type"],
                predicted_value=doc["predicted_value"],
                confidence=doc["confidence"],
                confidence_level=doc["confidence_level"],
                prediction_horizon=doc["prediction_horizon"],
                factors=doc["factors"],
                model_used=doc["model_used"],
                accuracy_score=doc["accuracy_score"],
                created_at=doc["created_at"],
                valid_until=doc["valid_until"]
            ))
        
        return predictions
        
    except Exception as e:
        logger.error(f"Error getting predictions for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get predictions"
        )

# Optimization Endpoints
@router.post("/api/predictive/optimization", response_model=List[OptimizationRecommendationResponse], summary="Generate Optimization Recommendations")
async def generate_optimization_recommendations(
    request: OptimizationRequest = Body(...),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Generate optimization recommendations for a campaign.
    Returns actionable recommendations with expected impact and implementation steps.
    """
    try:
        recommendations = await predictive_service.get_optimization_recommendations(
            request.campaign_id, request.campaign_data
        )
        
        return [OptimizationRecommendationResponse(**rec.__dict__) for rec in recommendations]
        
    except Exception as e:
        logger.error(f"Error generating optimization recommendations for campaign {request.campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate optimization recommendations"
        )

@router.get("/api/predictive/optimization/{campaign_id}", response_model=List[OptimizationRecommendationResponse], summary="Get Campaign Optimization Recommendations")
async def get_campaign_optimization_recommendations(
    campaign_id: str,
    status: Optional[str] = Query("pending", description="Filter by recommendation status"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Get optimization recommendations for a specific campaign.
    Returns recommendations with filtering options.
    """
    try:
        # Build query
        query = {"target_campaign_id": campaign_id}
        
        if status:
            query["status"] = status
        
        if priority:
            query["priority"] = priority
        
        # Get recommendations from database
        recommendations_docs = await predictive_service.db.optimization_recommendations.find(query).sort("created_at", -1).to_list(length=None)
        
        recommendations = []
        for doc in recommendations_docs:
            recommendations.append(OptimizationRecommendationResponse(
                recommendation_id=doc["recommendation_id"],
                action=doc["action"],
                target_campaign_id=doc["target_campaign_id"],
                expected_impact=doc["expected_impact"],
                confidence=doc["confidence"],
                reasoning=doc["reasoning"],
                implementation_steps=doc["implementation_steps"],
                risk_level=doc["risk_level"],
                priority=doc["priority"],
                created_at=doc["created_at"]
            ))
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting optimization recommendations for campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get optimization recommendations"
        )

@router.put("/api/predictive/optimization/{recommendation_id}/implement", summary="Implement Optimization Recommendation")
async def implement_optimization_recommendation(
    recommendation_id: str,
    implementation_notes: Optional[str] = Body(None, description="Implementation notes"),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Mark optimization recommendation as implemented.
    Updates recommendation status and records implementation.
    """
    try:
        # Update recommendation status
        update_result = await predictive_service.db.optimization_recommendations.update_one(
            {"recommendation_id": recommendation_id},
            {
                "$set": {
                    "status": "implemented",
                    "implemented_at": datetime.utcnow().isoformat(),
                    "implementation_notes": implementation_notes
                }
            }
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found"
            )
        
        return {
            "recommendation_id": recommendation_id,
            "status": "implemented",
            "implemented_at": datetime.utcnow().isoformat(),
            "message": "Recommendation marked as implemented"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error implementing recommendation {recommendation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to implement recommendation"
        )

# Market Forecasting Endpoints
@router.post("/api/predictive/forecast", response_model=MarketForecastResponse, summary="Generate Market Forecast")
async def generate_market_forecast(
    request: MarketForecastRequest = Body(...),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Generate market forecast for specified segment.
    Returns forecast with growth predictions, drivers, risks, and opportunities.
    """
    try:
        forecast = await predictive_service.get_market_forecast(
            request.market_segment, request.forecast_period
        )
        
        return MarketForecastResponse(**forecast.__dict__)
        
    except Exception as e:
        logger.error(f"Error generating market forecast for {request.market_segment}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate market forecast"
        )

@router.get("/api/predictive/forecast", response_model=List[MarketForecastResponse], summary="Get Market Forecasts")
async def get_market_forecasts(
    market_segment: Optional[str] = Query(None, description="Filter by market segment"),
    forecast_period: Optional[str] = Query(None, description="Filter by forecast period"),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Get market forecasts with filtering options.
    Returns historical forecasts for analysis.
    """
    try:
        # Build query
        query = {}
        
        if market_segment:
            query["market_segment"] = market_segment
        
        if forecast_period:
            query["forecast_period"] = forecast_period
        
        # Get forecasts from database
        forecasts_docs = await predictive_service.db.market_forecasts.find(query).sort("created_at", -1).limit(20).to_list(length=None)
        
        forecasts = []
        for doc in forecasts_docs:
            forecasts.append(MarketForecastResponse(
                forecast_id=doc["forecast_id"],
                market_segment=doc["market_segment"],
                forecast_period=doc["forecast_period"],
                predicted_growth=doc["predicted_growth"],
                confidence=doc["confidence"],
                key_drivers=doc["key_drivers"],
                risks=doc["risks"],
                opportunities=doc["opportunities"],
                created_at=doc["created_at"]
            ))
        
        return forecasts
        
    except Exception as e:
        logger.error(f"Error getting market forecasts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get market forecasts"
        )

# Model Management Endpoints
@router.post("/api/predictive/models/train", summary="Train Predictive Models")
async def train_predictive_models(
    training_data_type: str = Body(..., description="Type of training data"),
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Train predictive models with new data.
    Updates model performance and accuracy.
    """
    try:
        # Generate mock training data - in production, load from actual data sources
        training_data = {}
        
        if training_data_type == "campaign_performance":
            # Mock campaign performance data
            data = {
                'budget': np.random.uniform(1000, 10000, 1000),
                'daily_budget': np.random.uniform(50, 500, 1000),
                'targeting_score': np.random.uniform(0.3, 1.0, 1000),
                'creative_score': np.random.uniform(0.3, 1.0, 1000),
                'seasonality': np.random.uniform(0.0, 1.0, 1000),
                'competition_level': np.random.uniform(0.0, 1.0, 1000),
                'conversion_rate': np.random.uniform(0.01, 0.1, 1000)
            }
            training_data["campaign_performance"] = pd.DataFrame(data)
        
        elif training_data_type == "conversion_rate":
            # Mock conversion rate data
            data = {
                'ctr': np.random.uniform(0.01, 0.1, 1000),
                'landing_page_score': np.random.uniform(0.3, 1.0, 1000),
                'audience_quality': np.random.uniform(0.3, 1.0, 1000),
                'creative_relevance': np.random.uniform(0.3, 1.0, 1000),
                'device_type': np.random.uniform(0.0, 1.0, 1000),
                'conversion_rate': np.random.uniform(0.01, 0.15, 1000)
            }
            training_data["conversion_rate"] = pd.DataFrame(data)
        
        # Train models
        results = await predictive_service.train_all_models(training_data)
        
        return {
            "training_results": results,
            "trained_at": datetime.utcnow().isoformat(),
            "message": f"Successfully trained models for {training_data_type}"
        }
        
    except Exception as e:
        logger.error(f"Error training models for {training_data_type}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to train models"
        )

@router.get("/api/predictive/models/performance", summary="Get Model Performance")
async def get_model_performance(
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Get performance metrics for all predictive models.
    Returns accuracy scores, training data, and model metadata.
    """
    try:
        model_performance = predictive_service.model_manager.model_metadata
        
        return {
            "model_performance": model_performance,
            "total_models": len(model_performance),
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get model performance"
        )

# Dashboard Endpoint
@router.get("/api/predictive/dashboard/{client_id}", response_model=PredictiveDashboardResponse, summary="Get Predictive Intelligence Dashboard")
async def get_predictive_dashboard(
    client_id: str,
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Get comprehensive predictive intelligence dashboard.
    Returns predictions, recommendations, forecasts, and model performance.
    """
    try:
        dashboard = await predictive_service.get_predictive_dashboard(client_id)
        
        return PredictiveDashboardResponse(
            client_id=dashboard["client_id"],
            predictions=[PredictionResponse(**pred.__dict__) for pred in dashboard["predictions"]],
            optimization_recommendations=[OptimizationRecommendationResponse(**rec.__dict__) for rec in dashboard["optimization_recommendations"]],
            market_forecast=MarketForecastResponse(**dashboard["market_forecast"].__dict__),
            model_performance=dashboard["model_performance"],
            generated_at=dashboard["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"Error getting predictive dashboard for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get predictive dashboard"
        )

# Predictive Intelligence Health Check
@router.get("/api/predictive/health", summary="Predictive Intelligence Health Check")
async def predictive_health_check(
    predictive_service: PredictiveIntelligenceService = Depends(get_predictive_service)
):
    """
    Check the health of the predictive intelligence system.
    Returns service status and model capabilities.
    """
    try:
        # Check database connection
        await predictive_service.db.admin.command('ping')
        
        # Check model status
        model_status = {
            "total_models": len(predictive_service.model_manager.models),
            "trained_models": len(predictive_service.model_manager.model_metadata),
            "model_types": list(predictive_service.model_manager.models.keys())
        }
        
        # Check optimization engine
        optimization_status = {
            "optimization_rules": len(predictive_service.optimization_engine.optimization_rules),
            "rule_categories": list(predictive_service.optimization_engine.optimization_rules.keys())
        }
        
        # Check forecasting engine
        forecasting_status = {
            "forecast_models": len(predictive_service.forecasting_engine.forecast_models),
            "model_types": list(predictive_service.forecasting_engine.forecast_models.keys())
        }
        
        all_healthy = (
            model_status["total_models"] > 0 and
            optimization_status["optimization_rules"] > 0 and
            forecasting_status["forecast_models"] > 0
        )
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "model_status": model_status,
            "optimization_status": optimization_status,
            "forecasting_status": forecasting_status,
            "capabilities": {
                "predictive_analytics": True,
                "optimization_recommendations": True,
                "market_forecasting": True,
                "model_training": True,
                "real_time_predictions": True
            },
            "supported_prediction_types": [pt.value for pt in PredictionType],
            "supported_optimization_actions": [oa.value for oa in OptimizationAction],
            "supported_confidence_levels": [cl.value for cl in ConfidenceLevel],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking predictive intelligence health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
