'use client';

import { useState } from 'react';

interface ConnectPlatformsStepProps {
  data: {
    connectedPlatforms: string[];
  };
  onNext: (data: any) => void;
  onBack: () => void;
}

const PLATFORMS = [
  { id: 'meta', name: 'Meta Ads', icon: '📘', required: true },
  { id: 'google', name: 'Google Ads', icon: '🔍', required: false },
  { id: 'tiktok', name: 'TikTok Ads', icon: '🎵', required: false },
  { id: 'shopify', name: 'Shopify', icon: '🛍️', required: false },
];

export function ConnectPlatformsStep({ data, onNext, onBack }: ConnectPlatformsStepProps) {
  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>(data.connectedPlatforms);
  const [connecting, setConnecting] = useState<string | null>(null);

  const handleConnect = async (platformId: string) => {
    setConnecting(platformId);
    
    try {
      // Start OAuth flow
      const response = await fetch(`/api/connectors/${platformId}/auth`, {
        method: 'GET',
      });

      if (response.ok) {
        const { authUrl } = await response.json();
        // Redirect to OAuth provider
        window.location.href = authUrl;
      } else {
        console.error('Failed to start OAuth flow');
        setConnecting(null);
      }
    } catch (error) {
      console.error('Error connecting platform:', error);
      setConnecting(null);
    }
  };

  const handleNext = () => {
    if (connectedPlatforms.length === 0) {
      alert('Please connect at least Meta Ads to continue');
      return;
    }
    onNext({ connectedPlatforms });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Connect your ad platforms</h2>
      <p className="text-gray-600 mb-6">Connect at least Meta Ads to get started</p>

      <div className="space-y-4">
        {PLATFORMS.map((platform) => {
          const isConnected = connectedPlatforms.includes(platform.id);
          const isConnecting = connecting === platform.id;

          return (
            <div
              key={platform.id}
              className={`p-4 border-2 rounded-lg ${
                isConnected
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{platform.icon}</span>
                  <div>
                    <h3 className="font-medium text-gray-900">{platform.name}</h3>
                    {platform.required && (
                      <span className="text-xs text-gray-500">Required</span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => handleConnect(platform.id)}
                  disabled={isConnected || isConnecting}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    isConnected
                      ? 'bg-green-600 text-white cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50'
                  }`}
                >
                  {isConnected
                    ? '✓ Connected'
                    : isConnecting
                    ? 'Connecting...'
                    : 'Connect'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex gap-4">
        <button
          onClick={onBack}
          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Back
        </button>
        <button
          onClick={handleNext}
          className="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  );
}


