# 🧪 Local Testing Requirements Analysis

**Date**: November 22, 2025  
**Purpose**: Comprehensive guide for setting up and running tests locally  
**Status**: Complete Analysis

---

## 📋 Executive Summary

This document identifies all requirements, dependencies, and setup steps needed to test the OmniFy Cloud Connect platform locally. The system supports multiple testing approaches: unit tests, integration tests, end-to-end tests, and containerized testing.

**Key Findings:**
- ✅ **Backend Tests**: Can run without external services (uses mocks)
- ⚠️ **Integration Tests**: Require MongoDB (local or Docker)
- ⚠️ **E2E Tests**: Require full stack (backend + frontend + database)
- ✅ **Docker Testing**: Fully containerized option available

---

## 🎯 Testing Approaches

### Approach 1: Unit Tests Only (Fastest, No Dependencies)
**Best for**: Quick development feedback, CI/CD pipelines

### Approach 2: Integration Tests (Requires MongoDB)
**Best for**: Testing database operations, API endpoints

### Approach 3: Full Stack Testing (Requires All Services)
**Best for**: End-to-end validation, pre-deployment testing

### Approach 4: Docker Compose Testing (Recommended)
**Best for**: Production-like environment, consistent testing

---

## 📦 Prerequisites

### Required Software

#### 1. Python Environment
- **Version**: Python 3.11 or higher
- **Installation**:
  ```bash
  # Windows (using Chocolatey)
  choco install python311

  # Or download from python.org
  # Verify installation
  python --version
  ```

#### 2. Node.js & npm
- **Version**: Node.js 18+ and npm 8+
- **Installation**:
  ```bash
  # Windows (using Chocolatey)
  choco install nodejs

  # Verify installation
  node --version
  npm --version
  ```

#### 3. Docker Desktop (Recommended)
- **Version**: Docker Desktop 20.10+ and Docker Compose 2.0+
- **Installation**: Download from https://www.docker.com/products/docker-desktop
- **Purpose**: Containerized testing, MongoDB, Redis

#### 4. Git
- **Version**: Git 2.30+
- **Installation**: Usually pre-installed or download from git-scm.com

---

## 🔧 Environment Setup

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd omnifyproduct
```

### Step 2: Backend Setup

#### Create Virtual Environment
```bash
# Windows (Command Prompt)
cd backend
python -m venv venv
venv\Scripts\activate

# Windows (Git Bash) / Linux / Mac
cd backend
python -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
# Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install test dependencies
pip install -r ../tests/requirements-test.txt
```

#### Configure Environment Variables
```bash
# Copy example file
cp ../env.example .env

# Edit .env with minimum required variables:
```

**Minimum Required Variables for Testing:**
```bash
# Database (can use mock for unit tests)
MONGO_URL=mongodb://localhost:27017
DB_NAME=omnify_cloud

# Authentication
JWT_SECRET_KEY=test-secret-key-minimum-32-characters-long-for-testing
JWT_ALGORITHM=HS256

# AI Services (can use test keys)
OPENAI_API_KEY=sk-test-key
AGENTKIT_API_KEY=test-agentkit-key

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

**Optional Variables (for integration tests):**
```bash
# Redis (optional, can use mock)
REDIS_URL=redis://localhost:6379/0

# Platform Integrations (optional, can use mocks)
GOOGLE_ADS_DEVELOPER_TOKEN=test-token
META_APP_ID=test-app-id
TRIPLEWHALE_API_KEY=test-key
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env
echo "REACT_APP_ENVIRONMENT=development" >> .env
```

---

## 🗄️ Database Setup

### Option 1: Docker MongoDB (Recommended)
```bash
# Start MongoDB in Docker
docker run -d \
  --name omnify-mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_DATABASE=omnify_cloud \
  mongo:7

# Verify connection
docker exec omnify-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Option 2: Local MongoDB Installation
```bash
# Windows (using Chocolatey)
choco install mongodb

# Start MongoDB service
net start MongoDB

# Or manually start
mongod --dbpath C:\data\db
```

### Option 3: MongoDB Atlas (Cloud)
1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create free M0 cluster
3. Get connection string
4. Update `MONGO_URL` in `.env`

### Option 4: Use Mocks (Unit Tests Only)
- Tests use `mongomock` for unit tests
- No database required for unit tests
- Integration tests require real MongoDB

---

## 🧪 Running Tests

### Backend Tests

#### Unit Tests (No External Dependencies)
```bash
# Run all unit tests
pytest tests/ -m unit -v

