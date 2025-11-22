import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@omnify/shared-ui';
import { Activity, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

const SystemHealth = () => {
  const services = [
    { name: 'Backend API', status: 'healthy', responseTime: 45, uptime: '99.9%' },
    { name: 'MongoDB', status: 'healthy', responseTime: 12, uptime: '100%' },
    { name: 'Redis', status: 'healthy', responseTime: 3, uptime: '99.8%' },
    { name: 'RabbitMQ', status: 'warning', responseTime: 89, uptime: '98.5%' }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Activity className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      healthy: 'default',
      warning: 'secondary',
      critical: 'destructive'
    };
    return <Badge variant={variants[status] || 'secondary'} className="capitalize">{status}</Badge>;
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">System Health</h1>
        <p className="text-gray-600">Monitor system services and performance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {services.map((service) => (
          <Card key={service.name}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  {getStatusIcon(service.status)}
                  <span className="ml-2">{service.name}</span>
                </CardTitle>
                {getStatusBadge(service.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Response Time:</span>
                  <span className="font-semibold">{service.responseTime}ms</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Uptime:</span>
                  <span className="font-semibold">{service.uptime}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default SystemHealth;
