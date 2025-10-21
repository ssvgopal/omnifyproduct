import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ErrorFallback from '@/components/ui/ErrorFallback';

// Lazy load main pages
const Home = lazy(() => import('@/pages/Home'));
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Agents = lazy(() => import('@/pages/Agents'));
const Workflows = lazy(() => import('@/pages/Workflows'));
const Analytics = lazy(() => import('@/pages/Analytics'));
const Settings = lazy(() => import('@/pages/Settings'));

// Lazy load dashboard components
const BrainLogicPanel = lazy(() => import('@/components/Dashboard/BrainLogicPanel'));
const AnalyticsDashboard = lazy(() => import('@/components/Dashboard/AnalyticsDashboard'));
const EyesModule = lazy(() => import('@/components/Dashboard/EyesModule'));
const ProactiveIntelligenceDashboard = lazy(() => import('@/components/Dashboard/ProactiveIntelligenceDashboard'));
const MagicalOnboardingWizard = lazy(() => import('@/components/Onboarding/MagicalOnboardingWizard'));
const InstantValueDeliveryDashboard = lazy(() => import('@/components/Dashboard/InstantValueDeliveryDashboard'));
const CustomerOrchestrationDashboard = lazy(() => import('@/components/Dashboard/CustomerOrchestrationDashboard'));
const PredictiveIntelligenceDashboard = lazy(() => import('@/components/Dashboard/PredictiveIntelligenceDashboard'));
const AdaptiveClientLearningDashboard = lazy(() => import('@/components/Dashboard/AdaptiveClientLearningDashboard'));
const HumanExpertInterventionDashboard = lazy(() => import('@/components/Dashboard/HumanExpertInterventionDashboard'));
const CriticalDecisionHandHoldingDashboard = lazy(() => import('@/components/Dashboard/CriticalDecisionHandHoldingDashboard'));

// Lazy load admin components
const AdminDashboard = lazy(() => import('@/components/Admin/AdminDashboard'));

// Loading component for Suspense
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="large" />
  </div>
);

// Error boundary for route-level errors
const RouteErrorBoundary = ({ children }) => (
  <ErrorBoundary
    FallbackComponent={ErrorFallback}
    onError={(error, errorInfo) => {
      console.error('Route Error:', error, errorInfo);
      // Log to monitoring service
    }}
  >
    {children}
  </ErrorBoundary>
);

const AppRoutes = () => {
  return (
    <Router>
      <RouteErrorBoundary>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/workflows" element={<Workflows />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </Suspense>
      </RouteErrorBoundary>
    </Router>
  );
};

export default AppRoutes;
