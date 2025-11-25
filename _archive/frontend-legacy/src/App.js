import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import AdminDashboard from './components/Admin/AdminDashboard';
import Home from '@/pages/Home';
import Signup from '@/pages/Signup';
import Login from '@/pages/Login';
import VerifyEmail from '@/pages/VerifyEmail';
import ForgotPassword from '@/pages/ForgotPassword';
import ResetPassword from '@/pages/ResetPassword';
import CookieConsent from '@/components/Legal/CookieConsent';
import { logger } from './services/logger';
import '@/App.css';

function App() {
  useEffect(() => {
    // Set up user context for logging (in a real app, this would come from auth)
    const userId = localStorage.getItem('userId') || 'anonymous';
    const organizationId = localStorage.getItem('organizationId');

    logger.setUser(userId, organizationId);

    // Track app initialization
    logger.info('OmnifyProduct frontend initialized', {
      eventType: 'app_init',
      userAgent: navigator.userAgent,
      url: window.location.href
    });

    // Track page visibility changes
    const handleVisibilityChange = () => {
      logger.trackUserAction(
        document.hidden ? 'page_hidden' : 'page_visible',
        { visibilityState: document.visibilityState }
      );
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Track before unload
    const handleBeforeUnload = () => {
      logger.trackUserAction('page_unload');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  return (
    <ErrorBoundary>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
          </Routes>
          <CookieConsent />
        </BrowserRouter>
      </div>
    </ErrorBoundary>
  );
}

export default App;
