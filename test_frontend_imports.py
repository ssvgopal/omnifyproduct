#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
sys.path.insert(0, './frontend/src')

# Test basic React component imports
try:
    from components.Dashboard.PredictiveIntelligenceDashboard import default as PredictiveIntelligenceDashboard
    print('SUCCESS: PredictiveIntelligenceDashboard imported successfully')
except ImportError as e:
    print('FAILED: PredictiveIntelligenceDashboard import - ' + str(e))

try:
    from components.ErrorBoundary import default as ErrorBoundary
    print('SUCCESS: ErrorBoundary imported successfully')
except ImportError as e:
    print('FAILED: ErrorBoundary import - ' + str(e))

try:
    from components.ui.button import default as Button
    print('SUCCESS: Button component imported successfully')
except ImportError as e:
    print('FAILED: Button component import - ' + str(e))

print('Test completed')
