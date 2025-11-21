"""
Tests for FACE Customer Experience Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from services.face_experience_service import FaceExperienceService, UserBehavior, UXInsight, PersonalizationProfile


@pytest.fixture
def mock_db():
    """Mock database client"""
    db = AsyncMock()
    db.user_sessions = AsyncMock()
    db.user_feedback = AsyncMock()
    db.users = AsyncMock()
    db.onboarding_sessions = AsyncMock()
    return db


@pytest.fixture
def face_service(mock_db):
    """Create FACE service instance"""
    return FaceExperienceService(mock_db)


@pytest.mark.asyncio
async def test_analyze_user_behavior(face_service, mock_db):
    """Test user behavior analysis"""
    # Mock user sessions
    mock_db.user_sessions.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'session_1',
            'user_id': 'user_123',
            'created_at': datetime.utcnow() - timedelta(days=1),
            'duration_seconds': 600,
            'features_accessed': ['dashboard', 'campaigns'],
            'navigation_path': ['/dashboard', '/campaigns', '/analytics']
        },
        {
            '_id': 'session_2',
            'user_id': 'user_123',
            'created_at': datetime.utcnow() - timedelta(days=2),
            'duration_seconds': 300,
            'features_accessed': ['dashboard'],
            'navigation_path': ['/dashboard']
        }
    ])
    
    result = await face_service.analyze_user_behavior('user_123', 30)
    
    assert isinstance(result, UserBehavior)
    assert result.user_id == 'user_123'
    assert result.session_count == 2
    assert result.avg_session_duration > 0
    assert len(result.features_used) > 0
    assert result.engagement_score >= 0


@pytest.mark.asyncio
async def test_get_ux_insights(face_service, mock_db):
    """Test UX insights retrieval"""
    # Mock user feedback
    mock_db.user_feedback.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'feedback_1',
            'organization_id': 'org_123',
            'issue_type': 'navigation',
            'created_at': datetime.utcnow().isoformat()
        },
        {
            '_id': 'feedback_2',
            'organization_id': 'org_123',
            'issue_type': 'navigation',
            'created_at': datetime.utcnow().isoformat()
        }
    ])
    
    # Mock drop-off analysis
    with patch.object(face_service, '_analyze_organization_drop_offs', new_callable=AsyncMock) as mock_dropoffs:
        mock_dropoffs.return_value = [
            {
                'page': '/campaigns/create',
                'rate': 35.0,
                'visits': 100,
                'drop_offs': 35
            }
        ]
        
        result = await face_service.get_ux_insights('org_123')
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(i, UXInsight) for i in result)
        
        # Check for navigation insight
        nav_insights = [i for i in result if i.component == 'navigation']
        assert len(nav_insights) > 0


@pytest.mark.asyncio
async def test_create_personalization_profile(face_service, mock_db):
    """Test personalization profile creation"""
    # Mock user
    mock_db.users.find_one = AsyncMock(return_value={
        '_id': 'user_123',
        'preferences': {
            'theme': 'dark',
            'default_view': 'campaigns'
        }
    })
    
    # Mock behavior analysis
    with patch.object(face_service, 'analyze_user_behavior', new_callable=AsyncMock) as mock_behavior:
        mock_behavior.return_value = UserBehavior(
            user_id='user_123',
            session_count=10,
            avg_session_duration=450.0,
            features_used=['campaigns', 'analytics'],
            common_paths=[],
            drop_off_points=[],
            engagement_score=75.0
        )
        
        result = await face_service.create_personalization_profile('user_123')
        
        assert isinstance(result, PersonalizationProfile)
        assert result.user_id == 'user_123'
        assert len(result.recommended_features) > 0
        assert 'content_preferences' in result.__dict__
        assert 'ui_preferences' in result.__dict__


@pytest.mark.asyncio
async def test_optimize_onboarding(face_service, mock_db):
    """Test onboarding optimization"""
    # Mock onboarding sessions
    mock_db.onboarding_sessions.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'onboarding_1',
            'organization_id': 'org_123',
            'created_at': datetime.utcnow() - timedelta(days=1),
            'completed': True,
            'completion_time_seconds': 600,
            'current_step': 'completion'
        },
        {
            '_id': 'onboarding_2',
            'organization_id': 'org_123',
            'created_at': datetime.utcnow() - timedelta(days=2),
            'completed': False,
            'current_step': 'platform_connection'
        }
    ])
    
    result = await face_service.optimize_onboarding('org_123')
    
    assert 'completion_rate' in result
    assert 'avg_time' in result
    assert 'drop_off_steps' in result
    assert 'recommendations' in result
    assert isinstance(result['recommendations'], list)

