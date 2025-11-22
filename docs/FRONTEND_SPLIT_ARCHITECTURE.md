# Frontend Split Architecture & Use Cases

**Date**: December 2024  
**Status**: Architecture Proposal + Use Case Definitions  
**Purpose**: Split monolithic frontend into user-facing and backoffice applications

---

## 🎯 Executive Summary

The current frontend mixes user-facing features with administrative tools, creating confusion and complexity. This document proposes splitting into two focused applications:

1. **User-Facing Frontend** (`frontend-user/`): Demo-focused, marketing-oriented, self-service admin features
2. **Backoffice Frontend** (`frontend-admin/`): Complete administrative, monitoring, triaging, and logging interface

---

## 📐 Architecture Split Proposal

### Current State (Monolithic)

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Home.js          # Mixed: user + admin features
│   │   ├── Demo.jsx         # User-facing
│   │   ├── AnalyticsBI.jsx  # User-facing
│   │   ├── Workflows.jsx    # User-facing
│   │   ├── Settings.jsx     # User-facing
│   │   └── AdminDashboard.js # Admin-only
│   ├── components/
│   │   ├── Dashboard/        # Mixed: user analytics + admin tools
│   │   ├── Admin/            # Admin-only
│   │   └── ui/               # Shared components
│   └── routes/
│       └── AppRoutes.js      # All routes together
```

**Problems**:
- ❌ User sees admin complexity
- ❌ Admin tools mixed with user features
- ❌ Cannot deploy independently
- ❌ Security boundaries unclear
- ❌ Marketing/demo experience diluted

---

### Proposed State (Split Architecture)

```
frontend-user/                    # User-Facing Application
├── src/
│   ├── pages/
│   │   ├── Landing.jsx          # Marketing landing page
│   │   ├── Demo.jsx             # Interactive demo
│   │   ├── Dashboard.jsx        # User dashboard (MEMORY + ORACLE + CURIOSITY)
│   │   ├── Insights.jsx        # Insight cards & recommendations
│   │   ├── Workflows.jsx        # User workflow management
│   │   ├── Traces.jsx           # Workflow traces (if configured)
│   │   ├── Settings.jsx         # User self-service settings
│   │   └── Profile.jsx          # User profile & subscription
│   ├── components/
│   │   ├── Marketing/           # Marketing components
│   │   │   ├── Hero.jsx
│   │   │   ├── Features.jsx
│   │   │   ├── Pricing.jsx
│   │   │   └── Testimonials.jsx
│   │   ├── Dashboard/           # User dashboard components
│   │   │   ├── UnifiedAttribution.jsx    # MEMORY module
│   │   │   ├── PredictiveAlerts.jsx      # ORACLE module
│   │   │   ├── InsightCards.jsx          # CURIOSITY module
│   │   │   ├── BudgetShift.jsx           # Action execution
│   │   │   └── PerformanceMetrics.jsx    # ROAS, Revenue, etc.
│   │   ├── SelfService/         # User self-service admin
│   │   │   ├── IntegrationSetup.jsx
│   │   │   ├── ApiKeyManagement.jsx
│   │   │   ├── NotificationSettings.jsx
│   │   │   └── SubscriptionManagement.jsx
│   │   ├── Workflows/           # User workflow components
│   │   │   ├── WorkflowBuilder.jsx
│   │   │   ├── WorkflowMonitor.jsx
│   │   │   └── WorkflowTraces.jsx        # If subscription allows
│   │   └── ui/                  # Shared UI components
│   ├── services/
│   │   ├── api.js               # User-facing API client
│   │   └── analytics.js         # User analytics tracking
│   └── routes/
│       └── UserRoutes.js        # User-facing routes only

