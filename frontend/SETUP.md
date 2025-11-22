# 🚀 Frontend Setup Guide

**Last Updated**: November 22, 2025  
**Purpose**: Complete setup guide for OmniFy Cloud Connect Frontend

---

## 📋 Prerequisites

### Required Software
- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 8.0.0 or higher (comes with Node.js)
- **Git**: For version control

### Verify Installation
```bash
node --version  # Should show v18.x.x or higher
npm --version   # Should show 8.x.x or higher
```

---

## 🔧 Step-by-Step Setup

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
# Install all dependencies (this may take a few minutes)
npm install

# If you encounter issues, try:
npm install --legacy-peer-deps

# Or clear cache and reinstall:
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Step 3: Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
# Minimum required: REACT_APP_BACKEND_URL
```

**Required Environment Variables:**
```bash
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

**Optional Environment Variables:**
- `REACT_APP_API_BASE_URL` - Alternative API base URL
- `REACT_APP_GA_TRACKING_ID` - Google Analytics tracking
- `REACT_APP_SENTRY_DSN` - Error tracking
- `REACT_APP_STRIPE_PUBLISHABLE_KEY` - Payment integration

### Step 4: Verify Setup
```bash
# Check if dependencies are installed
npm list --depth=0

# Verify environment file exists
cat .env
```

---

## 🎯 Running the Application

### Development Mode
```bash
# Start development server
npm start

# The app will open at http://localhost:3000
# (Note: craco.config.js sets dev server to port 5000, but package.json uses 3000)
```

**What happens:**
- Development server starts
- Hot module replacement enabled
- Browser opens automatically
- Changes reload automatically

### Production Build
```bash
# Build for production
npm run build

# Build output will be in the 'build' directory
# Serve with: npx serve -s build
```

---

## 🧪 Testing

### Unit Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=Login
```

### Integration Tests
```bash
# Run integration tests
npm run test:integration
```

### E2E Tests (Cypress)
```bash
# Open Cypress test runner
npm run cypress:open

# Run Cypress tests headless
npm run cypress:run

# Run E2E tests (starts server and runs tests)
npm run test:e2e:cypress
```

### All Tests
```bash
# Run all test suites
npm run test:all
```

---

## 🔍 Code Quality

### Linting
```bash
# Check for linting errors
npm run lint

# Fix linting errors automatically
npm run lint:fix
```

### Formatting
```bash
# Format code with Prettier
npm run format

# Check formatting without changing files
npm run format:check
```

### Security Audit
```bash
# Check for security vulnerabilities
npm run security:audit

# Fix security issues (if possible)
npm run security:fix
```

### Bundle Analysis
```bash
# Analyze bundle size
npm run analyze
```

---

## 🐛 Troubleshooting

### Issue 1: Port Already in Use
**Error**: `Port 3000 is already in use`

**Solution**:
```bash
# Windows: Find process using port
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <pid> /F

# Or use different port
set PORT=3001
npm start
```

### Issue 2: Module Not Found
**Error**: `Cannot find module 'xxx'`

**Solution**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# If using yarn
rm -rf node_modules yarn.lock
yarn install
```

### Issue 3: Build Fails
**Error**: `npm run build` fails

**Solution**:
```bash
# Clear build cache
rm -rf build node_modules/.cache

# Reinstall dependencies
npm install

# Try building again
npm run build
```

### Issue 4: Tests Fail
**Error**: Tests fail with import errors

**Solution**:
```bash
# Clear Jest cache
npm test -- --clearCache

# Reinstall test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests again
npm test
```

### Issue 5: Backend Connection Failed
**Error**: `Network Error` or `Cannot connect to backend`

**Solution**:
1. Verify backend is running: `http://localhost:8000/health`
2. Check `.env` file has correct `REACT_APP_BACKEND_URL`
3. Verify CORS is enabled in backend
4. Check firewall/antivirus isn't blocking connections

---

## 📁 Project Structure

```
frontend/
├── public/              # Static files
│   ├── index.html      # HTML template
│   └── sw.js          # Service worker
├── src/
│   ├── components/    # React components
│   │   ├── ui/        # UI components (shadcn/ui)
│   │   ├── Dashboard/ # Dashboard components
│   │   ├── Admin/     # Admin components
│   │   └── ...
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── utils/         # Utility functions
│   ├── hooks/         # Custom React hooks
│   ├── routes/        # Route configuration
│   └── __tests__/     # Test files
├── cypress/           # E2E tests
├── .env               # Environment variables (create from .env.example)
├── package.json       # Dependencies and scripts
├── jest.config.js     # Jest configuration
├── cypress.config.js  # Cypress configuration
├── tailwind.config.js # Tailwind CSS configuration
└── craco.config.js    # CRACO (Create React App Configuration Override)
```

