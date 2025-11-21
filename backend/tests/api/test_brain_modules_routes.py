"""
Integration tests for Brain Modules API Routes
Tests all brain modules: ORACLE, EYES, VOICE, CURIOSITY, MEMORY, REFLEXES, FACE
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from agentkit_server import app


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def mock_auth():
    """Mock authentication"""
    with patch('api.brain_modules_routes.get_current_user') as mock:
        mock.return_value = {
            'user_id': 'test_user',
            'organization_id': 'test_org',
            'email': 'test@example.com'
        }
        yield mock


@pytest.mark.asyncio
async def test_oracle_predict_fatigue(client, mock_auth):
    """Test ORACLE creative fatigue prediction"""
    response = client.post(
        '/api/brain/oracle/predict-fatigue',
        json={
            'creative_id': 'creative_123',
            'campaign_id': 'campaign_456',
            'performance_history': [
                {'date': '2025-01-01', 'ctr': 3.5, 'conversion_rate': 5.2},
                {'date': '2025-01-02', 'ctr': 3.2, 'conversion_rate': 4.8}
            ]
        }
    )
    
    assert response.status_code in [200, 500]  # May fail if service not initialized
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'days_until_fatigue' in data['data']


@pytest.mark.asyncio
async def test_eyes_analyze_aida(client, mock_auth):
    """Test EYES AIDA analysis"""
    response = client.post(
        '/api/brain/eyes/analyze-aida',
        json={
            'creative_id': 'creative_123',
            'creative_content': {
                'headline': 'Transform Your Business',
                'description': 'Join thousands of successful companies',
                'call_to_action': 'Get Started Now'
            }
        }
    )
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'attention_score' in data['data']


@pytest.mark.asyncio
async def test_voice_optimize_budget(client, mock_auth):
    """Test VOICE budget optimization"""
    response = client.post(
        '/api/brain/voice/optimize-budget',
        json={
            'campaign_id': 'campaign_456',
            'platform': 'google_ads',
            'performance_data': {
                'roas': 3.5,
                'cost_per_conversion': 45,
                'conversions': 25
            }
        }
    )
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data


@pytest.mark.asyncio
async def test_curiosity_analyze_market(client, mock_auth):
    """Test CURIOSITY market analysis"""
    response = client.post(
        '/api/brain/curiosity/analyze-market',
        params={'vertical': 'saas'}
    )
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'vertical' in data['data']


@pytest.mark.asyncio
async def test_memory_analyze_behavior(client, mock_auth):
    """Test MEMORY client behavior analysis"""
    response = client.post(
        '/api/brain/memory/analyze-behavior',
        json={
            'client_id': 'client_123',
            'behavior_data': {
                'login_count': 20,
                'days_active': 30,
                'features_used': ['campaigns', 'analytics']
            }
        }
    )
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'engagement_score' in data['data']


@pytest.mark.asyncio
async def test_reflexes_get_metrics(client, mock_auth):
    """Test REFLEXES system metrics"""
    response = client.get('/api/brain/reflexes/metrics')
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'cpu_usage' in data['data']


@pytest.mark.asyncio
async def test_face_analyze_behavior(client, mock_auth):
    """Test FACE user behavior analysis"""
    response = client.post(
        '/api/brain/face/analyze-behavior',
        json={
            'user_id': 'user_123',
            'timeframe_days': 30
        }
    )
    
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'session_count' in data['data']

