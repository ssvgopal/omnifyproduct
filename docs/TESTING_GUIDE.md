# 🧪 OmniFy Testing Guide

## 📋 Overview

This guide provides comprehensive instructions for testing the OmniFy Cloud Connect platform. The testing suite includes unit tests, integration tests, performance tests, security tests, and code quality checks.

## 🏗️ Testing Architecture

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API endpoints and database integration
- **Performance Tests**: Test system performance under load
- **Security Tests**: Test security vulnerabilities and compliance
- **Load Tests**: Test system behavior under high load
- **Stress Tests**: Test system behavior under extreme conditions

### Test Framework
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting
- **pytest-xdist**: Parallel test execution
- **httpx**: HTTP client for API testing
- **mongomock**: MongoDB mocking for tests

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- MongoDB (for integration tests)
- Redis (for integration tests)
- All dependencies installed

### Installation
```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Install development dependencies
pip install -r backend/requirements.txt
```

### Running Tests
```bash
# Run all tests
python scripts/run_tests.py --all

# Run specific test suites
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --performance

# Run specific test file
python scripts/run_tests.py --test tests/test_backend_services.py

# Generate coverage report
python scripts/run_tests.py --coverage
```

---

## 🧪 Unit Tests

### Purpose
Unit tests verify individual components work correctly in isolation.

### Test Files
- `tests/test_backend_services.py`: Backend service unit tests
- `tests/test_models.py`: Data model tests
- `tests/test_utils.py`: Utility function tests

### Running Unit Tests
```bash
# Run unit tests
pytest tests/test_backend_services.py -m unit -v

# Run with coverage
pytest tests/test_backend_services.py -m unit --cov=backend --cov-report=term-missing
```

### Example Unit Test
```python
@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent execution functionality"""
    client = AgentKitSDKClient("test-api-key")
    
    execution_request = AgentExecutionRequest(
        agent_id="test-agent",
        input_data={"test": "input"},
        context={"user_id": "test-user"}
    )
    
    result = await client.execute_agent(execution_request)
    
    assert result["status"] == "completed"
    assert "execution_id" in result
```

---

## 🔗 Integration Tests

### Purpose
Integration tests verify API endpoints and database operations work correctly together.

### Test Files
- `tests/test_api_integration.py`: API endpoint integration tests
- `tests/test_database_integration.py`: Database integration tests
- `tests/test_platform_integration.py`: Platform integration tests

### Running Integration Tests
```bash
# Run integration tests
pytest tests/test_api_integration.py -m integration -v

# Run with database
pytest tests/test_api_integration.py -m integration --cov=backend
```

### Example Integration Test
```python
@pytest.mark.asyncio
async def test_agentkit_endpoints(async_client):
    """Test AgentKit API endpoints"""
    agent_data = {
        "name": "test-agent",
        "description": "Test agent",
        "agent_type": "workflow",
        "config": {"test": "config"}
    }
    
    response = await async_client.post("/api/agentkit/agents", json=agent_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert "agent_id" in data
```

---

## ⚡ Performance Tests

### Purpose
Performance tests verify system performance under various load conditions.

### Test Files
- `tests/test_performance.py`: Performance and load tests
- `tests/test_benchmarks.py`: Benchmark tests

### Running Performance Tests
```bash
# Run performance tests
pytest tests/test_performance.py -m performance -v

# Run load tests
pytest tests/test_performance.py -m load -v

# Run stress tests
pytest tests/test_performance.py -m stress -v
```

### Performance Benchmarks
- **Agent Execution**: < 100ms average
- **Prediction Generation**: < 50ms average
- **API Response Time**: < 200ms average
- **Database Queries**: < 50ms average

### Example Performance Test
```python
def test_agent_execution_performance():
    """Test agent execution performance benchmarks"""
    execution_times = []
    
    for _ in range(100):
        start_time = time.time()
        # Simulate agent execution
        time.sleep(0.01)
        end_time = time.time()
        execution_times.append(end_time - start_time)
    
    avg_time = statistics.mean(execution_times)
    assert avg_time < 0.1, f"Average execution time too slow: {avg_time:.3f}s"
```

---

## 🔒 Security Tests

### Purpose
Security tests verify the system is secure and compliant.

### Test Files
- `tests/test_security.py`: Security vulnerability tests
- `tests/test_authentication.py`: Authentication tests
- `tests/test_authorization.py`: Authorization tests

### Running Security Tests
```bash
# Run security tests
pytest tests/ -m security -v

# Run security scans
bandit -r backend/ -f json -o security-report.json
safety check --json --output safety-report.json
```

### Security Checks
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Authentication**: JWT token validation
- **Authorization**: Role-based access control
- **Input Validation**: SQL injection prevention
- **XSS Protection**: Cross-site scripting prevention

---

## 📊 Code Coverage

