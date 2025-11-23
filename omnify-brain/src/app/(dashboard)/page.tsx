'use client';

import { useSession } from 'next-auth/react';
import { useBrainState } from '@/lib/hooks/useBrainState';
import { LoadingState } from '@/components/shared/LoadingState';
import { ErrorBoundary } from '@/components/shared/ErrorBoundary';

export default function Dashboard() {
  const { data: session, status } = useSession();
  const { brainState, error, isLoading, recompute } = useBrainState();

  if (status === 'loading') {
    return <LoadingState />;
  }

  if (!session) {
    return <div>Not authenticated</div>;
  }

  const handleRefresh = () => {
    recompute();
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Dashboard
            </h1>
            <p className="text-gray-600">
              Welcome back, {session.user?.email}
            </p>
            <div className="mt-4">
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                disabled={isLoading}
              >
                {isLoading ? 'Refreshing...' : 'Refresh Data'}
              </button>
            </div>
          </div>

          {/* Content */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <h3 className="text-red-800 font-medium">Error loading data</h3>
              <p className="text-red-600 text-sm mt-1">{error.message}</p>
            </div>
          )}

          {isLoading && !brainState && (
            <LoadingState />
          )}

          {brainState && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Memory Card */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Memory
                </h2>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-gray-600">Total Spend</span>
                    <p className="text-2xl font-bold text-gray-900">
                      ${brainState.memory?.totalSpend?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Total Revenue</span>
                    <p className="text-2xl font-bold text-green-600">
                      ${brainState.memory?.totalRevenue?.toLocaleString() || '0'}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Blended ROAS</span>
                    <p className="text-2xl font-bold text-blue-600">
                      {brainState.memory?.blendedRoas?.toFixed(2) || '0.00'}x
                    </p>
                  </div>
                </div>
              </div>

              {/* Oracle Card */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Oracle
                </h2>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-gray-600">Risk Score</span>
                    <p className="text-2xl font-bold text-orange-600">
                      {brainState.oracle?.globalRiskScore || 0}%
                    </p>
                  </div>
                  <div>
                    <span className="text-sm text-gray-600">Risk Factors</span>
                    <p className="text-lg font-medium text-gray-900">
                      {brainState.oracle?.risks?.length || 0} detected
                    </p>
                  </div>
                </div>
              </div>

              {/* Curiosity Card */}
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Curiosity
                </h2>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm text-gray-600">Recommendations</span>
                    <p className="text-lg font-medium text-gray-900">
                      {brainState.curiosity?.topActions?.length || 0} actions
                    </p>
                  </div>
                  {brainState.curiosity?.topActions?.[0] && (
                    <div className="bg-blue-50 rounded-lg p-3">
                      <p className="text-sm font-medium text-blue-900">
                        Top Action:
                      </p>
                      <p className="text-sm text-blue-700">
                        {brainState.curiosity.topActions[0].title}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {!brainState && !isLoading && !error && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <h3 className="text-gray-900 font-medium mb-2">No data available</h3>
              <p className="text-gray-600 mb-4">
                Click "Refresh Data" to load your brain state, or make sure your database is seeded with test data.
              </p>
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Load Data
              </button>
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
