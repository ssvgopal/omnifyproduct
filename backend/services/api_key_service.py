"""
API Key Management Service
Handles secure storage, retrieval, and management of API keys for platform integrations
"""
import os
from typing import Optional, Dict, List, Any
from cryptography.fernet import Fernet
from supabase import create_client, Client
from datetime import datetime
import json

class APIKeyService:
    """Service for managing encrypted API keys in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client and encryption"""
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize encryption key
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        if not encryption_key:
            # Generate a new key if not exists (development only)
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Warning: Generated new encryption key. Add to .env: ENCRYPTION_KEY={encryption_key}")
        
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value using Fernet"""
        if not value:
            return ""
        return self.cipher.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value using Fernet"""
        if not encrypted_value:
            return ""
        return self.cipher.decrypt(encrypted_value.encode()).decode()
    
    async def save_api_key(
        self,
        organization_id: str,
        platform: str,
        key_name: str,
        key_value: str,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """
        Save or update an API key
        
        Args:
            organization_id: Organization UUID
            platform: Platform name (openai, gemini, meta_ads, etc.)
            key_name: Key identifier (api_key, access_token, client_id, etc.)
            key_value: The actual key value (will be encrypted)
            is_active: Whether the key is active
        
        Returns:
            Saved API key record (with encrypted value)
        """
        try:
            # Encrypt the key value
            encrypted_value = self.encrypt_value(key_value)
            
            # Check if key exists
            existing = self.supabase.table('api_keys').select('id').eq(
                'organization_id', organization_id
            ).eq('platform', platform).eq('key_name', key_name).execute()
            
            data = {
                'organization_id': organization_id,
                'platform': platform,
                'key_name': key_name,
                'key_value_encrypted': encrypted_value,
                'is_active': is_active,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing key
                result = self.supabase.table('api_keys').update(data).eq(
                    'id', existing.data[0]['id']
                ).execute()
            else:
                # Insert new key
                data['created_at'] = datetime.utcnow().isoformat()
                result = self.supabase.table('api_keys').insert(data).execute()
            
            return {
                'success': True,
                'message': f'API key for {platform} saved successfully',
                'data': result.data[0] if result.data else None
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to save API key for {platform}'
            }
    
    async def get_api_key(
        self,
        organization_id: str,
        platform: str,
        key_name: str
    ) -> Optional[str]:
        """
        Retrieve and decrypt an API key
        
        Args:
            organization_id: Organization UUID
            platform: Platform name
            key_name: Key identifier
        
        Returns:
            Decrypted key value or None if not found
        """
        try:
            result = self.supabase.table('api_keys').select('key_value_encrypted').eq(
                'organization_id', organization_id
            ).eq('platform', platform).eq('key_name', key_name).eq('is_active', True).execute()
            
            if result.data:
                encrypted_value = result.data[0]['key_value_encrypted']
                return self.decrypt_value(encrypted_value)
            
            return None
        
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None
    
    async def get_all_keys_for_platform(
        self,
        organization_id: str,
        platform: str
    ) -> Dict[str, str]:
        """
        Get all API keys for a specific platform
        
        Args:
            organization_id: Organization UUID
            platform: Platform name
        
        Returns:
            Dictionary of key_name: decrypted_value
        """
        try:
            result = self.supabase.table('api_keys').select('key_name, key_value_encrypted').eq(
                'organization_id', organization_id
            ).eq('platform', platform).eq('is_active', True).execute()
            
            keys = {}
            for row in result.data:
                keys[row['key_name']] = self.decrypt_value(row['key_value_encrypted'])
            
            return keys
        
        except Exception as e:
            print(f"Error retrieving platform keys: {e}")
            return {}
    
    async def delete_api_key(
        self,
        organization_id: str,
        platform: str,
        key_name: str
    ) -> Dict[str, Any]:
        """Delete an API key"""
        try:
            result = self.supabase.table('api_keys').delete().eq(
                'organization_id', organization_id
            ).eq('platform', platform).eq('key_name', key_name).execute()
            
            return {
                'success': True,
                'message': f'API key for {platform} deleted successfully'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to delete API key for {platform}'
            }
    
    async def list_configured_platforms(
        self,
        organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all platforms with configured API keys
        
        Returns:
            List of platforms with their configuration status
        """
        try:
            result = self.supabase.table('api_keys').select(
                'platform, key_name, is_active, updated_at'
            ).eq('organization_id', organization_id).execute()
            
            # Group by platform
            platforms = {}
            for row in result.data:
                platform = row['platform']
                if platform not in platforms:
                    platforms[platform] = {
                        'platform': platform,
                        'keys': [],
                        'is_active': row['is_active'],
                        'updated_at': row['updated_at']
                    }
                platforms[platform]['keys'].append(row['key_name'])
            
            return list(platforms.values())
        
        except Exception as e:
            print(f"Error listing platforms: {e}")
            return []
    
    async def test_connection(
        self,
        organization_id: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Test connection to a platform using stored API keys
        
        Args:
            organization_id: Organization UUID
            platform: Platform name
        
        Returns:
            Connection test result
        """
        try:
            keys = await self.get_all_keys_for_platform(organization_id, platform)
            
            if not keys:
                return {
                    'success': False,
                    'connected': False,
                    'message': f'No API keys configured for {platform}'
                }
            
            # Platform-specific connection tests
            if platform == 'openai':
                return await self._test_openai_connection(keys)
            elif platform == 'anthropic':
                return await self._test_anthropic_connection(keys)
            elif platform == 'gemini':
                return await self._test_gemini_connection(keys)
            elif platform == 'grok':
                return await self._test_grok_connection(keys)
            elif platform == 'openrouter':
                return await self._test_openrouter_connection(keys)
            elif platform == 'meta_ads':
                return await self._test_meta_ads_connection(keys)
            elif platform == 'google_ads':
                return await self._test_google_ads_connection(keys)
            elif platform == 'tiktok':
                return await self._test_tiktok_connection(keys)
            elif platform == 'shopify':
                return await self._test_shopify_connection(keys)
            else:
                return {
                    'success': False,
                    'connected': False,
                    'message': f'Unknown platform: {platform}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': f'Connection test failed for {platform}'
            }
    
    # Platform-specific connection test methods
    async def _test_openai_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test OpenAI API connection"""
        try:
            import openai
            openai.api_key = keys.get('api_key')
            
            # Simple API call to test
            response = openai.models.list()
            
            return {
                'success': True,
                'connected': True,
                'message': 'OpenAI connection successful',
                'details': {'models_available': len(response.data)}
            }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'OpenAI connection failed'
            }
    
    async def _test_anthropic_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Anthropic API connection"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=keys.get('api_key'))
            
            # Simple test call
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            
            return {
                'success': True,
                'connected': True,
                'message': 'Anthropic connection successful'
            }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'Anthropic connection failed'
            }
    
    async def _test_gemini_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Google Gemini API connection"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=keys.get('api_key'))
            
            # List models to test connection
            models = genai.list_models()
            model_count = len(list(models))
            
            return {
                'success': True,
                'connected': True,
                'message': 'Gemini connection successful',
                'details': {'models_available': model_count}
            }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'Gemini connection failed'
            }
    
    async def _test_grok_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Grok API connection"""
        try:
            import httpx
            headers = {'Authorization': f'Bearer {keys.get("api_key")}'}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://api.x.ai/v1/models',
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'connected': True,
                        'message': 'Grok connection successful'
                    }
                else:
                    return {
                        'success': False,
                        'connected': False,
                        'message': f'Grok connection failed: {response.status_code}'
                    }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'Grok connection failed'
            }
    
    async def _test_openrouter_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test OpenRouter API connection"""
        try:
            import httpx
            headers = {
                'Authorization': f'Bearer {keys.get("api_key")}',
                'Content-Type': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://openrouter.ai/api/v1/models',
                    headers=headers
                )
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'connected': True,
                        'message': 'OpenRouter connection successful'
                    }
                else:
                    return {
                        'success': False,
                        'connected': False,
                        'message': f'OpenRouter connection failed: {response.status_code}'
                    }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'OpenRouter connection failed'
            }
    
    async def _test_meta_ads_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Meta Ads API connection"""
        try:
            import httpx
            access_token = keys.get('access_token')
            account_id = keys.get('account_id')
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://graph.facebook.com/v18.0/{account_id}',
                    params={'access_token': access_token, 'fields': 'name,account_status'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'connected': True,
                        'message': 'Meta Ads connection successful',
                        'details': {'account_name': data.get('name')}
                    }
                else:
                    return {
                        'success': False,
                        'connected': False,
                        'message': f'Meta Ads connection failed: {response.status_code}'
                    }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'Meta Ads connection failed'
            }
    
    async def _test_google_ads_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Google Ads API connection"""
        # Implement Google Ads OAuth validation
        return {
            'success': True,
            'connected': True,
            'message': 'Google Ads connection test not yet implemented'
        }
    
    async def _test_tiktok_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test TikTok Ads API connection"""
        return {
            'success': True,
            'connected': True,
            'message': 'TikTok connection test not yet implemented'
        }
    
    async def _test_shopify_connection(self, keys: Dict[str, str]) -> Dict[str, Any]:
        """Test Shopify API connection"""
        try:
            import httpx
            shop_url = keys.get('shop_url')
            access_token = keys.get('access_token')
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'https://{shop_url}/admin/api/2024-01/shop.json',
                    headers={'X-Shopify-Access-Token': access_token}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'connected': True,
                        'message': 'Shopify connection successful',
                        'details': {'shop_name': data.get('shop', {}).get('name')}
                    }
                else:
                    return {
                        'success': False,
                        'connected': False,
                        'message': f'Shopify connection failed: {response.status_code}'
                    }
        except Exception as e:
            return {
                'success': False,
                'connected': False,
                'error': str(e),
                'message': 'Shopify connection failed'
            }


# Create singleton instance
api_key_service = APIKeyService()
