import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@omnify/shared-ui';
import { BarChart3, TrendingUp } from 'lucide-react';

const UnifiedAttribution = () => {
  // This will be connected to MEMORY module API
  const attributionData = {
    meta: { revenue: 42, spend: 35, roas: 4.2 },
    google: { revenue: 31, spend: 28, roas: 3.8 },
    linkedin: { revenue: 18, spend: 15, roas: 3.5 },
    other: { revenue: 9, spend: 22, roas: 1.2 }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <BarChart3 className="h-5 w-5 mr-2" />
          Unified Attribution (MEMORY)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="text-sm text-gray-600 mb-4">
            Time-Decay Multi-Touch Attribution - Single Source of Truth
          </div>
          {Object.entries(attributionData).map(([platform, data]) => (
            <div key={platform} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex-1">
                <div className="font-medium capitalize">{platform}</div>
                <div className="text-sm text-gray-600">
                  {data.revenue}% of revenue • {data.spend}% of spend
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="font-semibold">{data.roas}x</div>
                  <div className="text-xs text-gray-500">ROAS</div>
                </div>
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-indigo-600 h-2 rounded-full" 
                    style={{ width: `${data.revenue}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Revenue Attribution</span>
              <span className="font-semibold">100%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default UnifiedAttribution;

