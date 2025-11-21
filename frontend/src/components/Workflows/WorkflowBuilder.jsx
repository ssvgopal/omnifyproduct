import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Plus,
  Trash2,
  Save,
  Play,
  Settings,
  Loader2,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  GripVertical
} from 'lucide-react';
import api from '@/services/api';

const WorkflowBuilder = () => {
  const [workflow, setWorkflow] = useState({
    name: '',
    description: '',
    steps: [],
    triggers: []
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const actionTypes = [
    { value: 'send_email', label: 'Send Email' },
    { value: 'create_campaign', label: 'Create Campaign' },
    { value: 'update_budget', label: 'Update Budget' },
    { value: 'pause_campaign', label: 'Pause Campaign' },
    { value: 'resume_campaign', label: 'Resume Campaign' },
    { value: 'send_notification', label: 'Send Notification' },
    { value: 'update_targeting', label: 'Update Targeting' },
    { value: 'generate_report', label: 'Generate Report' },
    { value: 'call_api', label: 'Call API' },
    { value: 'wait', label: 'Wait' },
    { value: 'condition', label: 'Condition' }
  ];

  const triggerTypes = [
    { value: 'schedule', label: 'Schedule' },
    { value: 'event', label: 'Event' },
    { value: 'webhook', label: 'Webhook' },
    { value: 'api_call', label: 'API Call' }
  ];

  const handleAddStep = () => {
    setWorkflow({
      ...workflow,
      steps: [
        ...workflow.steps,
        {
          id: `step_${Date.now()}`,
          action_type: 'send_email',
          name: 'New Step',
          config: {}
        }
      ]
    });
  };

  const handleRemoveStep = (stepId) => {
    setWorkflow({
      ...workflow,
      steps: workflow.steps.filter(s => s.id !== stepId)
    });
  };

  const handleStepChange = (stepId, field, value) => {
    setWorkflow({
      ...workflow,
      steps: workflow.steps.map(step =>
        step.id === stepId ? { ...step, [field]: value } : step
      )
    });
  };

  const handleAddTrigger = () => {
    setWorkflow({
      ...workflow,
      triggers: [
        ...workflow.triggers,
        {
          id: `trigger_${Date.now()}`,
          trigger_type: 'schedule',
          config: {}
        }
      ]
    });
  };

  const handleRemoveTrigger = (triggerId) => {
    setWorkflow({
      ...workflow,
      triggers: workflow.triggers.filter(t => t.id !== triggerId)
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      
      const response = await api.post('/api/workflows', {
        name: workflow.name,
        description: workflow.description,
        steps: workflow.steps,
        triggers: workflow.triggers,
        organization_id: 'demo-org-123' // Get from user context
      });

      if (response.data.success) {
        setSuccess('Workflow saved successfully');
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error saving workflow:', err);
      setError('Failed to save workflow');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Workflow Builder</h2>
          <p className="text-gray-600 mt-1">Create automated workflows for your marketing campaigns</p>
        </div>
        <Button onClick={handleSave} disabled={saving || !workflow.name}>
          {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
          Save Workflow
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="bg-green-50 border-green-200">
          <CheckCircle2 className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Workflow Details */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Workflow Name</Label>
            <Input
              id="name"
              value={workflow.name}
              onChange={(e) => setWorkflow({ ...workflow, name: e.target.value })}
              placeholder="e.g., Automated Campaign Optimization"
            />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={workflow.description}
              onChange={(e) => setWorkflow({ ...workflow, description: e.target.value })}
              placeholder="Describe what this workflow does..."
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Triggers */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Triggers</CardTitle>
              <CardDescription>Define when this workflow should run</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleAddTrigger}>
              <Plus className="h-4 w-4 mr-2" />
              Add Trigger
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {workflow.triggers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No triggers configured</p>
              <p className="text-sm mt-2">Add a trigger to define when this workflow runs</p>
            </div>
          ) : (
            <div className="space-y-3">
              {workflow.triggers.map((trigger, index) => (
                <Card key={trigger.id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 space-y-3">
                      <div className="flex items-center space-x-2">
                        <GripVertical className="h-4 w-4 text-gray-400" />
                        <Badge variant="outline">Trigger {index + 1}</Badge>
                      </div>
                      <div>
                        <Label>Trigger Type</Label>
                        <Select
                          value={trigger.trigger_type}
                          onValueChange={(value) => {
                            const newTriggers = [...workflow.triggers];
                            newTriggers[index].trigger_type = value;
                            setWorkflow({ ...workflow, triggers: newTriggers });
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {triggerTypes.map(type => (
                              <SelectItem key={type.value} value={type.value}>
                                {type.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      {trigger.trigger_type === 'schedule' && (
                        <div>
                          <Label>Cron Expression</Label>
                          <Input
                            placeholder="0 9 * * * (9 AM daily)"
                            value={trigger.config.cron || ''}
                            onChange={(e) => {
                              const newTriggers = [...workflow.triggers];
                              newTriggers[index].config = { ...newTriggers[index].config, cron: e.target.value };
                              setWorkflow({ ...workflow, triggers: newTriggers });
                            }}
                          />
                        </div>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveTrigger(trigger.id)}
                      className="ml-2"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Steps */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Workflow Steps</CardTitle>
              <CardDescription>Define the actions this workflow will perform</CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleAddStep}>
              <Plus className="h-4 w-4 mr-2" />
              Add Step
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {workflow.steps.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No steps configured</p>
              <p className="text-sm mt-2">Add steps to define what this workflow does</p>
            </div>
          ) : (
            <div className="space-y-4">
              {workflow.steps.map((step, index) => (
                <Card key={step.id} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 space-y-3">
                      <div className="flex items-center space-x-2">
                        <GripVertical className="h-4 w-4 text-gray-400" />
                        <Badge variant="outline">Step {index + 1}</Badge>
                        <ArrowRight className="h-4 w-4 text-gray-400" />
                      </div>
                      <div>
                        <Label>Action Type</Label>
                        <Select
                          value={step.action_type}
                          onValueChange={(value) => handleStepChange(step.id, 'action_type', value)}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {actionTypes.map(type => (
                              <SelectItem key={type.value} value={type.value}>
                                {type.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Step Name</Label>
                        <Input
                          value={step.name}
                          onChange={(e) => handleStepChange(step.id, 'name', e.target.value)}
                          placeholder="e.g., Send notification email"
                        />
                      </div>
                      {/* Action-specific configuration can be added here */}
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveStep(step.id)}
                      className="ml-2"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default WorkflowBuilder;

