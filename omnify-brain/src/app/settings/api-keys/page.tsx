'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import {
  Key,
  Check,
  X,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  TestTube,
  Save,
  Trash2,
  RefreshCw
} from 'lucide-react';

interface APIKeyConfig {
  platform: string;
  displayName: string;
  description: string;
  category: 'ai' | 'marketing';
  fields: {
    name: string;
    label: string;
    placeholder: string;
    type: 'text' | 'password';
    required: boolean;
  }[];
  docsUrl?: string;
}

const API_KEY_CONFIGS: APIKeyConfig[] = [
  // AI/LLM Platforms
  {
    platform: 'openai',
    displayName: 'OpenAI',
    description: 'GPT-4, GPT-4o, DALL-E for creative intelligence',
    category: 'ai',
    fields: [
      {
        name: 'api_key',
        label: 'API Key',
        placeholder: 'sk-...',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://platform.openai.com/api-keys'
  },
  {
    platform: 'anthropic',
    displayName: 'Anthropic Claude',
    description: 'Claude AI for advanced analysis',
    category: 'ai',
    fields: [
      {
        name: 'api_key',
        label: 'API Key',
        placeholder: 'sk-ant-...',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://console.anthropic.com/'
  },
  {
    platform: 'gemini',
    displayName: 'Google Gemini',
    description: 'Multi-modal AI and predictive analytics',
    category: 'ai',
    fields: [
      {
        name: 'api_key',
        label: 'API Key',
        placeholder: 'AIza...',
        type: 'password',
        required: true
      },
      {
        name: 'project_id',
        label: 'Project ID (Optional)',
        placeholder: 'your-project-id',
        type: 'text',
        required: false
      }
    ],
    docsUrl: 'https://makersuite.google.com/app/apikey'
  },
  {
    platform: 'grok',
    displayName: 'Grok (X.AI)',
    description: 'Real-time AI with access to X data',
    category: 'ai',
    fields: [
      {
        name: 'api_key',
        label: 'API Key',
        placeholder: 'xai-...',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://x.ai'
  },
  {
    platform: 'openrouter',
    displayName: 'OpenRouter',
    description: 'Unified access to multiple LLMs',
    category: 'ai',
    fields: [
      {
        name: 'api_key',
        label: 'API Key',
        placeholder: 'sk-or-...',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://openrouter.ai/keys'
  },
  
  // Marketing Platforms
  {
    platform: 'meta_ads',
    displayName: 'Meta Ads',
    description: 'Facebook & Instagram advertising',
    category: 'marketing',
    fields: [
      {
        name: 'access_token',
        label: 'Access Token',
        placeholder: 'EAA...',
        type: 'password',
        required: true
      },
      {
        name: 'account_id',
        label: 'Ad Account ID',
        placeholder: 'act_...',
        type: 'text',
        required: true
      }
    ],
    docsUrl: 'https://developers.facebook.com/tools/explorer/'
  },
  {
    platform: 'google_ads',
    displayName: 'Google Ads',
    description: 'Google advertising platform',
    category: 'marketing',
    fields: [
      {
        name: 'client_id',
        label: 'Client ID',
        placeholder: 'Your OAuth2 Client ID',
        type: 'text',
        required: true
      },
      {
        name: 'client_secret',
        label: 'Client Secret',
        placeholder: 'Your OAuth2 Client Secret',
        type: 'password',
        required: true
      },
      {
        name: 'refresh_token',
        label: 'Refresh Token',
        placeholder: 'Your OAuth2 Refresh Token',
        type: 'password',
        required: true
      },
      {
        name: 'customer_id',
        label: 'Customer ID',
        placeholder: '123-456-7890',
        type: 'text',
        required: true
      },
      {
        name: 'developer_token',
        label: 'Developer Token',
        placeholder: 'Your Google Ads Developer Token',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://ads.google.com/home/tools/manager-accounts/'
  },
  {
    platform: 'tiktok',
    displayName: 'TikTok Ads',
    description: 'TikTok advertising platform',
    category: 'marketing',
    fields: [
      {
        name: 'access_token',
        label: 'Access Token',
        placeholder: 'Your TikTok Access Token',
        type: 'password',
        required: true
      },
      {
        name: 'advertiser_id',
        label: 'Advertiser ID',
        placeholder: 'Your Advertiser ID',
        type: 'text',
        required: true
      }
    ],
    docsUrl: 'https://ads.tiktok.com/'
  },
  {
    platform: 'shopify',
    displayName: 'Shopify',
    description: 'E-commerce platform integration',
    category: 'marketing',
    fields: [
      {
        name: 'shop_url',
        label: 'Shop URL',
        placeholder: 'your-store.myshopify.com',
        type: 'text',
        required: true
      },
      {
        name: 'access_token',
        label: 'Access Token',
        placeholder: 'shpat_...',
        type: 'password',
        required: true
      }
    ],
    docsUrl: 'https://admin.shopify.com/'
  }
];

export default function APIKeysSettings() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'ai' | 'marketing'>('ai');
  const [formData, setFormData] = useState<Record<string, Record<string, string>>>({});
  const [showPassword, setShowPassword] = useState<Record<string, boolean>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  const [testResults, setTestResults] = useState<Record<string, any>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [configuredPlatforms, setConfiguredPlatforms] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock organization ID - replace with actual from session
  const organizationId = 'default-org-id';

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/login');
      return;
    }
    
    loadConfiguredPlatforms();
  }, [session, status, router]);

  const loadConfiguredPlatforms = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api-keys/list/${organizationId}`);
      const data = await response.json();
      
      if (data.platforms) {
        setConfiguredPlatforms(data.platforms.map((p: any) => p.platform));
      }
    } catch (error) {
      console.error('Failed to load configured platforms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (platform: string, field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        [field]: value
      }
    }));
  };

  const togglePasswordVisibility = (key: string) => {
    setShowPassword(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleSave = async (platform: string) => {
    setSaving(prev => ({ ...prev, [platform]: true }));
    
    try {
      const keys = formData[platform] || {};
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api-keys/save-bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_id: organizationId,
          platform,
          keys
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setTestResults(prev => ({
          ...prev,
          [platform]: { success: true, message: 'API keys saved successfully' }
        }));
        loadConfiguredPlatforms();
      } else {
        setTestResults(prev => ({
          ...prev,
          [platform]: { success: false, message: result.message || 'Failed to save API keys' }
        }));
      }
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [platform]: { success: false, message: 'Network error' }
      }));
    } finally {
      setSaving(prev => ({ ...prev, [platform]: false }));
    }
  };

  const handleTest = async (platform: string) => {
    setTesting(prev => ({ ...prev, [platform]: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api-keys/test-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          organization_id: organizationId,
          platform
        })
      });

      const result = await response.json();
      setTestResults(prev => ({ ...prev, [platform]: result }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [platform]: { success: false, connected: false, message: 'Network error' }
      }));
    } finally {
      setTesting(prev => ({ ...prev, [platform]: false }));
    }
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const filteredConfigs = API_KEY_CONFIGS.filter(config => config.category === activeTab);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-sm text-slate-600 hover:text-slate-900 mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-semibold text-slate-900 mb-2">API Keys & Integrations</h1>
          <p className="text-slate-600">
            Configure your API keys for AI services and marketing platforms
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg border border-slate-200 mb-6">
          <div className="border-b border-slate-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('ai')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'ai'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                AI / LLM Services
              </button>
              <button
                onClick={() => setActiveTab('marketing')}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'marketing'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                Marketing Platforms
              </button>
            </div>
          </div>
        </div>

        {/* Platform Cards */}
        <div className="grid grid-cols-1 gap-6">
          {filteredConfigs.map(config => {
            const isConfigured = configuredPlatforms.includes(config.platform);
            const testResult = testResults[config.platform];
            const isSaving = saving[config.platform];
            const isTesting = testing[config.platform];

            return (
              <div
                key={config.platform}
                className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden"
              >
                <div className="p-6">
                  {/* Platform Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-50 rounded-lg">
                        <Key className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">{config.displayName}</h3>
                        <p className="text-sm text-slate-600">{config.description}</p>
                      </div>
                    </div>
                    
                    {/* Status Badge */}
                    {isConfigured && (
                      <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-medium rounded-full">
                        <Check className="h-3 w-3" />
                        Configured
                      </span>
                    )}
                  </div>

                  {/* Input Fields */}
                  <div className="space-y-4 mb-4">
                    {config.fields.map(field => {
                      const fieldKey = `${config.platform}-${field.name}`;
                      const showPass = showPassword[fieldKey];

                      return (
                        <div key={field.name}>
                          <label className="block text-sm font-medium text-slate-700 mb-1.5">
                            {field.label}
                            {field.required && <span className="text-red-500 ml-1">*</span>}
                          </label>
                          <div className="relative">
                            <input
                              type={field.type === 'password' && !showPass ? 'password' : 'text'}
                              placeholder={field.placeholder}
                              value={formData[config.platform]?.[field.name] || ''}
                              onChange={(e) => handleInputChange(config.platform, field.name, e.target.value)}
                              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            {field.type === 'password' && (
                              <button
                                type="button"
                                onClick={() => togglePasswordVisibility(fieldKey)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                              >
                                {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                              </button>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Test Result */}
                  {testResult && (
                    <div className={`mb-4 p-3 rounded-lg flex items-start gap-2 ${
                      testResult.success && testResult.connected
                        ? 'bg-emerald-50 text-emerald-800'
                        : 'bg-red-50 text-red-800'
                    }`}>
                      {testResult.success && testResult.connected ? (
                        <Check className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      ) : (
                        <X className="h-4 w-4 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="text-sm">
                        <p className="font-medium">{testResult.message}</p>
                        {testResult.details && (
                          <p className="text-xs mt-1 opacity-80">
                            {JSON.stringify(testResult.details)}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => handleSave(config.platform)}
                      disabled={isSaving}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isSaving ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4" />
                      )}
                      Save
                    </button>
                    
                    <button
                      onClick={() => handleTest(config.platform)}
                      disabled={isTesting || !isConfigured}
                      className="flex items-center gap-2 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {isTesting ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <TestTube className="h-4 w-4" />
                      )}
                      Test Connection
                    </button>

                    {config.docsUrl && (
                      <a
                        href={config.docsUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        View Documentation →
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
