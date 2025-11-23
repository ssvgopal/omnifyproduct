'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { BarChart3, ArrowLeft } from 'lucide-react';

export default function AnalyticsPage() {
  const { data: session } = useSession();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>

        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-50 rounded-lg">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-slate-900">Analytics</h1>
              <p className="text-sm text-slate-600">Deep dive into performance metrics</p>
            </div>
          </div>

          <div className="border-t border-slate-200 pt-8">
            <p className="text-slate-600">Analytics dashboard coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  );
}

