'use client';

/**
 * Dashboard Layout V3 - FACE Wireframe Aligned
 * 
 * Two-column layout per FACE_Wireframes_v1:
 * - Left: Risks + Insights + Actions (main content)
 * - Right: Leaderboard + Channel Health (sidebar)
 * - Top: Sticky summary bar
 */

import { ReactNode } from 'react';

interface DashboardLayoutV3Props {
  topBar: ReactNode;
  mainContent: ReactNode;
  sidebar: ReactNode;
}

export function DashboardLayoutV3({ topBar, mainContent, sidebar }: DashboardLayoutV3Props) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sticky Top Bar */}
      <div className="sticky top-0 z-10 bg-white shadow-sm">
        {topBar}
      </div>

      {/* Main Content Area */}
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Main Content (2/3 width on desktop) */}
          <div className="lg:col-span-2 space-y-6">
            {mainContent}
          </div>

          {/* Right Column - Sidebar (1/3 width on desktop) */}
          <div className="space-y-6">
            {sidebar}
          </div>
        </div>
      </div>
    </div>
  );
}
