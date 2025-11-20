import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  ExternalLink,
  RefreshCw,
  Trash2,
  Key,
  Shield,
  TrendingUp
} from 'lucide-react';
import api from '@/services/api';

const IntegrationSetup = () => {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      // Check which integrations are connected
      const [googleAdsStatus, metaAdsStatus] = await Promise.all([
        checkIntegrationStatus('google-ads'),
        checkIntegrationStatus('meta-ads')
      ]);

      setIntegrations([
        {
          id: 'google-ads',
          name: 'Google Ads',
          description: 'Manage campaigns, keywords, and performance metrics',
          icon: '🔍',
          status: googleAdsStatus,
          color: 'blue'
        },
        {
          id: 'meta-ads',
          name: 'Meta Ads',
          description: 'Facebook and Instagram advertising management',
          icon: '📘',
          status: metaAdsStatus,
          color: 'purple'
        }
      ]);
    } catch (err) {
      console.error('Error loading integrations:', err);
      setError('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const checkIntegrationStatus = async (platform) => {
    try {
      // Try to get integration status
      const status = await api.getIntegrationStatus(platform);
      return status.connected ? 'connected' : 'disconnected';
    } catch (err) {
      return 'disconnected';
    }
  };

  const handleConnect = async (platform) => {
    try {
      setConnecting(platform);
      setError(null);

      // Get OAuth authorization URL
      const response = await api.getIntegrationAuthUrl(platform);
      
      if (response.success) {
        const { authorization_url, state } = response.data;
        
        // Store state in localStorage for verification
        localStorage.setItem(`${platform}_oauth_state`, state);
        
        // Open OAuth window
        const width = 600;
        const height = 700;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;
        
        const authWindow = window.open(
          authorization_url,
          `${platform}_oauth`,
          `width=${width},height=${height},left=${left},top=${top}`
        );

        // Listen for OAuth callback
        const messageListener = (event) => {
          if (event.data.type === 'oauth_callback' && event.data.platform === platform) {
            if (event.data.success) {
              handleOAuthCallback(platform, event.data.code, event.data.state);
            } else {
              setError(`Failed to connect ${platform}: ${event.data.error}`);
            }
            window.removeEventListener('message', messageListener);
            authWindow?.close();
          }
        };

        window.addEventListener('message', messageListener);

        // Check if window was closed manually
        const checkClosed = setInterval(() => {
          if (authWindow?.closed) {
            clearInterval(checkClosed);
            window.removeEventListener('message', messageListener);
            setConnecting(null);
          }
        }, 1000);
      }
    } catch (err) {
      console.error(`Error connecting ${platform}:`, err);
      setError(`Failed to connect ${platform}. Please try again.`);
      setConnecting(null);
    }
  };

  const handleOAuthCallback = async (platform, code, state) => {
    try {
      // Verify state
      const storedState = localStorage.getItem(`${platform}_oauth_state`);
      if (state !== storedState) {
        throw new Error('Invalid OAuth state');
      }

      // Exchange code for tokens
      const response = await api.handleIntegrationCallback(platform, code, state);

      if (response.success) {
        // Reload integrations
        await loadIntegrations();
        setError(null);
      } else {
        throw new Error(response.message || 'Connection failed');
      }
    } catch (err) {
      console.error('OAuth callback error:', err);
      setError(`Failed to complete connection: ${err.message}`);
    } finally {
      localStorage.removeItem(`${platform}_oauth_state`);
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platform) => {
    if (!confirm(`Are you sure you want to disconnect ${platform}?`)) {
      return;
    }

    try {
      await api.disconnectIntegration(platform);
      await loadIntegrations();
    } catch (err) {
      console.error(`Error disconnecting ${platform}:`, err);
      setError(`Failed to disconnect ${platform}`);
    }
  };

  const handleRefresh = async (platform) => {
    try {
      await api.refreshIntegrationToken(platform);
      await loadIntegrations();
    } catch (err) {
      console.error(`Error refreshing ${platform}:`, err);
      setError(`Failed to refresh ${platform} connection`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Platform Integrations</h2>
        <p className="text-gray-600">
          Connect your advertising platforms to manage campaigns and track performance
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {integrations.map((integration) => (
          <Card key={integration.id} className="relative">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-4xl">{integration.icon}</div>
                  <div>
                    <CardTitle className="text-xl">{integration.name}</CardTitle>
                    <CardDescription className="mt-1">
                      {integration.description}
                    </CardDescription>
                  </div>
                </div>
                <Badge 
                  variant={integration.status === 'connected' ? 'default' : 'secondary'}
                  className={
                    integration.status === 'connected' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-600'
                  }
                >
                  {integration.status === 'connected' ? (
                    <>
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Connected
                    </>
                  ) : (
                    <>
                      <XCircle className="h-3 w-3 mr-1" />
                      Not Connected
                    </>
                  )}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {integration.status === 'connected' ? (
                  <>
                    <div className="flex items-center space-x-2 text-sm text-green-600">
                      <Shield className="h-4 w-4" />
                      <span>Securely connected with OAuth2</span>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRefresh(integration.id)}
                        className="flex-1"
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDisconnect(integration.id)}
                        className="flex-1 text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Disconnect
                      </Button>
                    </div>
                  </>
                ) : (
                  <Button
                    onClick={() => handleConnect(integration.id)}
                    disabled={connecting === integration.id}
                    className="w-full"
                    variant={integration.color === 'blue' ? 'default' : 'secondary'}
                  >
                    {connecting === integration.id ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Key className="h-4 w-4 mr-2" />
                        Connect {integration.name}
                      </>
                    )}
                  </Button>
                )}

                <div className="pt-4 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Features</span>
                    <div className="flex items-center space-x-1 text-green-600">
                      <TrendingUp className="h-4 w-4" />
                      <span>Campaign Management</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-1">Secure OAuth2 Authentication</h3>
              <p className="text-sm text-blue-700">
                All integrations use industry-standard OAuth2 authentication. Your credentials are 
                encrypted and stored securely. You can revoke access at any time.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default IntegrationSetup;

