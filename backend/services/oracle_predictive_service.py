"""
ORACLE - Predictive Intelligence Brain Module
Creative fatigue prediction, LTV forecasting, performance anomaly detection
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import base64

logger = logging.getLogger(__name__)


@dataclass
class FatiguePrediction:
    """Creative fatigue prediction result"""
    creative_id: str
    campaign_id: str
    days_until_fatigue: int
    confidence: float
    current_performance: float
    predicted_performance: float
    recommendation: str
    urgency: str  # low, medium, high, critical


@dataclass
class LTVForecast:
    """LTV (Lifetime Value) forecast result"""
    customer_id: str
    forecasted_ltv: float
    confidence_interval: tuple
    days_forecast: int
    factors: Dict[str, float]
    risk_score: float


class OraclePredictiveService:
    """ORACLE - Predictive Intelligence Brain Module"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.fatigue_model = None
        self.ltv_model = None
        self.scaler = StandardScaler()
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models or initialize new ones"""
        try:
            # Try to load from database
            model_doc = self.db.ml_models.find_one({"type": "fatigue_prediction"})
            if model_doc and model_doc.get("model_data"):
                self.fatigue_model = pickle.loads(base64.b64decode(model_doc["model_data"]))
            
            model_doc = self.db.ml_models.find_one({"type": "ltv_forecast"})
            if model_doc and model_doc.get("model_data"):
                self.ltv_model = pickle.loads(base64.b64decode(model_doc["model_data"]))
        except Exception as e:
            logger.warning(f"Could not load models: {e}. Will use rule-based predictions.")
    
    async def predict_creative_fatigue(
        self,
        creative_id: str,
        campaign_id: str,
        performance_history: List[Dict[str, Any]]
    ) -> FatiguePrediction:
        """Predict when a creative will experience fatigue"""
        try:
            if not performance_history or len(performance_history) < 7:
                return FatiguePrediction(
                    creative_id=creative_id,
                    campaign_id=campaign_id,
                    days_until_fatigue=14,  # Default
                    confidence=0.5,
                    current_performance=0.0,
                    predicted_performance=0.0,
                    recommendation="Insufficient data for prediction. Monitor for 7+ days.",
                    urgency="low"
                )
            
            # Extract features from performance history
            recent_performance = performance_history[-7:]  # Last 7 days
            older_performance = performance_history[:-7] if len(performance_history) > 7 else []
            
            # Calculate metrics
            recent_ctr = np.mean([p.get("ctr", 0) for p in recent_performance])
            older_ctr = np.mean([p.get("ctr", 0) for p in older_performance]) if older_performance else recent_ctr
            
            recent_conversion_rate = np.mean([p.get("conversion_rate", 0) for p in recent_performance])
            older_conversion_rate = np.mean([p.get("conversion_rate", 0) for p in older_performance]) if older_performance else recent_conversion_rate
            
            # Calculate decline rate
            ctr_decline = (older_ctr - recent_ctr) / older_ctr if older_ctr > 0 else 0
            conversion_decline = (older_conversion_rate - recent_conversion_rate) / older_conversion_rate if older_conversion_rate > 0 else 0
            
            # Days since creative started
            days_active = len(performance_history)
            
            # Rule-based prediction (can be replaced with ML model)
            if ctr_decline > 0.3 or conversion_decline > 0.3:
                # Rapid decline - fatigue imminent
                days_until_fatigue = max(1, 7 - days_active // 2)
                urgency = "critical"
                recommendation = "Creative showing significant performance decline. Replace immediately."
            elif ctr_decline > 0.15 or conversion_decline > 0.15:
                # Moderate decline - fatigue approaching
                days_until_fatigue = max(3, 14 - days_active // 2)
                urgency = "high"
                recommendation = "Creative performance declining. Prepare replacement creative."
            elif days_active > 21:
                # Long-running creative - likely fatigued soon
                days_until_fatigue = max(5, 21 - days_active)
                urgency = "medium"
                recommendation = "Creative has been running for extended period. Consider refreshing."
            else:
                # Stable performance
                days_until_fatigue = max(7, 14 - days_active // 3)
                urgency = "low"
                recommendation = "Creative performing well. Monitor for changes."
            
            # Confidence based on data quality
            confidence = min(0.9, 0.5 + (len(performance_history) / 30) * 0.4)
            
            # Predict future performance
            predicted_performance = recent_ctr * (1 - ctr_decline * 0.5)
            
            return FatiguePrediction(
                creative_id=creative_id,
                campaign_id=campaign_id,
                days_until_fatigue=int(days_until_fatigue),
                confidence=confidence,
                current_performance=recent_ctr,
                predicted_performance=predicted_performance,
                recommendation=recommendation,
                urgency=urgency
            )
            
        except Exception as e:
            logger.error(f"Error predicting creative fatigue: {e}")
            raise
    
    async def forecast_ltv(
        self,
        customer_id: str,
        customer_data: Dict[str, Any],
        days: int = 90
    ) -> LTVForecast:
        """Forecast customer lifetime value"""
        try:
            # Extract features
            days_since_signup = customer_data.get("days_since_signup", 0)
            total_revenue = customer_data.get("total_revenue", 0)
            monthly_recurring = customer_data.get("monthly_recurring", 0)
            engagement_score = customer_data.get("engagement_score", 50)
            churn_risk = customer_data.get("churn_risk", 0.1)
            
            # Simple LTV calculation (can be enhanced with ML)
            if monthly_recurring > 0:
                # Subscription-based
                avg_monthly_value = monthly_recurring
                expected_months = max(1, (1 - churn_risk) * 12)  # Expected months before churn
                base_ltv = avg_monthly_value * expected_months
            else:
                # Transaction-based
                avg_transaction = total_revenue / max(1, customer_data.get("transaction_count", 1))
                expected_transactions = max(1, (1 - churn_risk) * 6)  # Expected transactions
                base_ltv = avg_transaction * expected_transactions
            
            # Adjust based on engagement
            engagement_multiplier = 0.5 + (engagement_score / 100) * 0.5
            forecasted_ltv = base_ltv * engagement_multiplier
            
            # Confidence interval (simplified)
            confidence_range = forecasted_ltv * 0.2  # ±20%
            confidence_interval = (
                max(0, forecasted_ltv - confidence_range),
                forecasted_ltv + confidence_range
            )
            
            # Risk score (inverse of confidence)
            risk_score = min(1.0, churn_risk + (1 - engagement_score / 100) * 0.3)
            
            # Factors influencing LTV
            factors = {
                "engagement": engagement_score / 100,
                "churn_risk": churn_risk,
                "tenure": min(1.0, days_since_signup / 365),
                "revenue_history": min(1.0, total_revenue / 10000)
            }
            
            return LTVForecast(
                customer_id=customer_id,
                forecasted_ltv=forecasted_ltv,
                confidence_interval=confidence_interval,
                days_forecast=days,
                factors=factors,
                risk_score=risk_score
            )
            
        except Exception as e:
            logger.error(f"Error forecasting LTV: {e}")
            raise
    
    async def detect_performance_anomalies(
        self,
        campaign_id: str,
        performance_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect performance anomalies in campaign data"""
        try:
            if len(performance_data) < 7:
                return []
            
            # Extract metrics
            metrics = ["ctr", "conversion_rate", "cost_per_conversion", "roas"]
            anomalies = []
            
            for metric in metrics:
                values = [p.get(metric, 0) for p in performance_data]
                
                if not values or all(v == 0 for v in values):
                    continue
                
                # Use Isolation Forest for anomaly detection
                if self.fatigue_model is None:
                    # Simple statistical method
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    
                    if std_val == 0:
                        continue
                    
                    # Z-score method
                    recent_values = values[-3:]  # Last 3 days
                    for i, val in enumerate(recent_values):
                        z_score = abs((val - mean_val) / std_val)
                        if z_score > 2.5:  # Significant anomaly
                            anomalies.append({
                                "metric": metric,
                                "value": val,
                                "expected": mean_val,
                                "deviation": z_score,
                                "severity": "high" if z_score > 3 else "medium",
                                "date": performance_data[-(3-i)]["date"] if "date" in performance_data[-(3-i)] else None
                            })
                else:
                    # Use ML model
                    X = np.array(values).reshape(-1, 1)
                    predictions = self.fatigue_model.predict(X)
                    
                    for i, (val, pred) in enumerate(zip(recent_values, predictions[-3:])):
                        if pred == -1:  # Anomaly detected
                            anomalies.append({
                                "metric": metric,
                                "value": val,
                                "expected": mean_val,
                                "deviation": abs(val - mean_val) / std_val if std_val > 0 else 0,
                                "severity": "high",
                                "date": performance_data[-(3-i)]["date"] if "date" in performance_data[-(3-i)] else None
                            })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    async def train_fatigue_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """Train creative fatigue prediction model"""
        try:
            # Prepare features
            X = []
            y = []
            
            for sample in training_data:
                features = [
                    sample.get("days_active", 0),
                    sample.get("ctr", 0),
                    sample.get("conversion_rate", 0),
                    sample.get("impressions", 0),
                    sample.get("decline_rate", 0)
                ]
                X.append(features)
                y.append(sample.get("fatigue_days", 14))  # Target: days until fatigue
            
            if len(X) < 10:
                logger.warning("Insufficient training data")
                return False
            
            # Train model
            X = np.array(X)
            y = np.array(y)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Save model
            model_data = base64.b64encode(pickle.dumps(model)).decode()
            await self.db.ml_models.update_one(
                {"type": "fatigue_prediction"},
                {
                    "$set": {
                        "type": "fatigue_prediction",
                        "model_data": model_data,
                        "trained_at": datetime.utcnow(),
                        "training_samples": len(X)
                    }
                },
                upsert=True
            )
            
            self.fatigue_model = model
            logger.info(f"Fatigue prediction model trained with {len(X)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training fatigue model: {e}")
            return False

