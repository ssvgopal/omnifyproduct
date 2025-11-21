import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import WorkflowBuilder from '@/components/Workflows/WorkflowBuilder';
import WorkflowMonitor from '@/components/Workflows/WorkflowMonitor';
import { Settings, Play, Plus } from 'lucide-react';

const Workflows = () => {
  const [activeTab, setActiveTab] = useState('builder');

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Automation Workflows</h1>
          <p className="text-gray-600 mt-2">Create and manage automated marketing workflows</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList>
            <TabsTrigger value="builder">
              <Plus className="h-4 w-4 mr-2" />
              Builder
            </TabsTrigger>
            <TabsTrigger value="monitor">
              <Play className="h-4 w-4 mr-2" />
              Monitor
            </TabsTrigger>
          </TabsList>

          <TabsContent value="builder">
            <WorkflowBuilder />
          </TabsContent>

          <TabsContent value="monitor">
            <WorkflowMonitor />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Workflows;

