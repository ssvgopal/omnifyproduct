import React from 'react';
import { Card, Button, Tabs, TabsContent, TabsList, TabsTrigger } from '@omnify/shared-ui';
import { 
  BarChart3, 
  TrendingUp, 
  Target,
  DollarSign,
  Users,
  Zap
} from 'lucide-react';

const Demo = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            See Omnify in Action
          </h1>
          <p className="text-xl text-gray-600">
            Interactive demo of our unified marketing intelligence platform
          </p>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="attribution">Attribution</TabsTrigger>
            <TabsTrigger value="predictions">Predictions</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Total Revenue</span>
                  <DollarSign className="h-5 w-5 text-green-500" />
                </div>
                <div className="text-2xl font-bold">$2.4M</div>
                <div className="text-sm text-green-600 mt-1">+12% vs last month</div>
              </Card>
              <Card className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">ROAS</span>
                  <TrendingUp className="h-5 w-5 text-blue-500" />
                </div>
                <div className="text-2xl font-bold">4.2x</div>
                <div className="text-sm text-blue-600 mt-1">+0.8x vs last month</div>
              </Card>
              <Card className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Active Campaigns</span>
                  <Target className="h-5 w-5 text-purple-500" />
                </div>
                <div className="text-2xl font-bold">24</div>
                <div className="text-sm text-gray-600 mt-1">8 performing above target</div>
              </Card>
              <Card className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Ad Spend</span>
                  <BarChart3 className="h-5 w-5 text-orange-500" />
                </div>
                <div className="text-2xl font-bold">$571k</div>
                <div className="text-sm text-gray-600 mt-1">On track for budget</div>
              </Card>
            </div>
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Top Performing Channels</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-green-50 rounded">
                  <span className="font-medium">Meta Ads</span>
                  <span className="text-green-600 font-semibold">4.8x ROAS</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded">
                  <span className="font-medium">Google Search</span>
                  <span className="text-blue-600 font-semibold">4.2x ROAS</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-purple-50 rounded">
                  <span className="font-medium">LinkedIn Ads</span>
                  <span className="text-purple-600 font-semibold">3.9x ROAS</span>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="attribution">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Multi-Touch Attribution</h3>
              <p className="text-gray-600 mb-4">
                See how each touchpoint contributes to revenue across the customer journey.
              </p>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-500">
                  Demo attribution data will be displayed here. This shows unified data from 
                  Meta, Google, LinkedIn, and other platforms.
                </p>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="predictions">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Predictive Alerts</h3>
              <div className="space-y-4">
                <div className="p-4 border-l-4 border-yellow-400 bg-yellow-50">
                  <div className="flex items-center mb-2">
                    <Zap className="h-5 w-5 text-yellow-600 mr-2" />
                    <span className="font-semibold">Creative Fatigue Warning</span>
                  </div>
                  <p className="text-sm text-gray-700">
                    Campaign "Summer Sale" shows 15% engagement drop. Predicted to hit 
                    fatigue threshold in 4 days.
                  </p>
                </div>
                <div className="p-4 border-l-4 border-green-400 bg-green-50">
                  <div className="flex items-center mb-2">
                    <TrendingUp className="h-5 w-5 text-green-600 mr-2" />
                    <span className="font-semibold">Opportunity Detected</span>
                  </div>
                  <p className="text-sm text-gray-700">
                    Google Search campaign performing 25% above forecast. Consider 
                    increasing budget.
                  </p>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="recommendations">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Prescriptive Recommendations</h3>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">Shift Budget from Meta to Google</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Google Search is driving 3x more profit per dollar spent.
                      </p>
                    </div>
                    <Button size="sm">Apply</Button>
                  </div>
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Expected Impact:</span>
                      <span className="font-semibold text-green-600">+$75k Revenue</span>
                    </div>
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold">Rotate Creative Set</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Current creative showing fatigue signals. Activate backup creative.
                      </p>
                    </div>
                    <Button size="sm">Apply</Button>
                  </div>
                  <div className="mt-3 pt-3 border-t">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Expected Impact:</span>
                      <span className="font-semibold text-green-600">Maintain 4.2x ROAS</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        <div className="mt-12 text-center">
          <Button size="lg" className="px-8">
            Start Free Trial
          </Button>
          <p className="mt-4 text-sm text-gray-500">
            No credit card required • 14-day free trial
          </p>
        </div>
      </div>
    </div>
  );
};

export default Demo;


