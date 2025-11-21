import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Plus,
  Calendar,
  Clock,
  Mail,
  Download,
  Trash2,
  Play,
  Pause,
  Edit,
  Loader2,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import api from '@/services/api';

const ScheduledReports = () => {
  const [scheduledReports, setScheduledReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    report_id: '',
    schedule_type: 'daily',
    time: '09:00',
    recipients: [],
    format: 'pdf'
  });

  const scheduleTypes = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'custom', label: 'Custom' }
  ];

  const formats = [
    { value: 'pdf', label: 'PDF' },
    { value: 'excel', label: 'Excel' },
    { value: 'csv', label: 'CSV' }
  ];

  useEffect(() => {
    loadScheduledReports();
  }, []);

  const loadScheduledReports = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/reporting/scheduled-reports', {
        params: { organization_id: 'demo-org-123' }
      });
      if (response.data && response.data.schedules) {
        setScheduledReports(response.data.schedules || []);
      }
    } catch (err) {
      console.error('Error loading scheduled reports:', err);
      // Use mock data as fallback
      setScheduledReports([
        {
          id: 'schedule_1',
          report_name: 'Weekly Campaign Performance',
          schedule_type: 'weekly',
          time: '09:00',
          day_of_week: 'Monday',
          recipients: ['admin@example.com'],
          format: 'pdf',
          status: 'active',
          last_run: '2025-01-20T09:00:00Z',
          next_run: '2025-01-27T09:00:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSchedule = async () => {
    try {
      setCreating(true);
      const response = await api.post('/api/reporting/scheduled-reports', {
        ...newSchedule,
        organization_id: 'demo-org-123'
      });

      if (response.data) {
        await loadScheduledReports();
        setShowCreateDialog(false);
        setNewSchedule({
          report_id: '',
          schedule_type: 'daily',
          time: '09:00',
          recipients: [],
          format: 'pdf'
        });
      }
    } catch (err) {
      console.error('Error creating schedule:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleToggleSchedule = async (scheduleId, currentStatus) => {
    try {
      await api.put(`/api/reporting/scheduled-reports/${scheduleId}/status`, {
        status: currentStatus === 'active' ? 'paused' : 'active'
      });
      await loadScheduledReports();
    } catch (err) {
      console.error('Error toggling schedule:', err);
    }
  };

  const handleDeleteSchedule = async (scheduleId) => {
    if (!confirm('Are you sure you want to delete this scheduled report?')) {
      return;
    }

    try {
      await api.delete(`/api/reporting/scheduled-reports/${scheduleId}`);
      await loadScheduledReports();
    } catch (err) {
      console.error('Error deleting schedule:', err);
    }
  };

  const getStatusBadge = (status) => {
    return status === 'active' ? (
      <Badge className="bg-green-100 text-green-800">Active</Badge>
    ) : (
      <Badge className="bg-yellow-100 text-yellow-800">Paused</Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Scheduled Reports</h2>
          <p className="text-gray-600 mt-1">Automate report generation and delivery</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Report
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Schedule Report</DialogTitle>
              <DialogDescription>Configure automated report generation and delivery</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="report_id">Report</Label>
                <Input
                  id="report_id"
                  value={newSchedule.report_id}
                  onChange={(e) => setNewSchedule({ ...newSchedule, report_id: e.target.value })}
                  placeholder="Report ID or name"
                />
              </div>
              <div>
                <Label htmlFor="schedule_type">Schedule Type</Label>
                <Select
                  value={newSchedule.schedule_type}
                  onValueChange={(value) => setNewSchedule({ ...newSchedule, schedule_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {scheduleTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="time">Time</Label>
                <Input
                  id="time"
                  type="time"
                  value={newSchedule.time}
                  onChange={(e) => setNewSchedule({ ...newSchedule, time: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="format">Format</Label>
                <Select
                  value={newSchedule.format}
                  onValueChange={(value) => setNewSchedule({ ...newSchedule, format: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {formats.map(format => (
                      <SelectItem key={format.value} value={format.value}>
                        {format.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateSchedule} disabled={creating || !newSchedule.report_id}>
                  {creating ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                  Create Schedule
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500">Loading scheduled reports...</p>
          </CardContent>
        </Card>
      ) : scheduledReports.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-semibold mb-2">No Scheduled Reports</h3>
            <p className="text-gray-600 mb-4">Create your first scheduled report to automate delivery</p>
            <Button onClick={() => setShowCreateDialog(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Report
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {scheduledReports.map((schedule) => (
            <Card key={schedule.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{schedule.report_name}</CardTitle>
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {schedule.schedule_type}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {schedule.time}
                      </div>
                      {schedule.day_of_week && (
                        <div>{schedule.day_of_week}</div>
                      )}
                    </div>
                  </div>
                  {getStatusBadge(schedule.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Format</p>
                    <p className="font-semibold uppercase">{schedule.format}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Recipients</p>
                    <p className="font-semibold">{schedule.recipients?.length || 0}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Last Run</p>
                    <p className="font-semibold text-sm">
                      {schedule.last_run ? new Date(schedule.last_run).toLocaleDateString() : 'Never'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Next Run</p>
                    <p className="font-semibold text-sm">
                      {schedule.next_run ? new Date(schedule.next_run).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
                {schedule.recipients && schedule.recipients.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">Recipients:</p>
                    <div className="flex flex-wrap gap-2">
                      {schedule.recipients.map((email, index) => (
                        <Badge key={index} variant="outline">
                          <Mail className="h-3 w-3 mr-1" />
                          {email}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-end space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleToggleSchedule(schedule.id, schedule.status)}
                >
                  {schedule.status === 'active' ? (
                    <>
                      <Pause className="h-3 w-3 mr-1" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="h-3 w-3 mr-1" />
                      Resume
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDeleteSchedule(schedule.id)}
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  Delete
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScheduledReports;

