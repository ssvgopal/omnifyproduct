import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge, Button } from '@omnify/shared-ui';
import { Play, Pause, CheckCircle2, XCircle, Clock, Eye } from 'lucide-react';

const WorkflowMonitor = () => {
  const [workflows] = useState([
    {
      id: 1,
      name: 'Auto Budget Optimization',
      status: 'running',
      lastRun: '2 hours ago',
      nextRun: 'In 6 hours',
      executions: 24,
      successRate: 95
    },
    {
      id: 2,
      name: 'Creative Rotation',
      status: 'paused',
      lastRun: '1 day ago',
      nextRun: 'Paused',
      executions: 12,
      successRate: 100
    },
    {
      id: 3,
      name: 'Daily Performance Report',
      status: 'running',
      lastRun: '5 minutes ago',
      nextRun: 'Tomorrow 9:00 AM',
      executions: 30,
      successRate: 98
    }
  ]);

  const getStatusBadge = (status) => {
    if (status === 'running') {
      return <Badge className="bg-green-100 text-green-800">Running</Badge>;
    }
    return <Badge variant="secondary">Paused</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Active Workflows</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {workflows.map((workflow) => (
            <div key={workflow.id} className="p-4 border rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-semibold text-lg">{workflow.name}</h4>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                    <span className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      Last run: {workflow.lastRun}
                    </span>
                    <span>Next: {workflow.nextRun}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusBadge(workflow.status)}
                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Button>
                </div>
              </div>
              <div className="flex items-center justify-between pt-3 border-t">
                <div className="flex items-center space-x-4 text-sm">
                  <span className="text-gray-600">
                    Executions: <span className="font-semibold">{workflow.executions}</span>
                  </span>
                  <span className="text-gray-600">
                    Success Rate: <span className="font-semibold text-green-600">{workflow.successRate}%</span>
                  </span>
                </div>
                <div className="flex space-x-2">
                  {workflow.status === 'running' ? (
                    <Button variant="outline" size="sm">
                      <Pause className="h-4 w-4 mr-2" />
                      Pause
                    </Button>
                  ) : (
                    <Button size="sm">
                      <Play className="h-4 w-4 mr-2" />
                      Start
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default WorkflowMonitor;

