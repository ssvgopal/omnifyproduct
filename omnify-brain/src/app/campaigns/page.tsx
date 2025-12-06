'use client';

import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import {
  Megaphone,
  Filter,
  Search,
  ChevronDown,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Loader2,
  RefreshCw
} from 'lucide-react';
import { platformAPI } from '@/lib/api/platform-api';

interface Campaign {
  id: string;
  name: string;
  platform: string;
  status: string;
  spend: number;
  revenue: number;
  roas: number;
  impressions?: number;
  clicks?: number;
}

export default function CampaignsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'spend' | 'roas'>('spend');
  
  const organizationId = 'default-org-id';

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/login');
      return;
    }
    
    loadCampaigns();
  }, [session, status, router]);

  const loadCampaigns = async () => {
    setLoading(true);
    try {
      const allCampaigns: Campaign[] = [];
      
      // Fetch Meta Ads campaigns
      try {
        const metaResult = await platformAPI.getMetaCampaigns(organizationId);
        if (metaResult.success && metaResult.campaigns) {
          const metaCampaigns = metaResult.campaigns.map((c: any) => ({
            id: c.id,
            name: c.name,
            platform: 'Meta Ads',
            status: c.status || c.effective_status,
            spend: 0,
            revenue: 0,
            roas: 0
          }));
          allCampaigns.push(...metaCampaigns);
        }
      } catch (err) {
        console.error('Failed to fetch Meta campaigns:', err);
      }
      
      // Fetch Google Ads campaigns
      try {
        const googleResult = await platformAPI.getGoogleCampaigns(organizationId);
        if (googleResult.success && googleResult.campaigns) {
          const googleCampaigns = googleResult.campaigns.map((c: any) => ({
            id: c.id,
            name: c.name,
            platform: 'Google Ads',
            status: c.status,
            spend: 0,
            revenue: 0,
            roas: 0
          }));
          allCampaigns.push(...googleCampaigns);
        }
      } catch (err) {
        console.error('Failed to fetch Google campaigns:', err);
      }
      
      setCampaigns(allCampaigns);
    } catch (err) {
      console.error('Failed to load campaigns:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort campaigns
  const filteredCampaigns = campaigns
    .filter(c => {
      if (selectedPlatform !== 'all' && c.platform !== selectedPlatform) return false;
      if (searchQuery && !c.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'name') return a.name.localeCompare(b.name);
      if (sortBy === 'spend') return b.spend - a.spend;
      if (sortBy === 'roas') return b.roas - a.roas;
      return 0;
    });

  const platforms = ['all', ...new Set(campaigns.map(c => c.platform))];

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-sm text-slate-600 font-medium">Loading campaigns...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-sm text-slate-600 hover:text-slate-900 mb-4"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-semibold text-slate-900 mb-2">Campaigns</h1>
            <p className="text-slate-600">
              Manage campaigns across all platforms
            </p>
          </div>
          
          <button
            onClick={loadCampaigns}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg border border-slate-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search campaigns..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Platform Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <select
                value={selectedPlatform}
                onChange={(e) => setSelectedPlatform(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                {platforms.map(p => (
                  <option key={p} value={p}>
                    {p === 'all' ? 'All Platforms' : p}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
            </div>

            {/* Sort By */}
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="name">Sort by Name</option>
                <option value="spend">Sort by Spend</option>
                <option value="roas">Sort by ROAS</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Campaigns List */}
        {filteredCampaigns.length === 0 ? (
          <div className="bg-white rounded-lg border border-slate-200 p-12 text-center">
            <Megaphone className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">No campaigns found</h3>
            <p className="text-slate-600 mb-4">
              {searchQuery || selectedPlatform !== 'all' 
                ? 'Try adjusting your filters'
                : 'Connect your ad platforms in settings to see campaigns'}
            </p>
            <button
              onClick={() => router.push('/settings/api-keys')}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Go to Settings →
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Campaign
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Platform
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Spend
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Revenue
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-600 uppercase tracking-wider">
                    ROAS
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {filteredCampaigns.map((campaign) => (
                  <tr key={campaign.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Megaphone className="h-4 w-4 text-slate-400" />
                        <span className="font-medium text-slate-900">{campaign.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm text-slate-600">{campaign.platform}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        campaign.status.toLowerCase() === 'active' || campaign.status.toLowerCase() === 'enabled'
                          ? 'bg-emerald-50 text-emerald-700'
                          : campaign.status.toLowerCase() === 'paused'
                          ? 'bg-amber-50 text-amber-700'
                          : 'bg-slate-50 text-slate-700'
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-sm font-medium text-slate-900">
                        ${campaign.spend.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-sm font-medium text-emerald-600">
                        ${campaign.revenue.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        {campaign.roas > 0 ? (
                          <>
                            <span className="text-sm font-medium text-slate-900">
                              {campaign.roas.toFixed(2)}x
                            </span>
                            {campaign.roas >= 3 ? (
                              <TrendingUp className="h-4 w-4 text-emerald-600" />
                            ) : campaign.roas < 2 ? (
                              <TrendingDown className="h-4 w-4 text-red-600" />
                            ) : null}
                          </>
                        ) : (
                          <span className="text-sm text-slate-400">—</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-blue-600 hover:text-blue-700">
                        <ExternalLink className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Summary */}
        {filteredCampaigns.length > 0 && (
          <div className="mt-4 text-sm text-slate-600">
            Showing {filteredCampaigns.length} campaign{filteredCampaigns.length !== 1 ? 's' : ''}
            {selectedPlatform !== 'all' && ` from ${selectedPlatform}`}
          </div>
        )}
      </div>
    </div>
  );
}
