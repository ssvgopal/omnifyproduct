import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@omnify/shared-ui';
import { Target, ArrowRight, TrendingUp } from 'lucide-react';

const InsightCards = () => {
  // This will be connected to CURIOSITY module API
  const recommendations = [
    {
      id: 1,
      title: 'Shift $50k from Meta to Google',
      reason: 'Google Search is driving 3x more profit per dollar spent',
      expectedLift: '$75k Revenue',
      confidence: 'High',
      action: 'budget_shift'
    },
    {
      id: 2,
      title: 'Rotate Creative Set "Summer Sale"',
      reason: 'Creative showing fatigue signals. Backup creative expected to maintain 4.2x ROAS',
      expectedLift: 'Maintain Performance',
      confidence: 'Medium',
      action: 'creative_rotation'
    },
    {
      id: 3,
      title: 'Increase LinkedIn Budget by 20%',
      reason: 'LinkedIn campaigns performing 15% above target with room to scale',
      expectedLift: '+$28k Revenue',
      confidence: 'High',
      action: 'budget_increase'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Target className="h-5 w-5 mr-2" />
          Prescriptive Recommendations (CURIOSITY)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <div key={rec.id} className="p-4 border rounded-lg hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-semibold text-lg mb-1">{rec.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{rec.reason}</p>
                  <div className="flex items-center space-x-4 mt-3">
                    <div>
                      <span className="text-xs text-gray-500">Expected Impact:</span>
                      <span className="ml-2 font-semibold text-green-600">{rec.expectedLift}</span>
                    </div>
                    <Badge variant={rec.confidence === 'High' ? 'default' : 'secondary'}>
                      {rec.confidence} Confidence
                    </Badge>
                  </div>
                </div>
              </div>
              <div className="flex items-center justify-between pt-3 border-t">
                <div className="text-xs text-gray-500">
                  Action: {rec.action.replace('_', ' ')}
                </div>
                <Button size="sm" className="ml-auto">
                  Apply Recommendation
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t text-center">
          <p className="text-sm text-gray-600">
            Recommendations updated in real-time based on performance data
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default InsightCards;

