'use client';

/**
 * Dashboard V3 - Requirements V3 Compliant
 * 
 * Main dashboard page implementing the 4-layer MVP:
 * MEMORY → ORACLE → CURIOSITY → FACE
 * 
 * Features:
 * - Persona toggle (Sarah/Jason/Emily)
 * - Top bar with key metrics
 * - Three-column layout for brain modules
 * - Real-time data from brain state
 */

import { useEffect, useState } from 'react';
import { PersonaProvider } from '@/lib/persona-context';
import { TopBarV3 } from '@/components/dashboard/TopBarV3';
import { MemoryCardV3 } from '@/components/dashboard/MemoryCardV3';
import { OracleCardV3 } from '@/components/dashboard/OracleCardV3';
import { CuriosityCardV3 } from '@/components/dashboard/CuriosityCardV3';
import { LeaderboardV3 } from '@/components/dashboard/LeaderboardV3';
import { ApplyAllActionsV3 } from '@/components/dashboard/ApplyAllActionsV3';
import { ChannelHealthV3 } from '@/components/dashboard/ChannelHealthV3';
import { BrainStateV3 } from '@/lib/types';
import { Loader2 } from 'lucide-react';

// Demo brain state for development
// In production, this would come from Supabase or API
const DEMO_BRAIN_STATE: BrainStateV3 = {
  timestamp: new Date().toISOString(),
  organizationId: 'org_demo_beauty_65m',
  memory: {
    timestamp: new Date().toISOString(),
    totals: {
      totalSpend: 234500,
      totalRevenue: 702450,
      ltvAdjustedRevenue: 614143,
      blendedRoas: 2.99,
      ltvRoas: 2.62,
      mer: 2.99,
    },
    channels: [
      {
        id: 'ch_meta',
        name: 'Meta Ads',
        platform: 'Meta',
        spend: 120000,
        revenue: 438000,
        roas: 3.65,
        status: 'winner',
        contribution: 62.4,
        trend: 'stable',
      },
      {
        id: 'ch_google',
        name: 'Google Ads',
        platform: 'Google',
        spend: 60000,
        revenue: 141000,
        roas: 2.35,
        status: 'neutral',
        contribution: 20.1,
        trend: 'up',
      },
      {
        id: 'ch_tiktok',
        name: 'TikTok Ads',
        platform: 'TikTok',
        spend: 54500,
        revenue: 123450,
        roas: 2.26,
        status: 'loser',
        contribution: 17.5,
        trend: 'down',
      },
    ],
    ltvFactor: 0.875,
    baselineCohortMonth: '2024-04',
    recentCohortMonth: '2024-11',
  },
  oracle: {
    timestamp: new Date().toISOString(),
    globalRiskLevel: 'yellow',
    globalRiskScore: 45,
    creativeFatigue: [
      {
        creativeId: 'cr_c12',
        creativeName: 'Creative C12 - UGC Testimonial',
        channelId: 'ch_meta',
        fatigueProbability7d: 0.78,
        fatigueProbability14d: 0.92,
        predictedPerformanceDrop: 0.35,
        recentCvr: 0.052,
        baselineCvr: 0.078,
        recentCpa: 38.50,
        baselineCpa: 26.00,
        frequency: 3.8,
        recommendedAction: 'Pause Creative C12 and rotate in fresh creative.',
      },
    ],
    roiDecay: [
      {
        channelId: 'ch_tiktok',
        channelName: 'TikTok Ads',
        recentRoas: 1.95,
        baselineRoas: 2.65,
        decayPercentage: 26.4,
        decaySeverity: 'high',
        recommendedAction: 'Shift 20% of TikTok budget to Meta immediately.',
      },
    ],
    ltvDrift: {
      recentCohortMonth: '2024-11',
      baselineCohortMonth: '2024-04',
      recentLtv90d: 112,
      baselineLtv90d: 128,
      driftPercentage: 12.5,
      driftSeverity: 'medium',
      trend: 'stabilizing',
      recommendedAction: 'Investigate cohort quality. Consider retention-focused initiatives.',
    },
    risks: [],
  },
  curiosity: {
    timestamp: new Date().toISOString(),
    topActions: [
      {
        id: 'act_pause_cr_c12',
        type: 'pause_creative',
        title: 'Pause Creative C12 - UGC Testimonial',
        description: 'Creative showing 78% fatigue probability. CVR dropped 33%.',
        estimatedImpactUsd: 3150,
        impactFormatted: '+$3.2K/week',
        confidence: 'high',
        confidenceScore: 85,
        urgency: 'high',
        urgencyScore: 92,
        score: 78.5,
        entities: ['cr_c12'],
        rationale: 'CVR dropped from 7.8% to 5.2%. Frequency at 3.8x. Predicted 35% further decline if not paused.',
        microcopy: {
          sarah: 'Creative C12 will die in 3 days. Pause now to save $3.2K/week.',
          jason: 'C12 fatigue: CVR 5.2% (was 7.8%), Freq 3.8x. 78% probability of failure in 7d.',
          emily: 'Pause Creative C12 NOW. Rotate in backup.',
        },
      },
      {
        id: 'act_shift_tiktok_meta',
        type: 'shift_budget',
        title: 'Shift Budget: TikTok → Meta',
        description: 'Move $5,450 from TikTok (ROAS 1.95x) to Meta (ROAS 3.65x).',
        estimatedImpactUsd: 9265,
        impactFormatted: '+$9.3K/mo',
        confidence: 'high',
        confidenceScore: 88,
        urgency: 'high',
        urgencyScore: 85,
        score: 72.3,
        entities: ['ch_tiktok', 'ch_meta'],
        rationale: 'TikTok ROAS dropped 26% from baseline. Meta has capacity for additional spend at 3.65x ROAS.',
        microcopy: {
          sarah: "Here's exactly where to move budget: Shift $5.5K from TikTok to Meta for +$9.3K/mo.",
          jason: 'TikTok ROAS (1.95x) is 35% below blended. Shift 10% to Meta (3.65x).',
          emily: 'Move $5,450 from TikTok → Meta. Execute in platform now.',
        },
      },
      {
        id: 'act_focus_retention',
        type: 'focus_retention',
        title: 'Focus on Customer Retention',
        description: 'New cohort LTV is 12.5% lower than baseline. Trend is stabilizing.',
        estimatedImpactUsd: 4500,
        impactFormatted: '+$4.5K/mo',
        confidence: 'medium',
        confidenceScore: 65,
        urgency: 'medium',
        urgencyScore: 60,
        score: 48.2,
        entities: [],
        rationale: 'Recent cohorts (2024-11) showing $112 90-day LTV vs $128 baseline. Trend: stabilizing.',
        microcopy: {
          sarah: 'Customer quality is declining 12.5% - this will compound. Prioritize retention.',
          jason: 'LTV drift: Nov cohort at $112 vs $128 baseline (stabilizing). Review acquisition channels.',
          emily: 'Launch retention campaign. Review email flows.',
        },
      },
    ],
    totalOpportunityUsd: 16915,
    totalOpportunityFormatted: '+$16.9K/mo',
  },
};

