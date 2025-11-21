"""
Tests for MEMORY Client Intelligence Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from services.memory_client_service import MemoryClientService, ClientProfile, ChurnPrediction, ClientSegment


@pytest.fixture
def mock_db():
    """Mock database client"""
    db = AsyncMock()
    db.clients = AsyncMock()
    return db


@pytest.fixture
def memory_service(mock_db):
    """Create MEMORY service instance"""
    return MemoryClientService(mock_db)


@pytest.mark.asyncio
async def test_analyze_client_behavior(memory_service, mock_db):
    """Test client behavior analysis"""
    behavior_data = {
        'login_count': 20,
        'days_active': 30,
        'features_used': ['campaigns', 'analytics', 'reports'],
        'avg_session_minutes': 15,
        'support_tickets': 2
    }
    
    with patch.object(memory_service.client_intelligence, 'analyze_behavior', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {
            'engagement_score': 75.0,
            'success_score': 80.0,
            'behavior_patterns': {
                'frequency': 'daily',
                'engagement_level': 'high'
            },
            'preferences': {
                'dashboard_layout': 'detailed',
                'notifications': 'enabled'
            },
            'recommendations': ['Use advanced features', 'Explore analytics']
        }
        
        result = await memory_service.analyze_client_behavior('client_123', behavior_data)
        
        assert isinstance(result, ClientProfile)
        assert result.client_id == 'client_123'
        assert result.engagement_score == 75.0
        assert result.success_score == 80.0
        assert result.health_score == 77.5  # (75 + 80) / 2


@pytest.mark.asyncio
async def test_predict_churn(memory_service, mock_db):
    """Test churn prediction"""
    client_data = {
        'engagement_score': 45.0,
        'days_since_last_login': 15,
        'support_tickets': 5,
        'feature_usage': ['basic']
    }
    
    with patch.object(memory_service.client_intelligence, 'predict_churn', new_callable=AsyncMock) as mock_predict:
        mock_predict.return_value = {
            'churn_probability': 0.65,
            'days_until_churn': 30,
            'factors': {
                'low_engagement': 0.3,
                'reduced_usage': 0.25,
                'support_issues': 0.1
            },
            'recommendations': [
                'Schedule success review',
                'Offer training',
                'Identify pain points'
            ]
        }
        
        result = await memory_service.predict_churn('client_123', client_data)
        
        assert isinstance(result, ChurnPrediction)
        assert result.client_id == 'client_123'
        assert result.churn_probability == 0.65
        assert result.churn_risk_level == 'high'  # >= 0.5
        assert result.days_until_churn == 30


@pytest.mark.asyncio
async def test_segment_clients(memory_service, mock_db):
    """Test client segmentation"""
    # Mock clients
    mock_db.clients.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'client_1',
            'organization_id': 'org_123',
            'ltv': 15000,
            'behavior_data': {
                'login_count': 30,
                'days_active': 30,
                'features_used': ['campaigns', 'analytics']
            }
        },
        {
            '_id': 'client_2',
            'organization_id': 'org_123',
            'ltv': 5000,
            'behavior_data': {
                'login_count': 5,
                'days_active': 30,
                'features_used': ['campaigns']
            }
        }
    ])
    
    with patch.object(memory_service.client_intelligence, 'analyze_behavior', new_callable=AsyncMock) as mock_analyze:
        def analyze_side_effect(client_id, behavior_data):
            engagement = behavior_data.get('login_count', 0) / max(behavior_data.get('days_active', 1), 1)
            success = min(engagement * 10, 100)
            return {
                'engagement_score': engagement * 10,
                'success_score': success,
                'churn_probability': 0.1 if engagement > 0.5 else 0.6
            }
        
        mock_analyze.side_effect = lambda client_id, behavior_data: AsyncMock(return_value=analyze_side_effect(client_id, behavior_data))()
        
        result = await memory_service.segment_clients('org_123')
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(seg, ClientSegment) for seg in result)


@pytest.mark.asyncio
async def test_identify_success_patterns(memory_service, mock_db):
    """Test success pattern identification"""
    # Mock successful clients
    mock_db.clients.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'client_1',
            'organization_id': 'org_123',
            'ltv': 20000,
            'churn_probability': 0.2,
            'features_used': ['campaigns', 'analytics', 'reports'],
            'behavior_data': {
                'login_count': 30,
                'days_active': 30
            }
        }
    ])
    
    result = await memory_service.identify_success_patterns('org_123')
    
    assert 'patterns' in result
    assert 'top_features' in result
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)

