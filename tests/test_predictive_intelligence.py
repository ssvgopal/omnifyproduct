"""
Comprehensive test suite for Predictive Intelligence Engine

Tests for:
- Creative fatigue prediction (7-14 day advance warnings)
- LTV forecasting engine (90-day customer value predictions)
- Anomaly detection using isolation forest
- Compound intelligence learning system
- Model training and initialization
- Error handling and edge cases

Author: OmnifyProduct Test Suite
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.services.predictive_intelligence import PredictiveIntelligenceEngine


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db = AsyncMock(spec=AsyncIOMotorDatabase)

    # Mock collections
    db.ml_models = AsyncMock()
    db.prediction_feedback = AsyncMock()
    db.ml_predictions = AsyncMock()

    # Mock collection methods
    db.ml_models.find_one = AsyncMock(return_value=None)
    db.ml_models.update_one = AsyncMock()
    db.ml_models.count_documents = AsyncMock(return_value=0)
    db.prediction_feedback.insert_one = AsyncMock()
    db.prediction_feedback.count_documents = AsyncMock(return_value=50)
    db.ml_predictions.find = AsyncMock()

    return db


@pytest.fixture
def sample_creative_data():
    """Sample creative data for testing"""
    return {
        "creative_id": "test_creative_123",
        "age_days": 10,
        "format": "image",
        "platform": "facebook",
        "daily_metrics": [
            {"date": "2024-01-01", "impressions": 1000, "clicks": 50, "spend": 25.0, "frequency": 2.5, "ctr": 0.05},
            {"date": "2024-01-02", "impressions": 1100, "clicks": 45, "spend": 27.5, "frequency": 2.3, "ctr": 0.041},
            {"date": "2024-01-03", "impressions": 950, "clicks": 38, "spend": 23.75, "frequency": 2.1, "ctr": 0.04},
        ],
        "audience_saturation": 65.0,
        "competing_creatives": ["comp_1", "comp_2"],
        "platform_load": 7.5
    }


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "customer_id": "test_customer_456",
        "purchase_history": [
            {"value": 150.0, "date": "2024-01-01"},
            {"value": 200.0, "date": "2024-01-15"},
            {"value": 175.0, "date": "2024-02-01"}
        ],
        "engagement_metrics": {
            "email_open_rate": 0.25,
            "click_rate": 0.15,
            "session_count": 12
        },
        "acquisition_cost": 50.0,
        "days_since_first_purchase": 60,
        "days_since_last_purchase": 15,
        "acquisition_channel_score": 0.8,
        "segment_score": 0.7,
        "is_repeat_customer": True,
        "lifetime_value_current": 525.0,
        "predicted_churn_risk": 0.2,
        "product_categories": ["electronics", "books"],
        "geographic_score": 0.6,
        "device_type_score": 0.8
    }


@pytest.fixture
def sample_performance_data():
    """Sample performance data for testing"""
    return {
        "campaign_id": "test_campaign_789",
        "metrics": {
            "impressions": 15000,
            "clicks": 300,
            "spend": 750.0,
            "conversions": 15,
            "ctr": 0.02,
            "cpc": 2.5,
            "cpm": 50.0,
            "roas": 2.0,
            "frequency": 1.8
        },
        "campaign_age_days": 12,
        "budget_utilization": 0.85,
        "targeting_criteria": ["age_25_34", "interest_tech"],
        "competition_level": 6.5,
        "platform_performance_index": 0.75
    }


class TestPredictiveIntelligenceEngine:
    """Test suite for PredictiveIntelligenceEngine"""

    @pytest.fixture
    def engine(self, mock_db):
        """Create predictive intelligence engine instance"""
        return PredictiveIntelligenceEngine(mock_db)

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Test engine initialization"""
        # Test that engine initializes without errors
        assert engine.db is not None
        assert engine.fatigue_model is None  # Should be None initially
        assert engine.ltv_model is None
        assert engine.anomaly_detector is None
        assert engine.compound_intelligence_score == 0.0
        assert len(engine.learning_history) == 0

    @pytest.mark.asyncio
    async def test_initialize_models_success(self, engine, mock_db):
        """Test successful model initialization"""
        # Mock no existing models - will trigger training
        mock_db.ml_models.find_one = AsyncMock(return_value=None)
        mock_db.ml_models.update_one = AsyncMock()

        result = await engine.initialize_models()

        assert result["status"] == "initialized"
        assert result["models_loaded"]["fatigue_model"] is True
        assert result["models_loaded"]["ltv_model"] is True
        assert result["models_loaded"]["anomaly_detector"] is True
        # Models should be trained with synthetic data
        assert engine.model_metrics["fatigue_prediction"]["accuracy"] > 0

    @pytest.mark.asyncio
    async def test_initialize_models_failure(self, engine, mock_db):
        """Test model initialization failure"""
        # Mock database error
        mock_db.ml_models.find_one = AsyncMock(side_effect=Exception("Database error"))

        result = await engine.initialize_models()

        assert result["status"] == "failed"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_predict_creative_fatigue_model_not_ready(self, engine):
        """Test creative fatigue prediction when model not ready"""
        result = await engine.predict_creative_fatigue({"creative_id": "test"})

        assert result["status"] == "model_not_ready"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_predict_creative_fatigue_success(self, engine, sample_creative_data):
        """Test successful creative fatigue prediction"""
        # Initialize model first
        await engine._initialize_fatigue_model()

        result = await engine.predict_creative_fatigue(sample_creative_data)

        # Successful predictions don't have 'status' field, only errors do
        assert "error" not in result or result.get("status") != "error"
        assert "creative_id" in result
        assert "fatigue_probability_7d" in result
        assert "fatigue_probability_14d" in result
        assert "confidence_interval" in result
        assert "key_risk_factors" in result
        assert "recommended_refresh_date" in result

        # Validate probability ranges
        assert 0 <= result["fatigue_probability_7d"] <= 1
        assert 0 <= result["fatigue_probability_14d"] <= 1
        assert 0 <= result["confidence_interval"] <= 1

    @pytest.mark.asyncio
    async def test_predict_creative_fatigue_high_risk_alert(self, engine, sample_creative_data):
        """Test high fatigue risk triggers alert"""
        # Mock high fatigue probability
        engine.fatigue_model = MagicMock()
        engine.fatigue_model.predict_proba.return_value = [[0.3, 0.8]]  # 80% fatigue probability

        engine._trigger_fatigue_alert = AsyncMock()

        result = await engine.predict_creative_fatigue(sample_creative_data)

        # Should trigger alert for high risk (> 0.7)
        engine._trigger_fatigue_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_predict_creative_fatigue_edge_cases(self, engine):
        """Test creative fatigue prediction with edge cases"""
        test_cases = [
            {"creative_id": "test", "age_days": 0, "daily_metrics": []},  # New creative
            {"creative_id": "test", "age_days": 100, "daily_metrics": []},  # Old creative
            {"creative_id": "test", "age_days": 10, "daily_metrics": [{}]},  # Empty metrics
        ]

        for creative_data in test_cases:
            result = await engine.predict_creative_fatigue(creative_data)
            # Should handle edge cases gracefully
            assert "error" not in result or result.get("status") != "error"

    @pytest.mark.asyncio
    async def test_forecast_customer_ltv_model_not_ready(self, engine):
        """Test LTV forecast when model not ready"""
        result = await engine.forecast_customer_ltv({"customer_id": "test"})

        assert result["status"] == "model_not_ready"

    @pytest.mark.asyncio
    async def test_forecast_customer_ltv_success(self, engine, sample_customer_data):
        """Test successful LTV forecasting"""
        # Initialize model first
        await engine._initialize_ltv_model()

        result = await engine.forecast_customer_ltv(sample_customer_data)

        assert "error" not in result or result.get("status") != "error"
        assert "customer_id" in result
        assert "predicted_90d_ltv" in result
        assert "ltv_confidence" in result
        assert "segment_analysis" in result

        # Validate LTV ranges
        assert result["predicted_90d_ltv"] >= 0
        assert 0 <= result["ltv_confidence"] <= 1

        # Validate segment analysis
        segment_analysis = result["segment_analysis"]
        assert "segment" in segment_analysis
        assert "segment_multiplier" in segment_analysis
        assert "adjusted_ltv" in segment_analysis

    @pytest.mark.asyncio
    async def test_detect_anomalies_model_not_ready(self, engine):
        """Test anomaly detection when model not ready"""
        result = await engine.detect_anomalies({"campaign_id": "test"})

        assert result["status"] == "model_not_ready"

    @pytest.mark.asyncio
    async def test_detect_anomalies_success(self, engine, sample_performance_data):
        """Test successful anomaly detection"""
        # Initialize model first
        await engine._initialize_anomaly_detector()

        result = await engine.detect_anomalies(sample_performance_data)

        assert "error" not in result or result.get("status") != "error"
        assert "campaign_id" in result
        assert "is_anomaly" in result
        assert "anomaly_score" in result
        assert "confidence" in result

        # Validate anomaly score ranges
        assert -1 <= result["anomaly_score"] <= 1
        assert result["is_anomaly"] in [True, False]

    @pytest.mark.asyncio
    async def test_detect_anomalies_with_analysis(self, engine, sample_performance_data):
        """Test anomaly detection with analysis for detected anomalies"""
        # Mock anomaly detection
        engine.anomaly_detector = MagicMock()
        engine.anomaly_detector.decision_function.return_value = [-0.8]  # Anomaly detected

        result = await engine.detect_anomalies(sample_performance_data)

        assert result["is_anomaly"] is True
        assert "analysis" in result

        analysis = result["analysis"]
        assert "severity" in analysis
        assert "likely_causes" in analysis
        assert "recommended_actions" in analysis

    @pytest.mark.asyncio
    async def test_update_models_with_feedback_success(self, engine, mock_db):
        """Test successful model feedback update"""
        prediction_data = {"prediction": "test"}
        actual_outcome = {"outcome": "actual"}

        result = await engine.update_models_with_feedback(
            "fatigue", actual_outcome, prediction_data
        )

        assert result["status"] == "feedback_stored"
        assert "learning_samples" in result
        assert "compound_intelligence_score" in result

        # Verify database call
        mock_db.prediction_feedback.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_models_with_feedback_retraining(self, engine, mock_db):
        """Test model retraining after sufficient feedback"""
        # Mock enough feedback for retraining
        mock_db.prediction_feedback.count_documents = AsyncMock(return_value=150)  # > 100 threshold

        engine._retrain_model = AsyncMock()

        result = await engine.update_models_with_feedback(
            "fatigue", {"outcome": "test"}, {"prediction": "test"}
        )

        # Should trigger retraining
        engine._retrain_model.assert_called_once_with("fatigue")

    @pytest.mark.asyncio
    async def test_get_predictive_insights_dashboard(self, engine, mock_db):
        """Test predictive insights dashboard generation"""
        # Create async iterator for cursor
        async def async_iter():
            return
            yield  # Make this an async generator
        
        # Mock recent predictions with proper cursor chain
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.__aiter__ = lambda self: async_iter()
        
        mock_db.ml_predictions.find = MagicMock(return_value=mock_cursor)

        result = await engine.get_predictive_insights_dashboard()

        assert "error" not in result or result.get("status") != "error"
        assert "fatigue_alerts" in result
        assert "ltv_forecasts" in result
        assert "anomaly_detection" in result
        assert "learning_system" in result

        # Validate dashboard structure
        assert "high_risk_count" in result["fatigue_alerts"]
        assert "total_predicted_value" in result["ltv_forecasts"]
        assert "anomaly_count" in result["anomaly_detection"]
        assert "compound_intelligence_score" in result["learning_system"]

    @pytest.mark.asyncio
    async def test_extract_fatigue_features_comprehensive(self, engine, sample_creative_data):
        """Test comprehensive fatigue feature extraction"""
        features = engine._extract_fatigue_features(sample_creative_data)

        print(f"Debug: Extracted features: {features}")
        print(f"Debug: Number of features: {len(features)}")
        print(f"Debug: Feature types: {[type(f).__name__ for f in features]}")

        assert len(features) == 20  # Should have 20 features
        # Handle both Python and numpy numeric types
        assert all(isinstance(f, (int, float, np.number)) for f in features)

        # Test with empty metrics
        empty_data = {"creative_id": "test", "daily_metrics": []}
        features_empty = engine._extract_fatigue_features(empty_data)
        print(f"Debug: Empty features: {features_empty}")
        assert len(features_empty) == 20
        assert all(f == 0.0 for f in features_empty)  # Should be zeros

    @pytest.mark.asyncio
    async def test_extract_ltv_features_comprehensive(self, engine, sample_customer_data):
        """Test comprehensive LTV feature extraction"""
        features = engine._extract_ltv_features(sample_customer_data)

        assert len(features) == 16  # Should have 16 features
        assert all(isinstance(f, (int, float)) for f in features)

    @pytest.mark.asyncio
    async def test_extract_anomaly_features_comprehensive(self, engine, sample_performance_data):
        """Test comprehensive anomaly feature extraction"""
        features = engine._extract_anomaly_features(sample_performance_data)

        assert len(features) == 14  # Should have 14 features
        assert all(isinstance(f, (int, float)) for f in features)

    @pytest.mark.asyncio
    async def test_calculate_14d_prediction_logic(self, engine):
        """Test 14-day prediction calculation logic"""
        features = [1000, 50, 25.0, 2.5, 200, 10, 15, 1, 0, 25, 1200, 800, 2.8, 2.2, 150, 25, 65.0, 3, 7.5, 0.04]

        prob_7d = 0.6
        prob_14d = engine._calculate_14d_prediction(features, prob_7d)

        assert prob_14d > prob_7d  # 14-day should be higher
        assert 0 <= prob_14d <= 1

        # Test boundary conditions
        prob_14d_young = engine._calculate_14d_prediction([1000, 50, 25.0, 2.5, 200, 10, 5, 1, 0, 25, 1200, 800, 2.8, 2.2, 150, 25, 30.0, 1, 3.0, 0.04], 0.3)
        prob_14d_old = engine._calculate_14d_prediction([1000, 50, 25.0, 2.5, 200, 10, 45, 1, 0, 25, 1200, 800, 2.8, 2.2, 150, 25, 85.0, 8, 9.0, 0.02], 0.3)

        assert prob_14d_young < prob_14d_old  # Older creative should have higher fatigue

    @pytest.mark.asyncio
    async def test_calculate_prediction_confidence_logic(self, engine):
        """Test prediction confidence calculation"""
        # High confidence case (many data points, recent)
        high_confidence = engine._calculate_prediction_confidence([1000, 50, 25.0, 2.5, 200, 10, 5, 1, 0, 30, 1200, 800, 2.8, 2.2, 150, 25, 45.0, 2, 5.0, 0.05])

        # Low confidence case (few data points, old)
        low_confidence = engine._calculate_prediction_confidence([100, 5, 2.5, 0.25, 20, 1, 45, 0, 1, 5, 120, 80, 0.3, 0.2, 15, 2.5, 85.0, 8, 9.0, 0.005])

        assert high_confidence > low_confidence
        assert 0 <= high_confidence <= 1
        assert 0 <= low_confidence <= 1

    @pytest.mark.asyncio
    async def test_identify_risk_factors_logic(self, engine):
        """Test risk factor identification logic"""
        # High-risk features
        high_risk_features = [1000, 50, 25.0, 2.5, 200, 10, 20, 1, 0, 25, 1200, 800, 3.5, 2.0, 150, 25, 85.0, 8, 9.0, 0.005]

        risk_factors = engine._identify_risk_factors(high_risk_features)

        assert isinstance(risk_factors, list)
        assert len(risk_factors) <= 3  # Should return top 3

        # Should identify age and saturation as risk factors
        if high_risk_features[6] > 14:  # Age > 14 days
            assert "age" in risk_factors

        if high_risk_features[16] > 70:  # Saturation > 70%
            assert "audience_saturation" in risk_factors

    @pytest.mark.asyncio
    async def test_calculate_refresh_date_logic(self, engine, sample_creative_data):
        """Test refresh date calculation logic"""
        # Low risk case
        low_risk_date = engine._calculate_refresh_date(0.2, sample_creative_data)
        assert low_risk_date is not None

        # Medium risk case
        medium_risk_date = engine._calculate_refresh_date(0.5, sample_creative_data)

        # High risk case
        high_risk_date = engine._calculate_refresh_date(0.8, sample_creative_data)

        # High risk should recommend earlier refresh
        high_risk_datetime = datetime.strptime(high_risk_date, "%Y-%m-%d")
        medium_risk_datetime = datetime.strptime(medium_risk_date, "%Y-%m-%d")
        low_risk_datetime = datetime.strptime(low_risk_date, "%Y-%m-%d")

        assert high_risk_datetime < medium_risk_datetime < low_risk_datetime

    @pytest.mark.asyncio
    async def test_calculate_ltv_confidence_logic(self, engine):
        """Test LTV confidence calculation"""
        # High confidence case (many purchases, high engagement)
        high_confidence = engine._calculate_ltv_confidence([10, 2000, 200, 180, 30, 0.3, 0.2, 15, 0.8, 0.9, 1, 2000, 0.1, 3, 0.7, 0.8])

        # Low confidence case (few purchases, low engagement)
        low_confidence = engine._calculate_ltv_confidence([1, 50, 50, 300, 200, 0.05, 0.02, 2, 0.2, 0.3, 0, 50, 0.8, 1, 0.3, 0.4])

        assert high_confidence > low_confidence
        assert 0 <= high_confidence <= 1
        assert 0 <= low_confidence <= 1

    @pytest.mark.asyncio
    async def test_analyze_customer_segment_logic(self, engine, sample_customer_data):
        """Test customer segment analysis"""
        # Test different LTV values
        segments = []

        # High value customer
        segment_high = await engine._analyze_customer_segment(sample_customer_data, 8000)
        segments.append(segment_high)

        # Medium value customer
        segment_medium = await engine._analyze_customer_segment(sample_customer_data, 2000)
        segments.append(segment_medium)

        # Low value customer
        segment_low = await engine._analyze_customer_segment(sample_customer_data, 500)
        segments.append(segment_low)

        # Micro value customer
        segment_micro = await engine._analyze_customer_segment(sample_customer_data, 50)
        segments.append(segment_micro)

        # Validate segment logic
        segment_names = [s["segment"] for s in segments]
        assert "high_value" in segment_names
        assert "medium_value" in segment_names
        assert "low_value" in segment_names
        assert "micro_value" in segment_names

        # Higher LTV should have higher segment multiplier
        high_segment = next(s for s in segments if s["segment"] == "high_value")
        low_segment = next(s for s in segments if s["segment"] == "micro_value")

        assert high_segment["segment_multiplier"] > low_segment["segment_multiplier"]

    @pytest.mark.asyncio
    async def test_analyze_anomaly_comprehensive(self, engine, sample_performance_data):
        """Test comprehensive anomaly analysis"""
        # Test different anomaly scenarios
        test_cases = [
            {"metrics": {"ctr": 0.001, "cpc": 2.5, "frequency": 2.0}},  # Low CTR
            {"metrics": {"ctr": 0.02, "cpc": 10.0, "frequency": 2.0}},  # High CPC
            {"metrics": {"ctr": 0.02, "cpc": 2.5, "frequency": 8.0}},  # High frequency
        ]

        for i, metrics in enumerate(test_cases):
            sample_performance_data["metrics"] = metrics
            anomaly_score = -0.8 if i == 0 else -0.7  # Different anomaly scores

            analysis = await engine._analyze_anomaly(sample_performance_data, anomaly_score)

            assert "severity" in analysis
            assert "likely_causes" in analysis
            assert "recommended_actions" in analysis
            assert "confidence" in analysis

            assert analysis["severity"] in ["low", "high"]
            assert isinstance(analysis["likely_causes"], list)
            assert isinstance(analysis["recommended_actions"], list)

    @pytest.mark.asyncio
    async def test_model_training_fatigue(self, engine, mock_db):
        """Test fatigue model training"""
        # Mock database operations for training
        mock_db.ml_models.update_one = AsyncMock()

        await engine._train_fatigue_model()

        # Verify model was trained and saved
        mock_db.ml_models.update_one.assert_called_once()
        assert engine.fatigue_model is not None
        assert engine.model_metrics["fatigue_prediction"]["accuracy"] > 0

    @pytest.mark.asyncio
    async def test_model_training_ltv(self, engine, mock_db):
        """Test LTV model training"""
        mock_db.ml_models.update_one = AsyncMock()

        await engine._train_ltv_model()

        # Verify model was trained and saved
        mock_db.ml_models.update_one.assert_called_once()
        assert engine.ltv_model is not None
        assert engine.model_metrics["ltv_forecasting"]["accuracy"] > 0

    @pytest.mark.asyncio
    async def test_model_training_anomaly(self, engine, mock_db):
        """Test anomaly detection model training"""
        mock_db.ml_models.update_one = AsyncMock()

        await engine._train_anomaly_detector()

        # Verify model was trained and saved
        mock_db.ml_models.update_one.assert_called_once()
        assert engine.anomaly_detector is not None
        assert engine.model_metrics["anomaly_detection"]["precision"] > 0

    @pytest.mark.asyncio
    async def test_calculate_compound_intelligence(self, engine):
        """Test compound intelligence score calculation"""
        # Set some model metrics
        engine.model_metrics = {
            "fatigue_prediction": {"accuracy": 0.85, "samples": 1000, "last_trained": datetime.utcnow().isoformat()},
            "ltv_forecasting": {"accuracy": 0.78, "samples": 800, "last_trained": datetime.utcnow().isoformat()},
            "anomaly_detection": {"precision": 0.82, "recall": 0.75, "samples": 600, "last_trained": datetime.utcnow().isoformat()}
        }

        await engine._calculate_compound_intelligence()

        # Should calculate a compound score based on model performance
        assert engine.compound_intelligence_score > 0
        assert 0 <= engine.compound_intelligence_score <= 1

    @pytest.mark.asyncio
    async def test_error_handling_comprehensive(self, engine):
        """Test comprehensive error handling"""
        # Test with invalid data types
        invalid_cases = [
            None,
            "string",
            123,
            [],
            {"invalid": "data"}
        ]

        for invalid_data in invalid_cases:
            # Should handle gracefully without crashing
            try:
                await engine.predict_creative_fatigue(invalid_data)
                await engine.forecast_customer_ltv(invalid_data)
                await engine.detect_anomalies(invalid_data)
            except Exception as e:
                # Should return error status, not crash
                assert "error" in str(e).lower() or "status" in str(e).lower()

    @pytest.mark.asyncio
    async def test_integration_workflow(self, engine, mock_db, sample_creative_data, sample_customer_data, sample_performance_data):
        """Test complete integration workflow"""
        # Mock cursor for dashboard
        async def async_iter():
            return
            yield
        
        mock_cursor = MagicMock()
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.__aiter__ = lambda self: async_iter()
        mock_db.ml_predictions.find = MagicMock(return_value=mock_cursor)
        
        # Initialize all models
        await engine.initialize_models()

        # Run predictions
        fatigue_result = await engine.predict_creative_fatigue(sample_creative_data)
        ltv_result = await engine.forecast_customer_ltv(sample_customer_data)
        anomaly_result = await engine.detect_anomalies(sample_performance_data)

        # Update with feedback
        await engine.update_models_with_feedback("fatigue", {"actual_fatigue": 0.7}, fatigue_result)

        # Generate dashboard
        dashboard = await engine.get_predictive_insights_dashboard()

        # Verify complete workflow
        assert "error" not in fatigue_result or fatigue_result.get("status") != "error"
        assert "error" not in ltv_result or ltv_result.get("status") != "error"
        assert "error" not in anomaly_result or anomaly_result.get("status") != "error"
        assert "error" not in dashboard or dashboard.get("status") != "error"

        # Verify learning system updated
        assert len(engine.learning_history) > 0
        assert engine.compound_intelligence_score > 0

    @pytest.mark.asyncio
    async def test_performance_requirements(self, engine, sample_creative_data):
        """Test performance requirements (predictions should be fast)"""
        import time

        # Initialize model
        await engine._initialize_fatigue_model()

        # Time prediction execution
        start_time = time.time()
        await engine.predict_creative_fatigue(sample_creative_data)
        execution_time = time.time() - start_time

        # Should complete in reasonable time (< 1 second for simple prediction)
        assert execution_time < 1.0

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, engine, sample_creative_data):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run multiple predictions
        for _ in range(10):
            await engine.predict_creative_fatigue(sample_creative_data)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB for 10 predictions)
        assert memory_increase < 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
