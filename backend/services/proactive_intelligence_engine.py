"""
Hybrid Proactive Intelligence Engine
Adaptive AI with human expert oversight for critical decisions
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ClientPreferenceLevel(Enum):
    """Client preference for automation vs human oversight"""
    FULLY_AUTONOMOUS = "fully_autonomous"  # AI handles everything
    GUIDED_AUTOMATION = "guided_automation"  # AI with human approval
    HUMAN_LED = "human_led"  # Human makes decisions, AI provides insights
    EXPERT_REQUIRED = "expert_required"  # Always requires expert intervention

class DecisionCriticality(Enum):
    """Criticality level for decision making"""
    LOW = "low"  # Routine optimizations
    MEDIUM = "medium"  # Campaign adjustments
    HIGH = "high"  # Budget reallocation
    CRITICAL = "critical"  # Strategic changes

class ActionType(Enum):
    """Types of proactive actions"""
    CREATIVE_FATIGUE_PREDICTION = "creative_fatigue_prediction"
    LTV_FORECASTING = "ltv_forecasting"
    CHURN_PREVENTION = "churn_prevention"
    BUDGET_OPTIMIZATION = "budget_optimization"
    BID_OPTIMIZATION = "bid_optimization"
    AUDIENCE_EXPANSION = "audience_expansion"
    CAMPAIGN_SCALING = "campaign_scaling"
    PERFORMANCE_ANOMALY_DETECTION = "performance_anomaly_detection"

@dataclass
class ClientProfile:
    """Client preference and behavior profile"""
    client_id: str
    organization_id: str
    preference_level: ClientPreferenceLevel = ClientPreferenceLevel.GUIDED_AUTOMATION
    risk_tolerance: float = 0.5  # 0.0 = conservative, 1.0 = aggressive
    learning_rate: float = 0.1  # How quickly to adapt to new patterns
    expert_preferences: Dict[str, Any] = field(default_factory=dict)
    historical_decisions: List[Dict[str, Any]] = field(default_factory=list)
    performance_patterns: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ProactiveAction:
    """Proactive action recommendation"""
    action_id: str
    action_type: ActionType
    client_id: str
    campaign_id: Optional[str]
    priority: int  # 1-10, higher = more urgent
    confidence: float  # 0.0-1.0
    expected_impact: float  # Expected improvement percentage
    risk_level: float  # 0.0-1.0
    requires_human_approval: bool
    human_expert_required: bool
    reasoning: str
    data_evidence: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

@dataclass
class ExpertIntervention:
    """Human expert intervention record"""
    intervention_id: str
    action_id: str
    expert_id: str
    decision: str  # "approved", "rejected", "modified"
    reasoning: str
    modifications: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

class ProactiveIntelligenceEngine:
    """
    Hybrid Proactive Intelligence Engine
    Combines AI predictions with human expert oversight
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client_profiles: Dict[str, ClientProfile] = {}
        self.active_actions: Dict[str, ProactiveAction] = {}
        self.expert_interventions: Dict[str, ExpertIntervention] = {}
        
        # AI Models
        self.fatigue_predictor = None
        self.ltv_predictor = None
        self.churn_predictor = None
        self.anomaly_detector = None
        
        # Configuration
        self.min_confidence_threshold = 0.7
        self.max_risk_threshold = 0.8
        self.learning_window_days = 30
        
        logger.info("Proactive Intelligence Engine initialized")

    async def initialize_models(self):
        """Initialize AI models for predictions"""
        try:
            # Load historical data for model training
            historical_data = await self._load_historical_data()
            
            if len(historical_data) > 100:  # Minimum data for training
                await self._train_fatigue_predictor(historical_data)
                await self._train_ltv_predictor(historical_data)
                await self._train_churn_predictor(historical_data)
                await self._train_anomaly_detector(historical_data)
                
                logger.info("AI models trained successfully")
            else:
                logger.warning("Insufficient historical data for model training")
                
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")

    async def analyze_client_preferences(self, client_id: str) -> ClientProfile:
        """Analyze and learn client preferences"""
        try:
            # Load client data
            client_data = await self._load_client_data(client_id)
            
            # Analyze decision patterns
            preference_level = await self._analyze_automation_preference(client_data)
            risk_tolerance = await self._calculate_risk_tolerance(client_data)
            learning_rate = await self._calculate_learning_rate(client_data)
            
            # Create or update client profile
            profile = ClientProfile(
                client_id=client_id,
                organization_id=client_data.get("organization_id", "default"),
                preference_level=preference_level,
                risk_tolerance=risk_tolerance,
                learning_rate=learning_rate,
                expert_preferences=client_data.get("expert_preferences", {}),
                historical_decisions=client_data.get("decisions", []),
                performance_patterns=client_data.get("patterns", {}),
                last_updated=datetime.utcnow()
            )
            
            self.client_profiles[client_id] = profile
            await self._save_client_profile(profile)
            
            logger.info(f"Client preferences analyzed for {client_id}", extra={
                "preference_level": preference_level.value,
                "risk_tolerance": risk_tolerance,
                "learning_rate": learning_rate
            })
            
            return profile
            
        except Exception as e:
            logger.error(f"Client preference analysis failed: {str(e)}")
            return ClientProfile(client_id=client_id, organization_id="default")

    async def generate_proactive_actions(self, client_id: str) -> List[ProactiveAction]:
        """Generate proactive actions based on client preferences and data"""
        try:
            profile = self.client_profiles.get(client_id)
            if not profile:
                profile = await self.analyze_client_preferences(client_id)
            
            actions = []
            
            # Generate actions based on client preference level
            if profile.preference_level in [ClientPreferenceLevel.FULLY_AUTONOMOUS, ClientPreferenceLevel.GUIDED_AUTOMATION]:
                actions.extend(await self._generate_autonomous_actions(client_id, profile))
            
            if profile.preference_level in [ClientPreferenceLevel.GUIDED_AUTOMATION, ClientPreferenceLevel.HUMAN_LED]:
                actions.extend(await self._generate_guided_actions(client_id, profile))
            
            if profile.preference_level in [ClientPreferenceLevel.HUMAN_LED, ClientPreferenceLevel.EXPERT_REQUIRED]:
                actions.extend(await self._generate_expert_actions(client_id, profile))
            
            # Filter actions based on confidence and risk
            filtered_actions = [
                action for action in actions
                if action.confidence >= self.min_confidence_threshold
                and action.risk_level <= self.max_risk_threshold
            ]
            
            # Store active actions
            for action in filtered_actions:
                self.active_actions[action.action_id] = action
            
            logger.info(f"Generated {len(filtered_actions)} proactive actions for {client_id}")
            return filtered_actions
            
        except Exception as e:
            logger.error(f"Proactive action generation failed: {str(e)}")
            return []

    async def _generate_autonomous_actions(self, client_id: str, profile: ClientProfile) -> List[ProactiveAction]:
        """Generate actions that can be executed autonomously"""
        actions = []
        
        # Creative fatigue prediction
        if self.fatigue_predictor:
            fatigue_prediction = await self._predict_creative_fatigue(client_id)
            if fatigue_prediction["confidence"] > 0.8:
                actions.append(ProactiveAction(
                    action_id=f"fatigue_{client_id}_{datetime.utcnow().timestamp()}",
                    action_type=ActionType.CREATIVE_FATIGUE_PREDICTION,
                    client_id=client_id,
                    campaign_id=fatigue_prediction.get("campaign_id"),
                    priority=fatigue_prediction["urgency"],
                    confidence=fatigue_prediction["confidence"],
                    expected_impact=fatigue_prediction["expected_improvement"],
                    risk_level=0.2,  # Low risk for creative refresh
                    requires_human_approval=False,
                    human_expert_required=False,
                    reasoning=fatigue_prediction["reasoning"],
                    data_evidence=fatigue_prediction["evidence"],
                    expires_at=datetime.utcnow() + timedelta(days=7)
                ))
        
        # Bid optimization
        bid_optimization = await self._optimize_bids(client_id, profile)
        if bid_optimization["confidence"] > 0.7:
            actions.append(ProactiveAction(
                action_id=f"bid_opt_{client_id}_{datetime.utcnow().timestamp()}",
                action_type=ActionType.BID_OPTIMIZATION,
                client_id=client_id,
                campaign_id=bid_optimization.get("campaign_id"),
                priority=bid_optimization["priority"],
                confidence=bid_optimization["confidence"],
                expected_impact=bid_optimization["expected_improvement"],
                risk_level=0.3,
                requires_human_approval=profile.risk_tolerance < 0.5,
                human_expert_required=False,
                reasoning=bid_optimization["reasoning"],
                data_evidence=bid_optimization["evidence"]
            ))
        
        return actions

    async def _generate_guided_actions(self, client_id: str, profile: ClientProfile) -> List[ProactiveAction]:
        """Generate actions that require human guidance"""
        actions = []
        
        # Budget optimization
        budget_optimization = await self._optimize_budget_allocation(client_id, profile)
        if budget_optimization["confidence"] > 0.6:
            actions.append(ProactiveAction(
                action_id=f"budget_opt_{client_id}_{datetime.utcnow().timestamp()}",
                action_type=ActionType.BUDGET_OPTIMIZATION,
                client_id=client_id,
                campaign_id=budget_optimization.get("campaign_id"),
                priority=budget_optimization["priority"],
                confidence=budget_optimization["confidence"],
                expected_impact=budget_optimization["expected_improvement"],
                risk_level=0.6,
                requires_human_approval=True,
                human_expert_required=False,
                reasoning=budget_optimization["reasoning"],
                data_evidence=budget_optimization["evidence"]
            ))
        
        # Campaign scaling
        scaling_recommendation = await self._recommend_campaign_scaling(client_id, profile)
        if scaling_recommendation["confidence"] > 0.6:
            actions.append(ProactiveAction(
                action_id=f"scaling_{client_id}_{datetime.utcnow().timestamp()}",
                action_type=ActionType.CAMPAIGN_SCALING,
                client_id=client_id,
                campaign_id=scaling_recommendation.get("campaign_id"),
                priority=scaling_recommendation["priority"],
                confidence=scaling_recommendation["confidence"],
                expected_impact=scaling_recommendation["expected_improvement"],
                risk_level=0.7,
                requires_human_approval=True,
                human_expert_required=False,
                reasoning=scaling_recommendation["reasoning"],
                data_evidence=scaling_recommendation["evidence"]
            ))
        
        return actions

    async def _generate_expert_actions(self, client_id: str, profile: ClientProfile) -> List[ProactiveAction]:
        """Generate actions that require expert intervention"""
        actions = []
        
        # LTV forecasting and churn prevention
        if self.ltv_predictor and self.churn_predictor:
            ltv_forecast = await self._forecast_ltv(client_id)
            churn_prediction = await self._predict_churn(client_id)
            
            if ltv_forecast["confidence"] > 0.5 or churn_prediction["confidence"] > 0.5:
                actions.append(ProactiveAction(
                    action_id=f"ltv_churn_{client_id}_{datetime.utcnow().timestamp()}",
                    action_type=ActionType.CHURN_PREVENTION,
                    client_id=client_id,
                    campaign_id=None,
                    priority=max(ltv_forecast.get("priority", 5), churn_prediction.get("priority", 5)),
                    confidence=max(ltv_forecast["confidence"], churn_prediction["confidence"]),
                    expected_impact=max(ltv_forecast.get("expected_improvement", 0), churn_prediction.get("expected_improvement", 0)),
                    risk_level=0.8,
                    requires_human_approval=True,
                    human_expert_required=True,
                    reasoning=f"LTV forecast: {ltv_forecast['reasoning']}. Churn risk: {churn_prediction['reasoning']}",
                    data_evidence={
                        "ltv_forecast": ltv_forecast["evidence"],
                        "churn_prediction": churn_prediction["evidence"]
                    }
                ))
        
        # Performance anomaly detection
        if self.anomaly_detector:
            anomalies = await self._detect_performance_anomalies(client_id)
            for anomaly in anomalies:
                if anomaly["confidence"] > 0.6:
                    actions.append(ProactiveAction(
                        action_id=f"anomaly_{client_id}_{datetime.utcnow().timestamp()}",
                        action_type=ActionType.PERFORMANCE_ANOMALY_DETECTION,
                        client_id=client_id,
                        campaign_id=anomaly.get("campaign_id"),
                        priority=anomaly["priority"],
                        confidence=anomaly["confidence"],
                        expected_impact=anomaly.get("expected_improvement", 0),
                        risk_level=0.9,
                        requires_human_approval=True,
                        human_expert_required=True,
                        reasoning=anomaly["reasoning"],
                        data_evidence=anomaly["evidence"]
                    ))
        
        return actions

    async def execute_action(self, action_id: str, expert_decision: Optional[ExpertIntervention] = None) -> Dict[str, Any]:
        """Execute a proactive action with optional expert intervention"""
        try:
            action = self.active_actions.get(action_id)
            if not action:
                raise ValueError(f"Action {action_id} not found")
            
            # Apply expert modifications if provided
            if expert_decision:
                action = await self._apply_expert_modifications(action, expert_decision)
                self.expert_interventions[expert_decision.intervention_id] = expert_decision
            
            # Execute based on action type
            result = await self._execute_action_by_type(action)
            
            # Update client profile with decision outcome
            await self._update_client_profile_from_action(action, result)
            
            # Remove from active actions
            del self.active_actions[action_id]
            
            logger.info(f"Action {action_id} executed successfully", extra={
                "action_type": action.action_type.value,
                "client_id": action.client_id,
                "expert_intervention": expert_decision is not None
            })
            
            return {
                "success": True,
                "action_id": action_id,
                "result": result,
                "expert_intervention": expert_decision.dict() if expert_decision else None
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {str(e)}")
            return {
                "success": False,
                "action_id": action_id,
                "error": str(e)
            }

    async def get_client_insights(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive insights for a client"""
        try:
            profile = self.client_profiles.get(client_id)
            if not profile:
                profile = await self.analyze_client_preferences(client_id)
            
            # Get active actions
            active_actions = [action for action in self.active_actions.values() if action.client_id == client_id]
            
            # Get recent interventions
            recent_interventions = [
                intervention for intervention in self.expert_interventions.values()
                if any(action.client_id == client_id for action in self.active_actions.values() if action.action_id == intervention.action_id)
            ]
            
            # Generate insights
            insights = {
                "client_profile": {
                    "preference_level": profile.preference_level.value,
                    "risk_tolerance": profile.risk_tolerance,
                    "learning_rate": profile.learning_rate,
                    "last_updated": profile.last_updated.isoformat()
                },
                "active_actions": len(active_actions),
                "pending_approvals": len([a for a in active_actions if a.requires_human_approval]),
                "expert_required": len([a for a in active_actions if a.human_expert_required]),
                "recent_interventions": len(recent_interventions),
                "recommendations": await self._generate_client_recommendations(client_id, profile)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Client insights generation failed: {str(e)}")
            return {"error": str(e)}

    # Helper methods for data loading and model training
    async def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Load historical campaign and performance data"""
        try:
            # This would load from MongoDB collections
            campaigns = await self.db.campaigns.find({}).to_list(length=1000)
            performance_data = await self.db.performance_metrics.find({}).to_list(length=1000)
            
            # Combine and structure data
            historical_data = []
            for campaign in campaigns:
                campaign_performance = [
                    p for p in performance_data 
                    if p.get("campaign_id") == campaign["_id"]
                ]
                
                historical_data.append({
                    "campaign_id": str(campaign["_id"]),
                    "client_id": campaign.get("client_id"),
                    "campaign_data": campaign,
                    "performance_data": campaign_performance
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Historical data loading failed: {str(e)}")
            return []

    async def _load_client_data(self, client_id: str) -> Dict[str, Any]:
        """Load client-specific data"""
        try:
            client = await self.db.clients.find_one({"client_id": client_id})
            campaigns = await self.db.campaigns.find({"client_id": client_id}).to_list(length=100)
            decisions = await self.db.client_decisions.find({"client_id": client_id}).to_list(length=100)
            
            return {
                "client": client or {},
                "campaigns": campaigns,
                "decisions": decisions,
                "organization_id": client.get("organization_id", "default") if client else "default"
            }
            
        except Exception as e:
            logger.error(f"Client data loading failed: {str(e)}")
            return {}

    async def _save_client_profile(self, profile: ClientProfile):
        """Save client profile to database"""
        try:
            await self.db.client_profiles.update_one(
                {"client_id": profile.client_id},
                {"$set": profile.__dict__},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Client profile saving failed: {str(e)}")

    # Placeholder methods for AI model training and predictions
    async def _train_fatigue_predictor(self, data: List[Dict[str, Any]]):
        """Train creative fatigue prediction model"""
        # Implementation would use historical creative performance data
        self.fatigue_predictor = "trained_model"  # Placeholder
        logger.info("Creative fatigue predictor trained")

    async def _train_ltv_predictor(self, data: List[Dict[str, Any]]):
        """Train LTV prediction model"""
        self.ltv_predictor = "trained_model"  # Placeholder
        logger.info("LTV predictor trained")

    async def _train_churn_predictor(self, data: List[Dict[str, Any]]):
        """Train churn prediction model"""
        self.churn_predictor = "trained_model"  # Placeholder
        logger.info("Churn predictor trained")

    async def _train_anomaly_detector(self, data: List[Dict[str, Any]]):
        """Train performance anomaly detection model"""
        self.anomaly_detector = "trained_model"  # Placeholder
        logger.info("Anomaly detector trained")

    # Placeholder methods for specific predictions and optimizations
    async def _predict_creative_fatigue(self, client_id: str) -> Dict[str, Any]:
        """Predict creative fatigue for client campaigns"""
        return {
            "confidence": 0.85,
            "urgency": 7,
            "expected_improvement": 15.0,
            "reasoning": "Creative performance declining over 7 days",
            "evidence": {"ctr_trend": -0.12, "days_active": 7},
            "campaign_id": "campaign_123"
        }

    async def _optimize_bids(self, client_id: str, profile: ClientProfile) -> Dict[str, Any]:
        """Optimize bids for client campaigns"""
        return {
            "confidence": 0.78,
            "priority": 6,
            "expected_improvement": 12.0,
            "reasoning": "Bid adjustments can improve ROAS by 12%",
            "evidence": {"current_roas": 3.2, "optimized_roas": 3.6},
            "campaign_id": "campaign_456"
        }

    async def _optimize_budget_allocation(self, client_id: str, profile: ClientProfile) -> Dict[str, Any]:
        """Optimize budget allocation across campaigns"""
        return {
            "confidence": 0.72,
            "priority": 8,
            "expected_improvement": 18.0,
            "reasoning": "Reallocating budget to high-performing campaigns",
            "evidence": {"current_allocation": "suboptimal", "recommended_allocation": "optimized"}
        }

    async def _recommend_campaign_scaling(self, client_id: str, profile: ClientProfile) -> Dict[str, Any]:
        """Recommend campaign scaling opportunities"""
        return {
            "confidence": 0.68,
            "priority": 7,
            "expected_improvement": 25.0,
            "reasoning": "Campaign performing well, ready for scaling",
            "evidence": {"performance_score": 8.5, "scaling_potential": "high"}
        }

    async def _forecast_ltv(self, client_id: str) -> Dict[str, Any]:
        """Forecast customer lifetime value"""
        return {
            "confidence": 0.65,
            "priority": 9,
            "expected_improvement": 30.0,
            "reasoning": "LTV forecast indicates growth opportunity",
            "evidence": {"current_ltv": 150, "forecasted_ltv": 195}
        }

    async def _predict_churn(self, client_id: str) -> Dict[str, Any]:
        """Predict customer churn risk"""
        return {
            "confidence": 0.70,
            "priority": 10,
            "expected_improvement": 40.0,
            "reasoning": "High churn risk detected, intervention needed",
            "evidence": {"churn_probability": 0.75, "risk_factors": ["engagement_decline", "support_tickets"]}
        }

    async def _detect_performance_anomalies(self, client_id: str) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        return [{
            "confidence": 0.80,
            "priority": 9,
            "expected_improvement": 20.0,
            "reasoning": "Unusual performance drop detected",
            "evidence": {"anomaly_score": 0.85, "affected_metrics": ["ctr", "conversion_rate"]},
            "campaign_id": "campaign_789"
        }]

    async def _apply_expert_modifications(self, action: ProactiveAction, expert_decision: ExpertIntervention) -> ProactiveAction:
        """Apply expert modifications to action"""
        if expert_decision.modifications:
            # Apply modifications to action parameters
            for key, value in expert_decision.modifications.items():
                if hasattr(action, key):
                    setattr(action, key, value)
        
        return action

    async def _execute_action_by_type(self, action: ProactiveAction) -> Dict[str, Any]:
        """Execute action based on its type"""
        # This would integrate with platform APIs and execute the actual action
        return {
            "executed": True,
            "action_type": action.action_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "result": "Action executed successfully"
        }

    async def _update_client_profile_from_action(self, action: ProactiveAction, result: Dict[str, Any]):
        """Update client profile based on action outcome"""
        profile = self.client_profiles.get(action.client_id)
        if profile:
            profile.historical_decisions.append({
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            })
            profile.last_updated = datetime.utcnow()

    async def _generate_client_recommendations(self, client_id: str, profile: ClientProfile) -> List[str]:
        """Generate personalized recommendations for client"""
        recommendations = []
        
        if profile.preference_level == ClientPreferenceLevel.FULLY_AUTONOMOUS:
            recommendations.append("Consider enabling more autonomous optimizations")
        elif profile.preference_level == ClientPreferenceLevel.EXPERT_REQUIRED:
            recommendations.append("Schedule expert consultation for strategic decisions")
        
        if profile.risk_tolerance < 0.3:
            recommendations.append("Conservative approach detected - consider gradual optimization")
        elif profile.risk_tolerance > 0.7:
            recommendations.append("Aggressive approach - monitor for over-optimization")
        
        return recommendations

    async def _analyze_automation_preference(self, client_data: Dict[str, Any]) -> ClientPreferenceLevel:
        """Analyze client's automation preference from historical data"""
        decisions = client_data.get("decisions", [])
        
        if not decisions:
            return ClientPreferenceLevel.GUIDED_AUTOMATION
        
        # Analyze decision patterns
        autonomous_decisions = len([d for d in decisions if d.get("automated", False)])
        total_decisions = len(decisions)
        
        automation_ratio = autonomous_decisions / total_decisions if total_decisions > 0 else 0
        
        if automation_ratio > 0.8:
            return ClientPreferenceLevel.FULLY_AUTONOMOUS
        elif automation_ratio > 0.5:
            return ClientPreferenceLevel.GUIDED_AUTOMATION
        elif automation_ratio > 0.2:
            return ClientPreferenceLevel.HUMAN_LED
        else:
            return ClientPreferenceLevel.EXPERT_REQUIRED

    async def _calculate_risk_tolerance(self, client_data: Dict[str, Any]) -> float:
        """Calculate client's risk tolerance from historical decisions"""
        decisions = client_data.get("decisions", [])
        
        if not decisions:
            return 0.5  # Default moderate risk tolerance
        
        # Analyze risk-taking patterns
        high_risk_decisions = len([d for d in decisions if d.get("risk_level", 0) > 0.7])
        total_decisions = len(decisions)
        
        return high_risk_decisions / total_decisions if total_decisions > 0 else 0.5

    async def _calculate_learning_rate(self, client_data: Dict[str, Any]) -> float:
        """Calculate client's learning rate from decision patterns"""
        decisions = client_data.get("decisions", [])
        
        if len(decisions) < 2:
            return 0.1  # Default learning rate
        
        # Analyze how quickly client adapts to new patterns
        recent_decisions = sorted(decisions, key=lambda x: x.get("timestamp", ""))[-10:]
        
        # Simple heuristic: more recent decisions = higher learning rate
        return min(0.3, len(recent_decisions) * 0.03)

# Global instance
proactive_intelligence_engine = None

def get_proactive_intelligence_engine(db: AsyncIOMotorDatabase) -> ProactiveIntelligenceEngine:
    """Get or create proactive intelligence engine instance"""
    global proactive_intelligence_engine
    if proactive_intelligence_engine is None:
        proactive_intelligence_engine = ProactiveIntelligenceEngine(db)
    return proactive_intelligence_engine
