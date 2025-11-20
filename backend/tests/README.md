# Testing Guide

## Test Structure

```
backend/tests/
├── conftest.py              # Pytest fixtures
├── api/                     # API route tests
│   ├── test_auth_routes.py
│   ├── test_campaign_routes.py
│   └── test_integration_routes.py
├── services/                # Service tests
│   ├── test_campaign_service.py
│   └── test_mfa_service.py
├── integration/             # Integration tests
│   └── test_api_flows.py
├── e2e/                      # End-to-end tests
│   └── test_e2e_scenarios.py
└── load/                     # Load tests
    ├── locustfile.py
    └── k6_test.js
```

## Running Tests

### Unit Tests
```bash
# Run all tests
pytest backend/tests/

# Run specific test file
pytest backend/tests/api/test_auth_routes.py

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run with coverage threshold (fail if below 70%)
pytest backend/tests/ --cov=backend --cov-report=term --cov-fail-under=70
```

### Integration Tests
```bash
pytest backend/tests/integration/
```

### E2E Tests
```bash
# Requires Playwright or Cypress setup
pytest backend/tests/e2e/
```

### Load Tests

#### Using Locust
```bash
# Install Locust
pip install locust

# Run Locust
locust -f backend/tests/load/locustfile.py

# Access web UI at http://localhost:8089
```

#### Using k6
```bash
# Install k6 (see https://k6.io/docs/getting-started/installation/)
# Run k6 test
k6 run backend/tests/load/k6_test.js

# Run with custom base URL
k6 run -e BASE_URL=http://staging.example.com backend/tests/load/k6_test.js
```

## Coverage Target

**Target**: 70%+ test coverage

**Current**: ~30% (in progress)

## Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test interactions between components
3. **E2E Tests**: Test complete user journeys
4. **Load Tests**: Test system performance under load

## Writing New Tests

1. Follow the existing test structure
2. Use fixtures from `conftest.py`
3. Mock external dependencies (database, APIs)
4. Test both success and failure cases
5. Use descriptive test names

## CI Integration

Tests run automatically on:
- Pull requests
- Commits to main branch
- Coverage threshold enforced (70%)

