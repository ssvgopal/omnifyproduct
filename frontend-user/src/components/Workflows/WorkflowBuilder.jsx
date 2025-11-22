import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Label, Textarea } from '@omnify/shared-ui';
import { Plus, Save, Play } from 'lucide-react';

const WorkflowBuilder = () => {
  const [workflow, setWorkflow] = useState({
    name: '',
    description: '',
    steps: []
  });

  const addStep = () => {
    setWorkflow({
      ...workflow,
      steps: [...workflow.steps, { id: Date.now(), type: 'action', name: '' }]
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create New Workflow</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label htmlFor="name">Workflow Name</Label>
            <Input 
              id="name" 
              value={workflow.name}
              onChange={(e) => setWorkflow({...workflow, name: e.target.value})}
              placeholder="e.g., Auto Budget Optimization"
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea 
              id="description"
              value={workflow.description}
              onChange={(e) => setWorkflow({...workflow, description: e.target.value})}
              placeholder="Describe what this workflow does..."
            />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label>Workflow Steps</Label>
              <Button onClick={addStep} size="sm" variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add Step
              </Button>
            </div>
            <div className="space-y-2">
              {workflow.steps.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  No steps added yet. Click "Add Step" to begin.
                </p>
              ) : (
                workflow.steps.map((step) => (
                  <div key={step.id} className="p-3 border rounded">
                    <Input 
                      value={step.name}
                      onChange={(e) => {
                        const updatedSteps = workflow.steps.map(s => 
                          s.id === step.id ? {...s, name: e.target.value} : s
                        );
                        setWorkflow({...workflow, steps: updatedSteps});
                      }}
                      placeholder="Step name..."
                    />
                  </div>
                ))
              )}
            </div>
          </div>
          <div className="flex space-x-2">
            <Button>
              <Save className="h-4 w-4 mr-2" />
              Save Workflow
            </Button>
            <Button variant="outline">
              <Play className="h-4 w-4 mr-2" />
              Test Workflow
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default WorkflowBuilder;

