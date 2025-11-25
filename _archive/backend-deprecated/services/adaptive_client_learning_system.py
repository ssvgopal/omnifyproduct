"""
Adaptive Client Learning System
Builds intelligence to vary application of thought process depending on client preferences
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class ClientPersonalityType(Enum):
    """Client personality types based on decision-making patterns"""
    ANALYTICAL = "analytical"  # Data-driven, methodical
    INTUITIVE = "intuitive"    # Gut-feeling, quick decisions
    COLLABORATIVE = "collaborative"  # Team-oriented, consensus-driven
    AUTONOMOUS = "autonomous"  # Independent, self-directed
    CAUTIOUS = "cautious"     # Risk-averse, thorough
    AGGRESSIVE = "aggressive"  # Fast-moving, high-risk tolerance

class LearningStyle(Enum):
    """How clients prefer to receive information and make decisions"""
    VISUAL = "visual"         # Charts, graphs, dashboards
    NUMERICAL = "numerical"    # Numbers, metrics, KPIs
    NARRATIVE = "narrative"   # Stories, case studies, examples
    INTERACTIVE = "interactive" # Hands-on, trial-and-error
    EXPERT_GUIDED = "expert_guided" # Human expert recommendations

class CommunicationPreference(Enum):
    """Communication style preferences"""
    CONCISE = "concise"       # Brief, to-the-point
    DETAILED = "detailed"     # Comprehensive, thorough
    FREQUENT = "frequent"     # Regular updates
    ON_DEMAND = "on_demand"   # Only when requested
    PROACTIVE = "proactive"   # Anticipatory updates

@dataclass
class ClientBehaviorPattern:
    """Patterns observed in client behavior"""
    decision_speed: float  # 0-1, how quickly they make decisions
    risk_tolerance: float  # 0-1, willingness to take risks
    data_reliance: float   # 0-1, how much they rely on data
    collaboration_level: float  # 0-1, preference for team input
    autonomy_level: float  # 0-1, preference for independent action
    communication_frequency: float  # 0-1, how often they want updates
    detail_preference: float  # 0-1, preference for detailed vs concise info

@dataclass
class ClientLearningProfile:
    """Comprehensive client learning profile"""
    client_id: str
    personality_type: ClientPersonalityType
    learning_style: LearningStyle
    communication_preference: CommunicationPreference
    behavior_patterns: ClientBehaviorPattern
    confidence_level: float  # 0-1, confidence in AI recommendations
    adaptation_rate: float   # 0-1, how quickly they adapt to new approaches
    success_patterns: List[str]  # What has worked well for them
    failure_patterns: List[str]   # What hasn't worked
    preferences: Dict[str, Any]   # Custom preferences
    last_updated: datetime
    learning_score: float  # Overall learning effectiveness score

@dataclass
class AdaptiveRecommendation:
    """Recommendation tailored to client's learning profile"""
    recommendation_type: str
    content: str
    presentation_style: str
    confidence_level: float
    reasoning: str
    alternatives: List[str]
    expected_outcome: str
    risk_assessment: str
    follow_up_actions: List[str]

