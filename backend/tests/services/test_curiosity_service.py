"""
Tests for CURIOSITY Market Intelligence Service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from services.curiosity_market_service import CuriosityMarketService, MarketAnalysis, CompetitiveAnalysis, TrendAnalysis


@pytest.fixture
def mock_db():
    """Mock database client"""
    db = AsyncMock()
    db.campaigns = AsyncMock()
    return db


@pytest.fixture
def curiosity_service(mock_db):
    """Create CURIOSITY service instance"""
    return CuriosityMarketService(mock_db)


@pytest.mark.asyncio
async def test_analyze_market(curiosity_service, mock_db):
    """Test market analysis"""
    # Mock market intelligence response
    with patch.object(curiosity_service.market_intelligence, 'analyze_vertical', new_callable=AsyncMock) as mock_analyze:
        mock_analyze.return_value = {
            'market_size': 1000000.0,
            'growth_rate': 15.5,
            'key_trends': ['AI adoption', 'Automation'],
            'opportunities': ['SaaS market', 'Enterprise'],
            'competition_level': 'high',
            'key_players': ['Company A', 'Company B'],
            'market_gaps': ['Feature X', 'Feature Y'],
            'predictions': ['Growth in 2025', 'Market consolidation'],
            'investment_areas': ['AI', 'Automation'],
            'confidence': 0.85
        }
        
        result = await curiosity_service.analyze_market('saas')
        
        assert isinstance(result, MarketAnalysis)
        assert result.vertical == 'saas'
        assert result.market_size == 1000000.0
        assert result.growth_rate == 15.5
        assert len(result.key_trends) == 2
        assert result.confidence == 0.85


@pytest.mark.asyncio
async def test_analyze_competition(curiosity_service, mock_db):
    """Test competitive analysis"""
    with patch.object(curiosity_service.market_intelligence, 'analyze_competition', new_callable=AsyncMock) as mock_comp:
        mock_comp.return_value = {
            'competitors': [
                {
                    'name': 'Competitor A',
                    'market_share': 25.0,
                    'strengths': ['Strong brand', 'Large user base'],
                    'weaknesses': ['High pricing', 'Slow innovation'],
                    'positioning': 'Premium',
                    'threat_level': 'high',
                    'recommendations': ['Focus on innovation', 'Competitive pricing']
                }
            ]
        }
        
        result = await curiosity_service.analyze_competition('saas')
        
        assert len(result) == 1
        assert isinstance(result[0], CompetitiveAnalysis)
        assert result[0].competitor_name == 'Competitor A'
        assert result[0].market_share == 25.0
        assert result[0].threat_level == 'high'


@pytest.mark.asyncio
async def test_identify_trends(curiosity_service, mock_db):
    """Test trend identification"""
    with patch.object(curiosity_service.market_intelligence, 'identify_trends', new_callable=AsyncMock) as mock_trends:
        mock_trends.return_value = {
            'trends': [
                {
                    'name': 'AI Integration',
                    'category': 'technology',
                    'impact': 'high',
                    'timeframe': 'short-term',
                    'opportunities': ['AI features', 'Automation'],
                    'threats': ['Competition', 'Cost'],
                    'confidence': 0.8
                }
            ]
        }
        
        result = await curiosity_service.identify_trends('saas', 90)
        
        assert len(result) == 1
        assert isinstance(result[0], TrendAnalysis)
        assert result[0].trend_name == 'AI Integration'
        assert result[0].impact == 'high'
        assert result[0].confidence == 0.8


@pytest.mark.asyncio
async def test_compare_platforms(curiosity_service, mock_db):
    """Test platform comparison"""
    # Mock campaign data
    mock_db.campaigns.find.return_value.to_list = AsyncMock(return_value=[
        {
            '_id': 'campaign_1',
            'platform': 'google_ads',
            'status': 'active',
            'budget': {'daily_budget': 100},
            'performance': {'revenue': 500}
        },
        {
            '_id': 'campaign_2',
            'platform': 'meta_ads',
            'status': 'active',
            'budget': {'daily_budget': 150},
            'performance': {'revenue': 600}
        }
    ])
    
    result = await curiosity_service.compare_platforms(['google_ads', 'meta_ads'], ['roas', 'spend'])
    
    assert 'platforms' in result
    assert 'google_ads' in result['platforms']
    assert 'meta_ads' in result['platforms']
    assert 'comparison' in result
    assert 'recommendations' in result

