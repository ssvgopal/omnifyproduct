#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

try:
    import numpy as np
    print("numpy imported successfully")
except ImportError as e:
    print(f"Failed to import numpy: {e}")

try:
    import pandas as pd
    print("pandas imported successfully")
except ImportError as e:
    print(f"Failed to import pandas: {e}")

try:
    from sklearn.ensemble import RandomForestRegressor
    print("scikit-learn imported successfully")
except ImportError as e:
    print(f"Failed to import scikit-learn: {e}")

try:
    from backend.services.predictive_intelligence import PredictiveIntelligenceEngine
    print("PredictiveIntelligenceEngine imported successfully")
except ImportError as e:
    print(f"Failed to import PredictiveIntelligenceEngine: {e}")
