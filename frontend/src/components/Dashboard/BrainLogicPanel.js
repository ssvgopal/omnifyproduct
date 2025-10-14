import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Brain, 
  TrendingUp, 
  Users, 
  Settings, 
  Zap, 
  Shield, 
  BarChart3, 
  Target,
  Sparkles,
  Activity,
  CheckCircle,
  AlertTriangle,
  Clock
} from 'lucide-react';

const BrainLogicPanel = ({ onModuleSelect }) => {
  const [activeModule, setActiveModule] = useState('creative');
  const [moduleStats, setModuleStats] = useState({});

  useEffect(() => {
    // Simulate loading module statistics
    setModuleStats({
      creative: { accuracy: 94, predictions: 1247, status: 'excellent' },
      market: { accuracy: 89, predictions: 892, status: 'good' },
      client: { accuracy: 91, predictions: 1156, status: 'excellent' },
      customization: { accuracy: 87, predictions: 743, status: 'good' }
    });
  }, []);

  const modules = {
    creative: {
      name: 'Creative Intelligence',
      icon: Brain,
      description: 'AI-powered content analysis and optimization',
      features: [
        { name: 'Content Analysis', status: 'active', accuracy: 96 },
        { name: 'Content Repurposing', status: 'active', accuracy: 92 },
        { name: 'Brand Compliance', status: 'active', accuracy: 98 },
        { name: 'Performance Optimization', status: 'active', accuracy: 94 }
      ],
      color: 'blue',
      gradient: 'from-blue-500 to-blue-600'
    },
    market: {
      name: 'Market Intelligence',
      icon: TrendingUp,
      description: 'Real-time market analysis and trend prediction',
      features: [
        { name: 'Vertical Analysis', status: 'active', accuracy: 89 },
        { name: 'Trend Prediction', status: 'active', accuracy: 87 },
        { name: 'Competitor Analysis', status: 'active', accuracy: 91 },
        { name: 'Opportunity Identification', status: 'active', accuracy: 88 }
      ],
      color: 'green',
      gradient: 'from-green-500 to-green-600'
    },
    client: {
      name: 'Client Intelligence',
      icon: Users,
      description: 'Advanced client behavior and success prediction',
      features: [
        { name: 'Behavior Analysis', status: 'active', accuracy: 93 },
        { name: 'Success Prediction', status: 'active', accuracy: 91 },
        { name: 'Churn Risk Analysis', status: 'active', accuracy: 89 },
        { name: 'Satisfaction Tracking', status: 'active', accuracy: 95 }
      ],
      color: 'purple',
      gradient: 'from-purple-500 to-purple-600'
    },
    customization: {
      name: 'Customization Engine',
      icon: Settings,
      description: 'Adaptive workflows and integration management',
      features: [
        { name: 'Vertical Templates', status: 'active', accuracy: 87 },
        { name: 'Brand Customization', status: 'active', accuracy: 92 },
        { name: 'Custom Workflows', status: 'active', accuracy: 89 },
        { name: 'Integration Config', status: 'active', accuracy: 94 }
      ],
      color: 'orange',
      gradient: 'from-orange-500 to-orange-600'
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'excellent': return 'text-green-600 bg-green-100';
      case 'good': return 'text-blue-600 bg-blue-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 95) return 'text-green-600';
    if (accuracy >= 90) return 'text-blue-600';
    if (accuracy >= 85) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-white to-gray-50 border-0 shadow-lg" data-testid="brain-logic-panel">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Sparkles className="mr-3 text-blue-500" />
            Brain Logic Modules
          </h2>
          <p className="text-gray-600 mt-1">AI-powered intelligence for marketing success</p>
        </div>
        <Badge variant="outline" className="px-3 py-1">
          <Activity className="w-4 h-4 mr-1" />
          All Systems Active
        </Badge>
      </div>
      
      <Tabs value={activeModule} onValueChange={setActiveModule}>
        <TabsList className="grid w-full grid-cols-4 bg-gray-100 p-1 rounded-lg">
          {Object.entries(modules).map(([key, module]) => {
            const Icon = module.icon;
            const stats = moduleStats[key] || {};
            return (
              <TabsTrigger 
                key={key} 
                value={key} 
                className="flex items-center space-x-2 data-[state=active]:bg-white data-[state=active]:shadow-sm"
                data-testid={`module-tab-${key}`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline font-medium">{module.name.split(' ')[0]}</span>
                <Badge 
                  variant="secondary" 
                  className={`ml-1 text-xs ${getStatusColor(stats.status)}`}
                >
                  {stats.accuracy || 0}%
                </Badge>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {Object.entries(modules).map(([key, module]) => {
          const Icon = module.icon;
          const stats = moduleStats[key] || {};
          
          return (
            <TabsContent key={key} value={key} className="mt-6">
              <div className="space-y-6">
                {/* Module Header */}
                <div className="flex items-start justify-between p-6 bg-gradient-to-r from-white to-gray-50 rounded-xl border">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-r ${module.gradient} text-white`}>
                      <Icon className="w-8 h-8" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">{module.name}</h3>
                      <p className="text-gray-600 mt-1">{module.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">{stats.accuracy || 0}%</div>
                    <div className="text-sm text-gray-500">Accuracy</div>
                    <div className="text-sm text-gray-500">{stats.predictions || 0} predictions</div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-blue-800">Model Accuracy</p>
                        <p className="text-2xl font-bold text-blue-900">{stats.accuracy || 0}%</p>
                      </div>
                      <Target className="w-8 h-8 text-blue-600" />
                    </div>
                    <Progress value={stats.accuracy || 0} className="mt-2" />
                  </Card>

                  <Card className="p-4 bg-gradient-to-r from-green-50 to-green-100 border-green-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-green-800">Predictions Made</p>
                        <p className="text-2xl font-bold text-green-900">{stats.predictions || 0}</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="mt-2 text-sm text-green-700">+12% this week</div>
                  </Card>

                  <Card className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-purple-800">System Status</p>
                        <p className="text-lg font-bold text-purple-900 capitalize">{stats.status || 'active'}</p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-purple-600" />
                    </div>
                    <div className="mt-2 text-sm text-purple-700">Last updated: 2 min ago</div>
                  </Card>
                </div>
                
                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {module.features.map((feature, index) => (
                    <Card 
                      key={index}
                      className="p-4 hover:shadow-md transition-all duration-200 cursor-pointer border-l-4 border-l-blue-500"
                      onClick={() => onModuleSelect && onModuleSelect(key, feature.name)}
                      data-testid={`feature-${key}-${index}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Zap className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-gray-900">{feature.name}</h4>
                            <p className="text-sm text-gray-600">AI-powered analysis</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge 
                            variant="outline" 
                            className={`${getAccuracyColor(feature.accuracy)} border-current`}
                          >
                            {feature.accuracy}%
                          </Badge>
                          <div className="flex items-center mt-1">
                            <CheckCircle className="w-4 h-4 text-green-500 mr-1" />
                            <span className="text-xs text-green-600">Active</span>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>

                {/* Learning Progress */}
                <Card className="p-6 bg-gradient-to-r from-gray-50 to-gray-100">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-gray-900">Learning Progress</h4>
                    <Badge variant="outline" className="text-green-600 border-green-200">
                      <Clock className="w-3 h-3 mr-1" />
                      Improving
                    </Badge>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Model Training</span>
                      <span className="text-sm font-medium text-gray-900">87% Complete</span>
                    </div>
                    <Progress value={87} className="h-2" />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Data Processing</span>
                      <span className="text-sm font-medium text-gray-900">94% Complete</span>
                    </div>
                    <Progress value={94} className="h-2" />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Validation</span>
                      <span className="text-sm font-medium text-gray-900">91% Complete</span>
                    </div>
                    <Progress value={91} className="h-2" />
                  </div>
                </Card>
              </div>
            </TabsContent>
          );
        })}
      </Tabs>
    </Card>
  );
};

export default BrainLogicPanel;