# Run specific test file
pytest tests/test_auth_service.py -v

# Run with coverage
pytest tests/ -m unit --cov=backend --cov-report=html

# Run in parallel (faster)
pytest tests/ -m unit -n auto
```

#### Integration Tests (Requires MongoDB)
```bash
# Ensure MongoDB is running
docker ps | grep mongo

# Run integration tests
pytest tests/ -m integration -v

# Run specific integration test
pytest tests/test_api_integration.py -v
```

#### All Backend Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing

# Coverage report location: htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=Login

# Run E2E tests (requires backend running)
npm run test:e2e
```

### Integration Tests (Service Communication)

```bash
# Test service-to-service communication
pytest tests/integration/test_service_communication.py -v

# Requires:
# - Service authentication configured
# - Services running (or mocked)
```

---

## 🐳 Docker-Based Testing

### Option 1: Docker Compose (Recommended)

#### Monolith Deployment Testing
```bash
# Windows (Command Prompt)
docker compose -f ops\docker\docker-compose.monolith.yml up --build

# Windows (Git Bash) / Linux / Mac
docker compose -f ops/docker/docker-compose.monolith.yml up --build

# Run tests in container
docker compose -f ops/docker/docker-compose.monolith.yml exec api pytest tests/ -v
```

#### Microservices Deployment Testing
```bash
# Start all services
docker compose -f ops/docker/docker-compose.microservices.yml up --build

# Test specific service
docker compose -f ops/docker/docker-compose.microservices.yml exec auth-service pytest tests/ -v

# Test service communication
python scripts/test_hybrid_deployment.py
```

### Option 2: Individual Containers

```bash
# Build test image
docker build -f ops/docker/Dockerfile.backend -t omnify-backend-test .

# Run tests in container
docker run --rm \
  -v ${PWD}/tests:/app/tests \
  -v ${PWD}/backend:/app/backend \
  omnify-backend-test \
  pytest tests/ -v
```

---

## 📊 Test Categories

### 1. Unit Tests
**Location**: `tests/test_*.py`  
**Markers**: `@pytest.mark.unit`  
**Dependencies**: None (uses mocks)  
**Run Time**: < 1 minute

**Test Files:**
- `test_auth_service.py` - Authentication service tests
- `test_backend_services.py` - Backend service tests
- `test_user_models.py` - Data model tests
- `test_platform_manager.py` - Platform manager tests

**Run Command:**
```bash
pytest tests/ -m unit -v
```

### 2. Integration Tests
**Location**: `tests/test_*_integration.py`  
**Markers**: `@pytest.mark.integration`  
**Dependencies**: MongoDB (local or Docker)  
**Run Time**: 2-5 minutes

**Test Files:**
- `test_api_integration.py` - API endpoint tests
- `test_database_integration.py` - Database operation tests
- `test_platform_integration.py` - Platform integration tests
- `tests/integration/test_service_communication.py` - Service communication tests

**Run Command:**
```bash
# Ensure MongoDB is running
pytest tests/ -m integration -v
```

### 3. End-to-End Tests
**Location**: `tests/test_e2e_*.py`, `frontend/src/__tests__/e2e/`  
**Markers**: `@pytest.mark.e2e`  
**Dependencies**: Backend + Frontend + MongoDB  
**Run Time**: 5-10 minutes

**Test Files:**
- `test_e2e_comprehensive.py` - Comprehensive E2E tests
- `test_e2e_user_journeys.py` - User journey tests
- Frontend Cypress tests

**Run Command:**
```bash
# Start backend and frontend first
pytest tests/ -m e2e -v

# Or frontend E2E
cd frontend
npm run test:e2e
```

### 4. Performance Tests
**Location**: `tests/test_performance_*.py`  
**Markers**: `@pytest.mark.performance`  
**Dependencies**: MongoDB  
**Run Time**: 5-15 minutes

**Test Files:**
- `test_performance_benchmarks.py` - Performance benchmarks
- `test_performance_load.py` - Load tests
- `test_performance_comprehensive.py` - Comprehensive performance tests

**Run Command:**
```bash
pytest tests/ -m performance -v
```

