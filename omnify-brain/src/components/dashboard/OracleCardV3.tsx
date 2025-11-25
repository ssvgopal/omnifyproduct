'use client';

/**
 * OracleCard V3 - Requirements V3 Compliant
 * 
 * Implements persona-specific risk views per B.6.2.2-4:
 * - Sarah (CMO): "What will break if you don't act"
 * - Jason (VP Growth): Technical alerts with probabilities
 * - Emily (Director): Tactical flags with creative IDs
 */

import { OracleOutputV3, PersonaType } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { usePersona } from '@/lib/persona-context';
import { 
  Zap, 
  AlertTriangle, 
  TrendingDown, 
  Users, 
  Clock,
  AlertCircle
} from 'lucide-react';

interface OracleCardV3Props {
  data: OracleOutputV3;
}

// Persona-specific configuration
const personaConfig: Record<PersonaType, {
  title: string;
  description: string;
  showProbabilities: boolean;
  showTechnicalDetails: boolean;
  riskFormat: 'narrative' | 'technical' | 'tactical';
}> = {
  sarah: {
    title: "Risk Forecast",
    description: "What will break if you don't act this month.",
    showProbabilities: false,
    showTechnicalDetails: false,
    riskFormat: 'narrative',
  },
  jason: {
    title: "Predictive Alerts",
    description: "7-14 day early warning system for performance drift.",
    showProbabilities: true,
    showTechnicalDetails: true,
    riskFormat: 'technical',
  },
  emily: {
    title: "Fatigue & Decay Warnings",
    description: "Urgent issues requiring immediate action.",
    showProbabilities: false,
    showTechnicalDetails: false,
    riskFormat: 'tactical',
  },
};

