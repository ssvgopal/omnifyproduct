import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import BIDashboardEmbed from '@/components/Analytics/BIDashboardEmbed';
import ReportBuilder from '@/components/Analytics/ReportBuilder';
import ScheduledReports from '@/components/Analytics/ScheduledReports';
import { BarChart3, FileText, Calendar, Database } from 'lucide-react';

const AnalyticsBI = () => {
  const [activeTab, setActiveTab] = useState('dashboards');
  const [selectedDashboard, setSelectedDashboard] = useState(null);

  // In production, get these from user context
  const organizationId = 'demo-org-123';
  const userId = 'demo-user-123';

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Advanced Analytics & BI</h1>
          <p className="text-gray-600 mt-2">Business intelligence dashboards, custom reports, and scheduled analytics</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="dashboards">
              <Database className="h-4 w-4 mr-2" />
              BI Dashboards
            </TabsTrigger>
            <TabsTrigger value="reports">
              <FileText className="h-4 w-4 mr-2" />
              Report Builder
            </TabsTrigger>
            <TabsTrigger value="scheduled">
              <Calendar className="h-4 w-4 mr-2" />
              Scheduled Reports
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboards">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Business Intelligence Dashboards</h2>
                <select
                  className="px-4 py-2 border rounded-lg"
                  value={selectedDashboard || ''}
                  onChange={(e) => setSelectedDashboard(e.target.value)}
                >
                  <option value="">Select a dashboard...</option>
                  <option value="1">Executive Dashboard</option>
                  <option value="2">Operational Dashboard</option>
                  <option value="3">Analytical Dashboard</option>
                </select>
              </div>
              {selectedDashboard ? (
                <BIDashboardEmbed
                  dashboardId={parseInt(selectedDashboard)}
                  organizationId={organizationId}
                  userId={userId}
                />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                  <p>Select a dashboard to view</p>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="reports">
            <ReportBuilder />
          </TabsContent>

          <TabsContent value="scheduled">
            <ScheduledReports />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AnalyticsBI;

