"""
Google Ads Integration Service
Handles Google Ads data retrieval and campaign management
"""
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from services.api_key_service import api_key_service

class GoogleAdsService:
    """Service for Google Ads platform integration"""
    
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    ADS_API_URL = "https://googleads.googleapis.com/v14"
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token_cache = {}
    
    async def get_credentials(self, organization_id: str) -> Optional[Dict[str, str]]:
        """Get Google Ads credentials from encrypted storage"""
        keys = await api_key_service.get_all_keys_for_platform(organization_id, 'google_ads')
        
        required_keys = ['client_id', 'client_secret', 'refresh_token', 'customer_id', 'developer_token']
        if not keys or not all(k in keys for k in required_keys):
            return None
        
        # Remove dashes from customer ID
        keys['customer_id'] = keys['customer_id'].replace('-', '')
        
        return keys
    
    async def get_access_token(self, organization_id: str) -> Optional[str]:
        """Get or refresh OAuth access token"""
        # Check cache first
        if organization_id in self.access_token_cache:
            cached = self.access_token_cache[organization_id]
            if datetime.now() < cached['expires_at']:
                return cached['token']
        
        creds = await self.get_credentials(organization_id)
        if not creds:
            return None
        
        try:
            response = await self.client.post(
                self.TOKEN_URL,
                data={
                    'client_id': creds['client_id'],
                    'client_secret': creds['client_secret'],
                    'refresh_token': creds['refresh_token'],
                    'grant_type': 'refresh_token'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                access_token = data['access_token']
                expires_in = data.get('expires_in', 3600)
                
                # Cache the token
                self.access_token_cache[organization_id] = {
                    'token': access_token,
                    'expires_at': datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                }
                
                return access_token
            else:
                print(f"Failed to get Google Ads access token: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error getting Google Ads access token: {e}")
            return None
    
    async def execute_query(self, organization_id: str, query: str) -> Dict[str, Any]:
        """
        Execute a Google Ads Query Language (GAQL) query
        
        Args:
            organization_id: Organization UUID
            query: GAQL query string
        """
        creds = await self.get_credentials(organization_id)
        if not creds:
            return {'error': 'Google Ads credentials not configured'}
        
        access_token = await self.get_access_token(organization_id)
        if not access_token:
            return {'error': 'Failed to get access token'}
        
        try:
            response = await self.client.post(
                f"{self.ADS_API_URL}/customers/{creds['customer_id']}/googleAds:searchStream",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'developer-token': creds['developer_token'],
                    'login-customer-id': creds['customer_id'],
                    'Content-Type': 'application/json'
                },
                json={'query': query}
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'error': f"Google Ads API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    async def fetch_campaigns(self, organization_id: str) -> Dict[str, Any]:
        """Fetch all campaigns"""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.bidding_strategy_type
            FROM campaign
            WHERE campaign.status != 'REMOVED'
            ORDER BY campaign.name
        """
        
        result = await self.execute_query(organization_id, query)
        
        if not result.get('success'):
            return result
        
        # Parse campaigns from response
        campaigns = []
        for batch in result['data']:
            if 'results' in batch:
                for row in batch['results']:
                    campaign = row.get('campaign', {})
                    campaigns.append({
                        'id': campaign.get('id'),
                        'name': campaign.get('name'),
                        'status': campaign.get('status'),
                        'type': campaign.get('advertisingChannelType'),
                        'bidding_strategy': campaign.get('biddingStrategyType')
                    })
        
        return {
            'success': True,
            'campaigns': campaigns,
            'count': len(campaigns)
        }
    
    async def fetch_metrics(
        self,
        organization_id: str,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch performance metrics
        
        Args:
            organization_id: Organization UUID
            date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
        """
        # Default to last 30 days
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        
        query = f"""
            SELECT
                segments.date,
                metrics.cost_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date BETWEEN '{date_range['start']}' AND '{date_range['end']}'
            ORDER BY segments.date DESC
        """
        
        result = await self.execute_query(organization_id, query)
        
        if not result.get('success'):
            return result
        
        # Parse metrics
        metrics_list = []
        for batch in result['data']:
            if 'results' in batch:
                for row in batch['results']:
                    segments = row.get('segments', {})
                    metrics = row.get('metrics', {})
                    
                    spend = float(metrics.get('costMicros', 0)) / 1_000_000
                    revenue = float(metrics.get('conversionsValue', 0))
                    
                    metric_data = {
                        'date': segments.get('date'),
                        'spend': spend,
                        'impressions': int(metrics.get('impressions', 0)),
                        'clicks': int(metrics.get('clicks', 0)),
                        'conversions': float(metrics.get('conversions', 0)),
                        'revenue': revenue,
                        'ctr': float(metrics.get('ctr', 0)) * 100,
                        'cpc': float(metrics.get('averageCpc', 0)) / 1_000_000,
                        'roas': (revenue / spend) if spend > 0 else 0
                    }
                    
                    metrics_list.append(metric_data)
        
        return {
            'success': True,
            'metrics': metrics_list,
            'count': len(metrics_list),
            'date_range': date_range
        }
    
    async def calculate_summary_metrics(self, organization_id: str, days: int = 30) -> Dict[str, Any]:
        """Calculate summary metrics for dashboard"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_range = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        metrics_result = await self.fetch_metrics(organization_id, date_range)
        
        if not metrics_result.get('success'):
            return metrics_result
        
        metrics = metrics_result.get('metrics', [])
        
        # Calculate totals
        total_spend = sum(m['spend'] for m in metrics)
        total_revenue = sum(m['revenue'] for m in metrics)
        total_impressions = sum(m['impressions'] for m in metrics)
        total_clicks = sum(m['clicks'] for m in metrics)
        total_conversions = sum(m['conversions'] for m in metrics)
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpm = (total_spend / total_impressions * 1000) if total_impressions > 0 else 0
        blended_roas = (total_revenue / total_spend) if total_spend > 0 else 0
        
        return {
            'success': True,
            'platform': 'google_ads',
            'period': f'{days} days',
            'date_range': date_range,
            'metrics': {
                'spend': round(total_spend, 2),
                'revenue': round(total_revenue, 2),
                'impressions': total_impressions,
                'clicks': total_clicks,
                'conversions': round(total_conversions, 2),
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
google_ads_service = GoogleAdsService()
