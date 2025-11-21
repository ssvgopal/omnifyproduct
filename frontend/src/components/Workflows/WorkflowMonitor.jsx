import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Play,
  Pause,
  StopCircle,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Eye,
  AlertCircle
} from 'lucide-react';
import api from '@/services/api';

const WorkflowMonitor = () => {
  const [workflows, setWorkflows] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/workflows', {
        params: { organization_id: 'demo-org-123' }
      });
      if (response.data.success) {
        setWorkflows(response.data.workflows || []);
      }
    } catch (err) {
      console.error('Error loading workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadExecutions = async (workflowId) => {
    try {
      const response = await api.get(`/api/workflows/${workflowId}/executions`);
      if (response.data.success) {
        setExecutions(response.data.executions || []);
      }
    } catch (err) {
      console.error('Error loading executions:', err);
    }
  };

  const handleExecute = async (workflowId) => {
    try {
      await api.post(`/api/workflows/${workflowId}/execute`);
      await loadExecutions(workflowId);
    } catch (err) {
      console.error('Error executing workflow:', err);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'active': <Badge className="bg-green-100 text-green-800">Active</Badge>,
      'paused': <Badge className="bg-yellow-100 text-yellow-800">Paused</Badge>,
      'completed': <Badge className="bg-blue-100 text-blue-800">Completed</Badge>,
      'failed': <Badge className="bg-red-100 text-red-800">Failed</Badge>,
      'running': <Badge className="bg-blue-100 text-blue-800">Running</Badge>
    };
    return badges[status] || <Badge variant="outline">{status}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Workflow Monitor</h2>
          <p className="text-gray-600 mt-1">Monitor and manage your automation workflows</p>
        </div>
        <Button variant="outline" onClick={loadWorkflows}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Tabs defaultValue="workflows" className="space-y-4">
        <TabsList>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="executions">Executions</TabsTrigger>
        </TabsList>

        <TabsContent value="workflows">
          {loading ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
                <p className="text-gray-500">Loading workflows...</p>
              </CardContent>
            </Card>
          ) : workflows.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <AlertCircle className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-semibold mb-2">No Workflows</h3>
                <p className="text-gray-600">Create your first workflow to get started</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {workflows.map((workflow) => (
                <Card key={workflow.workflow_id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{workflow.name}</CardTitle>
                        <CardContent className="p-0 mt-2">
                          <p className="text-sm text-gray-600">{workflow.description || 'No description'}</p>
                        </CardContent>
                      </div>
                      {getStatusBadge(workflow.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-600">Steps</p>
                        <p className="font-semibold">{workflow.steps?.length || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Triggers</p>
                        <p className="font-semibold">{workflow.triggers?.length || 0}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Created</p>
                        <p className="font-semibold text-sm">
                          {workflow.created_at ? new Date(workflow.created_at).toLocaleDateString() : 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Last Run</p>
                        <p className="font-semibold text-sm">
                          {workflow.last_execution ? new Date(workflow.last_execution).toLocaleDateString() : 'Never'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedWorkflow(workflow);
                        loadExecutions(workflow.workflow_id);
                      }}
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      View Executions
                    </Button>
                    {workflow.status === 'active' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleExecute(workflow.workflow_id)}
                      >
                        <Play className="h-3 w-3 mr-1" />
                        Execute
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="executions">
          {selectedWorkflow ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Executions: {selectedWorkflow.name}</h3>
                <Button variant="outline" size="sm" onClick={() => setSelectedWorkflow(null)}>
                  Back to All
                </Button>
              </div>
              {executions.length === 0 ? (
                <Card>
                  <CardContent className="py-8 text-center text-gray-500">
                    No executions found for this workflow
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-3">
                  {executions.map((execution) => (
                    <Card key={execution.execution_id}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold">Execution {execution.execution_id}</p>
                            <p className="text-sm text-gray-600">
                              Started: {new Date(execution.started_at).toLocaleString()}
                            </p>
                          </div>
                          {getStatusBadge(execution.status)}
                        </div>
                        {execution.completed_at && (
                          <p className="text-sm text-gray-500 mt-2">
                            Completed: {new Date(execution.completed_at).toLocaleString()}
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-gray-500">
                Select a workflow to view executions
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WorkflowMonitor;

