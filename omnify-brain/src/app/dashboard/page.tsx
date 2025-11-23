'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Dashboard() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return; // Still loading
    if (!session) {
      router.push('/login');
      return;
    }
  }, [session, status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent mb-4"></div>
          <p className="text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <p className="text-lg text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
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
          <p className="text-sm text-gray-500 mt-1">
            Role: {(session.user as any)?.role || 'Unknown'}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Memory Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Memory
            </h2>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-600">Total Spend</span>
                <p className="text-2xl font-bold text-gray-900">$12,450</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Total Revenue</span>
                <p className="text-2xl font-bold text-green-600">$49,800</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Blended ROAS</span>
                <p className="text-2xl font-bold text-blue-600">4.0x</p>
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
                <p className="text-2xl font-bold text-orange-600">35%</p>
              </div>
              <div>
                <span className="text-sm text-gray-600">Risk Factors</span>
                <p className="text-lg font-medium text-gray-900">2 detected</p>
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
                <p className="text-lg font-medium text-gray-900">3 actions</p>
              </div>
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-sm font-medium text-blue-900">
                  Top Action:
                </p>
                <p className="text-sm text-blue-700">
                  Scale Meta Ads by 20%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
              <h3 className="font-medium text-gray-900">View Analytics</h3>
              <p className="text-sm text-gray-600 mt-1">Deep dive into performance metrics</p>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
              <h3 className="font-medium text-gray-900">Manage Campaigns</h3>
              <p className="text-sm text-gray-600 mt-1">Create and optimize campaigns</p>
            </button>
            <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left">
              <h3 className="font-medium text-gray-900">Settings</h3>
              <p className="text-sm text-gray-600 mt-1">Configure integrations and preferences</p>
            </button>
          </div>
        </div>

        {/* Role-based Navigation */}
        {(session.user as any)?.role === 'admin' && (
          <div className="mt-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 className="font-medium text-purple-900">Admin Panel</h3>
            <p className="text-sm text-purple-700 mt-1">
              You have admin access. <a href="/admin" className="underline">Go to Admin Panel</a>
            </p>
          </div>
        )}

        {(session.user as any)?.role === 'vendor' && (
          <div className="mt-6 bg-gray-900 text-white rounded-lg p-4">
            <h3 className="font-medium">Vendor Panel</h3>
            <p className="text-sm text-gray-300 mt-1">
              You have vendor access. <a href="/vendor" className="underline">Go to Vendor Panel</a>
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
