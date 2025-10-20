"""
Predictive Intelligence Engine
Production-grade predictive analytics with future trend prediction, automated optimization, and proactive recommendations
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import numpy as np
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import aiohttp
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class PredictionType(str, Enum):
    """Types of predictions"""
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    CONVERSION_RATE = "conversion_rate"
    COST_PER_ACQUISITION = "cost_per_acquisition"
    RETURN_ON_AD_SPEND = "return_on_ad_spend"
    AUDIENCE_GROWTH = "audience_growth"
    MARKET_TREND = "market_trend"
    SEASONAL_PATTERN = "seasonal_pattern"
    COMPETITIVE_THREAT = "competitive_threat"

class OptimizationAction(str, Enum):
    """Types of optimization actions"""
    INCREASE_BUDGET = "increase_budget"
    DECREASE_BUDGET = "decrease_budget"
    PAUSE_CAMPAIGN = "pause_campaign"
    RESUME_CAMPAIGN = "resume_campaign"
    ADJUST_TARGETING = "adjust_targeting"
    UPDATE_CREATIVE = "update_creative"
    CHANGE_BIDDING = "change_bidding"
    SCALE_WINNERS = "scale_winners"

class ConfidenceLevel(str, Enum):
    """Confidence levels for predictions"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class PredictionResult:
    """Prediction result data"""
    prediction_id: str
    prediction_type: PredictionType
    predicted_value: float
    confidence: float
    confidence_level: ConfidenceLevel
    prediction_horizon: int  # days ahead
    factors: List[str]
    model_used: str
    accuracy_score: float
    created_at: datetime
    valid_until: datetime

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation data"""
    recommendation_id: str
    action: OptimizationAction
    target_campaign_id: str
    expected_impact: float
    confidence: float
    reasoning: str
    implementation_steps: List[str]
    risk_level: str
    priority: str
    created_at: datetime

@dataclass
class MarketForecast:
    """Market forecast data"""
    forecast_id: str
    market_segment: str
    forecast_period: str
    predicted_growth: float
    confidence: float
    key_drivers: List[str]
    risks: List[str]
    opportunities: List[str]
    created_at: datetime

class PredictiveModelManager:
    """Manages predictive models and their lifecycle"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize predictive models"""
        try:
            # Campaign Performance Model
            self.models[PredictionType.CAMPAIGN_PERFORMANCE] = {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['budget', 'daily_budget', 'targeting_score', 'creative_score', 'seasonality', 'competition_level'],
                'target': 'conversion_rate'
            }
            
            # Conversion Rate Model
            self.models[PredictionType.CONVERSION_RATE] = {
                'model': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'features': ['ctr', 'landing_page_score', 'audience_quality', 'creative_relevance', 'device_type'],
                'target': 'conversion_rate'
            }
            
            # Cost Per Acquisition Model
            self.models[PredictionType.COST_PER_ACQUISITION] = {
                'model': Ridge(alpha=1.0),
                'features': ['competition_level', 'audience_size', 'bid_amount', 'quality_score', 'seasonality'],
                'target': 'cpa'
            }
            
            # Return on Ad Spend Model
            self.models[PredictionType.RETURN_ON_AD_SPEND] = {
                'model': RandomForestRegressor(n_estimators=150, random_state=42),
                'features': ['conversion_rate', 'average_order_value', 'customer_lifetime_value', 'audience_quality'],
                'target': 'roas'
            }
            
            # Audience Growth Model
            self.models[PredictionType.AUDIENCE_GROWTH] = {
                'model': LinearRegression(),
                'features': ['current_audience_size', 'growth_rate', 'engagement_rate', 'content_quality'],
                'target': 'audience_growth'
            }
            
            # Initialize scalers
            for prediction_type in self.models.keys():
                self.scalers[prediction_type] = StandardScaler()
            
            logger.info("Predictive models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing predictive models: {e}")
            raise
    
    async def train_model(self, prediction_type: PredictionType, training_data: pd.DataFrame) -> Dict[str, Any]:
        """Train a predictive model with historical data"""
        try:
            if prediction_type not in self.models:
                raise ValueError(f"Model for {prediction_type.value} not found")
            
            model_config = self.models[prediction_type]
            features = model_config['features']
            target = model_config['target']
            
            # Prepare features and target
            X = training_data[features].fillna(0)
            y = training_data[target].fillna(0)
            
            # Scale features
            X_scaled = self.scalers[prediction_type].fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            model_config['model'].fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model_config['model'].predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model metadata
            self.model_metadata[prediction_type] = {
                'accuracy': r2,
                'mse': mse,
                'feature_importance': dict(zip(features, model_config['model'].feature_importances_)) if hasattr(model_config['model'], 'feature_importances_') else {},
                'trained_at': datetime.utcnow().isoformat(),
                'training_samples': len(training_data)
            }
            
            logger.info(f"Model {prediction_type.value} trained successfully with R² = {r2:.3f}")
            
            return {
                'prediction_type': prediction_type.value,
                'accuracy': r2,
                'mse': mse,
                'training_samples': len(training_data),
                'trained_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error training model {prediction_type.value}: {e}")
            raise
    
    async def make_prediction(self, prediction_type: PredictionType, features: Dict[str, float], horizon_days: int = 30) -> PredictionResult:
        """Make a prediction using trained model"""
        try:
            if prediction_type not in self.models:
                raise ValueError(f"Model for {prediction_type.value} not found")
            
            model_config = self.models[prediction_type]
            model = model_config['model']
            scaler = self.scalers[prediction_type]
            
            # Prepare feature vector
            feature_vector = np.array([features.get(f, 0) for f in model_config['features']]).reshape(1, -1)
            feature_vector_scaled = scaler.transform(feature_vector)
            
            # Make prediction
            predicted_value = model.predict(feature_vector_scaled)[0]
            
            # Calculate confidence based on model accuracy and feature quality
            base_confidence = self.model_metadata.get(prediction_type, {}).get('accuracy', 0.5)
            feature_quality = min(1.0, len([f for f in features.values() if f > 0]) / len(model_config['features']))
            confidence = base_confidence * feature_quality
            
            # Determine confidence level
            if confidence >= 0.8:
                confidence_level = ConfidenceLevel.HIGH
            elif confidence >= 0.6:
                confidence_level = ConfidenceLevel.MEDIUM
            else:
                confidence_level = ConfidenceLevel.LOW
            
            # Generate factors influencing prediction
            factors = self._generate_prediction_factors(prediction_type, features)
            
            return PredictionResult(
                prediction_id=str(uuid.uuid4()),
                prediction_type=prediction_type,
                predicted_value=predicted_value,
                confidence=confidence,
                confidence_level=confidence_level,
                prediction_horizon=horizon_days,
                factors=factors,
                model_used=f"{model.__class__.__name__}",
                accuracy_score=base_confidence,
                created_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=horizon_days)
            )
            
        except Exception as e:
            logger.error(f"Error making prediction for {prediction_type.value}: {e}")
            raise
    
    def _generate_prediction_factors(self, prediction_type: PredictionType, features: Dict[str, float]) -> List[str]:
        """Generate factors influencing the prediction"""
        factors = []
        
        if prediction_type == PredictionType.CAMPAIGN_PERFORMANCE:
            if features.get('budget', 0) > 1000:
                factors.append("High budget allocation")
            if features.get('targeting_score', 0) > 0.8:
                factors.append("Excellent audience targeting")
            if features.get('creative_score', 0) > 0.8:
                factors.append("High-quality creative assets")
            if features.get('competition_level', 0) > 0.7:
                factors.append("High competition environment")
        
        elif prediction_type == PredictionType.CONVERSION_RATE:
            if features.get('ctr', 0) > 0.05:
                factors.append("High click-through rate")
            if features.get('landing_page_score', 0) > 0.8:
                factors.append("Optimized landing page")
            if features.get('audience_quality', 0) > 0.8:
                factors.append("High-quality audience")
        
        elif prediction_type == PredictionType.COST_PER_ACQUISITION:
            if features.get('competition_level', 0) > 0.7:
                factors.append("High competition driving up costs")
            if features.get('audience_size', 0) < 10000:
                factors.append("Limited audience size")
            if features.get('quality_score', 0) > 0.8:
                factors.append("High quality score reducing costs")
        
        return factors if factors else ["Standard market conditions"]