### Coverage Targets
- **Overall Coverage**: 80%+
- **Critical Components**: 90%+
- **API Endpoints**: 85%+
- **Business Logic**: 90%+

### Generating Coverage Reports
```bash
# Generate HTML coverage report
pytest tests/ --cov=backend --cov-report=html

# Generate XML coverage report
pytest tests/ --cov=backend --cov-report=xml

# Generate terminal coverage report
pytest tests/ --cov=backend --cov-report=term-missing
```

### Coverage Reports
- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml`
- **Terminal Report**: Console output

---

## 🔧 Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    load: Load tests
    stress: Stress tests
```

### Test Environment Variables
```bash
# Set test environment
export TESTING=true
export MONGODB_URL=mongodb://localhost:27017/test_omnify
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=test_secret_key
export JWT_SECRET=test_jwt_secret
```

---

## 🐳 Docker Testing

### Running Tests in Docker
```bash
# Build test image
docker build -f ops/docker/Dockerfile.test -t omnify-test .

# Run tests in container
docker run --rm omnify-test pytest tests/ -v

# Run specific test suite
docker run --rm omnify-test pytest tests/test_backend_services.py -m unit
```

### Docker Compose Testing
```bash
# Start test environment
docker compose -f ops/docker/docker-compose.test.yml up -d

# Run tests
docker compose -f ops/docker/docker-compose.test.yml exec app pytest tests/ -v

# Stop test environment
docker compose -f ops/docker/docker-compose.test.yml down
```

---

## 📈 Continuous Integration

### GitHub Actions
The CI/CD pipeline automatically runs tests on every commit:

```yaml
# .github/workflows/ci-cd.yml
- name: Run Tests
  run: |
    python scripts/run_tests.py --all
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### Test Stages
1. **Lint & Format**: Code quality checks
2. **Unit Tests**: Component testing
3. **Integration Tests**: API and database testing
4. **Performance Tests**: Performance benchmarking
5. **Security Tests**: Security vulnerability scanning
6. **Coverage Report**: Code coverage analysis

---

## 🚨 Troubleshooting

### Common Issues

#### Test Database Connection
```bash
# Check MongoDB connection
mongosh --eval "db.adminCommand('ping')"

# Check Redis connection
redis-cli ping
```

#### Test Dependencies
```bash
# Install missing dependencies
pip install -r tests/requirements-test.txt

# Update dependencies
pip install --upgrade -r tests/requirements-test.txt
```

#### Test Failures
```bash
# Run tests with verbose output
pytest tests/ -v -s

# Run specific failing test
pytest tests/test_backend_services.py::TestAgentKitSDKClient::test_create_agent -v

# Run tests with debugging
pytest tests/ --pdb
```

### Performance Issues
```bash
# Run tests in parallel
pytest tests/ -n auto

# Run tests with timeout
pytest tests/ --timeout=300

# Profile slow tests
pytest tests/ --profile
```

---

## 📊 Test Metrics

### Key Metrics
- **Test Coverage**: 80%+ overall
- **Test Execution Time**: < 5 minutes
- **API Response Time**: < 200ms
- **Database Query Time**: < 50ms
- **Memory Usage**: < 500MB
- **CPU Usage**: < 80%

### Test Reports
- **Coverage Report**: `htmlcov/index.html`
- **Performance Report**: `test-results.xml`
- **Security Report**: `security-report.json`
- **JUnit Report**: `test-results.xml`

---

## 🎯 Best Practices

### Writing Tests
1. **Test Naming**: Use descriptive test names
2. **Test Structure**: Follow Arrange-Act-Assert pattern
3. **Test Isolation**: Each test should be independent
4. **Test Data**: Use realistic test data
5. **Test Coverage**: Aim for high coverage

### Test Organization
1. **Group Related Tests**: Use test classes
2. **Use Fixtures**: For common test setup
3. **Mock External Dependencies**: Use mocks for external services
4. **Clean Up**: Clean up test data after tests

### Performance Testing
1. **Baseline Metrics**: Establish performance baselines
2. **Load Testing**: Test under expected load
3. **Stress Testing**: Test beyond expected capacity
4. **Regression Testing**: Detect performance regressions

---

## 📞 Support

### Getting Help
- **Documentation**: Check this guide and inline comments
- **Issues**: Create GitHub issues for test failures
- **Discussions**: Use GitHub discussions for questions
- **Email**: Contact team@omnify.com

### Test Maintenance
- **Regular Updates**: Keep test dependencies updated
- **Test Review**: Review tests during code reviews
- **Test Refactoring**: Refactor tests when code changes
- **Test Documentation**: Document complex test scenarios

---

## 🎉 Success!

If you've followed this guide, you should now have:
- ✅ Comprehensive test suite running
- ✅ High code coverage achieved
- ✅ Performance benchmarks established
- ✅ Security vulnerabilities identified
- ✅ CI/CD pipeline integrated

**Happy Testing!** 🧪
