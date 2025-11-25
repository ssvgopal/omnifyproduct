'use client';

/**
 * CuriosityCard V3 - Requirements V3 Compliant
 * 
 * Implements persona-specific action views per B.6.2.2-4:
 * - Sarah (CMO): Focus on expected impact ($), simplified language
 * - Jason (VP Growth): Show confidence scores, detailed rationale
 * - Emily (Director): Action-first format, tactical execution details
 */

import { CuriosityOutputV3, ActionRecommendationV3, PersonaType } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { usePersona } from '@/lib/persona-context';
import { 
  Lightbulb, 
  ArrowRight, 
  DollarSign,
  Pause,
  TrendingUp,
  RefreshCw,
  Users,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { useState } from 'react';

interface CuriosityCardV3Props {
  data: CuriosityOutputV3;
}

// Persona-specific configuration
const personaConfig: Record<PersonaType, {
  title: string;
  description: string;
  showConfidenceScore: boolean;
  showRationale: boolean;
  actionFormat: 'strategic' | 'detailed' | 'tactical';
  ctaText: string;
}> = {
  sarah: {
    title: "Strategic Moves",
    description: "High-impact decisions to optimize profitability.",
    showConfidenceScore: false,
    showRationale: false,
    actionFormat: 'strategic',
    ctaText: 'Approve',
  },
  jason: {
    title: "Growth Opportunities",
    description: "Tactical budget shifts with confidence scores.",
    showConfidenceScore: true,
    showRationale: true,
    actionFormat: 'detailed',
    ctaText: 'Review Details',
  },
  emily: {
    title: "Recommended Actions",
    description: "Execute these changes now to fix issues.",
    showConfidenceScore: false,
    showRationale: false,
    actionFormat: 'tactical',
    ctaText: 'Execute',
  },
};

// Action type icons
const actionIcons: Record<ActionRecommendationV3['type'], React.ReactNode> = {
  shift_budget: <RefreshCw className="h-4 w-4" />,
  pause_creative: <Pause className="h-4 w-4" />,
  increase_budget: <TrendingUp className="h-4 w-4" />,
  focus_retention: <Users className="h-4 w-4" />,
};

export function CuriosityCardV3({ data }: CuriosityCardV3Props) {
  const { persona } = usePersona();
  const config = personaConfig[persona];

  return (
    <Card className="h-full border-l-4 border-l-purple-500">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2 text-purple-600 mb-2">
          <Lightbulb className="h-5 w-5" />
          <span className="text-sm font-bold tracking-wider uppercase">Curiosity</span>
        </div>
        <CardTitle className="text-lg">{config.title}</CardTitle>
        <CardDescription>{config.description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Total Opportunity */}
        <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm font-medium text-purple-800">
                {persona === 'sarah' ? 'Potential Impact' : 'Total Opportunity'}
              </p>
              <p className="text-xs text-purple-600">
                {persona === 'emily' ? 'If you act today' : 'Monthly impact'}
              </p>
            </div>
            <div className="text-2xl font-bold text-purple-600">
              {data.totalOpportunityFormatted}
            </div>
          </div>
        </div>

        {/* Top 3 Actions */}
        <div className="space-y-3">
          {data.topActions.map((action, index) => (
            <ActionCard 
              key={action.id}
              action={action}
              index={index}
              persona={persona}
              config={config}
            />
          ))}
        </div>

        {/* Empty state */}
        {data.topActions.length === 0 && (
          <div className="p-4 bg-muted/50 rounded-lg text-center">
            <p className="text-muted-foreground">No actions recommended.</p>
            <p className="text-sm text-muted-foreground">Performance is optimal.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================
// Action Card Component
// ============================================

function ActionCard({ 
  action, 
  index, 
  persona,
  config 
}: { 
  action: ActionRecommendationV3;
  index: number;
  persona: PersonaType;
  config: typeof personaConfig[PersonaType];
}) {
  const [expanded, setExpanded] = useState(false);

  // Get persona-specific message
  const message = action.microcopy?.[persona] || action.description;

  // Urgency styling
  const urgencyStyles = {
    high: { bg: 'bg-red-50', border: 'border-red-200', badge: 'destructive' as const },
    medium: { bg: 'bg-orange-50', border: 'border-orange-200', badge: 'secondary' as const },
    low: { bg: 'bg-green-50', border: 'border-green-200', badge: 'outline' as const },
  };
  const urgencyStyle = urgencyStyles[action.urgency];

  return (
    <div className={`relative p-4 rounded-lg border ${urgencyStyle.border} ${urgencyStyle.bg} shadow-sm`}>
      {/* Rank Badge */}
      <div className="absolute -top-2 -left-2 w-6 h-6 bg-purple-600 text-white rounded-full flex items-center justify-center text-xs font-bold shadow">
        {index + 1}
      </div>

      {/* Header */}
      <div className="flex justify-between items-start mb-2 pl-4">
        <div className="flex items-center gap-2">
          <span className="text-purple-600">{actionIcons[action.type]}</span>
          <h4 className="font-semibold text-sm">
            {config.actionFormat === 'tactical' 
              ? getShortTitle(action)
              : action.title}
          </h4>
        </div>
        <Badge variant="default" className="bg-green-600 hover:bg-green-600 text-white">
          {action.impactFormatted}
        </Badge>
      </div>

      {/* Message - persona specific */}
      <p className="text-sm text-muted-foreground mb-3 pl-4">
        {message}
      </p>

      {/* Metadata Row */}
      <div className="flex items-center justify-between pl-4">
        <div className="flex gap-2">
          {/* Confidence (Jason only) */}
          {config.showConfidenceScore && (
            <Badge variant="outline" className="text-[10px] h-5">
              {action.confidenceScore}% Confidence
            </Badge>
          )}
          
          {/* Urgency */}
          <Badge variant={urgencyStyle.badge} className="text-[10px] h-5">
            {action.urgency.toUpperCase()}
          </Badge>

          {/* Score (Jason only) */}
          {config.showConfidenceScore && (
            <Badge variant="outline" className="text-[10px] h-5">
              Score: {action.score.toFixed(1)}
            </Badge>
          )}
        </div>

        {/* CTA Button */}
        <Button 
          size="sm" 
          variant={config.actionFormat === 'tactical' ? 'default' : 'ghost'}
          className={`h-7 text-xs ${
            config.actionFormat === 'tactical' 
              ? 'bg-purple-600 hover:bg-purple-700 text-white' 
              : 'text-purple-600 hover:text-purple-700 hover:bg-purple-50'
          }`}
        >
          {config.ctaText}
          <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </div>

      {/* Expandable Rationale (Jason only) */}
      {config.showRationale && (
        <div className="mt-3 pl-4">
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            {expanded ? 'Hide rationale' : 'Show rationale'}
          </button>
          
          {expanded && (
            <div className="mt-2 p-2 bg-white/50 rounded text-xs text-muted-foreground">
              {action.rationale}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============================================
// Helper Functions
// ============================================

function getShortTitle(action: ActionRecommendationV3): string {
  switch (action.type) {
    case 'pause_creative':
      return `PAUSE: ${action.entities[0] || 'Creative'}`;
    case 'shift_budget':
      return `SHIFT: ${action.impactFormatted}`;
    case 'increase_budget':
      return `SCALE: ${action.entities[0] || 'Channel'}`;
    case 'focus_retention':
      return 'RETENTION: Launch campaign';
    default:
      return action.title;
  }
}
