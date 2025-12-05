'use client';

import { useState, useEffect } from 'react';
import { Link2, Check, X, ExternalLink, Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Integration {
  platform: string;
  name: string;
  description: string;
  icon: string;
  connected: boolean;
  lastSync?: string;
  status?: 'active' | 'error' | 'pending';
}

const PLATFORMS: Omit<Integration, 'connected' | 'lastSync' | 'status'>[] = [
  {
    platform: 'meta',
    name: 'Meta Ads',
    description: 'Connect Facebook and Instagram advertising accounts',
    icon: '📘',
  },
  {
    platform: 'google',
    name: 'Google Ads',
    description: 'Connect Google Ads and Performance Max campaigns',
    icon: '🔍',
  },
  {
    platform: 'tiktok',
    name: 'TikTok Ads',
    description: 'Connect TikTok For Business advertising',
    icon: '🎵',
  },
  {
    platform: 'shopify',
    name: 'Shopify',
    description: 'Connect your Shopify store for revenue data',
    icon: '🛒',
  },
];

export default function IntegrationsSettingsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  async function fetchIntegrations() {
    try {
      const response = await fetch('/api/integrations');
      if (response.ok) {
        const data = await response.json();
        // Merge platform info with connection status
        const merged = PLATFORMS.map(p => ({
          ...p,
          connected: data.connections?.some((c: any) => c.platform.toLowerCase() === p.platform) || false,
          lastSync: data.connections?.find((c: any) => c.platform.toLowerCase() === p.platform)?.lastSync,
          status: data.connections?.find((c: any) => c.platform.toLowerCase() === p.platform)?.status || 'pending',
        }));
        setIntegrations(merged);
      } else {
        // Use default state if API fails
        setIntegrations(PLATFORMS.map(p => ({ ...p, connected: false })));
      }
    } catch (err) {
      console.error('Failed to fetch integrations:', err);
      setIntegrations(PLATFORMS.map(p => ({ ...p, connected: false })));
    } finally {
      setLoading(false);
    }
  }

  async function handleConnect(platform: string) {
    // Redirect to OAuth flow
    window.location.href = `/api/connectors/${platform}/auth`;
  }

  async function handleDisconnect(platform: string) {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) return;

    try {
      const response = await fetch(`/api/connectors/${platform}/disconnect`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchIntegrations();
      }
    } catch (err) {
      console.error('Failed to disconnect:', err);
    }
  }

  async function handleSync(platform: string) {
    setSyncing(platform);
    try {
      const response = await fetch(`/api/connectors/${platform}/sync`, {
        method: 'POST',
      });
      if (response.ok) {
        fetchIntegrations();
      }
    } catch (err) {
      console.error('Failed to sync:', err);
    } finally {
      setSyncing(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="p-6 border-b">
          <div className="flex items-center gap-3">
            <Link2 className="h-6 w-6 text-purple-600" />
            <div>
              <h2 className="text-lg font-semibold">Platform Integrations</h2>
              <p className="text-sm text-gray-500">
                Connect your advertising and e-commerce platforms
              </p>
            </div>
          </div>
        </div>

        <div className="divide-y">
          {integrations.map((integration) => (
            <div
              key={integration.platform}
              className="p-6 flex items-center justify-between"
            >
              <div className="flex items-center gap-4">
                <div className="text-3xl">{integration.icon}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium">{integration.name}</h3>
                    {integration.connected && (
                      <Badge
                        variant={integration.status === 'active' ? 'default' : 'secondary'}
                        className={
                          integration.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : integration.status === 'error'
                            ? 'bg-red-100 text-red-700'
                            : ''
                        }
                      >
                        {integration.status === 'active' ? (
                          <>
                            <Check className="h-3 w-3 mr-1" />
                            Connected
                          </>
                        ) : integration.status === 'error' ? (
                          <>
                            <X className="h-3 w-3 mr-1" />
                            Error
                          </>
                        ) : (
                          'Pending'
                        )}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{integration.description}</p>
                  {integration.lastSync && (
                    <p className="text-xs text-gray-400 mt-1">
                      Last synced: {new Date(integration.lastSync).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {integration.connected ? (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleSync(integration.platform)}
                      disabled={syncing === integration.platform}
                    >
                      {syncing === integration.platform ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      <span className="ml-2">Sync</span>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDisconnect(integration.platform)}
                      className="text-red-600 hover:text-red-700"
                    >
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button
                    size="sm"
                    onClick={() => handleConnect(integration.platform)}
                  >
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Connect
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900">Need help connecting?</h4>
        <p className="text-sm text-blue-700 mt-1">
          Check our{' '}
          <a href="/docs/integrations" className="underline">
            integration guide
          </a>{' '}
          for step-by-step instructions on connecting each platform.
        </p>
      </div>
    </div>
  );
}
