#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
sys.path.insert(0, './backend')

from services.predictive_intelligence import PredictiveIntelligenceEngine

# Test the feature extraction directly
creative_data = {
    'creative_id': 'test_creative_123',
    'age_days': 10,
    'format': 'image',
    'daily_metrics': [
        {'impressions': 1000, 'clicks': 50, 'spend': 25.0, 'frequency': 2.5, 'ctr': 0.05},
    ]
}

engine = PredictiveIntelligenceEngine(None)
features = engine._extract_fatigue_features(creative_data)

print(f'Features: {features}')
print(f'Length: {len(features)}')
print(f'Types: {[type(f).__name__ for f in features]}')

# Test empty case
empty_data = {"creative_id": "test", "daily_metrics": []}
empty_features = engine._extract_fatigue_features(empty_data)
print(f'Empty features: {empty_features}')
print(f'Empty length: {len(empty_features)}')