export default function DashboardV3Page() {
  const [brainState, setBrainState] = useState<BrainStateV3 | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load brain state
    // In production, this would fetch from Supabase or API
    const loadBrainState = async () => {
      try {
        setLoading(true);
        
        // Try to load from local file first (for demo)
        try {
          const response = await fetch('/api/brain-state');
          if (response.ok) {
            const data = await response.json();
            setBrainState(data);
            return;
          }
        } catch {
          // Fall through to demo data
        }

        // Use demo data
        setBrainState(DEMO_BRAIN_STATE);
      } catch (err) {
        setError('Failed to load brain state');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadBrainState();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
          <p className="text-muted-foreground">Loading Omnify Brain...</p>
        </div>
      </div>
    );
  }

  if (error || !brainState) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-red-600 font-medium">{error || 'Failed to load data'}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <PersonaProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Sticky Top Bar */}
        <div className="sticky top-0 z-10 bg-white shadow-sm">
          <TopBarV3 state={brainState} />
        </div>

        {/* Main Content - Two Column FACE Wireframe Layout */}
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Main Content (2/3 width) */}
            <div className="lg:col-span-2 space-y-6">
              {/* Risk Cards (ORACLE) */}
              <OracleCardV3 data={brainState.oracle} />

              {/* Insights (MEMORY) */}
              <MemoryCardV3 data={brainState.memory} />

              {/* Recommendations (CURIOSITY) */}
              <CuriosityCardV3 data={brainState.curiosity} />

              {/* Apply All Actions */}
              <ApplyAllActionsV3 curiosity={brainState.curiosity} />
            </div>

            {/* Right Column - Sidebar (1/3 width) */}
            <div className="space-y-6">
              {/* Leaderboard */}
              <LeaderboardV3 state={brainState} />

              {/* Channel Health */}
              <ChannelHealthV3 state={brainState} />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-white text-center text-xs text-muted-foreground">
          <p>
            Omnify Brain V3 • Last updated: {new Date(brainState.timestamp).toLocaleString()}
            {' • '}
            Organization: {brainState.organizationId}
          </p>
        </div>
      </div>
    </PersonaProvider>
  );
}
