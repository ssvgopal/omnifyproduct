import React, { useState, useEffect } from 'react';
import PlatformSelector from '@/components/Dashboard/PlatformSelector';
import BrainLogicPanel from '@/components/Dashboard/BrainLogicPanel';
import AnalyticsDashboard from '@/components/Dashboard/AnalyticsDashboard';
import EyesModule from '@/components/Dashboard/EyesModule';
import ProactiveIntelligenceDashboard from '@/components/Dashboard/ProactiveIntelligenceDashboard';
import MagicalOnboardingWizard from '@/components/Onboarding/MagicalOnboardingWizard';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import api from '@/services/api';

const Home = () => {
  const [selectedPlatform, setSelectedPlatform] = useState('agentkit');
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const status = await api.getHealthStatus();
      setHealthStatus(status);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const handleModuleSelect = (module, feature) => {
    console.log(`Selected: ${module} - ${feature}`);
    // Could navigate to specific module page or open a modal
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🌐 Omnify Cloud Connect
              </h1>
              <p className="text-gray-600 mt-1">Unified Multi-Platform Solution</p>
            </div>
            <div className="flex items-center space-x-4">
              {healthStatus && (
                <div className="flex items-center space-x-2" data-testid="health-status">
                  <div className={`w-2 h-2 rounded-full ${
                    healthStatus.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  <span className="text-sm text-gray-600 capitalize">{healthStatus.status}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Platform Selector */}
        <PlatformSelector 
          selectedPlatform={selectedPlatform}
          onPlatformChange={setSelectedPlatform}
        />

        {/* Main Dashboard Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-7">
            <TabsTrigger value="overview" data-testid="tab-overview">Overview</TabsTrigger>
            <TabsTrigger value="brain-logic" data-testid="tab-brain-logic">Brain Logic</TabsTrigger>
            <TabsTrigger value="analytics" data-testid="tab-analytics">Analytics</TabsTrigger>
            <TabsTrigger value="eyes" data-testid="tab-eyes">EYES</TabsTrigger>
            <TabsTrigger value="proactive-intelligence" data-testid="tab-proactive-intelligence">🧠 Proactive AI</TabsTrigger>
            <TabsTrigger value="onboarding" data-testid="tab-onboarding">🎯 Onboarding</TabsTrigger>
            <TabsTrigger value="integrations" data-testid="tab-integrations">Integrations</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">🚀 Quick Start</h2>
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <h3 className="font-semibold mb-1">1. Select Your Platform</h3>
                    <p className="text-sm text-gray-600">Choose from AgentKit, GoHighLevel, or Custom</p>
                  </div>
                  <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <h3 className="font-semibold mb-1">2. Configure Brain Logic</h3>
                    <p className="text-sm text-gray-600">Customize AI intelligence for your vertical</p>
                  </div>
                  <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <h3 className="font-semibold mb-1">3. Connect Integrations</h3>
                    <p className="text-sm text-gray-600">Link your tools and services</p>
                  </div>
                  <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <h3 className="font-semibold mb-1">4. Monitor Analytics</h3>
                    <p className="text-sm text-gray-600">Track performance across platforms</p>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">🎯 Platform Features</h2>
                <div className="space-y-3">
                  {selectedPlatform === 'agentkit' && (
                    <>
                      <Feature icon="🤖" title="AI Agents" description="Visual workflow automation" />
                      <Feature icon="📊" title="ChatGPT Integration" description="Enterprise-grade AI" />
                      <Feature icon="🔒" title="SOC 2 Compliant" description="Built-in security" />
                    </>
                  )}
                  {selectedPlatform === 'gohighlevel' && (
                    <>
                      <Feature icon="💼" title="CRM System" description="Complete client management" />
                      <Feature icon="📧" title="Marketing Automation" description="Email & SMS campaigns" />
                      <Feature icon="🏷️" title="White Label" description="Custom branding" />
                    </>
                  )}
                  {selectedPlatform === 'custom' && (
                    <>
                      <Feature icon="⚙️" title="Microservices" description="Scalable architecture" />
                      <Feature icon="🚀" title="Kubernetes" description="Container orchestration" />
                      <Feature icon="🔧" title="Full Control" description="Complete customization" />
                    </>
                  )}
                </div>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="brain-logic">
            <BrainLogicPanel onModuleSelect={handleModuleSelect} />
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsDashboard />
          </TabsContent>

          <TabsContent value="eyes">
            <EyesModule />
          </TabsContent>

          <TabsContent value="proactive-intelligence">
            <ProactiveIntelligenceDashboard />
          </TabsContent>

          <TabsContent value="onboarding">
            <MagicalOnboardingWizard />
          </TabsContent>

          <TabsContent value="integrations">
            <IntegrationsPanel />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

const Feature = ({ icon, title, description }) => (
  <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
    <span className="text-2xl">{icon}</span>
    <div>
      <h4 className="font-semibold text-sm">{title}</h4>
      <p className="text-xs text-gray-600">{description}</p>
    </div>
  </div>
);

const IntegrationsPanel = () => {
  const [integrations, setIntegrations] = useState([]);
  const [available, setAvailable] = useState(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const [registered, availableData] = await Promise.all([
        api.listRegisteredIntegrations(),
        api.listAvailableIntegrations()
      ]);
      setIntegrations(registered.integrations || []);
      setAvailable(availableData);
    } catch (error) {
      console.error('Error loading integrations:', error);
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">🔗 Integration Hub</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          <IntegrationCategory icon="📱" title="Social Media" count={5} />
          <IntegrationCategory icon="🤖" title="AI Services" count={3} />
          <IntegrationCategory icon="📊" title="Analytics" count={3} />
          <IntegrationCategory icon="💬" title="Communication" count={3} />
          <IntegrationCategory icon="💳" title="Payment" count={2} />
          <IntegrationCategory icon="➕" title="Custom" count={0} />
        </div>

        {integrations.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-4">Registered Integrations</h3>
            <div className="space-y-2">
              {integrations.map((integration) => (
                <div key={integration.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{integration.name}</h4>
                    <p className="text-sm text-gray-600">{integration.type}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    integration.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {integration.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

const IntegrationCategory = ({ icon, title, count }) => (
  <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
    <div className="flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h4 className="font-medium">{title}</h4>
          <p className="text-xs text-gray-600">{count} available</p>
        </div>
      </div>
      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </div>
  </div>
);

export default Home;
