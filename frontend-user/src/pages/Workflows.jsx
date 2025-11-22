import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@omnify/shared-ui';
import WorkflowBuilder from '@/components/Workflows/WorkflowBuilder';
import WorkflowMonitor from '@/components/Workflows/WorkflowMonitor';

const Workflows = () => {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Workflows</h1>
          <p className="text-gray-600">Create and manage automated marketing workflows</p>
        </div>

        <Tabs defaultValue="monitor" className="space-y-6">
          <TabsList>
            <TabsTrigger value="monitor">Active Workflows</TabsTrigger>
            <TabsTrigger value="builder">Create Workflow</TabsTrigger>
          </TabsList>

          <TabsContent value="monitor">
            <WorkflowMonitor />
          </TabsContent>

          <TabsContent value="builder">
            <WorkflowBuilder />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Workflows;