frontend-admin/                   # Backoffice Application
├── src/
│   ├── pages/
│   │   ├── AdminDashboard.jsx   # Main admin dashboard
│   │   ├── SystemHealth.jsx     # System monitoring
│   │   ├── Logs.jsx             # Log analysis & triaging
│   │   ├── Workflows.jsx        # Workflow management & monitoring
│   │   ├── Performance.jsx      # Performance metrics
│   │   ├── ClientSupport.jsx    # Client issue triaging
│   │   ├── UserManagement.jsx   # User account management
│   │   ├── IntegrationManagement.jsx  # Integration config
│   │   └── Settings.jsx         # System settings
│   ├── components/
│   │   ├── Admin/
│   │   │   ├── SystemHealthPanel.jsx
│   │   │   ├── LogViewer.jsx
│   │   │   ├── LogFilters.jsx
│   │   │   ├── WorkflowMonitor.jsx
│   │   │   ├── PerformanceMetrics.jsx
│   │   │   ├── ClientIssueAnalyzer.jsx
│   │   │   ├── UserManagementTable.jsx
│   │   │   └── IntegrationConfig.jsx
│   │   └── ui/                  # Admin UI components
│   ├── services/
│   │   ├── adminApi.js          # Admin API client
│   │   └── logger.js            # Admin logging service
│   └── routes/
│       └── AdminRoutes.js       # Admin routes only
```

---

## 🔐 Access Control & Routing

### User-Facing Frontend Routes

```javascript
// frontend-user/src/routes/UserRoutes.js
const UserRoutes = () => (
  <Routes>
    {/* Public Routes */}
    <Route path="/" element={<Landing />} />
    <Route path="/demo" element={<Demo />} />
    <Route path="/pricing" element={<Pricing />} />
    <Route path="/features" element={<Features />} />
    
    {/* Authenticated User Routes */}
    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
    <Route path="/insights" element={<ProtectedRoute><Insights /></ProtectedRoute>} />
    <Route path="/workflows" element={<ProtectedRoute><Workflows /></ProtectedRoute>} />
    <Route path="/traces" element={<ProtectedRoute><SubscriptionGate><Traces /></SubscriptionGate></ProtectedRoute>} />
    <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
    <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
  </Routes>
);
```

### Backoffice Frontend Routes

```javascript
// frontend-admin/src/routes/AdminRoutes.js
const AdminRoutes = () => (
  <Routes>
    {/* Admin Authentication */}
    <Route path="/login" element={<AdminLogin />} />
    
    {/* Protected Admin Routes */}
    <Route path="/" element={<AdminProtectedRoute><AdminDashboard /></AdminProtectedRoute>} />
    <Route path="/health" element={<AdminProtectedRoute><SystemHealth /></AdminProtectedRoute>} />
    <Route path="/logs" element={<AdminProtectedRoute><Logs /></AdminProtectedRoute>} />
    <Route path="/workflows" element={<AdminProtectedRoute><Workflows /></AdminProtectedRoute>} />
    <Route path="/performance" element={<AdminProtectedRoute><Performance /></AdminProtectedRoute>} />
    <Route path="/support" element={<AdminProtectedRoute><ClientSupport /></AdminProtectedRoute>} />
    <Route path="/users" element={<AdminProtectedRoute><UserManagement /></AdminProtectedRoute>} />
    <Route path="/integrations" element={<AdminProtectedRoute><IntegrationManagement /></AdminProtectedRoute>} />
    <Route path="/settings" element={<AdminProtectedRoute><Settings /></AdminProtectedRoute>} />
  </Routes>
);
```

---

## 🎨 User-Facing Frontend Features

### Core Features

1. **Marketing & Demo**
   - Landing page with hero, features, pricing
   - Interactive demo showcasing core value
   - Testimonials and case studies
   - Clear CTAs for signup/trial

2. **User Dashboard (FACE Module)**
   - Unified attribution view (MEMORY)
   - Predictive alerts (ORACLE)
   - Insight cards with recommendations (CURIOSITY)
   - Top winners/losers panel
   - Executive-level simplicity

3. **Self-Service Admin**
   - Integration setup (HubSpot, Meta, Google, Shopify)
   - API key management
   - Notification preferences
   - Subscription management
   - User profile settings

4. **Workflow Management**
   - Workflow builder (visual)
   - Workflow monitor (status, progress)
   - Workflow traces (if subscription tier allows)

5. **Subscription-Gated Features**
   - Workflow traces (premium tier)
   - Advanced analytics (premium tier)
   - Custom integrations (enterprise tier)

---

## 🔧 Backoffice Frontend Features

### Core Features

1. **System Health Monitoring**
   - Real-time system status
   - Service health checks
   - Resource utilization
   - Alert management

2. **Log Analysis & Triaging**
   - Comprehensive log viewer
   - Advanced filtering (level, time, user, workflow)
   - Log search and analysis
   - Error pattern detection
   - Log export capabilities

3. **Workflow Management**
   - All user workflows overview
   - Workflow execution monitoring
   - Failed workflow triaging
   - Workflow performance metrics

4. **Performance Monitoring**
   - API performance metrics
   - Response time analysis
   - Bottleneck identification
   - Top endpoint analysis
   - Performance alerts

5. **Client Support Tools**
   - Client issue analysis
   - Log correlation by client
   - Issue triaging interface
   - Support ticket integration

6. **User Management**
   - User account management
   - Subscription management
   - Access control
   - User activity logs

7. **Integration Management**
   - Integration configuration
   - API key management
   - Integration health monitoring
   - Integration error handling

---

## 🚀 Deployment Strategy

### Independent Deployment

```yaml
# docker-compose.yml
services:
  frontend-user:
    build:
      context: ./frontend-user
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - .env.user
    environment:
      - REACT_APP_API_URL=http://api:8000
      - REACT_APP_ENV=production

  frontend-admin:
    build:
      context: ./frontend-admin
      dockerfile: Dockerfile
    ports:
      - "3001:3000"
    env_file:
      - .env.admin
    environment:
      - REACT_APP_API_URL=http://api:8000
      - REACT_APP_ENV=production
      - REACT_APP_ADMIN_MODE=true
