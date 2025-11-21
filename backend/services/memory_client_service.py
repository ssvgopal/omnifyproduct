"""
MEMORY - Client Intelligence Brain Module
Customer segmentation, churn prediction, success pattern identification
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
from brain_logic.client_intelligence import ClientIntelligence
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ClientSegment:
    """Client segment analysis"""
    segment_id: str
    segment_name: str
    client_count: int
    characteristics: List[str]
    avg_ltv: float
    churn_risk: float
    engagement_score: float
    recommendations: List[str]


@dataclass
class ChurnPrediction:
    """Churn prediction result"""
    client_id: str
    churn_probability: float
    churn_risk_level: str  # low, medium, high, critical
    days_until_churn: Optional[int]
    factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class ClientProfile:
    """Client profile analysis"""
    client_id: str
    engagement_score: float
    success_score: float
    health_score: float
    behavior_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    recommendations: List[str]


class MemoryClientService:
    """MEMORY - Client Intelligence Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.client_intelligence = ClientIntelligence()
    
    async def analyze_client_behavior(self, client_id: str, behavior_data: Dict[str, Any]) -> ClientProfile:
        """Analyze client behavior and create profile"""
        try:
            result = await self.client_intelligence.analyze_behavior(client_id, behavior_data)
            
            if 'error' in result:
                # Return default profile
                return ClientProfile(
                    client_id=client_id,
                    engagement_score=50.0,
                    success_score=50.0,
                    health_score=50.0,
                    behavior_patterns={},
                    preferences={},
                    recommendations=[]
                )
            
            # Calculate scores
            engagement_score = result.get('engagement_score', 50.0)
            success_score = result.get('success_score', 50.0)
            health_score = (engagement_score + success_score) / 2
            
            return ClientProfile(
                client_id=client_id,
                engagement_score=engagement_score,
                success_score=success_score,
                health_score=health_score,
                behavior_patterns=result.get('behavior_patterns', {}),
                preferences=result.get('preferences', {}),
                recommendations=result.get('recommendations', [])
            )
        except Exception as e:
            logger.error(f"Error analyzing client behavior: {str(e)}")
            raise
    
    async def predict_churn(self, client_id: str, client_data: Dict[str, Any]) -> ChurnPrediction:
        """Predict client churn"""
        try:
            result = await self.client_intelligence.predict_churn(client_id, client_data)
            
            if 'error' in result:
                return ChurnPrediction(
                    client_id=client_id,
                    churn_probability=0.0,
                    churn_risk_level='low',
                    days_until_churn=None,
                    factors={},
                    recommendations=[]
                )
            
            churn_prob = result.get('churn_probability', 0.0)
            
            # Determine risk level
            if churn_prob >= 0.7:
                risk_level = 'critical'
            elif churn_prob >= 0.5:
                risk_level = 'high'
            elif churn_prob >= 0.3:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return ChurnPrediction(
                client_id=client_id,
                churn_probability=churn_prob,
                churn_risk_level=risk_level,
                days_until_churn=result.get('days_until_churn'),
                factors=result.get('factors', {}),
                recommendations=result.get('recommendations', [])
            )
        except Exception as e:
            logger.error(f"Error predicting churn: {str(e)}")
            raise
    
    async def segment_clients(self, organization_id: str, criteria: Optional[Dict[str, Any]] = None) -> List[ClientSegment]:
        """Segment clients based on behavior and characteristics"""
        try:
            # Get all clients for organization
            clients = await self.db.clients.find({
                'organization_id': organization_id
            }).to_list(length=1000)
            
            if not clients:
                return []
            
            # Analyze each client
            segments = {}
            for client in clients:
                behavior_data = client.get('behavior_data', {})
                result = await self.client_intelligence.analyze_behavior(client['_id'], behavior_data)
                
                # Determine segment based on engagement and success scores
                engagement = result.get('engagement_score', 50.0)
                success = result.get('success_score', 50.0)
                
                if engagement >= 80 and success >= 80:
                    segment_name = 'champions'
                elif engagement >= 60 and success >= 60:
                    segment_name = 'loyal'
                elif engagement >= 40:
                    segment_name = 'at_risk'
                else:
                    segment_name = 'needs_attention'
                
                if segment_name not in segments:
                    segments[segment_name] = {
                        'clients': [],
                        'avg_ltv': 0.0,
                        'avg_churn_risk': 0.0,
                        'avg_engagement': 0.0
                    }
                
                segments[segment_name]['clients'].append(client['_id'])
                segments[segment_name]['avg_ltv'] += client.get('ltv', 0.0)
                segments[segment_name]['avg_churn_risk'] += result.get('churn_probability', 0.0)
                segments[segment_name]['avg_engagement'] += engagement
            
            # Create segment objects
            segment_list = []
            for segment_name, data in segments.items():
                count = len(data['clients'])
                if count > 0:
                    segment_list.append(ClientSegment(
                        segment_id=f"segment_{segment_name}",
                        segment_name=segment_name.replace('_', ' ').title(),
                        client_count=count,
                        characteristics=self._get_segment_characteristics(segment_name),
                        avg_ltv=data['avg_ltv'] / count,
                        churn_risk=data['avg_churn_risk'] / count,
                        engagement_score=data['avg_engagement'] / count,
                        recommendations=self._get_segment_recommendations(segment_name)
                    ))
            
            return segment_list
        except Exception as e:
            logger.error(f"Error segmenting clients: {str(e)}")
            raise
    
    def _get_segment_characteristics(self, segment_name: str) -> List[str]:
        """Get characteristics for segment"""
        characteristics = {
            'champions': ['High engagement', 'High success rate', 'Long tenure', 'Multiple features used'],
            'loyal': ['Regular usage', 'Good success metrics', 'Stable engagement'],
            'at_risk': ['Declining engagement', 'Reduced feature usage', 'Support tickets'],
            'needs_attention': ['Low engagement', 'Inactive periods', 'Low feature adoption']
        }
        return characteristics.get(segment_name, [])
    
    def _get_segment_recommendations(self, segment_name: str) -> List[str]:
        """Get recommendations for segment"""
        recommendations = {
            'champions': [
                'Consider upselling premium features',
                'Request case study or testimonial',
                'Invite to beta programs'
            ],
            'loyal': [
                'Maintain regular check-ins',
                'Share best practices',
                'Highlight new features'
            ],
            'at_risk': [
                'Schedule success review call',
                'Identify pain points',
                'Offer training or support'
            ],
            'needs_attention': [
                'Re-engagement campaign',
                'Identify barriers to adoption',
                'Consider account review'
            ]
        }
        return recommendations.get(segment_name, [])
    
    async def identify_success_patterns(self, organization_id: str) -> Dict[str, Any]:
        """Identify patterns in successful clients"""
        try:
            # Get successful clients (high LTV, low churn)
            successful_clients = await self.db.clients.find({
                'organization_id': organization_id,
                'ltv': {'$gt': 10000},
                'churn_probability': {'$lt': 0.3}
            }).to_list(length=100)
            
            if not successful_clients:
                return {
                    'patterns': [],
                    'recommendations': ['Insufficient data to identify patterns']
                }
            
            # Analyze common characteristics
            patterns = {
                'common_features': {},
                'common_behaviors': {},
                'common_attributes': {}
            }
            
            for client in successful_clients:
                # Track feature usage
                features = client.get('features_used', [])
                for feature in features:
                    patterns['common_features'][feature] = patterns['common_features'].get(feature, 0) + 1
                
                # Track behaviors
                behavior = client.get('behavior_data', {})
                login_freq = behavior.get('login_count', 0) / max(behavior.get('days_active', 1), 1)
                if login_freq > 0.5:
                    patterns['common_behaviors']['daily_login'] = patterns['common_behaviors'].get('daily_login', 0) + 1
            
            # Generate recommendations
            top_features = sorted(patterns['common_features'].items(), key=lambda x: x[1], reverse=True)[:5]
            recommendations = [
                f"Focus on promoting {feature} to at-risk clients" 
                for feature, count in top_features
            ]
            
            return {
                'patterns': patterns,
                'top_features': [f[0] for f in top_features],
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error identifying success patterns: {str(e)}")
            raise