### 5. Security Tests
**Location**: `tests/test_security_*.py`, `tests/test_owasp_*.py`  
**Markers**: `@pytest.mark.security`  
**Dependencies**: None  
**Run Time**: 2-5 minutes

**Test Files:**
- `test_security_comprehensive.py` - Security tests
- `test_owasp_security.py` - OWASP compliance tests
- `test_authentication.py` - Authentication security tests

**Run Command:**
```bash
pytest tests/ -m security -v

# Also run security scanners
bandit -r backend/ -f json
safety check
```

---

## 🔍 Test Configuration Files

### pytest.ini
**Location**: Root directory  
**Purpose**: Pytest configuration  
**Key Settings**:
- Test discovery paths
- Coverage thresholds (80% minimum)
- Test markers
- Output formats

### conftest.py
**Location**: `tests/conftest.py`, `backend/tests/conftest.py`  
**Purpose**: Shared test fixtures and configuration  
**Key Fixtures**:
- `mock_db` - Mock MongoDB client
- `mock_redis` - Mock Redis client
- `test_client` - FastAPI test client
- `auth_headers` - Authentication headers

### Frontend Test Config
**Location**: `frontend/jest.config.js`, `frontend/cypress.config.js`  
**Purpose**: Jest and Cypress configuration

---

## 🚀 Quick Start Commands

### Minimal Setup (Unit Tests Only)
```bash
# 1. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Run unit tests (no database needed)
pytest tests/ -m unit -v
```

### Full Setup (All Tests)
```bash
# 1. Start MongoDB in Docker
docker run -d --name mongodb -p 27017:27017 mongo:7

# 2. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp ../env.example .env
# Edit .env with MongoDB URL

# 3. Setup frontend
cd ../frontend
npm install
echo "REACT_APP_BACKEND_URL=http://localhost:8000" > .env

# 4. Run all tests
cd ..
pytest tests/ -v
cd frontend && npm test
```

### Docker Setup (Easiest)
```bash
# 1. Create .env file from env.example
cp env.example .env
# Edit .env with your values

# 2. Start all services
docker compose -f ops/docker/docker-compose.monolith.yml up --build

# 3. Run tests
docker compose -f ops/docker/docker-compose.monolith.yml exec api pytest tests/ -v
```

---

## 📋 Environment Variables Reference

### Critical (Required for Tests)
| Variable | Description | Example | Required For |
|----------|-------------|---------|--------------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` | Integration tests |
| `DB_NAME` | Database name | `omnify_cloud` | All tests |
| `JWT_SECRET_KEY` | JWT signing key | `test-secret-32-chars` | Auth tests |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | AI tests |
| `AGENTKIT_API_KEY` | AgentKit API key | `test-key` | AgentKit tests |

### Important (Recommended)
| Variable | Description | Example | Required For |
|----------|-------------|---------|--------------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | Caching tests |
| `ENVIRONMENT` | Environment name | `development` | All tests |
| `LOG_LEVEL` | Logging level | `INFO` | All tests |
| `DEBUG` | Debug mode | `true` | Development |

### Optional (Platform Integrations)
- `GOOGLE_ADS_*` - Google Ads integration
- `META_*` - Meta Ads integration
- `TRIPLEWHALE_API_KEY` - TripleWhale integration
- `HUBSPOT_API_KEY` - HubSpot integration
- `KLAVIYO_API_KEY` - Klaviyo integration

---

## 🛠️ Test Utilities

### Test Scripts
**Location**: `scripts/` directory

#### run_tests.py
```bash
# Run all tests
python scripts/run_tests.py --all

# Run specific suite
python scripts/run_tests.py --unit
python scripts/run_tests.py --integration
python scripts/run_tests.py --performance

# With coverage
python scripts/run_tests.py --coverage
```

#### test_hybrid_deployment.py
```bash
# Test hybrid deployment
python scripts/test_hybrid_deployment.py
```

### Coverage Reports
**Location**: `htmlcov/index.html`  
**Generate**:
```bash
pytest tests/ --cov=backend --cov-report=html
```

**View**: Open `htmlcov/index.html` in browser

---

## ⚠️ Common Issues & Solutions

### Issue 1: MongoDB Connection Failed
**Error**: `pymongo.errors.ServerSelectionTimeoutError`

**Solutions**:
```bash
# Check if MongoDB is running
docker ps | grep mongo

