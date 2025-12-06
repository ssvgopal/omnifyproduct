"""
Unified AI Service
Handles interactions with multiple LLM providers (OpenAI, Anthropic, Gemini, Grok, OpenRouter)
"""
import httpx
from typing import Dict, List, Any, Optional
from services.api_key_service import api_key_service
import json

class AIService:
    """Unified service for multiple AI/LLM providers"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def get_api_key(self, organization_id: str, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        return await api_key_service.get_api_key(organization_id, provider, 'api_key')
    
    # ========== OPENAI ==========
    
    async def openai_chat(
        self,
        organization_id: str,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        OpenAI Chat Completion
        
        Args:
            organization_id: Organization UUID
            messages: List of {role: str, content: str}
            model: Model name (gpt-4o, gpt-4o-mini, gpt-4-turbo, etc.)
            temperature: 0-2, controls randomness
            max_tokens: Maximum tokens in response
        """
        api_key = await self.get_api_key(organization_id, 'openai')
        if not api_key:
            return {'error': 'OpenAI API key not configured'}
        
        try:
            response = await self.client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'provider': 'openai',
                    'model': model,
                    'content': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'raw_response': data
                }
            else:
                return {'error': f"OpenAI API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    # ========== ANTHROPIC CLAUDE ==========
    
    async def anthropic_chat(
        self,
        organization_id: str,
        messages: List[Dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Anthropic Claude Chat
        
        Args:
            organization_id: Organization UUID
            messages: List of {role: str, content: str}
            model: Model name (claude-3-5-sonnet, claude-3-haiku, etc.)
            max_tokens: Maximum tokens in response
        """
        api_key = await self.get_api_key(organization_id, 'anthropic')
        if not api_key:
            return {'error': 'Anthropic API key not configured'}
        
        try:
            response = await self.client.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': messages,
                    'max_tokens': max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'provider': 'anthropic',
                    'model': model,
                    'content': data['content'][0]['text'],
                    'usage': data.get('usage', {}),
                    'raw_response': data
                }
            else:
                return {'error': f"Anthropic API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    # ========== GOOGLE GEMINI ==========
    
    async def gemini_chat(
        self,
        organization_id: str,
        prompt: str,
        model: str = "gemini-pro"
    ) -> Dict[str, Any]:
        """
        Google Gemini Chat
        
        Args:
            organization_id: Organization UUID
            prompt: Text prompt
            model: Model name (gemini-pro, gemini-pro-vision)
        """
        api_key = await self.get_api_key(organization_id, 'gemini')
        if not api_key:
            return {'error': 'Gemini API key not configured'}
        
        try:
            response = await self.client.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{
                        'parts': [{'text': prompt}]
                    }]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'success': True,
                    'provider': 'gemini',
                    'model': model,
                    'content': content,
                    'raw_response': data
                }
            else:
                return {'error': f"Gemini API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    # ========== GROK ==========
    
    async def grok_chat(
        self,
        organization_id: str,
        messages: List[Dict[str, str]],
        model: str = "grok-beta",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Grok (X.AI) Chat
        
        Args:
            organization_id: Organization UUID
            messages: List of {role: str, content: str}
            model: Model name (grok-beta)
            temperature: 0-2, controls randomness
            max_tokens: Maximum tokens in response
        """
        api_key = await self.get_api_key(organization_id, 'grok')
        if not api_key:
            return {'error': 'Grok API key not configured'}
        
        try:
            response = await self.client.post(
                'https://api.x.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': messages,
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'provider': 'grok',
                    'model': model,
                    'content': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'raw_response': data
                }
            else:
                return {'error': f"Grok API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    # ========== OPENROUTER ==========
    
    async def openrouter_chat(
        self,
        organization_id: str,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-4o-mini",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        OpenRouter Unified API
        
        Args:
            organization_id: Organization UUID
            messages: List of {role: str, content: str}
            model: Model identifier (openai/gpt-4o, anthropic/claude-3.5-sonnet, etc.)
            max_tokens: Maximum tokens in response
        """
        api_key = await self.get_api_key(organization_id, 'openrouter')
        if not api_key:
            return {'error': 'OpenRouter API key not configured'}
        
        try:
            response = await self.client.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://omnify.ai',
                    'X-Title': 'Omnify Cloud Connect'
                },
                json={
                    'model': model,
                    'messages': messages,
                    'max_tokens': max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'provider': 'openrouter',
                    'model': model,
                    'content': data['choices'][0]['message']['content'],
                    'usage': data.get('usage', {}),
                    'raw_response': data
                }
            else:
                return {'error': f"OpenRouter API Error: {response.status_code}", 'details': response.text}
        
        except Exception as e:
            return {'error': str(e)}
    
    # ========== UNIFIED INTERFACE ==========
    
    async def chat(
        self,
        organization_id: str,
        messages: List[Dict[str, str]],
        provider: str = "openai",
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Unified chat interface - automatically routes to correct provider
        
        Args:
            organization_id: Organization UUID
            messages: List of {role: str, content: str}
            provider: 'openai', 'anthropic', 'gemini', 'grok', 'openrouter'
            model: Optional model override
            **kwargs: Additional provider-specific parameters
        """
        if provider == 'openai':
            return await self.openai_chat(
                organization_id, messages,
                model=model or "gpt-4o-mini",
                **kwargs
            )
        elif provider == 'anthropic':
            return await self.anthropic_chat(
                organization_id, messages,
                model=model or "claude-3-5-sonnet-20241022",
                **kwargs
            )
        elif provider == 'gemini':
            # Convert messages to single prompt for Gemini
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            return await self.gemini_chat(
                organization_id, prompt,
                model=model or "gemini-pro"
            )
        elif provider == 'grok':
            return await self.grok_chat(
                organization_id, messages,
                model=model or "grok-beta",
                **kwargs
            )
        elif provider == 'openrouter':
            return await self.openrouter_chat(
                organization_id, messages,
                model=model or "openai/gpt-4o-mini",
                **kwargs
            )
        else:
            return {'error': f'Unknown provider: {provider}'}
    
    # ========== HIGH-LEVEL AI FUNCTIONS ==========
    
    async def analyze_creative(
        self,
        organization_id: str,
        creative_text: str,
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """
        Analyze creative copy using AI
        Returns AIDA scores and recommendations
        """
        prompt = f"""Analyze this marketing creative and provide scores for the AIDA framework:

Creative Text: "{creative_text}"

Provide your analysis in the following JSON format:
{{
    "attention": <score 0-100>,
    "interest": <score 0-100>,
    "desire": <score 0-100>,
    "action": <score 0-100>,
    "overall_score": <average score>,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""
        
        messages = [
            {"role": "system", "content": "You are an expert marketing analyst specializing in creative analysis."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat(organization_id, messages, provider)
        
        if not result.get('success'):
            return result
        
        try:
            # Parse JSON from response
            content = result['content']
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            analysis = json.loads(content)
            return {
                'success': True,
                'analysis': analysis,
                'provider': result['provider']
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}',
                'raw_content': result.get('content')
            }
    
    async def generate_recommendations(
        self,
        organization_id: str,
        performance_data: Dict[str, Any],
        provider: str = "openai"
    ) -> Dict[str, Any]:
        """Generate marketing recommendations based on performance data"""
        prompt = f"""Based on the following marketing performance data, provide 3 actionable recommendations:

Performance Data:
{json.dumps(performance_data, indent=2)}

Provide recommendations in JSON format:
{{
    "recommendations": [
        {{
            "title": "Recommendation title",
            "description": "Detailed description",
            "impact": "high/medium/low",
            "effort": "low/medium/high",
            "category": "budget/creative/targeting/other"
        }}
    ]
}}"""
        
        messages = [
            {"role": "system", "content": "You are an expert marketing strategist providing data-driven recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat(organization_id, messages, provider)
        
        if not result.get('success'):
            return result
        
        try:
            content = result['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            recommendations = json.loads(content)
            return {
                'success': True,
                'recommendations': recommendations.get('recommendations', []),
                'provider': result['provider']
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}',
                'raw_content': result.get('content')
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Singleton instance
ai_service = AIService()
