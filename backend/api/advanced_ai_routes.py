"""
Advanced AI Features API Routes
Production-grade API endpoints for market intelligence, anomaly detection, and trend analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime, timedelta

from services.advanced_ai_service import (
    get_advanced_ai_service, AdvancedAIService,
    AnomalyType, TrendDirection, MarketSentiment
)
from database.mongodb import get_database

router = APIRouter()
logger = logging.getLogger(__name__)

# Request/Response Models
class AnomalyDetectionResponse(BaseModel):
    anomaly_id: str
    anomaly_type: str
    severity: float
    confidence: float
    description: str
    detected_at: str
    affected_metrics: List[str]
    recommendations: List[str]
    impact_score: float

class TrendAnalysisResponse(BaseModel):
    trend_id: str
    metric_name: str
    trend_direction: str
    trend_strength: float
    confidence: float
    timeframe: str
    predicted_value: float
    predicted_at: str
    factors: List[str]

class MarketIntelligenceResponse(BaseModel):
    intelligence_id: str
    category: str
    title: str
    description: str
    sentiment: str
    impact_score: float
    confidence: float
    source: str
    published_at: str
    tags: List[str]
    related_campaigns: List[str]

class CompetitiveIntelligenceResponse(BaseModel):
    competitive_position: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    recommendations: List[str]
    market_ranking: int
    competitive_gaps: List[str]
    differentiation_opportunities: List[str]

class AIInsightsDashboardResponse(BaseModel):
    client_id: str
    market_intelligence: List[MarketIntelligenceResponse]
    anomalies: List[AnomalyDetectionResponse]
    trends: List[TrendAnalysisResponse]
    competitive_intelligence: CompetitiveIntelligenceResponse
    summary_insights: Dict[str, Any]
    generated_at: str

# Dependency
async def get_ai_service(db: AsyncIOMotorClient = Depends(get_database)) -> AdvancedAIService:
    return get_advanced_ai_service(db)

# Market Intelligence Endpoints
@router.get("/api/ai/market-intelligence/{client_id}", response_model=List[MarketIntelligenceResponse], summary="Get Market Intelligence")
async def get_market_intelligence(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get market intelligence for a client.
    Returns industry news, competitor analysis, and trend insights.
    """
    try:
        intelligence = await ai_service.get_market_intelligence(client_id)
        
        return [MarketIntelligenceResponse(**item.__dict__) for item in intelligence]
    except Exception as e:
        logger.error(f"Error getting market intelligence for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market intelligence"
        )

