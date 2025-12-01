'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { Settings, ArrowLeft, RefreshCw, Check, AlertCircle, Loader2 } from 'lucide-react';

interface Integration {
  id: string;
  platform: string;
  name: string;
  icon: string;
  status: 'connected' | 'disconnected' | 'error';
  lastSynced?: string;
  error?: string;
}

const PLATFORMS = [
  { id: 'meta', platform: 'Meta', name: 'Meta Ads', icon: '📘' },
  { id: 'google', platform: 'Google', name: 'Google Ads', icon: '🔍' },
  { id: 'tiktok', platform: 'TikTok', name: 'TikTok Ads', icon: '🎵' },
  { id: 'shopify', platform: 'Shopify', name: 'Shopify', icon: '🛍️' },
];

export default function IntegrationsSettingsPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await fetch('/api/integrations');
      if (response.ok) {
        const data = await response.json();
        setIntegrations(data.integrations || []);
      } else {
        // Use default disconnected state
        setIntegrations(PLATFORMS.map(p => ({
          ...p,
          status: 'disconnected' as const,
        })));
      }
    } catch (error) {
      setIntegrations(PLATFORMS.map(p => ({
        ...p,
        status: 'disconnected' as const,
      })));
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platformId: string) => {
    try {
      const response = await fetch(`/api/connectors/${platformId}/auth`);
      if (response.ok) {
        const { authUrl } = await response.json();
        window.location.href = authUrl;
      }
    } catch (error) {
      console.error('Failed to start OAuth:', error);
    }
  };

  const handleSync = async (platformId: string) => {
    setSyncing(platformId);
    try {
      const response = await fetch(`/api/connectors/${platformId}/sync`, {
        method: 'POST',
      });
      if (response.ok) {
        await loadIntegrations();
      }
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(null);
    }
  };

  const handleDisconnect = async (platformId: string) => {
    if (!confirm('Are you sure you want to disconnect this integration? You will need to reconnect to sync data again.')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/integrations/${platformId}/disconnect`, {
        method: 'POST',
      });
      
      if (response.ok) {
        await loadIntegrations();
      } else {
        const data = await response.json();
        alert(data.error || 'Failed to disconnect');
      }
    } catch (error) {
      console.error('Disconnect failed:', error);
      alert('Failed to disconnect integration');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'connected':
        return (
          <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <Check className="h-3 w-3" />
            Connected
          </span>
        );
      case 'error':
        return (
          <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
            <AlertCircle className="h-3 w-3" />
            Error
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">
            Not Connected
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => router.push('/dashboard-v3')}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm">
          <div className="p-6 border-b">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Settings className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold text-slate-900">Integrations</h1>
                <p className="text-sm text-slate-600">Connect your ad platforms and data sources</p>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="p-8 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" />
              <p className="mt-2 text-slate-600">Loading integrations...</p>
            </div>
          ) : (
            <div className="divide-y">
              {PLATFORMS.map((platform) => {
                const integration = integrations.find(i => i.platform === platform.platform);
                const isConnected = integration?.status === 'connected';
                const isSyncing = syncing === platform.id;

                return (
                  <div key={platform.id} className="p-6 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-3xl">{platform.icon}</span>
                      <div>
                        <h3 className="font-medium text-slate-900">{platform.name}</h3>
                        {isConnected && integration?.lastSynced && (
                          <p className="text-xs text-slate-500">
                            Last synced: {new Date(integration.lastSynced).toLocaleString()}
                          </p>
                        )}
                        {integration?.error && (
                          <p className="text-xs text-red-600">{integration.error}</p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      {getStatusBadge(integration?.status || 'disconnected')}
                      
                      {isConnected ? (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSync(platform.id)}
                            disabled={isSyncing}
                            className="flex items-center gap-1 px-3 py-2 text-sm border rounded-lg hover:bg-gray-50 disabled:opacity-50"
                          >
                            {isSyncing ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <RefreshCw className="h-4 w-4" />
                            )}
                            Sync
                          </button>
                          <button
                            onClick={() => handleDisconnect(platform.id)}
                            className="px-3 py-2 text-sm text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
                          >
                            Disconnect
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleConnect(platform.id)}
                          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                        >
                          Connect
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-blue-50 rounded-lg p-4">
          <h3 className="font-medium text-blue-900">Need help connecting?</h3>
          <p className="text-sm text-blue-700 mt-1">
            Each platform requires OAuth authentication. Click "Connect" to authorize Omnify Brain 
            to access your advertising data. We only request read access to your campaigns and metrics.
          </p>
        </div>
      </div>
    </div>
  );
}

