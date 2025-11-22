import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Badge, Button } from '@omnify/shared-ui';
import { Play, Pause, Eye, AlertCircle } from 'lucide-react';

const Workflows = () => {
  const [workflows] = useState([
    { id: 'wf1', name: 'Auto Budget Optimization', status: 'running', executions: 1247, successRate: 95.3, failures: 58 },
    { id: 'wf2', name: 'Creative Rotation', status: 'paused', executions: 892, successRate: 98.2, failures: 16 },
    { id: 'wf3', name: 'Daily Reports', status: 'running', executions: 30, successRate: 100, failures: 0 },
    { id: 'wf4', name: 'Fraud Detection', status: 'failed', executions: 234, successRate: 87.5, failures: 29 }
  ]);

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Workflow Management</h1>
        <p className="text-gray-600">Monitor and manage all user workflows</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Workflows</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Workflow Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Executions</TableHead>
                <TableHead>Success Rate</TableHead>
                <TableHead>Failures</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workflows.map((workflow) => (
                <TableRow key={workflow.id}>
                  <TableCell className="font-medium">{workflow.name}</TableCell>
                  <TableCell>
                    <Badge variant={workflow.status === 'running' ? 'default' : workflow.status === 'failed' ? 'destructive' : 'secondary'}>
                      {workflow.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{workflow.executions.toLocaleString()}</TableCell>
                  <TableCell>
                    <span className={workflow.successRate >= 95 ? 'text-green-600' : 'text-orange-600'}>
                      {workflow.successRate}%
                    </span>
                  </TableCell>
                  <TableCell>
                    {workflow.failures > 0 ? (
                      <span className="flex items-center text-red-600">
                        <AlertCircle className="h-4 w-4 mr-1" />
                        {workflow.failures}
                      </span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      {workflow.status === 'running' ? (
                        <Button variant="outline" size="sm">
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button variant="outline" size="sm">
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};

export default Workflows;


