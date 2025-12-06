"""
AI/LLM Integration Routes
Handles API endpoints for AI services
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])

# ========== REQUEST MODELS ==========

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    organization_id: str
    messages: List[ChatMessage]
    provider: str = Field(default="openai", description="AI provider: openai, anthropic, gemini, grok, openrouter")
    model: Optional[str] = Field(default=None, description="Optional model override")
    temperature: Optional[float] = Field(default=0.7, description="Temperature 0-2")
    max_tokens: Optional[int] = Field(default=1000, description="Max tokens in response")

class CreativeAnalysisRequest(BaseModel):
    organization_id: str
    creative_text: str = Field(..., description="Creative copy to analyze")
    provider: str = Field(default="openai", description="AI provider")

class RecommendationRequest(BaseModel):
    organization_id: str
    performance_data: Dict[str, Any] = Field(..., description="Performance data for analysis")
    provider: str = Field(default="openai", description="AI provider")

# ========== ROUTES ==========

@router.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Unified chat completion across all AI providers
    
    Supports: OpenAI, Anthropic, Gemini, Grok, OpenRouter
    """
    messages = [m.dict() for m in request.messages]
    
    result = await ai_service.chat(
        organization_id=request.organization_id,
        messages=messages,
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@router.post("/analyze-creative")
async def analyze_creative(request: CreativeAnalysisRequest):
    """
    Analyze marketing creative using AI
    
    Returns AIDA scores (Attention, Interest, Desire, Action) and recommendations
    """
    result = await ai_service.analyze_creative(
        organization_id=request.organization_id,
        creative_text=request.creative_text,
        provider=request.provider
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@router.post("/recommendations")
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate AI-powered marketing recommendations
    
    Based on performance data, provides actionable recommendations
    """
    result = await ai_service.generate_recommendations(
        organization_id=request.organization_id,
        performance_data=request.performance_data,
        provider=request.provider
    )
    
    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    
    return result

@router.get("/providers")
async def list_providers():
    """List available AI providers"""
    return {
        'providers': [
            {
                'id': 'openai',
                'name': 'OpenAI',
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo']
            },
            {
                'id': 'anthropic',
                'name': 'Anthropic Claude',
                'models': ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307']
            },
            {
                'id': 'gemini',
                'name': 'Google Gemini',
                'models': ['gemini-pro', 'gemini-pro-vision']
            },
            {
                'id': 'grok',
                'name': 'Grok (X.AI)',
                'models': ['grok-beta']
            },
            {
                'id': 'openrouter',
                'name': 'OpenRouter',
                'models': ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'google/gemini-pro']
            }
        ]
    }

@router.get("/health")
async def health_check():
    """Health check endpoint for AI service"""
    return {
        'status': 'healthy',
        'service': 'ai',
        'message': 'AI service is operational'
    }