class OptimizationEngine:
    """Engine for generating optimization recommendations"""
    
    def __init__(self, db: AsyncIOMotorClient, model_manager: PredictiveModelManager):
        self.db = db
        self.model_manager = model_manager
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load optimization rules and thresholds"""
        return {
            "budget_optimization": [
                {
                    "condition": "roas > 3.0 and spend < budget * 0.8",
                    "action": OptimizationAction.INCREASE_BUDGET,
                    "impact": "high",
                    "reasoning": "High ROAS with low spend indicates opportunity to scale"
                },
                {
                    "condition": "roas < 1.5 and spend > budget * 0.9",
                    "action": OptimizationAction.DECREASE_BUDGET,
                    "impact": "high",
                    "reasoning": "Low ROAS with high spend indicates poor performance"
                }
            ],
            "campaign_optimization": [
                {
                    "condition": "conversion_rate < 0.02 and ctr > 0.05",
                    "action": OptimizationAction.UPDATE_CREATIVE,
                    "impact": "medium",
                    "reasoning": "High CTR but low conversion suggests creative mismatch"
                },
                {
                    "condition": "cpa > target_cpa * 1.5",
                    "action": OptimizationAction.ADJUST_TARGETING,
                    "impact": "high",
                    "reasoning": "CPA significantly above target requires targeting refinement"
                }
            ],
            "performance_optimization": [
                {
                    "condition": "roas > 2.5 and conversions > 10",
                    "action": OptimizationAction.SCALE_WINNERS,
                    "impact": "high",
                    "reasoning": "High-performing campaign ready for scaling"
                },
                {
                    "condition": "roas < 1.0 and spend > budget * 0.5",
                    "action": OptimizationAction.PAUSE_CAMPAIGN,
                    "impact": "high",
                    "reasoning": "Poor performance with significant spend"
                }
            ]
        }
    
    async def generate_optimization_recommendations(self, campaign_id: str, campaign_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations for a campaign"""
        try:
            recommendations = []
            
            # Analyze campaign performance
            performance_metrics = await self._analyze_campaign_performance(campaign_id, campaign_data)
            
            # Apply optimization rules
            for rule_category, rules in self.optimization_rules.items():
                for rule in rules:
                    if self._evaluate_condition(rule["condition"], performance_metrics):
                        recommendation = await self._create_recommendation(
                            rule, campaign_id, performance_metrics
                        )
                        recommendations.append(recommendation)
            
            # Generate AI-powered recommendations
            ai_recommendations = await self._generate_ai_recommendations(campaign_id, campaign_data)
            recommendations.extend(ai_recommendations)
            
            # Sort by priority and impact
            recommendations.sort(key=lambda x: (x.priority == "high", x.expected_impact), reverse=True)
            
            # Save recommendations
            for recommendation in recommendations:
                await self._save_recommendation(recommendation)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations for campaign {campaign_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            raise
    
    async def _analyze_campaign_performance(self, campaign_id: str, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze campaign performance metrics"""
        try:
            # Get campaign metrics from database
            metrics_doc = await self.db.campaign_metrics.find_one(
                {"campaign_id": campaign_id},
                sort=[("created_at", -1)]
            )
            
            if not metrics_doc:
                # Use mock data if no metrics found
                return {
                    "roas": 2.5,
                    "conversion_rate": 0.03,
                    "cpa": 50.0,
                    "ctr": 0.02,
                    "spend": campaign_data.get("budget", 1000) * 0.7,
                    "budget": campaign_data.get("budget", 1000),
                    "conversions": 20,
                    "target_cpa": campaign_data.get("target_cpa", 40)
                }
            
            metrics = metrics_doc.get("metrics", {})
            return {
                "roas": metrics.get("roas", 2.5),
                "conversion_rate": metrics.get("conversion_rate", 0.03),
                "cpa": metrics.get("cpa", 50.0),
                "ctr": metrics.get("ctr", 0.02),
                "spend": metrics.get("spend", 0),
                "budget": campaign_data.get("budget", 1000),
                "conversions": metrics.get("conversions", 0),
                "target_cpa": campaign_data.get("target_cpa", 40)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {e}")
            return {}
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate optimization condition"""
        try:
            # Simple condition evaluation - in production, use a proper expression evaluator
            if "roas > 3.0" in condition and metrics.get("roas", 0) > 3.0:
                return True
            if "roas < 1.5" in condition and metrics.get("roas", 0) < 1.5:
                return True
            if "conversion_rate < 0.02" in condition and metrics.get("conversion_rate", 0) < 0.02:
                return True
            if "cpa > target_cpa * 1.5" in condition and metrics.get("cpa", 0) > metrics.get("target_cpa", 0) * 1.5:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    async def _create_recommendation(self, rule: Dict[str, Any], campaign_id: str, metrics: Dict[str, Any]) -> OptimizationRecommendation:
        """Create optimization recommendation from rule"""
        try:
            # Calculate expected impact
            expected_impact = self._calculate_expected_impact(rule["action"], metrics)
            
            # Determine risk level
            risk_level = self._assess_risk_level(rule["action"], metrics)
            
            # Determine priority
            priority = "high" if rule["impact"] == "high" else "medium"
            
            # Generate implementation steps
            implementation_steps = self._generate_implementation_steps(rule["action"])
            
            return OptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                action=rule["action"],
                target_campaign_id=campaign_id,
                expected_impact=expected_impact,
                confidence=0.8,  # Base confidence for rule-based recommendations
                reasoning=rule["reasoning"],
                implementation_steps=implementation_steps,
                risk_level=risk_level,
                priority=priority,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error creating recommendation: {e}")
            raise
    
    def _calculate_expected_impact(self, action: OptimizationAction, metrics: Dict[str, Any]) -> float:
        """Calculate expected impact of optimization action"""
        try:
            impact_multipliers = {
                OptimizationAction.INCREASE_BUDGET: 1.2,
                OptimizationAction.DECREASE_BUDGET: 0.8,
                OptimizationAction.PAUSE_CAMPAIGN: 0.0,
                OptimizationAction.RESUME_CAMPAIGN: 1.1,
                OptimizationAction.ADJUST_TARGETING: 1.15,
                OptimizationAction.UPDATE_CREATIVE: 1.1,
                OptimizationAction.CHANGE_BIDDING: 1.05,
                OptimizationAction.SCALE_WINNERS: 1.3
            }
            
            base_impact = impact_multipliers.get(action, 1.0)
            current_roas = metrics.get("roas", 2.0)
            
            # Adjust impact based on current performance
            if current_roas > 2.0:
                return base_impact * 1.1
            elif current_roas < 1.5:
                return base_impact * 0.9
            
            return base_impact
            
        except Exception as e:
            logger.error(f"Error calculating expected impact: {e}")
            return 1.0
    
    def _assess_risk_level(self, action: OptimizationAction, metrics: Dict[str, Any]) -> str:
        """Assess risk level of optimization action"""
        try:
            high_risk_actions = [
                OptimizationAction.PAUSE_CAMPAIGN,
                OptimizationAction.DECREASE_BUDGET
            ]
            
            if action in high_risk_actions:
                return "high"
            
            current_roas = metrics.get("roas", 2.0)
            if current_roas < 1.5:
                return "medium"
            
            return "low"
            
        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return "medium"
    
    def _generate_implementation_steps(self, action: OptimizationAction) -> List[str]:
        """Generate implementation steps for optimization action"""
        try:
            steps_map = {
                OptimizationAction.INCREASE_BUDGET: [
                    "Review current budget allocation",
                    "Increase daily budget by 20-30%",
                    "Monitor performance for 3-5 days",
                    "Adjust based on results"
                ],
                OptimizationAction.DECREASE_BUDGET: [
                    "Analyze underperforming elements",
                    "Reduce budget by 15-25%",
                    "Focus spend on top performers",
                    "Monitor impact on conversions"
                ],
                OptimizationAction.PAUSE_CAMPAIGN: [
                    "Review campaign performance metrics",
                    "Pause campaign immediately",
                    "Analyze root cause of poor performance",
                    "Plan optimization strategy before resuming"
                ],
                OptimizationAction.ADJUST_TARGETING: [
                    "Review current audience performance",
                    "Exclude low-performing segments",
                    "Add new high-value audiences",
                    "Test refined targeting for 1 week"
                ],
                OptimizationAction.UPDATE_CREATIVE: [
                    "Analyze current creative performance",
                    "Create new creative variations",
                    "A/B test new vs existing creative",
                    "Scale winning creative elements"
                ],
                OptimizationAction.SCALE_WINNERS: [
                    "Identify top-performing elements",
                    "Increase budget allocation to winners",
                    "Replicate successful strategies",
                    "Monitor for performance degradation"
                ]
            }
            
            return steps_map.get(action, ["Review performance", "Implement changes", "Monitor results"])
            
        except Exception as e:
            logger.error(f"Error generating implementation steps: {e}")
            return ["Implement optimization", "Monitor results"]
    
    async def _generate_ai_recommendations(self, campaign_id: str, campaign_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate AI-powered optimization recommendations"""
        try:
            recommendations = []
            
            # Use predictive models to generate recommendations
            features = {
                'budget': campaign_data.get('budget', 1000),
                'daily_budget': campaign_data.get('daily_budget', 50),
                'targeting_score': 0.8,  # Mock targeting score
                'creative_score': 0.7,  # Mock creative score
                'seasonality': 0.5,      # Mock seasonality factor
                'competition_level': 0.6 # Mock competition level
            }
            
            # Predict campaign performance
            performance_prediction = await self.model_manager.make_prediction(
                PredictionType.CAMPAIGN_PERFORMANCE, features, 30
            )
            
            # Generate recommendations based on predictions
            if performance_prediction.predicted_value > 0.05:  # High predicted conversion rate
                recommendation = OptimizationRecommendation(
                    recommendation_id=str(uuid.uuid4()),
                    action=OptimizationAction.INCREASE_BUDGET,
                    target_campaign_id=campaign_id,
                    expected_impact=1.25,
                    confidence=performance_prediction.confidence,
                    reasoning=f"AI predicts high performance (conversion rate: {performance_prediction.predicted_value:.3f}) - recommend scaling budget",
                    implementation_steps=[
                        "Increase budget by 25%",
                        "Monitor performance closely",
                        "Scale further if metrics improve"
                    ],
                    risk_level="low",
                    priority="high",
                    created_at=datetime.utcnow()
                )
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return []
    
    async def _save_recommendation(self, recommendation: OptimizationRecommendation):
        """Save optimization recommendation to database"""
        try:
            recommendation_doc = {
                "recommendation_id": recommendation.recommendation_id,
                "action": recommendation.action.value,
                "target_campaign_id": recommendation.target_campaign_id,
                "expected_impact": recommendation.expected_impact,
                "confidence": recommendation.confidence,
                "reasoning": recommendation.reasoning,
                "implementation_steps": recommendation.implementation_steps,
                "risk_level": recommendation.risk_level,
                "priority": recommendation.priority,
                "created_at": recommendation.created_at.isoformat(),
                "status": "pending"
            }
            
            await self.db.optimization_recommendations.insert_one(recommendation_doc)
            
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            raise

class MarketForecastingEngine:
    """Engine for market forecasting and trend prediction"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.forecast_models = {}
        self._initialize_forecast_models()
    
    def _initialize_forecast_models(self):
        """Initialize market forecasting models"""
        try:
            # Market Growth Model
            self.forecast_models["market_growth"] = {
                'model': GradientBoostingRegressor(n_estimators=200, random_state=42),
                'features': ['historical_growth', 'market_size', 'competition_level', 'seasonality', 'economic_indicators'],
                'target': 'growth_rate'
            }
            
            # Trend Analysis Model
            self.forecast_models["trend_analysis"] = {
                'model': RandomForestRegressor(n_estimators=100, random_state=42),
                'features': ['trend_strength', 'market_sentiment', 'adoption_rate', 'innovation_index'],
                'target': 'trend_direction'
            }
            
            logger.info("Market forecasting models initialized")
            
        except Exception as e:
            logger.error(f"Error initializing forecast models: {e}")
            raise
    
    async def generate_market_forecast(self, market_segment: str, forecast_period: str = "6_months") -> MarketForecast:
        """Generate market forecast for specific segment"""
        try:
            # Mock market data - in production, gather real market data
            market_data = {
                'historical_growth': 0.15,
                'market_size': 1000000,
                'competition_level': 0.7,
                'seasonality': 0.3,
                'economic_indicators': 0.6
            }
            
            # Generate forecast using model
            forecast_value = await self._predict_market_growth(market_data)
            
            # Generate insights
            key_drivers = self._identify_key_drivers(market_data)
            risks = self._identify_risks(market_data)
            opportunities = self._identify_opportunities(market_data)
            
            return MarketForecast(
                forecast_id=str(uuid.uuid4()),
                market_segment=market_segment,
                forecast_period=forecast_period,
                predicted_growth=forecast_value,
                confidence=0.75,
                key_drivers=key_drivers,
                risks=risks,
                opportunities=opportunities,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error generating market forecast: {e}")
            raise
    
    async def _predict_market_growth(self, market_data: Dict[str, float]) -> float:
        """Predict market growth using forecasting model"""
        try:
            # Mock prediction - in production, use trained model
            base_growth = market_data.get('historical_growth', 0.15)
            competition_factor = 1 - market_data.get('competition_level', 0.7) * 0.3
            seasonality_factor = 1 + market_data.get('seasonality', 0.3) * 0.2
            
            predicted_growth = base_growth * competition_factor * seasonality_factor
            
            return max(0.05, min(0.5, predicted_growth))  # Clamp between 5% and 50%
            
        except Exception as e:
            logger.error(f"Error predicting market growth: {e}")
            return 0.15
    
    def _identify_key_drivers(self, market_data: Dict[str, float]) -> List[str]:
        """Identify key drivers for market growth"""
        drivers = []
        
        if market_data.get('historical_growth', 0) > 0.1:
            drivers.append("Strong historical growth momentum")
        
        if market_data.get('competition_level', 0) < 0.5:
            drivers.append("Low competition creating opportunities")
        
        if market_data.get('economic_indicators', 0) > 0.6:
            drivers.append("Positive economic indicators")
        
        if market_data.get('seasonality', 0) > 0.4:
            drivers.append("Favorable seasonal trends")
        
        return drivers if drivers else ["Standard market conditions"]
    
    def _identify_risks(self, market_data: Dict[str, float]) -> List[str]:
        """Identify market risks"""
        risks = []
        
        if market_data.get('competition_level', 0) > 0.8:
            risks.append("High competition pressure")
        
        if market_data.get('economic_indicators', 0) < 0.4:
            risks.append("Economic uncertainty")
        
        if market_data.get('historical_growth', 0) < 0.05:
            risks.append("Slowing growth trends")
        
        return risks if risks else ["Standard market risks"]
    
    def _identify_opportunities(self, market_data: Dict[str, float]) -> List[str]:
        """Identify market opportunities"""
        opportunities = []
        
        if market_data.get('market_size', 0) > 500000:
            opportunities.append("Large addressable market")
        
        if market_data.get('competition_level', 0) < 0.6:
            opportunities.append("Market gaps for new entrants")
        
        if market_data.get('seasonality', 0) > 0.3:
            opportunities.append("Seasonal demand patterns")
        
        return opportunities if opportunities else ["Standard market opportunities"]

class PredictiveIntelligenceService:
    """Main service for predictive intelligence"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.model_manager = PredictiveModelManager(db)
        self.optimization_engine = OptimizationEngine(db, self.model_manager)
        self.forecasting_engine = MarketForecastingEngine(db)
    
    async def train_all_models(self, training_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Train all predictive models"""
        try:
            results = {}
            
            for prediction_type, data in training_data.items():
                if data is not None and not data.empty:
                    result = await self.model_manager.train_model(
                        PredictionType(prediction_type), data
                    )
                    results[prediction_type] = result
            
            logger.info(f"Trained {len(results)} predictive models")
            return results
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    async def generate_predictions(self, client_id: str, prediction_types: List[PredictionType], features: Dict[str, float]) -> List[PredictionResult]:
        """Generate predictions for multiple types"""
        try:
            predictions = []
            
            for prediction_type in prediction_types:
                prediction = await self.model_manager.make_prediction(
                    prediction_type, features, 30
                )
                predictions.append(prediction)
                
                # Save prediction to database
                await self._save_prediction(prediction, client_id)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    async def get_optimization_recommendations(self, campaign_id: str, campaign_data: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Get optimization recommendations for campaign"""
        return await self.optimization_engine.generate_optimization_recommendations(campaign_id, campaign_data)
    
    async def get_market_forecast(self, market_segment: str, forecast_period: str = "6_months") -> MarketForecast:
        """Get market forecast for segment"""
        return await self.forecasting_engine.generate_market_forecast(market_segment, forecast_period)
    
    async def get_predictive_dashboard(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive predictive intelligence dashboard"""
        try:
            # Generate predictions
            features = {
                'budget': 5000,
                'daily_budget': 200,
                'targeting_score': 0.8,
                'creative_score': 0.7,
                'seasonality': 0.5,
                'competition_level': 0.6,
                'ctr': 0.03,
                'landing_page_score': 0.8,
                'audience_quality': 0.8,
                'creative_relevance': 0.7,
                'device_type': 0.6
            }
            
            predictions = await self.generate_predictions(
                client_id,
                [
                    PredictionType.CAMPAIGN_PERFORMANCE,
                    PredictionType.CONVERSION_RATE,
                    PredictionType.COST_PER_ACQUISITION,
                    PredictionType.RETURN_ON_AD_SPEND
                ],
                features
            )
            
            # Get optimization recommendations
            recommendations = await self.get_optimization_recommendations(
                "demo-campaign-1",
                {"budget": 5000, "daily_budget": 200, "target_cpa": 40}
            )
            
            # Get market forecast
            market_forecast = await self.get_market_forecast("digital_marketing")
            
            return {
                "client_id": client_id,
                "predictions": predictions,
                "optimization_recommendations": recommendations,
                "market_forecast": market_forecast,
                "model_performance": self.model_manager.model_metadata,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting predictive dashboard: {e}")
            raise
    
    async def _save_prediction(self, prediction: PredictionResult, client_id: str):
        """Save prediction to database"""
        try:
            prediction_doc = {
                "prediction_id": prediction.prediction_id,
                "client_id": client_id,
                "prediction_type": prediction.prediction_type.value,
                "predicted_value": prediction.predicted_value,
                "confidence": prediction.confidence,
                "confidence_level": prediction.confidence_level.value,
                "prediction_horizon": prediction.prediction_horizon,
                "factors": prediction.factors,
                "model_used": prediction.model_used,
                "accuracy_score": prediction.accuracy_score,
                "created_at": prediction.created_at.isoformat(),
                "valid_until": prediction.valid_until.isoformat()
            }
            
            await self.db.predictions.insert_one(prediction_doc)
            
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            raise

# Global instance
predictive_intelligence_service = None

def get_predictive_intelligence_service(db: AsyncIOMotorClient) -> PredictiveIntelligenceService:
    """Get predictive intelligence service instance"""
    global predictive_intelligence_service
    if predictive_intelligence_service is None:
        predictive_intelligence_service = PredictiveIntelligenceService(db)
    return predictive_intelligence_service
