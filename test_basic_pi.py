#!/usr/bin/env python3
"""
Simple test script for Predictive Intelligence Engine
"""
import sys
import asyncio
sys.path.insert(0, '.')
sys.path.insert(0, './backend')

from services.predictive_intelligence import PredictiveIntelligenceEngine

async def test_basic_functionality():
    """Test basic functionality of the Predictive Intelligence Engine"""
    print("Testing Predictive Intelligence Engine...")

    # Create mock database
    class MockDB:
        def __init__(self):
            self.ml_models = MockCollection()
            self.prediction_feedback = MockCollection()
            self.ml_predictions = MockCollection()

    class MockCollection:
        def __init__(self):
            pass

        async def find_one(self, query):
            return None

        async def update_one(self, query, update, upsert=False):
            return None

        async def insert_one(self, document):
            return None

        async def count_documents(self, query):
            return 0

        async def find(self, query=None, limit=None):
            return []

    # Initialize engine
    db = MockDB()
    engine = PredictiveIntelligenceEngine(db)

    print("✓ Engine initialized successfully")

    # Test feature extraction
    creative_data = {
        "creative_id": "test_creative_123",
        "age_days": 10,
        "format": "image",
        "daily_metrics": [
            {"impressions": 1000, "clicks": 50, "spend": 25.0, "frequency": 2.5, "ctr": 0.05},
        ]
    }

    features = engine._extract_fatigue_features(creative_data)
    print(f"✓ Fatigue features extracted: {len(features)} features")

    # Test LTV features
    customer_data = {
        "customer_id": "test_customer_456",
        "purchase_history": [{"value": 150.0}],
        "engagement_metrics": {"email_open_rate": 0.25, "click_rate": 0.15}
    }

    ltv_features = engine._extract_ltv_features(customer_data)
    print(f"✓ LTV features extracted: {len(ltv_features)} features")

    # Test anomaly features
    performance_data = {
        "campaign_id": "test_campaign_789",
        "metrics": {"impressions": 15000, "clicks": 300, "ctr": 0.02}
    }

    anomaly_features = engine._extract_anomaly_features(performance_data)
    print(f"✓ Anomaly features extracted: {len(anomaly_features)} features")

    print("✓ All basic tests passed!")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