# Start MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:7

# Or use mock for unit tests
pytest tests/ -m unit  # Doesn't need MongoDB
```

### Issue 2: Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'backend'`

**Solutions**:
```bash
# Ensure you're in the project root
cd /path/to/omnifyproduct

# Install backend as package
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue 3: Port Already in Use
**Error**: `Address already in use`

**Solutions**:
```bash
# Windows: Find process using port
netstat -ano | findstr :8000

# Kill process
taskkill /PID <pid> /F

# Or use different port
export PORT=8001
```

### Issue 4: Frontend Tests Fail
**Error**: `Cannot find module` or `SyntaxError`

**Solutions**:
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Clear Jest cache
npm test -- --clearCache
```

### Issue 5: Test Timeout
**Error**: `TimeoutError` or tests hang

**Solutions**:
```bash
# Increase timeout
pytest tests/ --timeout=600

# Run tests sequentially (not parallel)
pytest tests/ -n 0

# Run specific test to debug
pytest tests/test_specific.py::test_function -v -s
```

---

## 📈 Test Coverage Targets

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| **Overall** | 80%+ | ✅ Met |
| **Critical Components** | 90%+ | ✅ Met |
| **API Endpoints** | 85%+ | ✅ Met |
| **Business Logic** | 90%+ | ✅ Met |
| **Services** | 85%+ | ✅ Met |

**Check Coverage:**
```bash
pytest tests/ --cov=backend --cov-report=term-missing --cov-fail-under=80
```

---

## 🎯 Testing Workflows

### Development Workflow
```bash
# 1. Make code changes
# 2. Run unit tests (fast feedback)
pytest tests/ -m unit -v

# 3. Run integration tests (before commit)
pytest tests/ -m integration -v

# 4. Check coverage
pytest tests/ --cov=backend --cov-report=term-missing
```

### Pre-Commit Workflow
```bash
# 1. Run all tests
pytest tests/ -v

# 2. Run linting
flake8 backend/
black --check backend/

# 3. Run security checks
bandit -r backend/
safety check

# 4. Run frontend tests
cd frontend && npm test
```

### CI/CD Workflow
```bash
# All tests run automatically in CI
# See .github/workflows/ for configuration
```

---

## 📚 Additional Resources

### Documentation
- **Testing Guide**: `docs/TESTING_GUIDE.md`
- **Environment Setup**: `docs/ENVIRONMENT_SETUP_GUIDE.md`
- **Deployment Guide**: `docs/DEPLOYMENT_GUIDE_HYBRID.md`
- **Quick Start**: `QUICK_START.md`

### Test Examples
- **Unit Test Example**: `tests/test_auth_service.py`
- **Integration Test Example**: `tests/test_api_integration.py`
- **E2E Test Example**: `tests/test_e2e_user_journeys.py`

### Support
- **Issues**: Check GitHub issues
- **Documentation**: See `docs/` directory
- **Questions**: Review test files for examples

---

## ✅ Checklist for Local Testing Setup

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ and npm installed
- [ ] Docker Desktop installed (optional but recommended)
- [ ] Git installed

### Backend Setup
- [ ] Virtual environment created and activated
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Test dependencies installed (`pip install -r tests/requirements-test.txt`)
- [ ] `.env` file created from `env.example`
- [ ] Minimum environment variables configured

### Frontend Setup
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend `.env` file created
- [ ] `REACT_APP_BACKEND_URL` configured

### Database Setup
- [ ] MongoDB running (Docker or local)
- [ ] MongoDB connection verified
- [ ] OR using mocks for unit tests only

### Testing
- [ ] Unit tests pass (`pytest tests/ -m unit`)
- [ ] Integration tests pass (`pytest tests/ -m integration`)
- [ ] Frontend tests pass (`npm test`)
- [ ] Coverage meets targets (80%+)

---

## 🎉 Success Criteria

You have successfully set up local testing when:

1. ✅ Unit tests run without errors
2. ✅ Integration tests connect to MongoDB
3. ✅ Frontend tests pass
4. ✅ Coverage reports generate successfully
5. ✅ All test categories can be run independently

---

**Last Updated**: November 22, 2025  
**Maintained By**: Development Team  
**Questions**: See `docs/` directory or create GitHub issue


