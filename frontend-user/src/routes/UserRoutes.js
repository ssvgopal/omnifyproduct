import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';

// Lazy load pages
const Landing = lazy(() => import('@/pages/Landing'));
const Demo = lazy(() => import('@/pages/Demo'));
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const Insights = lazy(() => import('@/pages/Insights'));
const Workflows = lazy(() => import('@/pages/Workflows'));
const Traces = lazy(() => import('@/pages/Traces'));
const Settings = lazy(() => import('@/pages/Settings'));
const Profile = lazy(() => import('@/pages/Profile'));
const Pricing = lazy(() => import('@/pages/Pricing'));
const Features = lazy(() => import('@/pages/Features'));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
  </div>
);

// Protected Route component
const ProtectedRoute = ({ children }) => {
  // TODO: Implement authentication check
  const isAuthenticated = true; // Placeholder
  return isAuthenticated ? children : <Navigate to="/" replace />;
};

// Subscription Gate component
const SubscriptionGate = ({ children, requiredTier = 'premium' }) => {
  // TODO: Implement subscription check
  const hasAccess = true; // Placeholder
  return hasAccess ? children : <Navigate to="/pricing" replace />;
};

const UserRoutes = () => {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <Suspense fallback={<PageLoader />}>
        <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/features" element={<Features />} />
            
            {/* Authenticated User Routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/insights" 
              element={
                <ProtectedRoute>
                  <Insights />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workflows" 
              element={
                <ProtectedRoute>
                  <Workflows />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/traces" 
              element={
                <ProtectedRoute>
                  <SubscriptionGate>
                    <Traces />
                  </SubscriptionGate>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } 
            />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default UserRoutes;

