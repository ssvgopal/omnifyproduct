'use client';

import { useState, useEffect } from 'react';

interface SyncDataStepProps {
  data: {
    connectedPlatforms: string[];
  };
  onNext: (data: any) => void;
  onBack: () => void;
}

export function SyncDataStep({ data, onNext, onBack }: SyncDataStepProps) {
  const [syncProgress, setSyncProgress] = useState(0);
  const [currentPlatform, setCurrentPlatform] = useState<string>('');
  const [isSyncing, setIsSyncing] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Start data sync
    const syncData = async () => {
      try {
        for (let i = 0; i < data.connectedPlatforms.length; i++) {
          const platform = data.connectedPlatforms[i];
          setCurrentPlatform(platform);
          
          // Trigger sync for this platform
          const response = await fetch(`/api/connectors/${platform}/sync`, {
            method: 'POST',
          });

          if (!response.ok) {
            throw new Error(`Failed to sync ${platform}`);
          }

          // Update progress
          setSyncProgress(((i + 1) / data.connectedPlatforms.length) * 100);
        }

        // Run initial brain cycle
        const brainResponse = await fetch('/api/brain-cycle', {
          method: 'POST',
        });

        if (!brainResponse.ok) {
          throw new Error('Failed to run brain cycle');
        }

        setIsSyncing(false);
      } catch (err: any) {
        setError(err.message || 'Sync failed');
        setIsSyncing(false);
      }
    };

    syncData();
  }, [data.connectedPlatforms]);

  const handleNext = () => {
    if (isSyncing) {
      return;
    }
    onNext({});
  };

  const platformNames: Record<string, string> = {
    meta: 'Meta Ads',
    google: 'Google Ads',
    tiktok: 'TikTok Ads',
    shopify: 'Shopify',
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Syncing your data</h2>
      <p className="text-gray-600 mb-6">We're importing your historical data and running the first analysis</p>

      {isSyncing ? (
        <div className="space-y-4">
          <div className="bg-gray-100 rounded-full h-4 overflow-hidden">
            <div
              className="bg-blue-600 h-full transition-all duration-500"
              style={{ width: `${syncProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 text-center">
            {currentPlatform
              ? `Syncing ${platformNames[currentPlatform] || currentPlatform}...`
              : 'Preparing sync...'}
          </p>
        </div>
      ) : error ? (
        <div className="text-red-600 bg-red-50 p-4 rounded-lg">
          <p className="font-medium">Sync Error</p>
          <p className="text-sm mt-1">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      ) : (
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <p className="text-lg font-medium text-gray-900">Data sync complete!</p>
          <p className="text-sm text-gray-600 mt-2">Your first insights are ready</p>
        </div>
      )}

      <div className="mt-6 flex gap-4">
        <button
          onClick={onBack}
          disabled={isSyncing}
          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          Back
        </button>
        <button
          onClick={handleNext}
          disabled={isSyncing || !!error}
          className="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSyncing ? 'Syncing...' : 'Continue'}
        </button>
      </div>
    </div>
  );
}

