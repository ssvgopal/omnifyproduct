"""
Data Synchronization Service
Handles automated data pulling from all platforms and storage in Supabase
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from services.meta_ads_service import meta_ads_service
from services.google_ads_service import google_ads_service

class DataSyncService:
    """Service for synchronizing data from all platforms"""
    
    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
        
        if supabase_url and supabase_key:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        else:
            self.supabase = None
            print("Warning: Supabase not configured")
    
    async def sync_platform_data(
        self,
        organization_id: str,
        platform: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Sync data from a specific platform
        
        Args:
            organization_id: Organization UUID
            platform: Platform name (meta_ads, google_ads, etc.)
            days: Number of days to sync
        """
        if platform == 'meta_ads':
            return await self._sync_meta_ads(organization_id, days)
        elif platform == 'google_ads':
            return await self._sync_google_ads(organization_id, days)
        else:
            return {'error': f'Platform not supported: {platform}'}
    
    async def _sync_meta_ads(self, organization_id: str, days: int) -> Dict[str, Any]:
        """Sync Meta Ads data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_range = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        # Fetch insights from Meta
        insights_result = await meta_ads_service.fetch_insights(organization_id, date_range)
        
        if not insights_result.get('success'):
            return insights_result
        
        insights = insights_result.get('insights', [])
        
        # Store in database
        stored_count = 0
        errors = []
        
        for insight in insights:
            try:
                # Upsert daily metrics
                data = {
                    'organization_id': organization_id,
                    'platform': 'meta_ads',
                    'metric_date': insight['date'],
                    'spend': insight['spend'],
                    'revenue': insight['revenue'],
                    'impressions': insight['impressions'],
                    'clicks': insight['clicks'],
                    'conversions': insight['conversions'],
                    'roas': insight['roas'],
                    'ctr': insight['ctr'],
                    'cpc': insight['cpc'],
                    'cpm': insight['cpm'],
                    'raw_data': insight,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                if self.supabase:
                    # Check if record exists
                    existing = self.supabase.table('daily_metrics').select('id').eq(
                        'organization_id', organization_id
                    ).eq('platform', 'meta_ads').eq('metric_date', insight['date']).execute()
                    
                    if existing.data:
                        # Update
                        self.supabase.table('daily_metrics').update(data).eq(
                            'id', existing.data[0]['id']
                        ).execute()
                    else:
                        # Insert
                        self.supabase.table('daily_metrics').insert(data).execute()
                    
                    stored_count += 1
            
            except Exception as e:
                errors.append({'date': insight['date'], 'error': str(e)})
        
        return {
            'success': True,
            'platform': 'meta_ads',
            'synced': stored_count,
            'total': len(insights),
            'errors': errors,
            'date_range': date_range
        }
    
    async def _sync_google_ads(self, organization_id: str, days: int) -> Dict[str, Any]:
        """Sync Google Ads data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        date_range = {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        }
        
        # Fetch metrics from Google Ads
        metrics_result = await google_ads_service.fetch_metrics(organization_id, date_range)
        
        if not metrics_result.get('success'):
            return metrics_result
        
        metrics = metrics_result.get('metrics', [])
        
        # Store in database
        stored_count = 0
        errors = []
        
        for metric in metrics:
            try:
                data = {
                    'organization_id': organization_id,
                    'platform': 'google_ads',
                    'metric_date': metric['date'],
                    'spend': metric['spend'],
                    'revenue': metric['revenue'],
                    'impressions': metric['impressions'],
                    'clicks': metric['clicks'],
                    'conversions': metric['conversions'],
                    'roas': metric['roas'],
                    'ctr': metric['ctr'],
                    'cpc': metric['cpc'],
                    'raw_data': metric,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                if self.supabase:
                    existing = self.supabase.table('daily_metrics').select('id').eq(
                        'organization_id', organization_id
                    ).eq('platform', 'google_ads').eq('metric_date', metric['date']).execute()
                    
                    if existing.data:
                        self.supabase.table('daily_metrics').update(data).eq(
                            'id', existing.data[0]['id']
                        ).execute()
                    else:
                        self.supabase.table('daily_metrics').insert(data).execute()
                    
                    stored_count += 1
            
            except Exception as e:
                errors.append({'date': metric['date'], 'error': str(e)})
        
        return {
            'success': True,
            'platform': 'google_ads',
            'synced': stored_count,
            'total': len(metrics),
            'errors': errors,
            'date_range': date_range
        }
    
    async def sync_all_platforms(self, organization_id: str, days: int = 7) -> Dict[str, Any]:
        """Sync data from all configured platforms"""
        platforms = ['meta_ads', 'google_ads']
        results = {}
        
        for platform in platforms:
            try:
                result = await self.sync_platform_data(organization_id, platform, days)
                results[platform] = result
            except Exception as e:
                results[platform] = {'error': str(e)}
        
        total_synced = sum(r.get('synced', 0) for r in results.values() if isinstance(r, dict))
        
        return {
            'success': True,
            'organization_id': organization_id,
            'platforms_synced': len([r for r in results.values() if r.get('success')]),
            'total_records': total_synced,
            'results': results
        }
    
    async def get_unified_metrics(
        self,
        organization_id: str,
        date_range: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get unified metrics across all platforms from database
        
        Returns aggregated metrics for dashboard
        """
        if not self.supabase:
            return {'error': 'Supabase not configured'}
        
        # Default to last 30 days
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = {
                'start': start_date.strftime('%Y-%m-%d'),
                'end': end_date.strftime('%Y-%m-%d')
            }
        
        try:
            # Fetch all metrics for date range
            result = self.supabase.table('daily_metrics').select('*').eq(
                'organization_id', organization_id
            ).gte('metric_date', date_range['start']).lte('metric_date', date_range['end']).execute()
            
            metrics = result.data
            
            # Group by platform
            platform_metrics = {}
            
            for metric in metrics:
                platform = metric['platform']
                if platform not in platform_metrics:
                    platform_metrics[platform] = {
                        'spend': 0,
                        'revenue': 0,
                        'impressions': 0,
                        'clicks': 0,
                        'conversions': 0
                    }
                
                platform_metrics[platform]['spend'] += float(metric.get('spend', 0))
                platform_metrics[platform]['revenue'] += float(metric.get('revenue', 0))
                platform_metrics[platform]['impressions'] += int(metric.get('impressions', 0))
                platform_metrics[platform]['clicks'] += int(metric.get('clicks', 0))
                platform_metrics[platform]['conversions'] += int(metric.get('conversions', 0))
            
            # Calculate blended metrics
            total_spend = sum(p['spend'] for p in platform_metrics.values())
            total_revenue = sum(p['revenue'] for p in platform_metrics.values())
            total_impressions = sum(p['impressions'] for p in platform_metrics.values())
            total_clicks = sum(p['clicks'] for p in platform_metrics.values())
            total_conversions = sum(p['conversions'] for p in platform_metrics.values())
            
            blended_roas = (total_revenue / total_spend) if total_spend > 0 else 0
            blended_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            blended_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            
            return {
                'success': True,
                'date_range': date_range,
                'blended_metrics': {
                    'spend': round(total_spend, 2),
                    'revenue': round(total_revenue, 2),
                    'impressions': total_impressions,
                    'clicks': total_clicks,
                    'conversions': total_conversions,
                    'roas': round(blended_roas, 2),
                    'ctr': round(blended_ctr, 2),
                    'cpc': round(blended_cpc, 2)
                },
                'platform_breakdown': {
                    platform: {
                        'spend': round(data['spend'], 2),
                        'revenue': round(data['revenue'], 2),
                        'roas': round(data['revenue'] / data['spend'], 2) if data['spend'] > 0 else 0,
                        'impressions': data['impressions'],
                        'clicks': data['clicks'],
                        'conversions': data['conversions']
                    }
                    for platform, data in platform_metrics.items()
                }
            }
        
        except Exception as e:
            return {'error': str(e)}


# Singleton instance
data_sync_service = DataSyncService()
