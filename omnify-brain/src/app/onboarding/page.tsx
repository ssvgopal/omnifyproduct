'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { CompanyInfoStep } from '@/components/onboarding/CompanyInfoStep';
import { ConnectPlatformsStep } from '@/components/onboarding/ConnectPlatformsStep';
import { SyncDataStep } from '@/components/onboarding/SyncDataStep';
import { CompleteStep } from '@/components/onboarding/CompleteStep';

type OnboardingStep = 'company' | 'platforms' | 'sync' | 'complete';

export default function OnboardingPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('company');
  const [onboardingData, setOnboardingData] = useState({
    companyName: '',
    industry: '',
    revenueRange: '',
    connectedPlatforms: [] as string[],
  });

  // Redirect if not authenticated
  if (status === 'unauthenticated') {
    router.push('/login');
    return null;
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  const handleNext = (stepData?: any) => {
    if (stepData) {
      setOnboardingData({ ...onboardingData, ...stepData });
    }

    const steps: OnboardingStep[] = ['company', 'platforms', 'sync', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const handleBack = () => {
    const steps: OnboardingStep[] = ['company', 'platforms', 'sync', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const handleComplete = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Progress Bar */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="flex items-center justify-between mb-2">
            <div className={`flex-1 h-2 rounded-full ${currentStep === 'company' || currentStep === 'platforms' || currentStep === 'sync' || currentStep === 'complete' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="mx-2 w-2 h-2 rounded-full bg-gray-300"></div>
            <div className={`flex-1 h-2 rounded-full ${currentStep === 'platforms' || currentStep === 'sync' || currentStep === 'complete' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="mx-2 w-2 h-2 rounded-full bg-gray-300"></div>
            <div className={`flex-1 h-2 rounded-full ${currentStep === 'sync' || currentStep === 'complete' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
            <div className="mx-2 w-2 h-2 rounded-full bg-gray-300"></div>
            <div className={`flex-1 h-2 rounded-full ${currentStep === 'complete' ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
          </div>
          <div className="flex justify-between text-xs text-gray-600">
            <span>Company Info</span>
            <span>Connect Platforms</span>
            <span>Sync Data</span>
            <span>Complete</span>
          </div>
        </div>

        {/* Step Content */}
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-xl p-8">
          {currentStep === 'company' && (
            <CompanyInfoStep
              data={onboardingData}
              onNext={handleNext}
            />
          )}
          {currentStep === 'platforms' && (
            <ConnectPlatformsStep
              data={onboardingData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 'sync' && (
            <SyncDataStep
              data={onboardingData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {currentStep === 'complete' && (
            <CompleteStep
              data={onboardingData}
              onComplete={handleComplete}
            />
          )}
        </div>
      </div>
    </div>
  );
}