```

### Separate Domains

- **User-Facing**: `app.omnify.com` or `omnify.com`
- **Backoffice**: `admin.omnify.com` or `ops.omnify.com`

---

## 📦 Shared Components Strategy

### Option 1: Shared Package (Recommended)

```
packages/
└── shared-ui/
    ├── components/          # Shared UI components
    ├── hooks/              # Shared React hooks
    ├── utils/              # Shared utilities
    └── types/              # Shared TypeScript types
```

Both frontends import from `@omnify/shared-ui`.

### Option 2: Git Submodule

Keep shared components in a separate repo and include as submodule.

---

## 🔄 Migration Plan

### Phase 1: Preparation (Week 1)
1. Create `frontend-user/` and `frontend-admin/` directories
2. Set up separate package.json files
3. Create shared components package
4. Define routing structure

### Phase 2: User-Facing Frontend (Week 2)
1. Migrate marketing/demo components
2. Migrate user dashboard components
3. Migrate self-service admin features
4. Implement subscription gating

### Phase 3: Backoffice Frontend (Week 3)
1. Migrate admin dashboard
2. Migrate log viewer
3. Migrate monitoring components
4. Implement admin authentication

### Phase 4: Testing & Deployment (Week 4)
1. Test both applications independently
2. Update CI/CD pipelines
3. Deploy to staging
4. Production deployment

---

## ✅ Success Criteria

1. **User-Facing Frontend**
   - ✅ Clean, demo-focused experience
   - ✅ No admin complexity visible
   - ✅ Fast load times (< 2s)
   - ✅ Mobile responsive
   - ✅ Clear value proposition

2. **Backoffice Frontend**
   - ✅ Complete admin functionality
   - ✅ Efficient log triaging
   - ✅ Real-time monitoring
   - ✅ Fast search and filtering
   - ✅ Secure access control

---

## 📊 Next Steps

1. **Review & Approval**: Team review of architecture proposal
2. **Resource Allocation**: Assign developers to each frontend
3. **Timeline**: Set sprint goals for migration
4. **Testing Strategy**: Define testing approach for split
5. **Documentation**: Update user and admin documentation

---

**Status**: Ready for team review and implementation planning

