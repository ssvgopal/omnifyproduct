"""
CURIOSITY - Market Intelligence Brain Module
Market research, competitive analysis, trend identification
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
from brain_logic.market_intelligence import MarketIntelligence

logger = logging.getLogger(__name__)


@dataclass
class MarketAnalysis:
    """Market analysis result"""
    vertical: str
    market_size: float
    growth_rate: float
    key_trends: List[str]
    opportunities: List[str]
    competition_level: str
    key_players: List[str]
    market_gaps: List[str]
    predictions: List[str]
    investment_areas: List[str]
    confidence: float


@dataclass
class CompetitiveAnalysis:
    """Competitive analysis result"""
    competitor_name: str
    market_share: float
    strengths: List[str]
    weaknesses: List[str]
    positioning: str
    threat_level: str  # low, medium, high, critical
    recommendations: List[str]


@dataclass
class TrendAnalysis:
    """Market trend analysis result"""
    trend_name: str
    category: str
    impact: str  # low, medium, high
    timeframe: str
    opportunities: List[str]
    threats: List[str]
    confidence: float


class CuriosityMarketService:
    """CURIOSITY - Market Intelligence Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.market_intelligence = MarketIntelligence()
    
    async def analyze_market(self, vertical: str, data: Optional[Dict[str, Any]] = None) -> MarketAnalysis:
        """Analyze market for a specific vertical"""
        try:
            result = await self.market_intelligence.analyze_vertical(vertical, data)
            
            if 'error' in result:
                # Return default analysis if error
                return MarketAnalysis(
                    vertical=vertical,
                    market_size=0.0,
                    growth_rate=0.0,
                    key_trends=[],
                    opportunities=[],
                    competition_level="unknown",
                    key_players=[],
                    market_gaps=[],
                    predictions=[],
                    investment_areas=[],
                    confidence=0.0
                )
            
            return MarketAnalysis(
                vertical=vertical,
                market_size=result.get('market_size', 0.0),
                growth_rate=result.get('growth_rate', 0.0),
                key_trends=result.get('key_trends', []),
                opportunities=result.get('opportunities', []),
                competition_level=result.get('competition_level', 'medium'),
                key_players=result.get('key_players', []),
                market_gaps=result.get('market_gaps', []),
                predictions=result.get('predictions', []),
                investment_areas=result.get('investment_areas', []),
                confidence=result.get('confidence', 0.8)
            )
        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            raise
    
    async def analyze_competition(self, vertical: str, competitor_data: Optional[List[Dict[str, Any]]] = None) -> List[CompetitiveAnalysis]:
        """Analyze competitive landscape"""
        try:
            result = await self.market_intelligence.analyze_competition(vertical, competitor_data)
            
            if 'error' in result:
                return []
            
            analyses = []
            for comp in result.get('competitors', []):
                analyses.append(CompetitiveAnalysis(
                    competitor_name=comp.get('name', 'Unknown'),
                    market_share=comp.get('market_share', 0.0),
                    strengths=comp.get('strengths', []),
                    weaknesses=comp.get('weaknesses', []),
                    positioning=comp.get('positioning', 'Unknown'),
                    threat_level=comp.get('threat_level', 'medium'),
                    recommendations=comp.get('recommendations', [])
                ))
            
            return analyses
        except Exception as e:
            logger.error(f"Error analyzing competition: {str(e)}")
            raise
    
    async def identify_trends(self, vertical: str, timeframe_days: int = 90) -> List[TrendAnalysis]:
        """Identify market trends"""
        try:
            result = await self.market_intelligence.identify_trends(vertical, timeframe_days)
            
            if 'error' in result:
                return []
            
            trends = []
            for trend in result.get('trends', []):
                trends.append(TrendAnalysis(
                    trend_name=trend.get('name', 'Unknown Trend'),
                    category=trend.get('category', 'general'),
                    impact=trend.get('impact', 'medium'),
                    timeframe=trend.get('timeframe', 'short-term'),
                    opportunities=trend.get('opportunities', []),
                    threats=trend.get('threats', []),
                    confidence=trend.get('confidence', 0.7)
                ))
            
            return trends
        except Exception as e:
            logger.error(f"Error identifying trends: {str(e)}")
            raise
    
    async def get_market_opportunities(self, vertical: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get market opportunities"""
        try:
            result = await self.market_intelligence.get_opportunities(vertical, filters)
            
            if 'error' in result:
                return []
            
            return result.get('opportunities', [])
        except Exception as e:
            logger.error(f"Error getting market opportunities: {str(e)}")
            raise
    
    async def compare_platforms(self, platforms: List[str], metrics: List[str]) -> Dict[str, Any]:
        """Compare performance across platforms"""
        try:
            # Get platform performance data
            platform_data = {}
            for platform in platforms:
                # Query campaign performance for platform
                campaigns = await self.db.campaigns.find({
                    'platform': platform,
                    'status': 'active'
                }).to_list(length=100)
                
                if campaigns:
                    total_spend = sum(c.get('budget', {}).get('daily_budget', 0) * 30 for c in campaigns)
                    total_revenue = sum(c.get('performance', {}).get('revenue', 0) for c in campaigns)
                    avg_roas = total_revenue / total_spend if total_spend > 0 else 0
                    
                    platform_data[platform] = {
                        'campaigns': len(campaigns),
                        'total_spend': total_spend,
                        'total_revenue': total_revenue,
                        'roas': avg_roas,
                        'metrics': {}
                    }
            
            return {
                'platforms': platform_data,
                'comparison': self._calculate_comparison(platform_data, metrics),
                'recommendations': self._generate_platform_recommendations(platform_data)
            }
        except Exception as e:
            logger.error(f"Error comparing platforms: {str(e)}")
            raise
    
    def _calculate_comparison(self, platform_data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Calculate platform comparison"""
        comparison = {}
        
        for metric in metrics:
            values = {}
            for platform, data in platform_data.items():
                if metric in data.get('metrics', {}):
                    values[platform] = data['metrics'][metric]
                elif metric == 'roas':
                    values[platform] = data.get('roas', 0)
                elif metric == 'spend':
                    values[platform] = data.get('total_spend', 0)
            
            if values:
                best_platform = max(values.items(), key=lambda x: x[1])[0]
                comparison[metric] = {
                    'values': values,
                    'best': best_platform,
                    'worst': min(values.items(), key=lambda x: x[1])[0] if len(values) > 1 else None
                }
        
        return comparison
    
    def _generate_platform_recommendations(self, platform_data: Dict[str, Any]) -> List[str]:
        """Generate platform recommendations"""
        recommendations = []
        
        if not platform_data:
            return ["No platform data available for comparison"]
        
        # Find best performing platform
        best_platform = max(platform_data.items(), key=lambda x: x[1].get('roas', 0))[0]
        worst_platform = min(platform_data.items(), key=lambda x: x[1].get('roas', 0))[0]
        
        if platform_data[best_platform]['roas'] > platform_data[worst_platform]['roas'] * 1.2:
            recommendations.append(f"Consider increasing budget allocation to {best_platform} (ROAS: {platform_data[best_platform]['roas']:.2f}x)")
        
        return recommendations

