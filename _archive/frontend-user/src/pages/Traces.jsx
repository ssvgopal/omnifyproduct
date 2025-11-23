import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@omnify/shared-ui';
import { CheckCircle2, XCircle, Clock, Eye } from 'lucide-react';

const Traces = () => {
  // This is subscription-gated content
  const traces = [
    {
      id: 1,
      workflow: 'Auto Budget Optimization',
      status: 'success',
      started: '2 hours ago',
      duration: '45s',
      steps: 5,
      completed: 5
    },
    {
      id: 2,
      workflow: 'Creative Rotation',
      status: 'success',
      started: '5 hours ago',
      duration: '12s',
      steps: 3,
      completed: 3
    },
    {
      id: 3,
      workflow: 'Daily Performance Report',
      status: 'failed',
      started: '1 day ago',
      duration: '2m',
      steps: 8,
      completed: 6
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Workflow Traces</h1>
              <p className="text-gray-600">Detailed execution traces for your workflows (Premium Feature)</p>
            </div>
            <Badge className="bg-indigo-100 text-indigo-800">Premium</Badge>
          </div>
        </div>

        <div className="space-y-4">
          {traces.map((trace) => (
            <Card key={trace.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{trace.workflow}</h3>
                    <p className="text-sm text-gray-600">Started {trace.started} • Duration: {trace.duration}</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    {trace.status === 'success' ? (
                      <Badge className="bg-green-100 text-green-800">
                        <CheckCircle2 className="h-4 w-4 mr-1" />
                        Success
                      </Badge>
                    ) : (
                      <Badge variant="destructive">
                        <XCircle className="h-4 w-4 mr-1" />
                        Failed
                      </Badge>
                    )}
                    <button className="text-indigo-600 hover:text-indigo-800">
                      <Eye className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                <div className="pt-4 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      Steps: {trace.completed}/{trace.steps}
                    </span>
                    <div className="w-48 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          trace.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${(trace.completed / trace.steps) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Traces;


