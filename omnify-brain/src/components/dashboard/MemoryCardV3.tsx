'use client';

/**
 * MemoryCard V3 - Requirements V3 Compliant
 * 
 * Implements persona-specific views per B.6.2.2-4:
 * - Sarah (CMO): LTV-ROAS focus, executive summary
 * - Jason (VP Growth): Channel comparison, ROAS trends
 * - Emily (Director): Tactical numbers, quick scannability
 */

import { MemoryOutputV3, PersonaType } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { usePersona } from '@/lib/persona-context';
import { Brain, TrendingUp, TrendingDown, Minus, DollarSign } from 'lucide-react';

interface MemoryCardV3Props {
  data: MemoryOutputV3;
}

// Persona-specific configuration
const personaConfig: Record<PersonaType, {
  title: string;
  description: string;
  focusMetric: 'ltvRoas' | 'blendedRoas' | 'spend';
  showLtvDetails: boolean;
  showTrends: boolean;
  channelFormat: 'summary' | 'detailed' | 'tactical';
}> = {
  sarah: {
    title: "Attribution Truth",
    description: "Here's the truth about your spend efficiency.",
    focusMetric: 'ltvRoas',
    showLtvDetails: true,
    showTrends: false,
    channelFormat: 'summary',
  },
  jason: {
    title: "Channel Performance",
    description: "Real-time ROAS vs targets with trend analysis.",
    focusMetric: 'blendedRoas',
    showLtvDetails: true,
    showTrends: true,
    channelFormat: 'detailed',
  },
  emily: {
    title: "Daily ROAS Tracker",
    description: "Quick scan: which channels need attention today.",
    focusMetric: 'spend',
    showLtvDetails: false,
    showTrends: true,
    channelFormat: 'tactical',
  },
};

export function MemoryCardV3({ data }: MemoryCardV3Props) {
  const { persona } = usePersona();
  const config = personaConfig[persona];

  return (
    <Card className="h-full border-l-4 border-l-blue-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2 text-blue-600 mb-2">
          <Brain className="h-5 w-5" />
          <span className="text-sm font-bold tracking-wider uppercase">Memory</span>
        </div>
        <CardTitle className="text-lg">{config.title}</CardTitle>
        <CardDescription>{config.description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Primary Metrics */}
        <PrimaryMetrics data={data} persona={persona} config={config} />

        {/* LTV Details (Sarah & Jason only) */}
        {config.showLtvDetails && (
          <LtvDetails data={data} persona={persona} />
        )}

        {/* Channel Performance */}
        <ChannelList data={data} persona={persona} config={config} />
      </CardContent>
    </Card>
  );
}

// ============================================
// Sub-components
// ============================================

function PrimaryMetrics({ 
  data, 
  persona, 
  config 
}: { 
  data: MemoryOutputV3; 
  persona: PersonaType;
  config: typeof personaConfig[PersonaType];
}) {
  const { totals } = data;

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Total Spend */}
      <div className="p-3 bg-muted/50 rounded-lg">
        <p className="text-xs text-muted-foreground mb-1">
          {persona === 'emily' ? 'Spend (30d)' : 'Total Spend'}
        </p>
        <p className="text-xl font-bold">${totals.totalSpend.toLocaleString()}</p>
      </div>

      {/* Focus Metric based on persona */}
      <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
        <p className="text-xs text-blue-600 mb-1">
          {config.focusMetric === 'ltvRoas' ? 'LTV-ROAS' : 
           config.focusMetric === 'blendedRoas' ? 'Blended ROAS' : 
           'Revenue'}
        </p>
        <p className="text-xl font-bold text-blue-600">
          {config.focusMetric === 'ltvRoas' ? `${totals.ltvRoas.toFixed(2)}x` :
           config.focusMetric === 'blendedRoas' ? `${totals.blendedRoas.toFixed(2)}x` :
           `$${totals.totalRevenue.toLocaleString()}`}
        </p>
      </div>
    </div>
  );
}

function LtvDetails({ data, persona }: { data: MemoryOutputV3; persona: PersonaType }) {
  const { totals, ltvFactor, baselineCohortMonth, recentCohortMonth } = data;

  // Sarah sees simplified view, Jason sees detailed
  if (persona === 'sarah') {
    return (
      <div className="p-3 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-100">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-xs text-muted-foreground">LTV-Adjusted Revenue</p>
            <p className="text-lg font-bold">${totals.ltvAdjustedRevenue.toLocaleString()}</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">LTV Factor</p>
            <Badge variant={ltvFactor >= 1 ? 'default' : 'destructive'} className="text-xs">
              {ltvFactor.toFixed(2)}x
            </Badge>
          </div>
        </div>
      </div>
    );
  }

  // Jason sees detailed cohort comparison
  return (
    <div className="p-3 bg-muted/30 rounded-lg space-y-2">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">LTV Factor</span>
        <span className="font-medium">{ltvFactor.toFixed(3)}x</span>
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">Baseline Cohort</span>
        <span className="font-medium">{baselineCohortMonth}</span>
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">Recent Cohort</span>
        <span className="font-medium">{recentCohortMonth}</span>
      </div>
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">LTV-Adjusted Revenue</span>
        <span className="font-medium text-blue-600">${totals.ltvAdjustedRevenue.toLocaleString()}</span>
      </div>
    </div>
  );
}

function ChannelList({ 
  data, 
  persona, 
  config 
}: { 
  data: MemoryOutputV3; 
  persona: PersonaType;
  config: typeof personaConfig[PersonaType];
}) {
  const TrendIcon = ({ trend }: { trend: string }) => {
    if (trend === 'up') return <TrendingUp className="h-3 w-3 text-green-500" />;
    if (trend === 'down') return <TrendingDown className="h-3 w-3 text-red-500" />;
    return <Minus className="h-3 w-3 text-gray-400" />;
  };

  const statusColors = {
    winner: { dot: 'bg-green-500', badge: 'default' as const },
    loser: { dot: 'bg-red-500', badge: 'destructive' as const },
    neutral: { dot: 'bg-yellow-500', badge: 'secondary' as const },
  };

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
        {persona === 'emily' ? 'Channel Status' : 'Channel Performance'}
      </p>
      
      <div className="space-y-2">
        {data.channels.map(channel => {
          const colors = statusColors[channel.status];

          return (
            <div 
              key={channel.id} 
              className="flex items-center justify-between p-2.5 bg-muted/50 rounded-lg hover:bg-muted/70 transition-colors"
            >
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${colors.dot}`} />
                <div>
                  <p className="font-medium text-sm">{channel.name}</p>
                  {config.channelFormat !== 'tactical' && (
                    <p className="text-xs text-muted-foreground">
                      {channel.contribution.toFixed(0)}% of revenue
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* ROAS */}
                <div className="text-right">
                  <p className="font-bold text-sm">{channel.roas.toFixed(2)}x</p>
                  {config.channelFormat === 'tactical' && (
                    <p className="text-xs text-muted-foreground">
                      ${channel.spend.toLocaleString()}
                    </p>
                  )}
                </div>

                {/* Trend (Jason & Emily) */}
                {config.showTrends && <TrendIcon trend={channel.trend} />}

                {/* Status Badge */}
                <Badge 
                  variant={colors.badge} 
                  className="text-[10px] h-5 min-w-[60px] justify-center"
                >
                  {channel.status.toUpperCase()}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
