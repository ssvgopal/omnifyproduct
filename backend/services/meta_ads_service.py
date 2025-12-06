"""
Meta Ads Integration Service
Handles Facebook/Instagram advertising data retrieval and management
"""
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from services.api_key_service import api_key_service

class MetaAdsService:
    """Service for Meta Ads (Facebook/Instagram) platform integration"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_credentials(self, organization_id: str) -> Optional[Dict[str, str]]:
        """Get Meta Ads credentials from encrypted storage"""
        keys = await api_key_service.get_all_keys_for_platform(organization_id, 'meta_ads')
        
        if not keys or 'access_token' not in keys or 'account_id' not in keys:
            return None
        
        return {
            'access_token': keys['access_token'],
            'account_id': keys['account_id']
        }
    
    async def fetch_account_info(self, organization_id: str) -> Dict[str, Any]:
        """Fetch Meta Ads account information"""
        creds = await self.get_credentials(organization_id)
        if not creds:
            return {'error': 'Meta Ads credentials not configured'}
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{creds['account_id']}",
                params={
                    'access_token': creds['access_token'],
                    'fields': 'name,account_id,account_status,currency,timezone_name'
                }
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'error': f"Meta API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def fetch_campaigns(self, organization_id: str, limit: int = 100) -> Dict[str, Any]:
        """Fetch all campaigns from Meta Ads account"""
        creds = await self.get_credentials(organization_id)
        if not creds:
            return {'error': 'Meta Ads credentials not configured'}
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{creds['account_id']}/campaigns",
                params={
                    'access_token': creds['access_token'],
                    'fields': 'id,name,status,objective,effective_status,created_time,updated_time',
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'campaigns': data.get('data', []),
                    'count': len(data.get('data', []))
                }
            else:
                return {'error': f"Meta API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def fetch_insights(
        self,
        organization_id: str,
        date_range: Optional[Dict[str, str]] = None,
        level: str = 'account'
    ) -> Dict[str, Any]:
        """
        Fetch performance insights from Meta Ads
        
        Args:
            organization_id: Organization UUID
            date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
            level: 'account', 'campaign', 'adset', or 'ad'
        """
        creds = await self.get_credentials(organization_id)
        if not creds:
            return {'error': 'Meta Ads credentials not configured'}
        
        # Default to last 30 days
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{creds['account_id']}/insights",
                params={
                    'access_token': creds['access_token'],
                    'time_range': f"{{'since':'{date_range['start']}','until':'{date_range['end']}'}}",
                    'time_increment': 1,  # Daily breakdown
                    'level': level,
                    'fields': 'spend,impressions,clicks,reach,actions,action_values,cost_per_action_type,ctr,cpc,cpp,cpm',
                    'limit': 1000
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get('data', [])
                
                # Process insights to extract key metrics
                processed_insights = []
                for insight in insights:
                    processed = {
                        'date': insight.get('date_start'),
                        'spend': float(insight.get('spend', 0)),
                        'impressions': int(insight.get('impressions', 0)),
                        'clicks': int(insight.get('clicks', 0)),
                        'reach': int(insight.get('reach', 0)),
                        'ctr': float(insight.get('ctr', 0)),
                        'cpc': float(insight.get('cpc', 0)),
                        'cpm': float(insight.get('cpm', 0)),
                        'conversions': 0,
                        'revenue': 0
                    }
                    
                    # Extract conversions and revenue from actions
                    actions = insight.get('actions', [])
                    action_values = insight.get('action_values', [])
                    
                    for action in actions:
                        if action.get('action_type') in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                            processed['conversions'] += int(action.get('value', 0))
                    
                    for action_value in action_values:
                        if action_value.get('action_type') in ['purchase', 'offsite_conversion.fb_pixel_purchase']:
                            processed['revenue'] += float(action_value.get('value', 0))
                    
                    # Calculate ROAS
                    if processed['spend'] > 0:
                        processed['roas'] = processed['revenue'] / processed['spend']
                    else:
                        processed['roas'] = 0
                    
                    processed_insights.append(processed)
                
                return {
                    'success': True,
                    'insights': processed_insights,
                    'count': len(processed_insights),
                    'date_range': date_range
                }
            else:
                return {'error': f"Meta API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def fetch_ads_with_creatives(self, organization_id: str, limit: int = 100) -> Dict[str, Any]:
        """Fetch ads with creative information"""
        creds = await self.get_credentials(organization_id)
        if not creds:
            return {'error': 'Meta Ads credentials not configured'}
        
        try:
            response = await self.client.get(
                f"{self.BASE_URL}/{creds['account_id']}/ads",
                params={
                    'access_token': creds['access_token'],
                    'fields': 'id,name,status,effective_status,creative{id,name,object_story_spec,image_url,video_id}',
                    'limit': limit
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'ads': data.get('data', []),
                    'count': len(data.get('data', []))
                }
            else:
                return {'error': f"Meta API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def calculate_summary_metrics(self, organization_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate summary metrics for dashboard"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_range = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        insights_result = await self.fetch_insights(organization_id, date_range)
        
        if not insights_result.get('success'):
            return insights_result
        
        insights = insights_result.get('insights', [])
        
        # Calculate totals
        total_spend = sum(i['spend'] for i in insights)
        total_revenue = sum(i['revenue'] for i in insights)
        total_impressions = sum(i['impressions'] for i in insights)
        total_clicks = sum(i['clicks'] for i in insights)
        total_conversions = sum(i['conversions'] for i in insights)
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        blended_roas = (total_revenue / total_spend) if total_spend > 0 else 0
        
        return {
            'success': True,
            'platform': 'meta_ads',
            'period': f'{days} days',
            'date_range': date_range,
            'metrics': {
                'spend': round(total_spend, 2),
                'revenue': round(total_revenue, 2),
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': total_conversions,
                'ctr': round(avg_ctr, 2),
                'cpc': round(avg_cpc, 2),
                'cpm': round(avg_cpm, 2),
                'roas': round(blended_roas, 2)
            }
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
meta_ads_service = MetaAdsService()
