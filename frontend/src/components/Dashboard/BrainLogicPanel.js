import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const BrainLogicPanel = ({ onModuleSelect }) => {
  const [activeModule, setActiveModule] = useState('creative');

  const modules = {
    creative: {
      name: 'Creative Intelligence',
      icon: '🎨',
      features: ['Content Analysis', 'Content Repurposing', 'Brand Compliance', 'Performance Optimization']
    },
    market: {
      name: 'Market Intelligence',
      icon: '📈',
      features: ['Vertical Analysis', 'Trend Prediction', 'Competitor Analysis', 'Opportunity Identification']
    },
    client: {
      name: 'Client Intelligence',
      icon: '👥',
      features: ['Behavior Analysis', 'Success Prediction', 'Churn Risk Analysis', 'Satisfaction Tracking']
    },
    customization: {
      name: 'Customization Engine',
      icon: '⚙️',
      features: ['Vertical Templates', 'Brand Customization', 'Custom Workflows', 'Integration Config']
    }
  };

  return (
    <Card className="p-6" data-testid="brain-logic-panel">
      <h2 className="text-2xl font-bold mb-6">🧠 Brain Logic Modules</h2>
      
      <Tabs value={activeModule} onValueChange={setActiveModule}>
        <TabsList className="grid w-full grid-cols-4">
          {Object.entries(modules).map(([key, module]) => (
            <TabsTrigger key={key} value={key} data-testid={`module-tab-${key}`}>
              <span className="mr-2">{module.icon}</span>
              <span className="hidden sm:inline">{module.name.split(' ')[0]}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {Object.entries(modules).map(([key, module]) => (
          <TabsContent key={key} value={key} className="mt-6">
            <div className="space-y-4">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-3xl">{module.icon}</span>
                <h3 className="text-xl font-semibold">{module.name}</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {module.features.map((feature, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onModuleSelect && onModuleSelect(key, feature)}
                    data-testid={`feature-${key}-${index}`}
                  >
                    <p className="font-medium text-sm">{feature}</p>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </Card>
  );
};

export default BrainLogicPanel;