class AdaptiveClientLearningSystem:
    """Core adaptive learning system for client personalization"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client_profiles: Dict[str, ClientLearningProfile] = {}
        self.behavior_tracking: Dict[str, List[Dict]] = {}
        self.learning_models: Dict[str, Any] = {}
        
        # Learning configuration
        self.min_interactions_for_profile = 10
        self.profile_update_frequency = 7  # days
        self.learning_decay_factor = 0.95  # How much old patterns fade
        
        # Personality detection weights
        self.personality_weights = {
            'decision_speed': {'analytical': 0.3, 'intuitive': 0.8, 'cautious': 0.2, 'aggressive': 0.9},
            'risk_tolerance': {'cautious': 0.2, 'aggressive': 0.9, 'analytical': 0.4, 'autonomous': 0.7},
            'data_reliance': {'analytical': 0.9, 'intuitive': 0.3, 'collaborative': 0.6, 'autonomous': 0.5},
            'collaboration_level': {'collaborative': 0.9, 'autonomous': 0.2, 'analytical': 0.6, 'intuitive': 0.4}
        }
        
        # Learning style preferences
        self.learning_style_preferences = {
            'visual': ['charts', 'graphs', 'dashboards', 'infographics'],
            'numerical': ['metrics', 'kpis', 'numbers', 'statistics'],
            'narrative': ['stories', 'case_studies', 'examples', 'scenarios'],
            'interactive': ['hands_on', 'trial', 'experiment', 'demo'],
            'expert_guided': ['recommendations', 'expert_opinion', 'best_practices']
        }

    async def initialize_system(self):
        """Initialize the adaptive learning system"""
        try:
            # Load existing client profiles
            await self._load_client_profiles()
            
            # Initialize learning models
            await self._initialize_learning_models()
            
            logger.info("✅ Adaptive Client Learning System initialized", extra={
                "loaded_profiles": len(self.client_profiles),
                "tracking_clients": len(self.behavior_tracking)
            })
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Adaptive Client Learning System: {e}")
            raise

    async def _load_client_profiles(self):
        """Load existing client profiles from database"""
        try:
            profiles_collection = self.db.client_learning_profiles
            async for profile_doc in profiles_collection.find():
                profile = ClientLearningProfile(
                    client_id=profile_doc['client_id'],
                    personality_type=ClientPersonalityType(profile_doc['personality_type']),
                    learning_style=LearningStyle(profile_doc['learning_style']),
                    communication_preference=CommunicationPreference(profile_doc['communication_preference']),
                    behavior_patterns=ClientBehaviorPattern(**profile_doc['behavior_patterns']),
                    confidence_level=profile_doc['confidence_level'],
                    adaptation_rate=profile_doc['adaptation_rate'],
                    success_patterns=profile_doc['success_patterns'],
                    failure_patterns=profile_doc['failure_patterns'],
                    preferences=profile_doc['preferences'],
                    last_updated=profile_doc['last_updated'],
                    learning_score=profile_doc['learning_score']
                )
                self.client_profiles[profile.client_id] = profile
                
        except Exception as e:
            logger.error(f"Error loading client profiles: {e}")

    async def _initialize_learning_models(self):
        """Initialize machine learning models for pattern recognition"""
        # Placeholder for ML models - in production, these would be trained models
        self.learning_models = {
            'personality_classifier': None,  # Would classify personality type
            'preference_predictor': None,   # Would predict preferences
            'success_pattern_detector': None, # Would detect success patterns
            'risk_assessor': None           # Would assess risk tolerance
        }

    async def track_client_interaction(self, client_id: str, interaction_data: Dict[str, Any]):
        """Track client interaction for learning"""
        try:
            if client_id not in self.behavior_tracking:
                self.behavior_tracking[client_id] = []
            
            # Add timestamp and interaction data
            interaction_data['timestamp'] = datetime.utcnow()
            interaction_data['interaction_id'] = f"{client_id}_{len(self.behavior_tracking[client_id])}"
            
            self.behavior_tracking[client_id].append(interaction_data)
            
            # Update client profile if enough data
            if len(self.behavior_tracking[client_id]) >= self.min_interactions_for_profile:
                await self._update_client_profile(client_id)
            
            # Save to database
            await self._save_interaction_data(client_id, interaction_data)
            
            logger.info(f"Tracked interaction for client {client_id}", extra={
                "interaction_type": interaction_data.get('type', 'unknown'),
                "total_interactions": len(self.behavior_tracking[client_id])
            })
            
        except Exception as e:
            logger.error(f"Error tracking client interaction: {e}")

    async def _update_client_profile(self, client_id: str):
        """Update client profile based on tracked behavior"""
        try:
            interactions = self.behavior_tracking.get(client_id, [])
            if len(interactions) < self.min_interactions_for_profile:
                return
            
            # Analyze behavior patterns
            behavior_patterns = await self._analyze_behavior_patterns(interactions)
            
            # Determine personality type
            personality_type = await self._classify_personality(behavior_patterns)
            
            # Determine learning style
            learning_style = await self._classify_learning_style(interactions)
            
            # Determine communication preference
            communication_preference = await self._classify_communication_preference(interactions)
            
            # Calculate confidence and adaptation rates
            confidence_level = await self._calculate_confidence_level(interactions)
            adaptation_rate = await self._calculate_adaptation_rate(interactions)
            
            # Identify success and failure patterns
            success_patterns = await self._identify_success_patterns(interactions)
            failure_patterns = await self._identify_failure_patterns(interactions)
            
            # Calculate learning score
            learning_score = await self._calculate_learning_score(
                behavior_patterns, confidence_level, adaptation_rate
            )
            
            # Create or update profile
            profile = ClientLearningProfile(
                client_id=client_id,
                personality_type=personality_type,
                learning_style=learning_style,
                communication_preference=communication_preference,
                behavior_patterns=behavior_patterns,
                confidence_level=confidence_level,
                adaptation_rate=adaptation_rate,
                success_patterns=success_patterns,
                failure_patterns=failure_patterns,
                preferences={},  # Would be populated from interaction analysis
                last_updated=datetime.utcnow(),
                learning_score=learning_score
            )
            
            self.client_profiles[client_id] = profile
            
            # Save to database
            await self._save_client_profile(profile)
            
            logger.info(f"Updated client profile for {client_id}", extra={
                "personality_type": personality_type.value,
                "learning_style": learning_style.value,
                "learning_score": learning_score
            })
            
        except Exception as e:
            logger.error(f"Error updating client profile: {e}")

    async def _analyze_behavior_patterns(self, interactions: List[Dict]) -> ClientBehaviorPattern:
        """Analyze behavior patterns from interactions"""
        try:
            # Calculate decision speed (time between interaction and action)
            decision_times = []
            for i, interaction in enumerate(interactions):
                if 'action_taken' in interaction and 'timestamp' in interaction:
                    # Find next interaction with action
                    for j in range(i + 1, len(interactions)):
                        if 'action_taken' in interactions[j]:
                            time_diff = (interactions[j]['timestamp'] - interaction['timestamp']).total_seconds()
                            decision_times.append(time_diff)
                            break
            
            decision_speed = 1.0 - (np.mean(decision_times) / 3600) if decision_times else 0.5  # Normalize to hours
            
            # Calculate risk tolerance (based on action types)
            risk_actions = ['experiment', 'test_new_approach', 'increase_budget', 'try_new_platform']
            risk_count = sum(1 for interaction in interactions 
                           if any(action in str(interaction.get('action_taken', '')).lower() 
                                for action in risk_actions))
            risk_tolerance = min(risk_count / len(interactions), 1.0) if interactions else 0.5
            
            # Calculate data reliance (based on data requests)
            data_requests = sum(1 for interaction in interactions 
                               if 'data_request' in interaction or 'analytics' in str(interaction))
            data_reliance = min(data_requests / len(interactions), 1.0) if interactions else 0.5
            
            # Calculate collaboration level (based on team interactions)
            team_interactions = sum(1 for interaction in interactions 
                                  if 'team' in str(interaction) or 'collaboration' in str(interaction))
            collaboration_level = min(team_interactions / len(interactions), 1.0) if interactions else 0.5
            
            # Calculate autonomy level (based on independent actions)
            independent_actions = sum(1 for interaction in interactions 
                                    if 'independent' in str(interaction) or 'self_directed' in str(interaction))
            autonomy_level = min(independent_actions / len(interactions), 1.0) if interactions else 0.5
            
            # Calculate communication frequency
            communication_frequency = len(interactions) / 30  # Interactions per day over 30 days
            communication_frequency = min(communication_frequency, 1.0)
            
            # Calculate detail preference (based on information depth requests)
            detail_requests = sum(1 for interaction in interactions 
                                if 'detailed' in str(interaction) or 'comprehensive' in str(interaction))
            detail_preference = min(detail_requests / len(interactions), 1.0) if interactions else 0.5
            
            return ClientBehaviorPattern(
                decision_speed=decision_speed,
                risk_tolerance=risk_tolerance,
                data_reliance=data_reliance,
                collaboration_level=collaboration_level,
                autonomy_level=autonomy_level,
                communication_frequency=communication_frequency,
                detail_preference=detail_preference
            )
            
        except Exception as e:
            logger.error(f"Error analyzing behavior patterns: {e}")
            # Return default patterns
            return ClientBehaviorPattern(
                decision_speed=0.5,
                risk_tolerance=0.5,
                data_reliance=0.5,
                collaboration_level=0.5,
                autonomy_level=0.5,
                communication_frequency=0.5,
                detail_preference=0.5
            )

    async def _classify_personality(self, behavior_patterns: ClientBehaviorPattern) -> ClientPersonalityType:
        """Classify personality type based on behavior patterns"""
        try:
            scores = {}
            
            # Calculate scores for each personality type
            for personality in ClientPersonalityType:
                score = 0
                weights = self.personality_weights.get(personality.value, {})
                
                for pattern, weight in weights.items():
                    pattern_value = getattr(behavior_patterns, pattern, 0.5)
                    score += pattern_value * weight
                
                scores[personality] = score
            
            # Return personality with highest score
            return max(scores, key=scores.get)
            
        except Exception as e:
            logger.error(f"Error classifying personality: {e}")
            return ClientPersonalityType.ANALYTICAL  # Default

    async def _classify_learning_style(self, interactions: List[Dict]) -> LearningStyle:
        """Classify learning style based on interaction preferences"""
        try:
            style_scores = {style: 0 for style in LearningStyle}
            
            for interaction in interactions:
                content = str(interaction).lower()
                
                for style, keywords in self.learning_style_preferences.items():
                    for keyword in keywords:
                        if keyword in content:
                            style_scores[LearningStyle(style)] += 1
            
            # Return learning style with highest score
            return max(style_scores, key=style_scores.get)
            
        except Exception as e:
            logger.error(f"Error classifying learning style: {e}")
            return LearningStyle.VISUAL  # Default

    async def _classify_communication_preference(self, interactions: List[Dict]) -> CommunicationPreference:
        """Classify communication preference based on interaction patterns"""
        try:
            # Analyze communication patterns
            concise_interactions = sum(1 for interaction in interactions 
                                     if 'brief' in str(interaction) or 'quick' in str(interaction))
            detailed_interactions = sum(1 for interaction in interactions 
                                      if 'detailed' in str(interaction) or 'comprehensive' in str(interaction))
            frequent_interactions = len(interactions) > 20  # High frequency threshold
            
            if detailed_interactions > concise_interactions:
                return CommunicationPreference.DETAILED
            elif frequent_interactions:
                return CommunicationPreference.FREQUENT
            else:
                return CommunicationPreference.CONCISE
                
        except Exception as e:
            logger.error(f"Error classifying communication preference: {e}")
            return CommunicationPreference.CONCISE  # Default

    async def _calculate_confidence_level(self, interactions: List[Dict]) -> float:
        """Calculate confidence level in AI recommendations"""
        try:
            # Count interactions where client followed AI recommendations
            followed_recommendations = sum(1 for interaction in interactions 
                                         if interaction.get('followed_recommendation', False))
            
            total_recommendations = sum(1 for interaction in interactions 
                                      if 'recommendation' in interaction)
            
            if total_recommendations > 0:
                return followed_recommendations / total_recommendations
            else:
                return 0.5  # Default confidence
                
        except Exception as e:
            logger.error(f"Error calculating confidence level: {e}")
            return 0.5

    async def _calculate_adaptation_rate(self, interactions: List[Dict]) -> float:
        """Calculate how quickly client adapts to new approaches"""
        try:
            # Count successful adaptations
            adaptations = sum(1 for interaction in interactions 
                            if interaction.get('successful_adaptation', False))
            
            total_attempts = sum(1 for interaction in interactions 
                               if 'adaptation_attempt' in interaction)
            
            if total_attempts > 0:
                return adaptations / total_attempts
            else:
                return 0.5  # Default adaptation rate
                
        except Exception as e:
            logger.error(f"Error calculating adaptation rate: {e}")
            return 0.5

    async def _identify_success_patterns(self, interactions: List[Dict]) -> List[str]:
        """Identify patterns that led to success"""
        try:
            success_patterns = []
            
            for interaction in interactions:
                if interaction.get('outcome') == 'success':
                    # Extract patterns from successful interactions
                    if 'data_driven' in str(interaction):
                        success_patterns.append('data_driven_decisions')
                    if 'collaborative' in str(interaction):
                        success_patterns.append('collaborative_approach')
                    if 'experiment' in str(interaction):
                        success_patterns.append('experimental_approach')
                    if 'quick_action' in str(interaction):
                        success_patterns.append('quick_action')
            
            return list(set(success_patterns))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error identifying success patterns: {e}")
            return []

    async def _identify_failure_patterns(self, interactions: List[Dict]) -> List[str]:
        """Identify patterns that led to failure"""
        try:
            failure_patterns = []
            
            for interaction in interactions:
                if interaction.get('outcome') == 'failure':
                    # Extract patterns from failed interactions
                    if 'rushed' in str(interaction):
                        failure_patterns.append('rushed_decisions')
                    if 'no_data' in str(interaction):
                        failure_patterns.append('insufficient_data')
                    if 'ignored_recommendation' in str(interaction):
                        failure_patterns.append('ignored_recommendations')
            
            return list(set(failure_patterns))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error identifying failure patterns: {e}")
            return []

    async def _calculate_learning_score(self, behavior_patterns: ClientBehaviorPattern, 
                                      confidence_level: float, adaptation_rate: float) -> float:
        """Calculate overall learning effectiveness score"""
        try:
            # Weighted combination of different factors
            weights = {
                'confidence': 0.3,
                'adaptation_rate': 0.3,
                'data_reliance': 0.2,
                'collaboration_level': 0.1,
                'autonomy_level': 0.1
            }
            
            score = (
                confidence_level * weights['confidence'] +
                adaptation_rate * weights['adaptation_rate'] +
                behavior_patterns.data_reliance * weights['data_reliance'] +
                behavior_patterns.collaboration_level * weights['collaboration_level'] +
                behavior_patterns.autonomy_level * weights['autonomy_level']
            )
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating learning score: {e}")
            return 0.5

    async def get_client_profile(self, client_id: str) -> Optional[ClientLearningProfile]:
        """Get client learning profile"""
        return self.client_profiles.get(client_id)

    async def generate_adaptive_recommendation(self, client_id: str, context: Dict[str, Any]) -> AdaptiveRecommendation:
        """Generate recommendation tailored to client's learning profile"""
        try:
            profile = await self.get_client_profile(client_id)
            
            if not profile:
                # Generate default recommendation
                return await self._generate_default_recommendation(context)
            
            # Generate personalized recommendation based on profile
            recommendation_type = await self._determine_recommendation_type(profile, context)
            content = await self._generate_personalized_content(profile, context)
            presentation_style = await self._determine_presentation_style(profile)
            confidence_level = profile.confidence_level
            reasoning = await self._generate_reasoning(profile, context)
            alternatives = await self._generate_alternatives(profile, context)
            expected_outcome = await self._predict_outcome(profile, context)
            risk_assessment = await self._assess_risk(profile, context)
            follow_up_actions = await self._generate_follow_up_actions(profile, context)
            
            return AdaptiveRecommendation(
                recommendation_type=recommendation_type,
                content=content,
                presentation_style=presentation_style,
                confidence_level=confidence_level,
                reasoning=reasoning,
                alternatives=alternatives,
                expected_outcome=expected_outcome,
                risk_assessment=risk_assessment,
                follow_up_actions=follow_up_actions
            )
            
        except Exception as e:
            logger.error(f"Error generating adaptive recommendation: {e}")
            return await self._generate_default_recommendation(context)

    async def _generate_default_recommendation(self, context: Dict[str, Any]) -> AdaptiveRecommendation:
        """Generate default recommendation when no profile exists"""
        return AdaptiveRecommendation(
            recommendation_type="general",
            content="Based on your current situation, I recommend a data-driven approach with regular monitoring.",
            presentation_style="balanced",
            confidence_level=0.5,
            reasoning="This is a general recommendation based on best practices.",
            alternatives=["Conservative approach", "Aggressive approach"],
            expected_outcome="Moderate improvement with manageable risk",
            risk_assessment="Medium risk",
            follow_up_actions=["Monitor results", "Adjust strategy if needed"]
        )

    async def _determine_recommendation_type(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> str:
        """Determine recommendation type based on client profile"""
        if profile.personality_type == ClientPersonalityType.ANALYTICAL:
            return "data_driven"
        elif profile.personality_type == ClientPersonalityType.INTUITIVE:
            return "intuitive"
        elif profile.personality_type == ClientPersonalityType.COLLABORATIVE:
            return "collaborative"
        elif profile.personality_type == ClientPersonalityType.AUTONOMOUS:
            return "autonomous"
        elif profile.personality_type == ClientPersonalityType.CAUTIOUS:
            return "conservative"
        elif profile.personality_type == ClientPersonalityType.AGGRESSIVE:
            return "aggressive"
        else:
            return "balanced"

    async def _generate_personalized_content(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> str:
        """Generate personalized content based on learning style"""
        base_content = "Here's my recommendation for your situation:"
        
        if profile.learning_style == LearningStyle.VISUAL:
            return f"{base_content} I'll show you charts and graphs to illustrate the approach."
        elif profile.learning_style == LearningStyle.NUMERICAL:
            return f"{base_content} Here are the key metrics and KPIs to focus on."
        elif profile.learning_style == LearningStyle.NARRATIVE:
            return f"{base_content} Let me tell you about a similar situation and how it was resolved."
        elif profile.learning_style == LearningStyle.INTERACTIVE:
            return f"{base_content} Let's try this approach together and see how it works."
        elif profile.learning_style == LearningStyle.EXPERT_GUIDED:
            return f"{base_content} Based on expert analysis, here's the recommended approach."
        else:
            return f"{base_content} Here's a comprehensive approach tailored to your needs."

    async def _determine_presentation_style(self, profile: ClientLearningProfile) -> str:
        """Determine presentation style based on communication preference"""
        if profile.communication_preference == CommunicationPreference.CONCISE:
            return "brief"
        elif profile.communication_preference == CommunicationPreference.DETAILED:
            return "comprehensive"
        elif profile.communication_preference == CommunicationPreference.FREQUENT:
            return "regular_updates"
        elif profile.communication_preference == CommunicationPreference.ON_DEMAND:
            return "on_request"
        elif profile.communication_preference == CommunicationPreference.PROACTIVE:
            return "anticipatory"
        else:
            return "balanced"

    async def _generate_reasoning(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> str:
        """Generate reasoning based on client's data reliance"""
        if profile.behavior_patterns.data_reliance > 0.7:
            return "This recommendation is based on comprehensive data analysis and proven patterns."
        elif profile.behavior_patterns.data_reliance > 0.4:
            return "This recommendation combines data insights with industry best practices."
        else:
            return "This recommendation is based on industry experience and successful case studies."

    async def _generate_alternatives(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> List[str]:
        """Generate alternatives based on risk tolerance"""
        if profile.behavior_patterns.risk_tolerance > 0.7:
            return ["Aggressive approach", "Conservative approach", "Balanced approach"]
        elif profile.behavior_patterns.risk_tolerance > 0.4:
            return ["Conservative approach", "Balanced approach"]
        else:
            return ["Conservative approach", "Very conservative approach"]

    async def _predict_outcome(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> str:
        """Predict outcome based on success patterns"""
        if 'data_driven_decisions' in profile.success_patterns:
            return "High probability of success with data-driven approach"
        elif 'collaborative_approach' in profile.success_patterns:
            return "Good success probability with team collaboration"
        else:
            return "Moderate success probability with careful execution"

    async def _assess_risk(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> str:
        """Assess risk based on client's risk tolerance"""
        if profile.behavior_patterns.risk_tolerance > 0.7:
            return "Low risk - client comfortable with uncertainty"
        elif profile.behavior_patterns.risk_tolerance > 0.4:
            return "Medium risk - manageable uncertainty"
        else:
            return "High risk - client prefers certainty"

    async def _generate_follow_up_actions(self, profile: ClientLearningProfile, context: Dict[str, Any]) -> List[str]:
        """Generate follow-up actions based on communication preference"""
        base_actions = ["Monitor results", "Track KPIs"]
        
        if profile.communication_preference == CommunicationPreference.FREQUENT:
            base_actions.append("Daily check-ins")
        elif profile.communication_preference == CommunicationPreference.PROACTIVE:
            base_actions.append("Proactive updates")
        else:
            base_actions.append("Weekly review")
        
        return base_actions

    async def _save_client_profile(self, profile: ClientLearningProfile):
        """Save client profile to database"""
        try:
            profiles_collection = self.db.client_learning_profiles
            await profiles_collection.replace_one(
                {'client_id': profile.client_id},
                asdict(profile),
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error saving client profile: {e}")

    async def _save_interaction_data(self, client_id: str, interaction_data: Dict[str, Any]):
        """Save interaction data to database"""
        try:
            interactions_collection = self.db.client_interactions
            await interactions_collection.insert_one({
                'client_id': client_id,
                **interaction_data
            })
        except Exception as e:
            logger.error(f"Error saving interaction data: {e}")

    async def get_learning_insights(self, client_id: str) -> Dict[str, Any]:
        """Get learning insights for a client"""
        try:
            profile = await self.get_client_profile(client_id)
            interactions = self.behavior_tracking.get(client_id, [])
            
            if not profile:
                return {
                    "status": "insufficient_data",
                    "message": "Need more interactions to generate insights",
                    "required_interactions": self.min_interactions_for_profile - len(interactions)
                }
            
            return {
                "status": "success",
                "profile": asdict(profile),
                "total_interactions": len(interactions),
                "learning_progress": profile.learning_score,
                "recommendations": {
                    "personality_match": f"Tailor recommendations to {profile.personality_type.value} personality",
                    "learning_style": f"Present information in {profile.learning_style.value} format",
                    "communication": f"Use {profile.communication_preference.value} communication style",
                    "risk_level": f"Client prefers {profile.behavior_patterns.risk_tolerance:.1%} risk tolerance"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting learning insights: {e}")
            return {"status": "error", "message": str(e)}

    async def close(self):
        """Close the adaptive learning system"""
        try:
            # Save any pending data
            for client_id, profile in self.client_profiles.items():
                await self._save_client_profile(profile)
            
            logger.info("✅ Adaptive Client Learning System closed")
            
        except Exception as e:
            logger.error(f"Error closing Adaptive Client Learning System: {e}")

# Global instance
_adaptive_learning_system = None

async def get_adaptive_learning_system(db: AsyncIOMotorDatabase) -> AdaptiveClientLearningSystem:
    """Get or create adaptive learning system instance"""
    global _adaptive_learning_system
    if _adaptive_learning_system is None:
        _adaptive_learning_system = AdaptiveClientLearningSystem(db)
        await _adaptive_learning_system.initialize_system()
    return _adaptive_learning_system
