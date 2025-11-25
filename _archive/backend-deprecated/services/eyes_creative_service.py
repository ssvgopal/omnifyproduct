"""
EYES - Creative Intelligence Brain Module
AIDA analysis, creative performance prediction, hook analysis
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
import json

logger = logging.getLogger(__name__)


@dataclass
class AIDAAnalysis:
    """AIDA (Attention, Interest, Desire, Action) analysis result"""
    creative_id: str
    attention_score: float  # 0-100
    interest_score: float  # 0-100
    desire_score: float  # 0-100
    action_score: float  # 0-100
    overall_score: float  # 0-100
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]


@dataclass
class CreativePrediction:
    """Creative performance prediction"""
    creative_id: str
    predicted_ctr: float
    predicted_conversion_rate: float
    predicted_roas: float
    confidence: float
    factors: Dict[str, float]
    recommendation: str


class EyesCreativeService:
    """EYES - Creative Intelligence Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._ai_api_key = os.environ.get('EMERGENT_LLM_KEY') or os.environ.get('OPENAI_API_KEY')
        self._ai_available = self._ai_api_key is not None
    
    def _get_llm_chat(self, system_message: str):
        """Get LLM chat instance"""
        if not self._ai_available:
            return None
        return LlmChat(
            api_key=self._ai_api_key,
            session_id=f"eyes_{datetime.utcnow().timestamp()}",
            system_message=system_message
        ).with_model("openai", "gpt-4o-mini")
    
    async def analyze_aida(
        self,
        creative_id: str,
        creative_content: Dict[str, Any]
    ) -> AIDAAnalysis:
        """Perform AIDA analysis on creative content"""
        try:
            # Extract content elements
            headline = creative_content.get("headline", "")
            description = creative_content.get("description", "")
            image_url = creative_content.get("image_url", "")
            call_to_action = creative_content.get("call_to_action", "")
            
            if self._ai_available:
                # Use AI for AIDA analysis
                chat = self._get_llm_chat(
                    "You are an expert marketing creative analyst. Analyze creatives using AIDA framework."
                )
                
                prompt = f"""Analyze this creative using the AIDA framework (Attention, Interest, Desire, Action).

Headline: {headline}
Description: {description}
Call to Action: {call_to_action}
Image: {image_url if image_url else 'No image provided'}

Provide analysis in JSON format:
{{
  "attention_score": 0-100 (how well it grabs attention),
  "interest_score": 0-100 (how well it maintains interest),
  "desire_score": 0-100 (how well it creates desire),
  "action_score": 0-100 (how well it drives action),
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["recommendation1", "recommendation2"]
}}

Return only valid JSON."""
                
                message = UserMessage(text=prompt)
                response = await chat.send_message(message)
                
                try:
                    analysis_data = json.loads(response)
                except:
                    # Fallback if not valid JSON
                    analysis_data = self._rule_based_aida(creative_content)
            else:
                # Rule-based analysis
                analysis_data = self._rule_based_aida(creative_content)
            
            # Calculate overall score
            overall_score = (
                analysis_data.get("attention_score", 50) * 0.3 +
                analysis_data.get("interest_score", 50) * 0.25 +
                analysis_data.get("desire_score", 50) * 0.25 +
                analysis_data.get("action_score", 50) * 0.2
            )
            
            return AIDAAnalysis(
                creative_id=creative_id,
                attention_score=analysis_data.get("attention_score", 50),
                interest_score=analysis_data.get("interest_score", 50),
                desire_score=analysis_data.get("desire_score", 50),
                action_score=analysis_data.get("action_score", 50),
                overall_score=overall_score,
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                recommendations=analysis_data.get("recommendations", [])
            )
            
        except Exception as e:
            logger.error(f"Error analyzing AIDA: {e}")
            # Return default analysis
            return AIDAAnalysis(
                creative_id=creative_id,
                attention_score=50,
                interest_score=50,
                desire_score=50,
                action_score=50,
                overall_score=50,
                strengths=[],
                weaknesses=["Analysis unavailable"],
                recommendations=["Review creative manually"]
            )
    
    def _rule_based_aida(self, creative_content: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based AIDA analysis fallback"""
        headline = creative_content.get("headline", "")
        description = creative_content.get("description", "")
        cta = creative_content.get("call_to_action", "")
        
        # Attention score (headline quality)
        attention_score = 50
        if len(headline) > 0:
            attention_score += min(20, len(headline) / 5)  # Length bonus
            if any(word in headline.lower() for word in ["free", "new", "limited", "now"]):
                attention_score += 15
            if "?" in headline or "!" in headline:
                attention_score += 10
        
        # Interest score (description quality)
        interest_score = 50
        if len(description) > 50:
            interest_score += min(25, len(description) / 10)
        
        # Desire score (benefits and value proposition)
        desire_score = 50
        benefit_words = ["save", "earn", "get", "win", "improve", "better"]
        if any(word in (headline + description).lower() for word in benefit_words):
            desire_score += 20
        
        # Action score (CTA quality)
        action_score = 50
        if cta:
            action_score += 20
            strong_ctas = ["buy", "sign up", "get started", "learn more", "shop now"]
            if any(cta_word in cta.lower() for cta_word in strong_ctas):
                action_score += 15
        
        return {
            "attention_score": min(100, attention_score),
            "interest_score": min(100, interest_score),
            "desire_score": min(100, desire_score),
            "action_score": min(100, action_score),
            "strengths": ["Basic structure present"],
            "weaknesses": ["AI analysis unavailable - using rule-based scoring"],
            "recommendations": ["Enable AI analysis for better insights"]
        }
    
    async def predict_creative_performance(
        self,
        creative_id: str,
        creative_content: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> CreativePrediction:
        """Predict creative performance"""
        try:
            # Get AIDA analysis
            aida = await self.analyze_aida(creative_id, creative_content)
            
            # Base predictions on AIDA scores
            # Higher AIDA scores correlate with better performance
            predicted_ctr = (aida.attention_score / 100) * 3.0  # Base CTR ~3%
            predicted_conversion_rate = (aida.action_score / 100) * 5.0  # Base conversion ~5%
            predicted_roas = (aida.overall_score / 100) * 2.5  # Base ROAS ~2.5x
            
            # Adjust based on historical data if available
            if historical_data and len(historical_data) > 0:
                avg_ctr = sum(d.get("ctr", 0) for d in historical_data) / len(historical_data)
                avg_conv = sum(d.get("conversion_rate", 0) for d in historical_data) / len(historical_data)
                
                # Blend historical and predicted
                predicted_ctr = (predicted_ctr * 0.3) + (avg_ctr * 0.7)
                predicted_conversion_rate = (predicted_conversion_rate * 0.3) + (avg_conv * 0.7)
                confidence = 0.8
            else:
                confidence = 0.5
            
            # Factors influencing prediction
            factors = {
                "aida_score": aida.overall_score / 100,
                "attention": aida.attention_score / 100,
                "action": aida.action_score / 100,
                "historical_data_available": len(historical_data) > 0 if historical_data else False
            }
            
            # Recommendation
            if aida.overall_score >= 80:
                recommendation = "High-performing creative. Deploy with confidence."
            elif aida.overall_score >= 60:
                recommendation = "Good creative. Consider minor improvements based on recommendations."
            else:
                recommendation = "Creative needs improvement. Review weaknesses and recommendations."
            
            return CreativePrediction(
                creative_id=creative_id,
                predicted_ctr=predicted_ctr,
                predicted_conversion_rate=predicted_conversion_rate,
                predicted_roas=predicted_roas,
                confidence=confidence,
                factors=factors,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error predicting creative performance: {e}")
            raise
    
    async def identify_hook_patterns(
        self,
        top_performers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify hook patterns from top-performing creatives"""
        try:
            if not top_performers:
                return {"patterns": [], "recommendations": []}
            
            # Analyze common elements in top performers
            headlines = [c.get("headline", "") for c in top_performers]
            descriptions = [c.get("description", "") for c in top_performers]
            
            # Extract common words/phrases
            from collections import Counter
            headline_words = []
            for h in headlines:
                headline_words.extend(h.lower().split())
            
            word_freq = Counter(headline_words)
            common_words = [word for word, count in word_freq.most_common(10) if count > 1]
            
            patterns = {
                "common_headline_words": common_words,
                "headline_length_avg": sum(len(h) for h in headlines) / len(headlines),
                "description_length_avg": sum(len(d) for d in descriptions) / len(descriptions),
                "sample_size": len(top_performers)
            }
            
            recommendations = [
                f"Consider using words like: {', '.join(common_words[:5])}",
                f"Optimal headline length: ~{int(patterns['headline_length_avg'])} characters",
                "Test variations of top-performing creatives"
            ]
            
            return {
                "patterns": patterns,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error identifying hook patterns: {e}")
            return {"patterns": {}, "recommendations": []}