---

## 🔐 Environment Variables Reference

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `http://localhost:8000` | ✅ Yes |
| `REACT_APP_ENVIRONMENT` | Environment name | `development` | ✅ Yes |

### Optional Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_BASE_URL` | Alternative API base URL | `http://localhost:8000` | ❌ No |
| `REACT_APP_GA_TRACKING_ID` | Google Analytics ID | `G-XXXXXXXXXX` | ❌ No |
| `REACT_APP_SENTRY_DSN` | Sentry error tracking | `https://...` | ❌ No |
| `REACT_APP_STRIPE_PUBLISHABLE_KEY` | Stripe key | `pk_test_...` | ❌ No |
| `REACT_APP_DEBUG` | Debug mode | `true` | ❌ No |
| `DISABLE_HOT_RELOAD` | Disable HMR | `false` | ❌ No |

---

## 🛠️ Available Scripts

### Development
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode

### Testing
- `npm run test:unit` - Run unit tests
- `npm run test:integration` - Run integration tests
- `npm run test:e2e` - Run E2E tests
- `npm run test:coverage` - Generate coverage report
- `npm run test:all` - Run all test suites

### Code Quality
- `npm run lint` - Check linting
- `npm run lint:fix` - Fix linting issues
- `npm run format` - Format code
- `npm run format:check` - Check formatting
- `npm run security:audit` - Security audit

### Analysis
- `npm run analyze` - Analyze bundle size
- `npm run cypress:open` - Open Cypress UI
- `npm run cypress:run` - Run Cypress tests

---

## 🎨 Tech Stack

### Core
- **React**: 19.0.0 - UI library
- **React Router**: 7.5.1 - Routing
- **Axios**: 1.8.4 - HTTP client

### UI Components
- **Radix UI**: Component primitives
- **Tailwind CSS**: Styling
- **Lucide React**: Icons
- **shadcn/ui**: Component library

### Forms & Validation
- **React Hook Form**: 7.56.2 - Form management
- **Zod**: 3.24.4 - Schema validation

### Testing
- **Jest**: 29.7.0 - Test framework
- **React Testing Library**: 14.1.2 - Component testing
- **Cypress**: 13.6.1 - E2E testing

### Build Tools
- **Create React App**: 5.0.1 - Build tooling
- **CRACO**: 7.1.0 - CRA configuration override
- **Babel**: Transpilation
- **Webpack**: Bundling

---

## ✅ Setup Checklist

### Initial Setup
- [ ] Node.js 18+ installed
- [ ] npm 8+ installed
- [ ] Dependencies installed (`npm install`)
- [ ] `.env` file created from `.env.example`
- [ ] `REACT_APP_BACKEND_URL` configured
- [ ] Backend server running (for testing)

### Verification
- [ ] `npm start` runs successfully
- [ ] App opens in browser at http://localhost:3000
- [ ] No console errors
- [ ] Can connect to backend API
- [ ] Tests run successfully (`npm test`)

### Development Ready
- [ ] Hot reload working
- [ ] Linting configured
- [ ] Tests passing
- [ ] Environment variables set
- [ ] Build succeeds (`npm run build`)

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
npm install

# 2. Create environment file
cp .env.example .env
# Edit .env with your backend URL

# 3. Start development server
npm start

# 4. Run tests
npm test

# 5. Build for production
npm run build
```

---

## 📚 Additional Resources

- **React Documentation**: https://react.dev/
- **Create React App**: https://create-react-app.dev/
- **Tailwind CSS**: https://tailwindcss.com/
- **Radix UI**: https://www.radix-ui.com/
- **React Router**: https://reactrouter.com/

---

## 🆘 Getting Help

### Common Issues
- Check **Troubleshooting** section above
- Review error messages in browser console
- Check backend is running and accessible

### Support
- **Documentation**: See `docs/` directory
- **Issues**: Create GitHub issue
- **Questions**: Review code comments and examples

---

**Status**: ✅ Ready for Development  
**Last Updated**: November 22, 2025

