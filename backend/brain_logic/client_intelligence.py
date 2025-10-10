from typing import Dict, Any, List
from datetime import datetime
import logging
import uuid
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class ClientIntelligence:
    """Client Intelligence Module for behavior analysis and success prediction"""
    
    def __init__(self):
        self.client_profiles = {}
        self.behavior_data = {}
        self._ai_api_key = None
        self._ai_available = None
    
    @property
    def ai_api_key(self):
        if self._ai_api_key is None:
            self._ai_api_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('OPENAI_API_KEY')
        return self._ai_api_key
    
    @property
    def ai_available(self):
        if self._ai_available is None:
            self._ai_available = self.ai_api_key is not None
        return self._ai_available
    
    def _get_llm_chat(self, system_message: str):
        """Get LLM chat instance"""
        if not self.ai_available:
            return None
        return LlmChat(
            api_key=self.ai_api_key,
            session_id=f"client_{uuid.uuid4()}",
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
    
    def _calculate_engagement_score(self, behavior_data: Dict[Any, Any]) -> float:
        """Calculate engagement score from behavior data"""
        score = 50.0  # Base score
        
        # Login frequency (max +15)
        logins = behavior_data.get('login_count', 0)
        score += min(logins / 2, 15)
        
        # Feature usage (max +20)
        features_used = len(behavior_data.get('features_used', []))
        score += min(features_used * 2, 20)
        
        # Session duration (max +10)
        avg_session = behavior_data.get('avg_session_minutes', 0)
        score += min(avg_session / 3, 10)
        
        # Support interactions (can be negative)
        support_tickets = behavior_data.get('support_tickets', 0)
        if support_tickets > 5:
            score -= (support_tickets - 5) * 2
        
        return min(max(score, 0), 100)  # Clamp between 0-100
        
    async def analyze_behavior(self, client_id: str, behavior_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Analyze client behavior patterns with real algorithms"""
        analysis_id = str(uuid.uuid4())
        
        # Store behavior data
        if client_id not in self.behavior_data:
            self.behavior_data[client_id] = []
        self.behavior_data[client_id].append({
            'data': behavior_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Calculate real metrics
        engagement_score = self._calculate_engagement_score(behavior_data)
        
        # Determine engagement level
        if engagement_score >= 80:
            engagement_level = 'very_high'
        elif engagement_score >= 60:
            engagement_level = 'high'
        elif engagement_score >= 40:
            engagement_level = 'medium'
        else:
            engagement_level = 'low'
        
        # Analyze frequency
        login_count = behavior_data.get('login_count', 0)
        days_active = behavior_data.get('days_active', 1)
        frequency = login_count / max(days_active, 1)
        
        if frequency >= 0.8:
            frequency_level = 'daily'
        elif frequency >= 0.4:
            frequency_level = 'regular'
        elif frequency >= 0.1:
            frequency_level = 'occasional'
        else:
            frequency_level = 'rare'
        
        # Analyze feature preferences
        features_used = behavior_data.get('features_used', [])
        feature_usage = behavior_data.get('feature_usage_count', {})
        preferred_features = sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        preferred_features = [f[0] for f in preferred_features] if preferred_features else features_used[:3]
        
        # Determine usage trend
        historical_data = self.behavior_data.get(client_id, [])
        if len(historical_data) >= 2:
            recent_logins = historical_data[-1]['data'].get('login_count', 0)
            previous_logins = historical_data[-2]['data'].get('login_count', 0)
            if recent_logins > previous_logins * 1.2:
                usage_trend = 'rapidly_increasing'
            elif recent_logins > previous_logins:
                usage_trend = 'increasing'
            elif recent_logins < previous_logins * 0.8:
                usage_trend = 'declining'
            else:
                usage_trend = 'stable'
        else:
            usage_trend = 'new_user'
        
        # Generate insights
        insights = []
        if engagement_score >= 70:
            insights.append(f'Client shows {engagement_level.replace("_", " ")} engagement (score: {engagement_score:.0f}/100)')
        if frequency_level in ['daily', 'regular']:
            insights.append(f'{frequency_level.capitalize()} usage pattern indicates strong adoption')
        if preferred_features:
            insights.append(f'Primary focus on: {", ".join(preferred_features[:3])}')
        if usage_trend == 'rapidly_increasing':
            insights.append('Usage is accelerating - strong growth signal')
        
        # Identify risk factors
        risk_factors = []
        if engagement_score < 40:
            risk_factors.append('Low engagement - churn risk')
        if usage_trend == 'declining':
            risk_factors.append('Declining usage pattern detected')
        if behavior_data.get('support_tickets', 0) > 5:
            risk_factors.append('High support ticket volume')
        if frequency_level == 'rare':
            risk_factors.append('Infrequent platform usage')
        
        # Identify opportunities
        opportunities = []
        if engagement_score >= 75 and not risk_factors:
            opportunities.append('Strong candidate for upsell to premium features')
            opportunities.append('Potential case study or testimonial')
        if len(preferred_features) < 3:
            opportunities.append('Opportunity to introduce additional features')
        if usage_trend in ['increasing', 'rapidly_increasing']:
            opportunities.append('Growing adoption - good timing for expansion')
        
        analysis = {
            'id': analysis_id,
            'client_id': client_id,
            'engagement_score': round(engagement_score, 1),
            'behavior_patterns': {
                'engagement_level': engagement_level,
                'frequency': frequency_level,
                'frequency_rate': round(frequency, 2),
                'preferred_features': preferred_features,
                'usage_trends': usage_trend,
                'total_sessions': login_count,
                'days_active': days_active
            },
            'insights': insights if insights else ['Insufficient data for detailed insights'],
            'risk_factors': risk_factors,
            'opportunities': opportunities if opportunities else ['Continue monitoring behavior patterns'],
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'analysis_type': 'algorithmic'
        }
        
        return analysis
    
    async def predict_success(self, client_id: str) -> Dict[Any, Any]:
        """Predict client success likelihood with real predictive algorithms"""
        prediction_id = str(uuid.uuid4())
        
        # Get client data
        client_behaviors = self.behavior_data.get(client_id, [])
        
        if not client_behaviors:
            return {
                'id': prediction_id,
                'client_id': client_id,
                'success_score': 50,
                'success_likelihood': 'unknown',
                'note': 'Insufficient behavior data for prediction',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Get latest behavior data
        latest_behavior = client_behaviors[-1]['data']
        
        # Calculate individual factor scores
        
        # 1. Engagement Score (weight: 0.3)
        engagement_score = self._calculate_engagement_score(latest_behavior)
        
        # 2. Adoption Rate Score (weight: 0.3)
        features_available = 10  # Assume 10 main features
        features_used = len(latest_behavior.get('features_used', []))
        adoption_rate = (features_used / features_available) * 100
        adoption_score = min(adoption_rate * 1.2, 100)  # Boost for early adopters
        
        # 3. Satisfaction Score (weight: 0.2)
        nps_score = latest_behavior.get('nps_score', 7)
        satisfaction_score = (nps_score / 10) * 100
        support_tickets = latest_behavior.get('support_tickets', 0)
        if support_tickets > 3:
            satisfaction_score -= support_tickets * 3  # Penalty for high support needs
        satisfaction_score = max(satisfaction_score, 0)
        
        # 4. Activity Consistency Score (weight: 0.2)
        days_active = latest_behavior.get('days_active', 0)
        account_age = latest_behavior.get('account_age_days', 30)
        consistency_rate = (days_active / account_age) if account_age > 0 else 0
        consistency_score = consistency_rate * 100
        
        # Calculate weighted success score
        weights = {
            'engagement': 0.3,
            'adoption_rate': 0.3,
            'satisfaction': 0.2,
            'consistency': 0.2
        }
        
        success_score = (
            engagement_score * weights['engagement'] +
            adoption_score * weights['adoption_rate'] +
            satisfaction_score * weights['satisfaction'] +
            consistency_score * weights['consistency']
        )
        
        # Determine likelihood
        if success_score >= 80:
            likelihood = 'very_high'
            timeline = '60 days'
        elif success_score >= 65:
            likelihood = 'high'
            timeline = '90 days'
        elif success_score >= 50:
            likelihood = 'moderate'
            timeline = '120 days'
        elif success_score >= 35:
            likelihood = 'low'
            timeline = '180 days'
        else:
            likelihood = 'very_low'
            timeline = '180+ days'
        
        # Determine impact for each factor
        def get_impact(score):
            if score >= 75:
                return 'strong_positive'
            elif score >= 60:
                return 'positive'
            elif score >= 40:
                return 'neutral'
            else:
                return 'negative'
        
        factors = {
            'engagement': {
                'score': round(engagement_score, 1),
                'weight': weights['engagement'],
                'impact': get_impact(engagement_score)
            },
            'adoption_rate': {
                'score': round(adoption_score, 1),
                'weight': weights['adoption_rate'],
                'impact': get_impact(adoption_score),
                'features_adopted': features_used
            },
            'satisfaction': {
                'score': round(satisfaction_score, 1),
                'weight': weights['satisfaction'],
                'impact': get_impact(satisfaction_score),
                'nps': nps_score
            },
            'consistency': {
                'score': round(consistency_score, 1),
                'weight': weights['consistency'],
                'impact': get_impact(consistency_score),
                'activity_rate': f'{round(consistency_rate * 100, 1)}%'
            }
        }
        
        # Generate recommendations
        recommendations = []
        if engagement_score < 60:
            recommendations.append('Increase engagement with targeted outreach')
        if adoption_score < 50:
            recommendations.append('Provide feature training and onboarding')
        if satisfaction_score < 60:
            recommendations.append('Address support issues proactively')
        if consistency_score < 40:
            recommendations.append('Implement re-engagement campaign')
        
        if likelihood in ['very_high', 'high']:
            recommendations.append('Maintain current engagement level')
            recommendations.append('Introduce advanced features for power users')
            recommendations.append('Consider for case study or referral program')
        
        prediction = {
            'id': prediction_id,
            'client_id': client_id,
            'success_score': round(success_score, 1),
            'success_likelihood': likelihood,
            'confidence': round((len(client_behaviors) / 10) * 100, 1),  # More data = higher confidence
            'factors': factors,
            'timeline': timeline,
            'recommendations': recommendations if recommendations else ['Continue monitoring client progress'],
            'risk_level': 'low' if likelihood in ['very_high', 'high'] else 'medium' if likelihood == 'moderate' else 'high',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'prediction_type': 'algorithmic',
            'data_points_used': len(client_behaviors)
        }
        
        return prediction
    
    async def generate_recommendations(self, client_id: str, context: Dict[Any, Any] = None) -> Dict[Any, Any]:
        """Generate personalized recommendations for client"""
        recommendation_id = str(uuid.uuid4())
        
        recommendations = {
            'id': recommendation_id,
            'client_id': client_id,
            'recommendations': [
                {
                    'category': 'feature_adoption',
                    'title': 'Enable advanced analytics',
                    'description': 'Unlock deeper insights with advanced analytics features',
                    'priority': 'high',
                    'expected_impact': 'Improved decision-making and ROI tracking'
                },
                {
                    'category': 'automation',
                    'title': 'Set up automated workflows',
                    'description': 'Save time with intelligent automation',
                    'priority': 'medium',
                    'expected_impact': 'Reduced manual work and increased efficiency'
                },
                {
                    'category': 'integration',
                    'title': 'Connect additional platforms',
                    'description': 'Integrate with more marketing channels',
                    'priority': 'medium',
                    'expected_impact': 'Broader reach and unified analytics'
                }
            ],
            'next_best_actions': [
                'Schedule onboarding call for advanced features',
                'Review automation opportunities',
                'Explore integration options'
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return recommendations
    
    async def predict_churn_risk(self, client_id: str) -> Dict[Any, Any]:
        """Predict client churn risk with real predictive algorithms"""
        risk_id = str(uuid.uuid4())
        
        # Get client data
        client_behaviors = self.behavior_data.get(client_id, [])
        
        if not client_behaviors:
            return {
                'id': risk_id,
                'client_id': client_id,
                'churn_risk': 'unknown',
                'risk_score': 50,
                'note': 'Insufficient data for churn prediction',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        latest_behavior = client_behaviors[-1]['data']
        
        # Calculate churn risk score (0-100, higher = more risk)
        risk_score = 0
        risk_factors = []
        protective_factors = []
        early_warnings = []
        
        # 1. Engagement decline (max +30 points)
        engagement = self._calculate_engagement_score(latest_behavior)
        if engagement < 30:
            risk_score += 30
            risk_factors.append('Very low engagement')
            early_warnings.append('Critical: Engagement below threshold')
        elif engagement < 50:
            risk_score += 20
            risk_factors.append('Low engagement level')
            early_warnings.append('Warning: Declining engagement')
        elif engagement >= 70:
            protective_factors.append('High engagement level')
        
        # 2. Usage frequency (max +25 points)
        login_count = latest_behavior.get('login_count', 0)
        days_active = latest_behavior.get('days_active', 1)
        frequency = login_count / max(days_active, 1)
        
        if frequency < 0.1:
            risk_score += 25
            risk_factors.append('Very infrequent usage')
            early_warnings.append('Critical: User barely active')
        elif frequency < 0.3:
            risk_score += 15
            risk_factors.append('Infrequent platform usage')
        elif frequency >= 0.7:
            protective_factors.append('Regular platform usage')
        
        # 3. Feature adoption (max +20 points)
        features_used = len(latest_behavior.get('features_used', []))
        if features_used < 2:
            risk_score += 20
            risk_factors.append('Minimal feature adoption')
            early_warnings.append('Warning: Not using key features')
        elif features_used < 4:
            risk_score += 10
            risk_factors.append('Limited feature usage')
        elif features_used >= 6:
            protective_factors.append('Good feature adoption')
        
        # 4. Support issues (max +15 points)
        support_tickets = latest_behavior.get('support_tickets', 0)
        if support_tickets > 8:
            risk_score += 15
            risk_factors.append('High support ticket volume')
            early_warnings.append('Warning: Multiple unresolved issues')
        elif support_tickets > 5:
            risk_score += 8
            risk_factors.append('Moderate support needs')
        elif support_tickets == 0:
            protective_factors.append('No support issues')
        
        # 5. Usage trend (max +10 points)
        if len(client_behaviors) >= 2:
            current_logins = client_behaviors[-1]['data'].get('login_count', 0)
            previous_logins = client_behaviors[-2]['data'].get('login_count', 0)
            
            if current_logins < previous_logins * 0.5:
                risk_score += 10
                risk_factors.append('Rapid usage decline')
                early_warnings.append('Alert: Usage dropped significantly')
            elif current_logins < previous_logins * 0.8:
                risk_score += 5
                risk_factors.append('Declining usage trend')
            elif current_logins > previous_logins * 1.2:
                protective_factors.append('Increasing usage trend')
        
        # 6. Satisfaction (affects overall risk)
        nps_score = latest_behavior.get('nps_score', 7)
        if nps_score <= 6:
            risk_score += 10
            risk_factors.append('Low satisfaction score (Detractor)')
            early_warnings.append('Critical: Client is a detractor')
        elif nps_score >= 9:
            protective_factors.append('High satisfaction (Promoter)')
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = 'critical'
        elif risk_score >= 50:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        elif risk_score >= 15:
            risk_level = 'low'
        else:
            risk_level = 'very_low'
        
        # Generate retention strategies
        retention_strategies = []
        
        if risk_level in ['critical', 'high']:
            retention_strategies.extend([
                'URGENT: Schedule immediate check-in call',
                'Assign dedicated success manager',
                'Offer personalized training session'
            ])
        
        if engagement < 50:
            retention_strategies.append('Launch re-engagement campaign')
        
        if features_used < 4:
            retention_strategies.append('Provide feature adoption workshop')
        
        if support_tickets > 5:
            retention_strategies.append('Expedite resolution of open issues')
        
        if risk_level in ['very_low', 'low']:
            retention_strategies.extend([
                'Continue proactive support',
                'Share success stories and best practices',
                'Offer exclusive features or early access'
            ])
        
        # Calculate confidence based on data availability
        confidence = min((len(client_behaviors) / 5) * 100, 95)
        
        risk_analysis = {
            'id': risk_id,
            'client_id': client_id,
            'churn_risk': risk_level,
            'risk_score': round(risk_score, 1),
            'risk_factors': risk_factors,
            'protective_factors': protective_factors if protective_factors else ['Monitor for positive signals'],
            'early_warning_indicators': early_warnings,
            'retention_strategies': retention_strategies,
            'priority': 'urgent' if risk_level in ['critical', 'high'] else 'normal',
            'recommended_action_within': '24 hours' if risk_level == 'critical' else '7 days' if risk_level == 'high' else '30 days',
            'confidence': round(confidence, 1),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'analysis_type': 'algorithmic',
            'metrics_analyzed': {
                'engagement': round(engagement, 1),
                'frequency': round(frequency, 2),
                'features_adopted': features_used,
                'support_tickets': support_tickets,
                'nps_score': nps_score
            }
        }
        
        return risk_analysis
    
    async def track_satisfaction(self, client_id: str, feedback_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Track client satisfaction"""
        tracking_id = str(uuid.uuid4())
        
        satisfaction = {
            'id': tracking_id,
            'client_id': client_id,
            'nps_score': feedback_data.get('nps_score', 8),
            'satisfaction_level': 'high',
            'feedback_sentiment': 'positive',
            'key_themes': [
                'Great platform features',
                'Responsive support team',
                'Easy to use interface'
            ],
            'areas_for_improvement': [
                'More integration options',
                'Advanced reporting features'
            ],
            'follow_up_actions': [
                'Thank client for feedback',
                'Address improvement suggestions',
                'Share product roadmap'
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return satisfaction
    
    async def create_client_profile(self, client_data: Dict[Any, Any]) -> Dict[Any, Any]:
        """Create a client intelligence profile"""
        client_id = str(uuid.uuid4())
        
        profile = {
            'id': client_id,
            'name': client_data.get('name', 'Unknown Client'),
            'industry': client_data.get('industry', 'general'),
            'size': client_data.get('size', 'medium'),
            'goals': client_data.get('goals', []),
            'preferences': {
                'communication_style': client_data.get('communication_style', 'professional'),
                'meeting_frequency': client_data.get('meeting_frequency', 'monthly'),
                'reporting_format': client_data.get('reporting_format', 'dashboard')
            },
            'success_metrics': client_data.get('success_metrics', []),
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.client_profiles[client_id] = profile
        logger.info(f"Created client profile: {profile['name']}")
        return profile

client_intelligence = ClientIntelligence()