/**
 * AI API Client
 * Handles communication with backend AI/LLM services
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  organization_id: string;
  messages: ChatMessage[];
  provider?: 'openai' | 'anthropic' | 'gemini' | 'grok' | 'openrouter';
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface CreativeAnalysisRequest {
  organization_id: string;
  creative_text: string;
  provider?: string;
}

export interface CreativeAnalysis {
  attention: number;
  interest: number;
  desire: number;
  action: number;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface Recommendation {
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'low' | 'medium' | 'high';
  category: string;
}

class AIAPIClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  // ========== CHAT ==========

  async chat(request: ChatRequest) {
    const response = await fetch(`${this.baseUrl}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`AI chat failed: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== CREATIVE ANALYSIS ==========

  async analyzeCreative(
    organizationId: string,
    creativeText: string,
    provider: string = 'openai'
  ): Promise<{ success: boolean; analysis?: CreativeAnalysis; error?: string }> {
    const response = await fetch(`${this.baseUrl}/ai/analyze-creative`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization_id: organizationId,
        creative_text: creativeText,
        provider
      })
    });

    if (!response.ok) {
      throw new Error(`Creative analysis failed: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== RECOMMENDATIONS ==========

  async generateRecommendations(
    organizationId: string,
    performanceData: any,
    provider: string = 'openai'
  ): Promise<{ success: boolean; recommendations?: Recommendation[]; error?: string }> {
    const response = await fetch(`${this.baseUrl}/ai/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        organization_id: organizationId,
        performance_data: performanceData,
        provider
      })
    });

    if (!response.ok) {
      throw new Error(`Recommendation generation failed: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== PROVIDERS ==========

  async listProviders() {
    const response = await fetch(`${this.baseUrl}/ai/providers`);
    
    if (!response.ok) {
      throw new Error(`Failed to list providers: ${response.statusText}`);
    }

    return response.json();
  }

  // ========== HEALTH CHECK ==========

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/ai/health`);
    return response.json();
  }
}

// Singleton instance
export const aiAPI = new AIAPIClient();
