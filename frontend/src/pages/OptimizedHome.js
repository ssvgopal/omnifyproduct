import React, { Suspense, lazy } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Lazy load heavy dashboard components
const BrainLogicPanel = lazy(() => import('@/components/Dashboard/BrainLogicPanel'));
const AnalyticsDashboard = lazy(() => import('@/components/Dashboard/AnalyticsDashboard'));
const EyesModule = lazy(() => import('@/components/Dashboard/EyesModule'));
const ProactiveIntelligenceDashboard = lazy(() => import('@/components/Dashboard/ProactiveIntelligenceDashboard'));
const MagicalOnboardingWizard = lazy(() => import('@/components/Onboarding/MagicalOnboardingWizard'));
const InstantValueDeliveryDashboard = lazy(() => import('@/components/Dashboard/InstantValueDeliveryDashboard'));
const CustomerOrchestrationDashboard = lazy(() => import('@/components/Dashboard/CustomerOrchestrationDashboard'));
const PredictiveIntelligenceDashboard = lazy(() => import('@/components/Dashboard/PredictiveIntelligenceDashboard'));
const AdaptiveClientLearningDashboard = lazy(() => import('@/components/Dashboard/AdaptiveClientLearningDashboard'));
const HumanExpertInterventionDashboard = lazy(() => import('@/components/Dashboard/HumanExpertInterventionDashboard'));
const CriticalDecisionHandHoldingDashboard = lazy(() => import('@/components/Dashboard/CriticalDecisionHandHoldingDashboard'));

// Loading component for dashboard tabs
const TabLoader = () => (
  <Card className="p-6">
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="medium" />
    </div>
  </Card>
);

const OptimizedHome = () => {
  const [selectedPlatform, setSelectedPlatform] = useState('agentkit');
  const [healthStatus, setHealthStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

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

  const handleTabChange = (value) => {
    setActiveTab(value);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            OmniFy Cloud Connect
          </h1>
          <p className="text-xl text-gray-600">
            Autonomous Growth OS
          </p>
          {healthStatus && (
            <div className="mt-4">
              <span className="text-sm text-gray-500">
                System Status: {healthStatus.status === 'healthy' ? 'Healthy' : 'Unknown'}
              </span>
            </div>
          )}
        </div>

        <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="brain-logic">Brain Logic</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="eyes">EYES</TabsTrigger>
            <TabsTrigger value="onboarding">Onboarding</TabsTrigger>
            <TabsTrigger value="instant-value">Instant Value</TabsTrigger>
            <TabsTrigger value="orchestration">Orchestration</TabsTrigger>
            <TabsTrigger value="predictive-intelligence">Predictive</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4">🚀 Quick Start</h2>
                <div className="space-y-3">
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
            <Suspense fallback={<TabLoader />}>
              <BrainLogicPanel />
            </Suspense>
          </TabsContent>

          <TabsContent value="analytics">
            <Suspense fallback={<TabLoader />}>
              <AnalyticsDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="eyes">
            <Suspense fallback={<TabLoader />}>
              <EyesModule />
            </Suspense>
          </TabsContent>

          <TabsContent value="onboarding">
            <Suspense fallback={<TabLoader />}>
              <MagicalOnboardingWizard />
            </Suspense>
          </TabsContent>

          <TabsContent value="instant-value">
            <Suspense fallback={<TabLoader />}>
              <InstantValueDeliveryDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="orchestration">
            <Suspense fallback={<TabLoader />}>
              <CustomerOrchestrationDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="predictive-intelligence">
            <Suspense fallback={<TabLoader />}>
              <PredictiveIntelligenceDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="adaptive-learning">
            <Suspense fallback={<TabLoader />}>
              <AdaptiveClientLearningDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="expert-intervention">
            <Suspense fallback={<TabLoader />}>
              <HumanExpertInterventionDashboard />
            </Suspense>
          </TabsContent>

          <TabsContent value="critical-decision">
            <Suspense fallback={<TabLoader />}>
              <CriticalDecisionHandHoldingDashboard />
            </Suspense>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default OptimizedHome;
