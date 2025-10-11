import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import AdminDashboard from './components/Admin/AdminDashboard';
import Home from '@/pages/Home';
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
          </Routes>
        </BrowserRouter>
      </div>
    </ErrorBoundary>
  );
}

export default App;
