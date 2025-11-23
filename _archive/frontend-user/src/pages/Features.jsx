import React from 'react';
import { Card } from '@omnify/shared-ui';
import { 
  BarChart3, 
  Zap, 
  Target,
  TrendingUp,
  Shield,
  Clock,
  Users,
  Globe
} from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: BarChart3,
      title: 'Unified Attribution',
      description: 'See the complete customer journey across all platforms with multi-touch attribution models.',
      color: 'blue'
    },
    {
      icon: Zap,
      title: 'Predictive Intelligence',
      description: 'Get 7-day advance warnings on creative fatigue, budget waste, and performance drops.',
      color: 'purple'
    },
    {
      icon: Target,
      title: 'Prescriptive Actions',
      description: 'Receive clear recommendations on what to change, why, and the expected impact.',
      color: 'green'
    },
    {
      icon: TrendingUp,
      title: 'Real-Time Optimization',
      description: 'Automatically reallocate budget to winning channels based on real-time performance.',
      color: 'orange'
    },
    {
      icon: Shield,
      title: 'Fraud Prevention',
      description: 'Detect and prevent ad fraud in real-time, protecting your budget and brand.',
      color: 'red'
    },
    {
      icon: Clock,
      title: 'Time Zone Optimization',
      description: 'Schedule campaigns for optimal engagement windows across global markets.',
      color: 'indigo'
    },
    {
      icon: Users,
      title: 'Audience Intelligence',
      description: 'Identify high-value customer segments and optimize targeting precision.',
      color: 'pink'
    },
    {
      icon: Globe,
      title: 'Cross-Channel Orchestration',
      description: 'Coordinate campaigns across channels to eliminate waste and reduce fatigue.',
      color: 'teal'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      purple: 'bg-purple-100 text-purple-600',
      green: 'bg-green-100 text-green-600',
      orange: 'bg-orange-100 text-orange-600',
      red: 'bg-red-100 text-red-600',
      indigo: 'bg-indigo-100 text-indigo-600',
      pink: 'bg-pink-100 text-pink-600',
      teal: 'bg-teal-100 text-teal-600'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Powerful Features for Modern Marketers
          </h1>
          <p className="text-xl text-gray-600">
            Everything you need to maximize ROAS and eliminate waste
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                <div className={`p-3 rounded-lg w-fit mb-4 ${getColorClasses(feature.color)}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </Card>
            );
          })}
        </div>

        <div className="mt-16 bg-white rounded-lg p-8 shadow-sm">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            Why Choose Omnify?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-indigo-600 mb-2">70%</div>
              <div className="text-gray-600">Cost savings vs competitors</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-indigo-600 mb-2">15min</div>
              <div className="text-gray-600">Weekly reporting time</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-indigo-600 mb-2">18%</div>
              <div className="text-gray-600">Average waste reduction</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Features;
