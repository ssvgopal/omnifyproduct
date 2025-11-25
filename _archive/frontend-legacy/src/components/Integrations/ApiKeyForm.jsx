import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Loader2, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const ApiKeyForm = ({ platform, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    api_key: '',
    api_secret: '',
    account_id: '',
    shop_id: ''
  });
  const [showApiKey, setShowApiKey] = useState(false);
  const [showApiSecret, setShowApiSecret] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Platform-specific fields
  const getFields = () => {
    switch (platform.id) {
      case 'triplewhale':
        return [
          { key: 'api_key', label: 'API Key', required: true, type: 'password' },
          { key: 'shop_id', label: 'Shop ID', required: true, type: 'text' }
        ];
      case 'hubspot':
        return [
          { key: 'api_key', label: 'API Key', required: true, type: 'password' }
        ];
      case 'klaviyo':
        return [
          { key: 'api_key', label: 'API Key', required: true, type: 'password' },
          { key: 'account_id', label: 'Account ID', required: false, type: 'text' }
        ];
      default:
        return [
          { key: 'api_key', label: 'API Key', required: true, type: 'password' }
        ];
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Get current user info
      const organizationId = localStorage.getItem('organization_id');
      const userId = localStorage.getItem('user_id');
      const accessToken = localStorage.getItem('access_token');

      if (!organizationId || !accessToken) {
        throw new Error('Please log in to connect integrations');
      }

      // Get or create a default client profile for the organization
      // For now, we'll use the organization_id as client_id
      const clientId = organizationId;

      // Prepare credentials
      const credentials = {
        platform: platform.id,
        api_key: formData.api_key,
        api_secret: formData.api_secret || null,
        account_id: formData.account_id || null,
        additional_config: {
          shop_id: formData.shop_id || null
        }
      };

      // Store credentials via client onboarding API
      const response = await axios.post(
        `${BACKEND_URL}/api/client-onboarding/credentials`,
        credentials,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          params: {
            client_id: clientId
          }
        }
      );

      // Test connection
      try {
        await axios.post(
          `${BACKEND_URL}/api/client-onboarding/credentials/test`,
          { platform: platform.id },
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            },
            params: {
              client_id: clientId
            }
          }
        );
      } catch (testError) {
        console.warn('Connection test failed, but credentials stored:', testError);
      }

      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to store credentials. Please try again.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const fields = getFields();

  return (
    <Dialog open={true} onOpenChange={onCancel}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Connect {platform.name}</DialogTitle>
          <DialogDescription>
            Enter your {platform.name} API credentials to connect your account
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {fields.map((field) => (
            <div key={field.key} className="space-y-2">
              <Label htmlFor={field.key}>
                {field.label}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </Label>
              <div className="relative">
                <Input
                  id={field.key}
                  type={field.type === 'password' && !showApiKey ? 'password' : 'text'}
                  value={formData[field.key] || ''}
                  onChange={(e) => setFormData({...formData, [field.key]: e.target.value})}
                  required={field.required}
                  disabled={loading}
                  placeholder={`Enter your ${field.label.toLowerCase()}`}
                  className="pr-10"
                />
                {field.type === 'password' && (
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                  >
                    {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                )}
              </div>
            </div>
          ))}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-2 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Connecting...
                </>
              ) : (
                'Connect'
              )}
            </Button>
          </div>
        </form>

        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <p className="text-xs text-blue-700">
            <strong>Where to find your API key:</strong>
            {platform.id === 'triplewhale' && (
              <> Go to TripleWhale Settings → API → Generate API Key</>
            )}
            {platform.id === 'hubspot' && (
              <> Go to HubSpot Settings → Integrations → Private Apps → Create API Key</>
            )}
            {platform.id === 'klaviyo' && (
              <> Go to Klaviyo Account → Settings → API Keys → Create API Key</>
            )}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ApiKeyForm;