export function OracleCardV3({ data }: OracleCardV3Props) {
  const { persona } = usePersona();
  const config = personaConfig[persona];

  // Risk level styling
  const riskStyles = {
    green: { bg: 'bg-green-100', border: 'border-green-200', text: 'text-green-700' },
    yellow: { bg: 'bg-yellow-100', border: 'border-yellow-200', text: 'text-yellow-700' },
    red: { bg: 'bg-red-100', border: 'border-red-200', text: 'text-red-700' },
  };
  const riskStyle = riskStyles[data.globalRiskLevel];

  return (
    <Card className="h-full border-l-4 border-l-orange-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2 text-orange-600 mb-2">
          <Zap className="h-5 w-5" />
          <span className="text-sm font-bold tracking-wider uppercase">Oracle</span>
        </div>
        <CardTitle className="text-lg">{config.title}</CardTitle>
        <CardDescription>{config.description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Global Risk Score */}
        <div className={`p-3 rounded-lg ${riskStyle.bg} ${riskStyle.border} border`}>
          <div className="flex justify-between items-center">
            <div>
              <p className={`text-sm font-medium ${riskStyle.text}`}>
                {persona === 'sarah' ? 'Overall Health' : 'Global Risk Score'}
              </p>
              <p className={`text-xs ${riskStyle.text} opacity-80`}>
                {data.globalRiskLevel === 'green' ? 'Looking good' :
                 data.globalRiskLevel === 'yellow' ? 'Needs attention' :
                 'Action required'}
              </p>
            </div>
            <div className={`text-3xl font-bold ${riskStyle.text}`}>
              {persona === 'sarah' 
                ? (data.globalRiskLevel === 'green' ? '✓' : data.globalRiskLevel === 'yellow' ? '!' : '⚠')
                : data.globalRiskScore}
            </div>
          </div>
        </div>

        {/* Risk Items */}
        <div className="space-y-3">
          {/* Creative Fatigue */}
          {data.creativeFatigue.length > 0 && (
            <RiskSection
              title="Creative Fatigue"
              icon={<TrendingDown className="h-4 w-4 text-red-500" />}
              items={data.creativeFatigue.map(f => ({
                id: f.creativeId,
                name: f.creativeName,
                severity: f.fatigueProbability7d > 0.8 ? 'high' : f.fatigueProbability7d > 0.6 ? 'medium' : 'low',
                message: formatFatigueMessage(f, persona),
                probability: f.fatigueProbability7d,
                details: config.showTechnicalDetails ? {
                  'CVR': `${(f.recentCvr * 100).toFixed(2)}% → ${(f.baselineCvr * 100).toFixed(2)}%`,
                  'CPA': `$${f.recentCpa} → $${f.baselineCpa}`,
                  'Frequency': `${f.frequency}x`,
                } : undefined,
              }))}
              config={config}
            />
          )}

          {/* ROI Decay */}
          {data.roiDecay.length > 0 && (
            <RiskSection
              title="ROI Decay"
              icon={<AlertTriangle className="h-4 w-4 text-orange-500" />}
              items={data.roiDecay.map(d => ({
                id: d.channelId,
                name: d.channelName,
                severity: d.decaySeverity,
                message: formatDecayMessage(d, persona),
                details: config.showTechnicalDetails ? {
                  'Recent ROAS': `${d.recentRoas}x`,
                  'Baseline ROAS': `${d.baselineRoas}x`,
                  'Drop': `${d.decayPercentage}%`,
                } : undefined,
              }))}
              config={config}
            />
          )}

          {/* LTV Drift */}
          {data.ltvDrift && (
            <RiskSection
              title="LTV Drift"
              icon={<Users className="h-4 w-4 text-purple-500" />}
              items={[{
                id: 'ltv_drift',
                name: 'Customer Quality',
                severity: data.ltvDrift.driftSeverity,
                message: formatLtvDriftMessage(data.ltvDrift, persona),
                details: config.showTechnicalDetails ? {
                  'Recent LTV': `$${data.ltvDrift.recentLtv90d}`,
                  'Baseline LTV': `$${data.ltvDrift.baselineLtv90d}`,
                  'Drift': `${data.ltvDrift.driftPercentage}%`,
                  'Trend': data.ltvDrift.trend,
                } : undefined,
              }]}
              config={config}
            />
          )}

          {/* No risks */}
          {data.creativeFatigue.length === 0 && 
           data.roiDecay.length === 0 && 
           !data.ltvDrift && (
            <div className="p-4 bg-green-50 rounded-lg border border-green-100 text-center">
              <p className="text-green-700 font-medium">All Clear</p>
              <p className="text-green-600 text-sm">No significant risks detected.</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================
// Sub-components
// ============================================

interface RiskItem {
  id: string;
  name: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  probability?: number;
  details?: Record<string, string>;
}

function RiskSection({ 
  title, 
  icon, 
  items, 
  config 
}: { 
  title: string;
  icon: React.ReactNode;
  items: RiskItem[];
  config: typeof personaConfig[PersonaType];
}) {
  const severityColors = {
    high: { bg: 'bg-red-50', border: 'border-red-200', badge: 'destructive' as const },
    medium: { bg: 'bg-orange-50', border: 'border-orange-200', badge: 'secondary' as const },
    low: { bg: 'bg-yellow-50', border: 'border-yellow-200', badge: 'outline' as const },
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        {icon}
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
          {title}
        </span>
        <Badge variant="outline" className="text-[10px] h-4">
          {items.length}
        </Badge>
      </div>

      {items.map(item => {
        const colors = severityColors[item.severity];

        return (
          <div 
            key={item.id}
            className={`p-3 rounded-lg ${colors.bg} ${colors.border} border`}
          >
            <div className="flex justify-between items-start mb-1">
              <span className="font-medium text-sm">{item.name}</span>
              <div className="flex items-center gap-2">
                {config.showProbabilities && item.probability !== undefined && (
                  <span className="text-xs text-muted-foreground">
                    {(item.probability * 100).toFixed(0)}%
                  </span>
                )}
                <Badge variant={colors.badge} className="text-[10px] h-5">
                  {item.severity.toUpperCase()}
                </Badge>
              </div>
            </div>
            
            <p className="text-sm text-muted-foreground">{item.message}</p>

            {/* Technical details (Jason only) */}
            {item.details && (
              <div className="mt-2 pt-2 border-t border-dashed grid grid-cols-2 gap-1 text-xs">
                {Object.entries(item.details).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="text-muted-foreground">{key}:</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ============================================
// Message Formatters
// ============================================

function formatFatigueMessage(fatigue: OracleOutputV3['creativeFatigue'][0], persona: PersonaType): string {
  const daysLeft = fatigue.fatigueProbability7d > 0.8 ? 3 : 7;
  const cvrDrop = ((fatigue.baselineCvr - fatigue.recentCvr) / fatigue.baselineCvr * 100).toFixed(0);

  switch (persona) {
    case 'sarah':
      return `Will die in ${daysLeft} days. Costing you money now.`;
    case 'jason':
      return `CVR dropped ${cvrDrop}%. Frequency at ${fatigue.frequency}x. ${(fatigue.fatigueProbability7d * 100).toFixed(0)}% probability of failure in 7d.`;
    case 'emily':
      return `Pause NOW. Replace with backup creative.`;
    default:
      return fatigue.recommendedAction;
  }
}

function formatDecayMessage(decay: OracleOutputV3['roiDecay'][0], persona: PersonaType): string {
  switch (persona) {
    case 'sarah':
      return `Efficiency dropping. Shift budget to winners.`;
    case 'jason':
      return `ROAS ${decay.recentRoas}x vs ${decay.baselineRoas}x baseline. ${decay.decayPercentage}% decline.`;
    case 'emily':
      return `Reduce spend 20%. Review targeting.`;
    default:
      return decay.recommendedAction;
  }
}

function formatLtvDriftMessage(drift: OracleOutputV3['ltvDrift'], persona: PersonaType): string {
  if (!drift) return '';

  switch (persona) {
    case 'sarah':
      return `Customer quality declining ${Math.abs(drift.driftPercentage)}%. This will compound.`;
    case 'jason':
      return `90d LTV: $${drift.recentLtv90d} vs $${drift.baselineLtv90d} baseline. Trend: ${drift.trend}.`;
    case 'emily':
      return `Launch retention campaign. Review acquisition sources.`;
    default:
      return drift.recommendedAction;
  }
}
