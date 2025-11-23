import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@omnify/shared-ui';
import InsightCards from '@/components/Dashboard/InsightCards';
import PredictiveAlerts from '@/components/Dashboard/PredictiveAlerts';

const Insights = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Insights & Recommendations</h1>
          <p className="text-gray-600">Actionable insights to optimize your marketing performance</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <PredictiveAlerts />
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600">Active Recommendations</span>
                  <span className="font-semibold">5</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Potential Revenue Lift</span>
                  <span className="font-semibold text-green-600">$180k</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Alerts This Week</span>
                  <span className="font-semibold">3</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <InsightCards />
      </div>
    </div>
  );
};

export default Insights;


