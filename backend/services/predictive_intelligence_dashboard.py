"""
Predictive Intelligence Dashboard
Shows customers future predictions, trends, and opportunities
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import random
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Types of predictions"""
    CREATIVE_FATIGUE = "creative_fatigue"
    LTV_FORECAST = "ltv_forecast"
    CHURN_RISK = "churn_risk"
    BUDGET_OPTIMIZATION = "budget_optimization"
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    MARKET_TRENDS = "market_trends"
    COMPETITOR_ACTIVITY = "competitor_activity"
    CUSTOMER_JOURNEY = "customer_journey"
    REVENUE_FORECAST = "revenue_forecast"
    SEASONAL_PATTERNS = "seasonal_patterns"

class PredictionConfidence(Enum):
    """Prediction confidence levels"""
    HIGH = "high"      # 80-100%
    MEDIUM = "medium"  # 60-79%
    LOW = "low"        # 40-59%
    VERY_LOW = "very_low"  # <40%

class TrendDirection(Enum):
    """Trend directions"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"

@dataclass
class PredictionData:
    """Data for a prediction"""
    prediction_id: str
    prediction_type: PredictionType
    title: str
    description: str
    current_value: float
    predicted_value: float
    confidence_score: float
    confidence_level: PredictionConfidence
    trend_direction: TrendDirection
    time_horizon: int  # days
    impact_score: float  # 0.0-1.0
    risk_level: str  # low, medium, high
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))

@dataclass
class TrendAnalysis:
    """Trend analysis data"""
    trend_id: str
    metric_name: str
    current_trend: TrendDirection
    trend_strength: float  # 0.0-1.0
    historical_data: List[float]
    predicted_data: List[float]
    key_insights: List[str]
    anomalies: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class OpportunityAlert:
    """Opportunity alert data"""
    alert_id: str
    opportunity_type: str
    title: str
    description: str
    potential_value: float
    confidence_score: float
    urgency_level: str  # low, medium, high, critical
    action_required: str
    time_sensitivity: int  # hours
    created_at: datetime = field(default_factory=datetime.utcnow)

class PredictiveIntelligenceDashboard:
    """
    Predictive Intelligence Dashboard
    Shows customers future predictions, trends, and opportunities
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.predictions: Dict[str, List[PredictionData]] = {}
        self.trend_analyses: Dict[str, List[TrendAnalysis]] = {}
        self.opportunity_alerts: Dict[str, List[OpportunityAlert]] = {}
        
        # Prediction models (in real implementation, these would be trained models)
        self.prediction_models = {}
        
        # Prediction templates
        self.prediction_templates = self._create_prediction_templates()
        
        # Trend analysis configurations
        self.trend_configs = self._create_trend_configurations()
        
        logger.info("Predictive Intelligence Dashboard initialized")

    def _create_prediction_templates(self) -> Dict[PredictionType, Dict[str, Any]]:
        """Create prediction templates"""
        return {
            PredictionType.CREATIVE_FATIGUE: {
                "title": "Creative Fatigue Prediction",
                "description": "Predicts when your creative assets will lose effectiveness",
                "time_horizon": 14,
                "impact_score": 0.8,
                "risk_level": "medium",
                "recommendations": [
                    "Prepare new creative variations",
                    "Test alternative messaging",
                    "Rotate creative assets more frequently"
                ]
            },
            PredictionType.LTV_FORECAST: {
                "title": "Customer Lifetime Value Forecast",
                "description": "Predicts future customer lifetime value",
                "time_horizon": 90,
                "impact_score": 0.9,
                "risk_level": "low",
                "recommendations": [
                    "Focus on high-LTV customer acquisition",
                    "Implement retention strategies",
                    "Optimize customer journey"
                ]
            },
            PredictionType.CHURN_RISK: {
                "title": "Customer Churn Risk Prediction",
                "description": "Identifies customers at risk of churning",
                "time_horizon": 30,
                "impact_score": 0.95,
                "risk_level": "high",
                "recommendations": [
                    "Implement retention campaigns",
                    "Offer personalized incentives",
                    "Improve customer experience"
                ]
            },
            PredictionType.BUDGET_OPTIMIZATION: {
                "title": "Budget Optimization Forecast",
                "description": "Predicts optimal budget allocation across campaigns",
                "time_horizon": 30,
                "impact_score": 0.85,
                "risk_level": "medium",
                "recommendations": [
                    "Reallocate budget to high-performing campaigns",
                    "Reduce spend on underperforming channels",
                    "Test new budget allocation strategies"
                ]
            },
            PredictionType.CAMPAIGN_PERFORMANCE: {
                "title": "Campaign Performance Forecast",
                "description": "Predicts future campaign performance metrics",
                "time_horizon": 14,
                "impact_score": 0.7,
                "risk_level": "low",
                "recommendations": [
                    "Optimize underperforming campaigns",
                    "Scale successful campaigns",
                    "Adjust targeting parameters"
                ]
            },
            PredictionType.MARKET_TRENDS: {
                "title": "Market Trend Analysis",
                "description": "Predicts upcoming market trends and opportunities",
                "time_horizon": 60,
                "impact_score": 0.6,
                "risk_level": "low",
                "recommendations": [
                    "Prepare for emerging trends",
                    "Adjust marketing strategy",
                    "Monitor competitor activities"
                ]
            },
            PredictionType.COMPETITOR_ACTIVITY: {
                "title": "Competitor Activity Prediction",
                "description": "Predicts competitor marketing activities",
                "time_horizon": 30,
                "impact_score": 0.75,
                "risk_level": "medium",
                "recommendations": [
                    "Prepare competitive responses",
                    "Differentiate marketing messages",
                    "Monitor competitor pricing"
                ]
            },
            PredictionType.CUSTOMER_JOURNEY: {
                "title": "Customer Journey Optimization",
                "description": "Predicts optimal customer journey paths",
                "time_horizon": 45,
                "impact_score": 0.8,
                "risk_level": "medium",
                "recommendations": [
                    "Optimize touchpoint sequences",
                    "Improve conversion funnels",
                    "Personalize customer experiences"
                ]
            },
            PredictionType.REVENUE_FORECAST: {
                "title": "Revenue Forecast",
                "description": "Predicts future revenue based on current trends",
                "time_horizon": 90,
                "impact_score": 0.95,
                "risk_level": "low",
                "recommendations": [
                    "Adjust sales targets",
                    "Plan resource allocation",
                    "Identify growth opportunities"
                ]
            },
            PredictionType.SEASONAL_PATTERNS: {
                "title": "Seasonal Pattern Analysis",
                "description": "Predicts seasonal trends and patterns",
                "time_horizon": 180,
                "impact_score": 0.7,
                "risk_level": "low",
                "recommendations": [
                    "Plan seasonal campaigns",
                    "Adjust inventory levels",
                    "Prepare for peak periods"
                ]
            }
        }

    def _create_trend_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Create trend analysis configurations"""
        return {
            "roas": {
                "name": "Return on Ad Spend",
                "unit": "%",
                "thresholds": {"high": 400, "medium": 300, "low": 200},
                "trend_periods": [7, 14, 30, 90]
            },
            "ctr": {
                "name": "Click-Through Rate",
                "unit": "%",
                "thresholds": {"high": 3.0, "medium": 2.0, "low": 1.0},
                "trend_periods": [7, 14, 30]
            },
            "conversion_rate": {
                "name": "Conversion Rate",
                "unit": "%",
                "thresholds": {"high": 5.0, "medium": 3.0, "low": 1.0},
                "trend_periods": [7, 14, 30, 90]
            },
            "cpc": {
                "name": "Cost Per Click",
                "unit": "$",
                "thresholds": {"high": 3.0, "medium": 2.0, "low": 1.0},
                "trend_periods": [7, 14, 30]
            },
            "engagement_rate": {
                "name": "Engagement Rate",
                "unit": "%",
                "thresholds": {"high": 5.0, "medium": 3.0, "low": 1.0},
                "trend_periods": [7, 14, 30]
            },
            "revenue": {
                "name": "Revenue",
                "unit": "$",
                "thresholds": {"high": 10000, "medium": 5000, "low": 1000},
                "trend_periods": [7, 14, 30, 90]
            }
        }

    async def generate_predictions(
        self, 
        client_id: str, 
        organization_id: str,
        prediction_types: List[PredictionType] = None
    ) -> Dict[str, Any]:
        """Generate predictions for a client"""
        try:
            if not prediction_types:
                prediction_types = list(PredictionType)
            
            predictions = []
            
            for prediction_type in prediction_types:
                prediction = await self._generate_prediction(
                    client_id, prediction_type
                )
                if prediction:
                    predictions.append(prediction)
            
            # Store predictions
            if client_id not in self.predictions:
                self.predictions[client_id] = []
            self.predictions[client_id].extend(predictions)
            
            logger.info(f"Generated {len(predictions)} predictions for client {client_id}")
            
            return {
                "success": True,
                "client_id": client_id,
                "predictions": [
                    {
                        "prediction_id": p.prediction_id,
                        "type": p.prediction_type.value,
                        "title": p.title,
                        "description": p.description,
                        "current_value": p.current_value,
                        "predicted_value": p.predicted_value,
                        "confidence_score": p.confidence_score,
                        "confidence_level": p.confidence_level.value,
                        "trend_direction": p.trend_direction.value,
                        "time_horizon": p.time_horizon,
                        "impact_score": p.impact_score,
                        "risk_level": p.risk_level,
                        "recommendations": p.recommendations,
                        "created_at": p.created_at.isoformat(),
                        "expires_at": p.expires_at.isoformat()
                    }
                    for p in predictions
                ]
            }
            
        except Exception as e:
            logger.error(f"Prediction generation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def analyze_trends(
        self, 
        client_id: str, 
        organization_id: str,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze trends for client metrics"""
        try:
            if not metrics:
                metrics = list(self.trend_configs.keys())
            
            trend_analyses = []
            
            for metric in metrics:
                trend_analysis = await self._analyze_metric_trend(
                    client_id, metric
                )
                if trend_analysis:
                    trend_analyses.append(trend_analysis)
            
            # Store trend analyses
            if client_id not in self.trend_analyses:
                self.trend_analyses[client_id] = []
            self.trend_analyses[client_id].extend(trend_analyses)
            
            logger.info(f"Generated {len(trend_analyses)} trend analyses for client {client_id}")
            
            return {
                "success": True,
                "client_id": client_id,
                "trend_analyses": [
                    {
                        "trend_id": t.trend_id,
                        "metric_name": t.metric_name,
                        "current_trend": t.current_trend.value,
                        "trend_strength": t.trend_strength,
                        "historical_data": t.historical_data,
                        "predicted_data": t.predicted_data,
                        "key_insights": t.key_insights,
                        "anomalies": t.anomalies,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in trend_analyses
                ]
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_opportunity_alerts(
        self, 
        client_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Generate opportunity alerts for a client"""
        try:
            alerts = await self._generate_opportunity_alerts(client_id)
            
            # Store alerts
            if client_id not in self.opportunity_alerts:
                self.opportunity_alerts[client_id] = []
            self.opportunity_alerts[client_id].extend(alerts)
            
            logger.info(f"Generated {len(alerts)} opportunity alerts for client {client_id}")
            
            return {
                "success": True,
                "client_id": client_id,
                "alerts": [
                    {
                        "alert_id": a.alert_id,
                        "opportunity_type": a.opportunity_type,
                        "title": a.title,
                        "description": a.description,
                        "potential_value": a.potential_value,
                        "confidence_score": a.confidence_score,
                        "urgency_level": a.urgency_level,
                        "action_required": a.action_required,
                        "time_sensitivity": a.time_sensitivity,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in alerts
                ]
            }
            
        except Exception as e:
            logger.error(f"Opportunity alert generation failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def get_prediction_dashboard(
        self, 
        client_id: str, 
        organization_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive prediction dashboard data"""
        try:
            # Get all data for client
            predictions = self.predictions.get(client_id, [])
            trend_analyses = self.trend_analyses.get(client_id, [])
            opportunity_alerts = self.opportunity_alerts.get(client_id, [])
            
            # Calculate dashboard metrics
            dashboard_metrics = await self._calculate_dashboard_metrics(
                predictions, trend_analyses, opportunity_alerts
            )
            
            # Generate insights
            insights = await self._generate_insights(
                predictions, trend_analyses, opportunity_alerts
            )
            
            return {
                "success": True,
                "client_id": client_id,
                "dashboard_metrics": dashboard_metrics,
                "insights": insights,
                "predictions": [
                    {
                        "prediction_id": p.prediction_id,
                        "type": p.prediction_type.value,
                        "title": p.title,
                        "current_value": p.current_value,
                        "predicted_value": p.predicted_value,
                        "confidence_score": p.confidence_score,
                        "confidence_level": p.confidence_level.value,
                        "trend_direction": p.trend_direction.value,
                        "time_horizon": p.time_horizon,
                        "impact_score": p.impact_score,
                        "risk_level": p.risk_level,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in predictions
                ],
                "trend_analyses": [
                    {
                        "trend_id": t.trend_id,
                        "metric_name": t.metric_name,
                        "current_trend": t.current_trend.value,
                        "trend_strength": t.trend_strength,
                        "key_insights": t.key_insights,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in trend_analyses
                ],
                "opportunity_alerts": [
                    {
                        "alert_id": a.alert_id,
                        "opportunity_type": a.opportunity_type,
                        "title": a.title,
                        "potential_value": a.potential_value,
                        "confidence_score": a.confidence_score,
                        "urgency_level": a.urgency_level,
                        "time_sensitivity": a.time_sensitivity,
                        "created_at": a.created_at.isoformat()
                    }
                    for a in opportunity_alerts
                ]
            }
            
        except Exception as e:
            logger.error(f"Dashboard data retrieval failed: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _generate_prediction(
        self, 
        client_id: str, 
        prediction_type: PredictionType
    ) -> Optional[PredictionData]:
        """Generate a specific prediction"""
        try:
            template = self.prediction_templates[prediction_type]
            
            # Simulate prediction generation (in real implementation, this would use trained models)
            current_value = random.uniform(10, 100)
            predicted_value = current_value * random.uniform(0.8, 1.3)
            confidence_score = random.uniform(0.6, 0.95)
            
            # Determine confidence level
            if confidence_score >= 0.8:
                confidence_level = PredictionConfidence.HIGH
            elif confidence_score >= 0.6:
                confidence_level = PredictionConfidence.MEDIUM
            elif confidence_score >= 0.4:
                confidence_level = PredictionConfidence.LOW
            else:
                confidence_level = PredictionConfidence.VERY_LOW
            
            # Determine trend direction
            if predicted_value > current_value * 1.05:
                trend_direction = TrendDirection.RISING
            elif predicted_value < current_value * 0.95:
                trend_direction = TrendDirection.FALLING
            else:
                trend_direction = TrendDirection.STABLE
            
            prediction = PredictionData(
                prediction_id=str(uuid.uuid4()),
                prediction_type=prediction_type,
                title=template["title"],
                description=template["description"],
                current_value=current_value,
                predicted_value=predicted_value,
                confidence_score=confidence_score,
                confidence_level=confidence_level,
                trend_direction=trend_direction,
                time_horizon=template["time_horizon"],
                impact_score=template["impact_score"],
                risk_level=template["risk_level"],
                recommendations=template["recommendations"]
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction generation failed for {prediction_type}: {str(e)}")
            return None

    async def _analyze_metric_trend(
        self, 
        client_id: str, 
        metric: str
    ) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric"""
        try:
            config = self.trend_configs[metric]
            
            # Generate historical data (in real implementation, this would come from actual data)
            historical_data = []
            for i in range(30):
                base_value = random.uniform(50, 150)
                trend_factor = 1 + (i * 0.01)  # Slight upward trend
                noise = random.uniform(0.9, 1.1)
                historical_data.append(base_value * trend_factor * noise)
            
            # Generate predicted data
            predicted_data = []
            last_value = historical_data[-1]
            for i in range(14):  # Predict next 14 days
                trend_factor = 1 + (i * 0.005)  # Continue trend
                noise = random.uniform(0.95, 1.05)
                predicted_data.append(last_value * trend_factor * noise)
            
            # Calculate trend strength
            trend_strength = random.uniform(0.3, 0.9)
            
            # Determine current trend
            recent_values = historical_data[-7:]
            if np.mean(recent_values) > np.mean(historical_data[-14:-7]):
                current_trend = TrendDirection.RISING
            elif np.mean(recent_values) < np.mean(historical_data[-14:-7]):
                current_trend = TrendDirection.FALLING
            else:
                current_trend = TrendDirection.STABLE
            
            # Generate insights
            insights = [
                f"{config['name']} shows {current_trend.value} trend over the last 7 days",
                f"Trend strength: {trend_strength:.1%}",
                f"Predicted {config['name']} will {'increase' if current_trend == TrendDirection.RISING else 'decrease'} by {abs(predicted_data[-1] - historical_data[-1]):.1f} {config['unit']} in the next 14 days"
            ]
            
            # Generate anomalies
            anomalies = []
            if random.random() < 0.3:  # 30% chance of anomaly
                anomalies.append({
                    "date": (datetime.utcnow() - timedelta(days=random.randint(1, 7))).isoformat(),
                    "value": historical_data[-random.randint(1, 7)],
                    "description": f"Unusual spike in {config['name']} detected"
                })
            
            trend_analysis = TrendAnalysis(
                trend_id=str(uuid.uuid4()),
                metric_name=metric,
                current_trend=current_trend,
                trend_strength=trend_strength,
                historical_data=historical_data,
                predicted_data=predicted_data,
                key_insights=insights,
                anomalies=anomalies
            )
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Trend analysis failed for {metric}: {str(e)}")
            return None

    async def _generate_opportunity_alerts(self, client_id: str) -> List[OpportunityAlert]:
        """Generate opportunity alerts"""
        alerts = []
        
        # Generate various types of opportunity alerts
        opportunity_types = [
            {
                "type": "budget_reallocation",
                "title": "Budget Reallocation Opportunity",
                "description": "High-performing campaign has room for additional budget",
                "potential_value": random.uniform(500, 2000),
                "confidence_score": random.uniform(0.7, 0.9),
                "urgency_level": "medium",
                "action_required": "Increase budget allocation",
                "time_sensitivity": 48
            },
            {
                "type": "audience_expansion",
                "title": "Audience Expansion Opportunity",
                "description": "Lookalike audience shows high conversion potential",
                "potential_value": random.uniform(300, 1500),
                "confidence_score": random.uniform(0.6, 0.8),
                "urgency_level": "low",
                "action_required": "Test lookalike audience",
                "time_sensitivity": 72
            },
            {
                "type": "creative_optimization",
                "title": "Creative Optimization Opportunity",
                "description": "New creative format shows promising early results",
                "potential_value": random.uniform(200, 800),
                "confidence_score": random.uniform(0.5, 0.7),
                "urgency_level": "low",
                "action_required": "Scale creative testing",
                "time_sensitivity": 96
            },
            {
                "type": "competitor_gap",
                "title": "Competitor Gap Opportunity",
                "description": "Competitor reduced ad spend in your key market",
                "potential_value": random.uniform(1000, 3000),
                "confidence_score": random.uniform(0.8, 0.95),
                "urgency_level": "high",
                "action_required": "Increase market presence",
                "time_sensitivity": 24
            }
        ]
        
        # Select 2-3 random opportunities
        selected_opportunities = random.sample(opportunity_types, random.randint(2, 3))
        
        for opp in selected_opportunities:
            alert = OpportunityAlert(
                alert_id=str(uuid.uuid4()),
                opportunity_type=opp["type"],
                title=opp["title"],
                description=opp["description"],
                potential_value=opp["potential_value"],
                confidence_score=opp["confidence_score"],
                urgency_level=opp["urgency_level"],
                action_required=opp["action_required"],
                time_sensitivity=opp["time_sensitivity"]
            )
            alerts.append(alert)
        
        return alerts

    async def _calculate_dashboard_metrics(
        self, 
        predictions: List[PredictionData], 
        trend_analyses: List[TrendAnalysis], 
        opportunity_alerts: List[OpportunityAlert]
    ) -> Dict[str, Any]:
        """Calculate dashboard metrics"""
        metrics = {
            "total_predictions": len(predictions),
            "high_confidence_predictions": len([p for p in predictions if p.confidence_level == PredictionConfidence.HIGH]),
            "rising_trends": len([t for t in trend_analyses if t.current_trend == TrendDirection.RISING]),
            "total_opportunities": len(opportunity_alerts),
            "high_value_opportunities": len([a for a in opportunity_alerts if a.potential_value > 1000]),
            "urgent_alerts": len([a for a in opportunity_alerts if a.urgency_level in ["high", "critical"]]),
            "average_confidence": np.mean([p.confidence_score for p in predictions]) if predictions else 0,
            "total_potential_value": sum([a.potential_value for a in opportunity_alerts])
        }
        
        return metrics

    async def _generate_insights(
        self, 
        predictions: List[PredictionData], 
        trend_analyses: List[TrendAnalysis], 
        opportunity_alerts: List[OpportunityAlert]
    ) -> List[str]:
        """Generate insights from predictions and trends"""
        insights = []
        
        # Generate insights based on predictions
        if predictions:
            high_confidence_predictions = [p for p in predictions if p.confidence_level == PredictionConfidence.HIGH]
            if high_confidence_predictions:
                insights.append(f"You have {len(high_confidence_predictions)} high-confidence predictions that require immediate attention")
            
            rising_predictions = [p for p in predictions if p.trend_direction == TrendDirection.RISING]
            if rising_predictions:
                insights.append(f"{len(rising_predictions)} metrics are predicted to rise, indicating positive momentum")
        
        # Generate insights based on trends
        if trend_analyses:
            strong_trends = [t for t in trend_analyses if t.trend_strength > 0.7]
            if strong_trends:
                insights.append(f"{len(strong_trends)} metrics show strong trends that should be monitored closely")
        
        # Generate insights based on opportunities
        if opportunity_alerts:
            high_value_opportunities = [a for a in opportunity_alerts if a.potential_value > 1000]
            if high_value_opportunities:
                insights.append(f"You have {len(high_value_opportunities)} high-value opportunities worth ${sum([a.potential_value for a in high_value_opportunities]):,.0f}")
            
            urgent_opportunities = [a for a in opportunity_alerts if a.urgency_level in ["high", "critical"]]
            if urgent_opportunities:
                insights.append(f"{len(urgent_opportunities)} urgent opportunities require immediate action")
        
        return insights

# Global instance
predictive_dashboard = None

def get_predictive_dashboard(db: AsyncIOMotorDatabase) -> PredictiveIntelligenceDashboard:
    """Get or create predictive dashboard instance"""
    global predictive_dashboard
    if predictive_dashboard is None:
        predictive_dashboard = PredictiveIntelligenceDashboard(db)
    return predictive_dashboard
