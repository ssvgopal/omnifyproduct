import React, { useState, useEffect } from 'react';
import UnifiedAttribution from '@/components/Dashboard/UnifiedAttribution';
import PredictiveAlerts from '@/components/Dashboard/PredictiveAlerts';
import InsightCards from '@/components/Dashboard/InsightCards';
import PerformanceMetrics from '@/components/Dashboard/PerformanceMetrics';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/services/api';
import { Loader2, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    metrics: null,
    alerts: null,
    recommendations: null,
    attribution: null,
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      if (!user?.organization_id) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const organizationId = user.organization_id;

        // Fetch all dashboard data in parallel
        const [metrics, alerts, recommendations, attribution] = await Promise.allSettled([
          api.getDashboardMetrics(organizationId),
          api.getPredictiveAlerts(organizationId),
          api.getRecommendations(organizationId),
          api.getDashboardMetrics(organizationId), // Attribution data comes from metrics
        ]);

        setDashboardData({
          metrics: metrics.status === 'fulfilled' ? metrics.value : null,
          alerts: alerts.status === 'fulfilled' ? alerts.value : null,
          recommendations: recommendations.status === 'fulfilled' ? recommendations.value : null,
          attribution: attribution.status === 'fulfilled' ? attribution.value : null,
        });
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Marketing Intelligence Dashboard
          </h1>
          <p className="text-gray-600">
            Unified view of your marketing performance across all platforms
          </p>
        </div>

        {/* Performance Metrics */}
        <div className="mb-6">
          <PerformanceMetrics data={dashboardData.metrics} />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Unified Attribution */}
          <UnifiedAttribution data={dashboardData.attribution} />

          {/* Predictive Alerts */}
          <PredictiveAlerts data={dashboardData.alerts} />
        </div>

        {/* Prescriptive Recommendations */}
        <div className="mb-6">
          <InsightCards data={dashboardData.recommendations} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


