import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@omnify/shared-ui';
import { Zap, AlertTriangle, TrendingUp } from 'lucide-react';

const PredictiveAlerts = () => {
  // This will be connected to ORACLE module API
  const alerts = [
    {
      type: 'warning',
      title: 'Creative Fatigue Warning',
      message: 'Meta ROAS dropped 12% week-over-week due to creative fatigue',
      riskFactors: ['High frequency (3.2x)', 'Audience saturation (78%)'],
      predictedDate: '4 days',
      icon: AlertTriangle
    },
    {
      type: 'opportunity',
      title: 'Performance Opportunity',
      message: 'Google Search campaign performing 25% above forecast',
      riskFactors: [],
      predictedDate: 'Ongoing',
      icon: TrendingUp
    }
  ];

  const getAlertColor = (type) => {
    return type === 'warning' ? 'yellow' : 'green';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Zap className="h-5 w-5 mr-2" />
          Predictive Alerts (ORACLE)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {alerts.map((alert, index) => {
            const Icon = alert.icon;
            const color = getAlertColor(alert.type);
            return (
              <div 
                key={index} 
                className={`p-4 border-l-4 rounded ${
                  color === 'yellow' 
                    ? 'border-yellow-400 bg-yellow-50' 
                    : 'border-green-400 bg-green-50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <Icon className={`h-5 w-5 mr-2 ${
                      color === 'yellow' ? 'text-yellow-600' : 'text-green-600'
                    }`} />
                    <span className="font-semibold">{alert.title}</span>
                  </div>
                  <Badge variant={color === 'yellow' ? 'destructive' : 'default'}>
                    {alert.type === 'warning' ? 'Warning' : 'Opportunity'}
                  </Badge>
                </div>
                <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
                {alert.riskFactors.length > 0 && (
                  <div className="mt-2">
                    <div className="text-xs font-medium text-gray-600 mb-1">Risk Factors:</div>
                    <ul className="text-xs text-gray-600 list-disc list-inside">
                      {alert.riskFactors.map((factor, i) => (
                        <li key={i}>{factor}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="mt-2 text-xs text-gray-500">
                  Predicted impact: {alert.predictedDate}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default PredictiveAlerts;

