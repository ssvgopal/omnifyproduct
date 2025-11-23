import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import Layout from '@/components/layout/Layout';

// Lazy load pages
const Landing = lazy(() => import('@/pages/Landing'));
const Login = lazy(() => import('@/pages/Login'));
const Register = lazy(() => import('@/pages/Register'));
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
  const token = localStorage.getItem('access_token');
  const isAuthenticated = !!token;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: { pathname: window.location.pathname } }} replace />;
  }
  
  return children;
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
            {/* Public Routes (without Layout) */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/demo" element={<Layout><Demo /></Layout>} />
            <Route path="/pricing" element={<Layout><Pricing /></Layout>} />
            <Route path="/features" element={<Layout><Features /></Layout>} />
            
            {/* Authenticated User Routes (with Layout) */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Layout><Dashboard /></Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/insights" 
              element={
                <ProtectedRoute>
                  <Layout><Insights /></Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/workflows" 
              element={
                <ProtectedRoute>
                  <Layout><Workflows /></Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/traces" 
              element={
                <ProtectedRoute>
                  <SubscriptionGate>
                    <Layout><Traces /></Layout>
                  </SubscriptionGate>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <ProtectedRoute>
                  <Layout><Settings /></Layout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <Layout><Profile /></Layout>
                </ProtectedRoute>
              } 
            />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default UserRoutes;

