'use client';

import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  AlertTriangle, 
  Lightbulb, 
  BarChart3, 
  Megaphone, 
  Settings,
  ArrowRight,
  Activity,
  Users,
  Target,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/login');
      return;
    }
  }, [session, status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-2 border-solid border-slate-600 border-r-transparent mb-4"></div>
          <p className="text-sm text-slate-600 font-medium">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-sm text-slate-600 font-medium">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  const handleQuickAction = (action: string) => {
    switch(action) {
      case 'analytics':
        router.push('/analytics');
        break;
      case 'campaigns':
        router.push('/campaigns');
        break;
      case 'settings':
        router.push('/settings/integrations');
        break;
      default:
        break;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header - Corporate Style with user menu */}
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-slate-900 mb-1">
              Marketing Dashboard
            </h1>
            <p className="text-slate-600 text-sm">
              Welcome back, <span className="font-medium text-slate-900">{session.user?.email}</span>
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-3 py-1.5 bg-slate-100 rounded-md">
              <span className="text-xs font-medium text-slate-700 uppercase tracking-wide">
                {(session.user as any)?.role || 'user'}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 rounded-md">
              <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
              <span className="text-xs font-medium text-emerald-700">Active</span>
            </div>
            {/* User menu: gear button with dropdown (Settings, Log out) */}
            <div className="relative">
              <button
                type="button"
                aria-label="User menu"
                className="inline-flex items-center justify-center h-9 w-9 rounded-full border border-slate-200 bg-white text-slate-600 shadow-sm hover:bg-slate-50"
                onClick={() => setIsUserMenuOpen((open) => !open)}
              >
                <Settings className="h-4 w-4" />
              </button>
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-40 rounded-md border border-slate-200 bg-white shadow-lg py-1 text-sm z-20">
                  <button
                    type="button"
                    className="flex w-full items-center px-3 py-2 text-slate-700 hover:bg-slate-50"
                    onClick={() => {
                      setIsUserMenuOpen(false);
                      router.push('/settings/integrations');
                    }}
                  >
                    Settings
                  </button>
                  <div className="my-1 h-px bg-slate-100" />
                  <button
                    type="button"
                    className="flex w-full items-center px-3 py-2 text-slate-700 hover:bg-slate-50"
                    onClick={() => {
                      setIsUserMenuOpen(false);
                      signOut({ callbackUrl: '/login' });
                    }}
                  >
                    Log out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Key Metrics - Professional Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Memory Card - Professional Blue */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-blue-50 rounded-lg">
                  <DollarSign className="h-5 w-5 text-blue-600" />
                </div>
                <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">Memory</h2>
              </div>
              <TrendingUp className="h-4 w-4 text-emerald-600" />
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs font-medium text-slate-500 mb-1">Total Spend (30d)</p>
                <p className="text-2xl font-semibold text-slate-900">$12,450</p>
                <p className="text-xs text-slate-500 mt-1">vs $11,200 last period</p>
              </div>
              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs font-medium text-slate-500 mb-1">Total Revenue</p>
                <p className="text-2xl font-semibold text-emerald-600">$49,800</p>
              </div>
              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs font-medium text-slate-500 mb-1">Blended ROAS</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-2xl font-semibold text-blue-600">4.0x</p>
                  <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                    +12%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Oracle Card - Professional Orange */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-amber-50 rounded-lg">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                </div>
                <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">Oracle</h2>
              </div>
              <AlertCircle className="h-4 w-4 text-amber-600" />
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs font-medium text-slate-500 mb-1">Risk Score</p>
                <div className="flex items-baseline gap-2 mb-2">
                  <p className="text-2xl font-semibold text-amber-600">35%</p>
                  <span className="text-xs font-medium text-slate-500">Moderate</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-amber-500 rounded-full h-2" style={{ width: '35%' }}></div>
                </div>
              </div>
              <div className="pt-4 border-t border-slate-100">
                <p className="text-xs font-medium text-slate-500 mb-1">Risk Factors</p>
                <p className="text-2xl font-semibold text-slate-900">2</p>
                <p className="text-xs text-slate-500 mt-1">issues detected</p>
              </div>
            </div>
          </div>

          {/* Curiosity Card - Professional Purple */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Lightbulb className="h-5 w-5 text-purple-600" />
                </div>
                <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">Curiosity</h2>
              </div>
              <Target className="h-4 w-4 text-purple-600" />
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-xs font-medium text-slate-500 mb-1">Recommendations</p>
                <p className="text-2xl font-semibold text-slate-900">3</p>
                <p className="text-xs text-slate-500 mt-1">action items ready</p>
              </div>
              <div className="pt-4 border-t border-slate-100">
                <div className="bg-slate-50 rounded-md p-3 border border-slate-200">
                  <p className="text-xs font-semibold text-slate-700 mb-1">Top Action</p>
                  <p className="text-sm font-medium text-slate-900 mb-2">Scale Meta Ads by 20%</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">High Impact</span>
                    <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded">Quick Win</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions - Corporate Style */}
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-8">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="h-5 w-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">Quick Actions</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => handleQuickAction('analytics')}
              className="group relative bg-white border-2 border-slate-200 rounded-lg p-5 text-left hover:border-blue-500 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <BarChart3 className="h-5 w-5 text-blue-600" />
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-1.5">View Analytics</h3>
              <p className="text-sm text-slate-600 leading-relaxed">Deep dive into performance metrics and insights</p>
            </button>

            <button 
              onClick={() => handleQuickAction('campaigns')}
              className="group relative bg-white border-2 border-slate-200 rounded-lg p-5 text-left hover:border-purple-500 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 bg-purple-50 rounded-lg group-hover:bg-purple-100 transition-colors">
                  <Megaphone className="h-5 w-5 text-purple-600" />
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-1.5">Manage Campaigns</h3>
              <p className="text-sm text-slate-600 leading-relaxed">Create and optimize your marketing campaigns</p>
            </button>

            <button 
              onClick={() => handleQuickAction('settings')}
              className="group relative bg-white border-2 border-slate-200 rounded-lg p-5 text-left hover:border-slate-400 hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="p-2 bg-slate-50 rounded-lg group-hover:bg-slate-100 transition-colors">
                  <Settings className="h-5 w-5 text-slate-600" />
                </div>
                <ArrowRight className="h-4 w-4 text-slate-400 group-hover:text-slate-600 group-hover:translate-x-1 transition-all" />
              </div>
              <h3 className="font-semibold text-slate-900 mb-1.5">Settings</h3>
              <p className="text-sm text-slate-600 leading-relaxed">Configure integrations and preferences</p>
            </button>
          </div>
        </div>

        {/* Role-based Navigation - Corporate Style */}
        {(session.user as any)?.role === 'admin' && (
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-50 rounded-lg">
                  <Users className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">Admin Access</h3>
                  <p className="text-sm text-slate-600">
                    Manage your organization and team settings
                  </p>
                </div>
              </div>
              <button 
                onClick={() => router.push('/settings/integrations')}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2"
              >
                Go to Settings
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {(session.user as any)?.role === 'vendor' && (
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-slate-100 rounded-lg">
                  <Target className="h-5 w-5 text-slate-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1">Vendor Access</h3>
                  <p className="text-sm text-slate-600">
                    Monitor all organizations and system health
                  </p>
                </div>
              </div>
              <button 
                onClick={() => router.push('/settings/integrations')}
                className="px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2"
              >
                Go to Settings
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