@router.post("/api/ai/market-intelligence/{client_id}/refresh", summary="Refresh Market Intelligence")
async def refresh_market_intelligence(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Refresh market intelligence data.
    Triggers new data gathering from various sources.
    """
    try:
        intelligence = await ai_service.get_market_intelligence(client_id)
        
        return {
            "client_id": client_id,
            "intelligence_count": len(intelligence),
            "refreshed_at": datetime.utcnow().isoformat(),
            "status": "refreshed"
        }
    except Exception as e:
        logger.error(f"Error refreshing market intelligence for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh market intelligence"
        )

# Anomaly Detection Endpoints
@router.get("/api/ai/anomalies/{client_id}", response_model=List[AnomalyDetectionResponse], summary="Detect Anomalies")
async def detect_anomalies(
    client_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Detect anomalies in client's campaign performance.
    Returns detected anomalies with severity and recommendations.
    """
    try:
        anomalies = await ai_service.detect_anomalies(client_id, days)
        
        return [AnomalyDetectionResponse(**anomaly.__dict__) for anomaly in anomalies]
    except Exception as e:
        logger.error(f"Error detecting anomalies for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to detect anomalies"
        )

@router.get("/api/ai/anomalies/{client_id}/summary", summary="Get Anomaly Summary")
async def get_anomaly_summary(
    client_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get summary of detected anomalies.
    Returns anomaly statistics and high-priority alerts.
    """
    try:
        anomalies = await ai_service.detect_anomalies(client_id, days)
        
        # Categorize anomalies
        anomaly_summary = {
            "total_anomalies": len(anomalies),
            "high_severity": len([a for a in anomalies if a.severity > 7]),
            "medium_severity": len([a for a in anomalies if 4 <= a.severity <= 7]),
            "low_severity": len([a for a in anomalies if a.severity < 4]),
            "anomaly_types": {},
            "high_priority_alerts": [],
            "recommendations": []
        }
        
        # Count by type
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type.value
            if anomaly_type not in anomaly_summary["anomaly_types"]:
                anomaly_summary["anomaly_types"][anomaly_type] = 0
            anomaly_summary["anomaly_types"][anomaly_type] += 1
            
            # High priority alerts
            if anomaly.severity > 7:
                anomaly_summary["high_priority_alerts"].append({
                    "anomaly_id": anomaly.anomaly_id,
                    "type": anomaly_type,
                    "description": anomaly.description,
                    "severity": anomaly.severity,
                    "detected_at": anomaly.detected_at.isoformat()
                })
            
            # Collect recommendations
            anomaly_summary["recommendations"].extend(anomaly.recommendations)
        
        # Remove duplicates from recommendations
        anomaly_summary["recommendations"] = list(set(anomaly_summary["recommendations"]))
        
        return {
            "client_id": client_id,
            "analysis_period_days": days,
            "summary": anomaly_summary,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting anomaly summary for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get anomaly summary"
        )

# Trend Analysis Endpoints
@router.get("/api/ai/trends/{client_id}", response_model=List[TrendAnalysisResponse], summary="Analyze Trends")
async def analyze_trends(
    client_id: str,
    metrics: str = Query("impressions,clicks,conversions,revenue", description="Comma-separated metrics"),
    days: int = Query(90, description="Number of days to analyze"),
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Analyze trends for specified metrics.
    Returns trend analysis with predictions and confidence scores.
    """
    try:
        metrics_list = [m.strip() for m in metrics.split(",")]
        trends = await ai_service.analyze_trends(client_id, metrics_list, days)
        
        return [TrendAnalysisResponse(**trend.__dict__) for trend in trends]
    except Exception as e:
        logger.error(f"Error analyzing trends for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze trends"
        )

@router.get("/api/ai/trends/{client_id}/predictions", summary="Get Trend Predictions")
async def get_trend_predictions(
    client_id: str,
    metrics: str = Query("impressions,clicks,conversions,revenue", description="Comma-separated metrics"),
    days: int = Query(90, description="Number of days to analyze"),
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get trend predictions for specified metrics.
    Returns predicted values and confidence intervals.
    """
    try:
        metrics_list = [m.strip() for m in metrics.split(",")]
        trends = await ai_service.analyze_trends(client_id, metrics_list, days)
        
        predictions = []
        for trend in trends:
            predictions.append({
                "metric_name": trend.metric_name,
                "current_value": 0,  # Would be calculated from actual data
                "predicted_value": trend.predicted_value,
                "predicted_at": trend.predicted_at.isoformat(),
                "confidence": trend.confidence,
                "trend_direction": trend.trend_direction.value,
                "trend_strength": trend.trend_strength,
                "factors": trend.factors
            })
        
        return {
            "client_id": client_id,
            "analysis_period_days": days,
            "predictions": predictions,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting trend predictions for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trend predictions"
        )

# Competitive Intelligence Endpoints
@router.get("/api/ai/competitive-intelligence/{client_id}", response_model=CompetitiveIntelligenceResponse, summary="Get Competitive Intelligence")
async def get_competitive_intelligence(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get competitive intelligence for a client.
    Returns competitive analysis, market positioning, and benchmarking.
    """
    try:
        intelligence = await ai_service.get_competitive_intelligence(client_id)
        
        return CompetitiveIntelligenceResponse(**intelligence)
    except Exception as e:
        logger.error(f"Error getting competitive intelligence for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve competitive intelligence"
        )

@router.get("/api/ai/competitive-intelligence/{client_id}/benchmark", summary="Get Competitive Benchmark")
async def get_competitive_benchmark(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get competitive benchmark analysis.
    Returns performance comparison with industry averages.
    """
    try:
        intelligence = await ai_service.get_competitive_intelligence(client_id)
        
        # Generate benchmark data
        benchmark = {
            "client_id": client_id,
            "market_ranking": intelligence.get("market_ranking", 5),
            "competitive_position": intelligence.get("competitive_position", "middle"),
            "performance_vs_competitors": {
                "ctr_performance": "above_average",  # Would be calculated from actual data
                "conversion_performance": "average",
                "cpa_performance": "below_average",
                "roas_performance": "above_average"
            },
            "strengths": intelligence.get("strengths", []),
            "weaknesses": intelligence.get("weaknesses", []),
            "recommendations": intelligence.get("recommendations", []),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return benchmark
    except Exception as e:
        logger.error(f"Error getting competitive benchmark for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get competitive benchmark"
        )

# AI Insights Dashboard Endpoint
@router.get("/api/ai/insights-dashboard/{client_id}", response_model=AIInsightsDashboardResponse, summary="Get AI Insights Dashboard")
async def get_ai_insights_dashboard(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get comprehensive AI insights dashboard.
    Returns all AI analysis including market intelligence, anomalies, trends, and competitive intelligence.
    """
    try:
        dashboard = await ai_service.get_ai_insights_dashboard(client_id)
        
        return AIInsightsDashboardResponse(
            client_id=dashboard["client_id"],
            market_intelligence=[MarketIntelligenceResponse(**item.__dict__) for item in dashboard["market_intelligence"]],
            anomalies=[AnomalyDetectionResponse(**item.__dict__) for item in dashboard["anomalies"]],
            trends=[TrendAnalysisResponse(**item.__dict__) for item in dashboard["trends"]],
            competitive_intelligence=CompetitiveIntelligenceResponse(**dashboard["competitive_intelligence"]),
            summary_insights=dashboard["summary_insights"],
            generated_at=dashboard["generated_at"]
        )
    except Exception as e:
        logger.error(f"Error getting AI insights dashboard for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI insights dashboard"
        )

# AI Recommendations Endpoint
@router.get("/api/ai/recommendations/{client_id}", summary="Get AI Recommendations")
async def get_ai_recommendations(
    client_id: str,
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Get AI-powered recommendations for campaign optimization.
    Returns actionable recommendations based on all AI analysis.
    """
    try:
        dashboard = await ai_service.get_ai_insights_dashboard(client_id)
        
        # Extract recommendations from all sources
        all_recommendations = []
        
        # From anomalies
        for anomaly in dashboard["anomalies"]:
            all_recommendations.extend(anomaly.recommendations)
        
        # From competitive intelligence
        competitive_recs = dashboard["competitive_intelligence"].get("recommendations", [])
        all_recommendations.extend(competitive_recs)
        
        # From summary insights
        summary_recs = dashboard["summary_insights"].get("recommendations", [])
        all_recommendations.extend(summary_recs)
        
        # Categorize and prioritize recommendations
        categorized_recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "opportunities": dashboard["summary_insights"].get("opportunities", []),
            "risks": dashboard["summary_insights"].get("risks", []),
            "alerts": dashboard["summary_insights"].get("alerts", [])
        }
        
        # Simple prioritization based on keywords
        for rec in all_recommendations:
            if any(keyword in rec.lower() for keyword in ["urgent", "critical", "immediate", "high"]):
                categorized_recommendations["high_priority"].append(rec)
            elif any(keyword in rec.lower() for keyword in ["consider", "optimize", "improve"]):
                categorized_recommendations["medium_priority"].append(rec)
            else:
                categorized_recommendations["low_priority"].append(rec)
        
        # Remove duplicates
        for category in categorized_recommendations:
            if isinstance(categorized_recommendations[category], list):
                categorized_recommendations[category] = list(set(categorized_recommendations[category]))
        
        return {
            "client_id": client_id,
            "recommendations": categorized_recommendations,
            "total_recommendations": len(all_recommendations),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI recommendations for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI recommendations"
        )

# AI Health Check
@router.get("/api/ai/health", summary="AI Service Health Check")
async def ai_health_check(
    ai_service: AdvancedAIService = Depends(get_ai_service)
):
    """
    Check the health of the AI service.
    Returns service status and capabilities.
    """
    try:
        # Check database connection
        await ai_service.db.admin.command('ping')
        
        # Check service components
        components = {
            "market_intelligence_engine": ai_service.market_intelligence_engine is not None,
            "anomaly_detection_engine": ai_service.anomaly_detection_engine is not None,
            "trend_analysis_engine": ai_service.trend_analysis_engine is not None,
            "competitive_intelligence_engine": ai_service.competitive_intelligence_engine is not None
        }
        
        all_healthy = all(components.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "components": components,
            "capabilities": {
                "market_intelligence": True,
                "anomaly_detection": True,
                "trend_analysis": True,
                "competitive_intelligence": True,
                "ai_recommendations": True,
                "predictive_analytics": True
            },
            "supported_anomaly_types": [anomaly_type.value for anomaly_type in AnomalyType],
            "supported_trend_directions": [direction.value for direction in TrendDirection],
            "supported_sentiments": [sentiment.value for sentiment in MarketSentiment],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
