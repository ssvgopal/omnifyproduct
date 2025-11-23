import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@omnify/shared-ui';
import { DollarSign, TrendingUp, Target, Users } from 'lucide-react';

const PerformanceMetrics = () => {
  const metrics = [
    {
      label: 'Total Revenue',
      value: '$2.4M',
      change: '+12%',
      changeType: 'positive',
      icon: DollarSign
    },
    {
      label: 'ROAS',
      value: '4.2x',
      change: '+0.8x',
      changeType: 'positive',
      icon: TrendingUp
    },
    {
      label: 'Active Campaigns',
      value: '24',
      change: '8 above target',
      changeType: 'neutral',
      icon: Target
    },
    {
      label: 'Ad Spend',
      value: '$571k',
      change: 'On track',
      changeType: 'neutral',
      icon: Users
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">{metric.label}</span>
                <Icon className="h-5 w-5 text-gray-400" />
              </div>
              <div className="text-2xl font-bold mb-1">{metric.value}</div>
              <div className={`text-sm ${
                metric.changeType === 'positive' 
                  ? 'text-green-600' 
                  : metric.changeType === 'negative'
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}>
                {metric.change}
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default PerformanceMetrics;

