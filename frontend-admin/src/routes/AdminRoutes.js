import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';

// Lazy load pages
const AdminLogin = lazy(() => import('@/pages/AdminLogin'));
const AdminDashboard = lazy(() => import('@/pages/AdminDashboard'));
const SystemHealth = lazy(() => import('@/pages/SystemHealth'));
const Logs = lazy(() => import('@/pages/Logs'));
const Workflows = lazy(() => import('@/pages/Workflows'));
const Performance = lazy(() => import('@/pages/Performance'));
const ClientSupport = lazy(() => import('@/pages/ClientSupport'));
const UserManagement = lazy(() => import('@/pages/UserManagement'));
const IntegrationManagement = lazy(() => import('@/pages/IntegrationManagement'));
const Settings = lazy(() => import('@/pages/Settings'));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
  </div>
);

// Admin Protected Route component
const AdminProtectedRoute = ({ children }) => {
  // TODO: Implement admin authentication check
  const isAdminAuthenticated = true; // Placeholder
  return isAdminAuthenticated ? children : <Navigate to="/login" replace />;
};

const AdminRoutes = () => {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <Suspense fallback={<PageLoader />}>
        <Routes>
            {/* Admin Authentication */}
            <Route path="/login" element={<AdminLogin />} />
            
            {/* Protected Admin Routes */}
            <Route 
              path="/" 
              element={
                <AdminProtectedRoute>
                  <AdminDashboard />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/health" 
              element={
                <AdminProtectedRoute>
                  <SystemHealth />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/logs" 
              element={
                <AdminProtectedRoute>
                  <Logs />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/workflows" 
              element={
                <AdminProtectedRoute>
                  <Workflows />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/performance" 
              element={
                <AdminProtectedRoute>
                  <Performance />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/support" 
              element={
                <AdminProtectedRoute>
                  <ClientSupport />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/users" 
              element={
                <AdminProtectedRoute>
                  <UserManagement />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/integrations" 
              element={
                <AdminProtectedRoute>
                  <IntegrationManagement />
                </AdminProtectedRoute>
              } 
            />
            <Route 
              path="/settings" 
              element={
                <AdminProtectedRoute>
                  <Settings />
                </AdminProtectedRoute>
              } 
            />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default AdminRoutes;

