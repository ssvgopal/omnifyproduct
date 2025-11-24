'use client';

interface CompleteStepProps {
  data: {
    companyName: string;
    connectedPlatforms: string[];
  };
  onComplete: () => void;
}

export function CompleteStep({ data, onComplete }: CompleteStepProps) {
  return (
    <div className="text-center">
      <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
        <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome to Omnify Brain!</h2>
      <p className="text-gray-600 mb-8">
        Your marketing intelligence platform is ready. Let's see what your data tells us.
      </p>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 text-left">
        <h3 className="font-medium text-gray-900 mb-2">What's next?</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start gap-2">
            <span className="text-blue-600">✓</span>
            <span>View your unified attribution truth (MEMORY)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600">✓</span>
            <span>See predictive alerts for next week (ORACLE)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-600">✓</span>
            <span>Get your top 3 recommended actions (CURIOSITY)</span>
          </li>
        </ul>
      </div>

      <button
        onClick={onComplete}
        className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
      >
        Go to Dashboard
      </button>
    </div>
  );
}

