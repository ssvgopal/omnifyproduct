import React from 'react';
import UnifiedAttribution from '@/components/Dashboard/UnifiedAttribution';
import PredictiveAlerts from '@/components/Dashboard/PredictiveAlerts';
import InsightCards from '@/components/Dashboard/InsightCards';
import PerformanceMetrics from '@/components/Dashboard/PerformanceMetrics';

const Dashboard = () => {
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
          <PerformanceMetrics />
        </div>

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Unified Attribution */}
          <UnifiedAttribution />

          {/* Predictive Alerts */}
          <PredictiveAlerts />
        </div>

        {/* Prescriptive Recommendations */}
        <div className="mb-6">
          <InsightCards />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;


