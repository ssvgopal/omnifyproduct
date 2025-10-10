import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const PlatformSelector = ({ selectedPlatform, onPlatformChange }) => {
  const platforms = [
    {
      id: 'agentkit',
      name: 'AgentKit',
      description: 'OpenAI AgentKit with visual workflows',
      icon: '🤖',
      color: 'bg-blue-500'
    },
    {
      id: 'gohighlevel',
      name: 'GoHighLevel',
      description: 'CRM & Marketing Automation',
      icon: '📊',
      color: 'bg-green-500'
    },
    {
      id: 'custom',
      name: 'Custom Platform',
      description: 'Microservices Architecture',
      icon: '⚙️',
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {platforms.map((platform) => (
        <Card
          key={platform.id}
          className={`p-6 cursor-pointer transition-all hover:shadow-lg ${
            selectedPlatform === platform.id ? 'ring-2 ring-blue-500 shadow-lg' : ''
          }`}
          onClick={() => onPlatformChange(platform.id)}
          data-testid={`platform-${platform.id}`}
        >
          <div className="flex items-start space-x-4">
            <div className={`text-4xl ${platform.color} p-3 rounded-lg bg-opacity-10`}>
              {platform.icon}
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-1">{platform.name}</h3>
              <p className="text-sm text-gray-600">{platform.description}</p>
              {selectedPlatform === platform.id && (
                <div className="mt-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Active
                  </span>
                </div>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default PlatformSelector;
