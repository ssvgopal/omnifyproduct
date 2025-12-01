'use client';

/**
 * Channel Health V3 - FACE Wireframe Component
 * 
 * Channel health summary per FACE_Wireframes_v1:
 * - Status indicator per channel (green/yellow/red)
 * - Quick health overview
 */

import { BrainStateV3 } from '@/lib/types';
import { Activity } from 'lucide-react';

interface ChannelHealthV3Props {
  state: BrainStateV3;
}

type HealthStatus = 'healthy' | 'warning' | 'critical';

interface ChannelHealth {
  id: string;
  name: string;
  platform: string;
  status: HealthStatus;
  statusLabel: string;
  roas: number;
  hasDecay: boolean;
  hasFatigue: boolean;
}

export function ChannelHealthV3({ state }: ChannelHealthV3Props) {
  const { memory, oracle } = state;

  // Determine health status for each channel
  const channelHealth: ChannelHealth[] = memory.channels.map(channel => {
    // Check for ROI decay
    const hasDecay = oracle.roiDecay.some(d => d.channelId === channel.id);
    
    // Check for creative fatigue in this channel
    const hasFatigue = oracle.creativeFatigue.some(cf => cf.channelId === channel.id);
    
    // Determine status
    let status: HealthStatus = 'healthy';
    let statusLabel = 'Stable';
    
    if (channel.status === 'loser' || hasDecay) {
      if (channel.trend === 'down' || (hasDecay && oracle.roiDecay.find(d => d.channelId === channel.id)?.decaySeverity === 'high')) {
        status = 'critical';
        statusLabel = 'High Risk';
      } else {
        status = 'warning';
        statusLabel = 'Medium Risk';
      }
    } else if (hasFatigue) {
      status = 'warning';
      statusLabel = 'Watch';
    } else if (channel.status === 'winner') {
      status = 'healthy';
      statusLabel = 'Strong';
    }

    return {
      id: channel.id,
      name: channel.name,
      platform: channel.platform,
      status,
      statusLabel,
      roas: channel.roas,
      hasDecay,
      hasFatigue,
    };
  });

  const statusStyles = {
    healthy: {
      bg: 'bg-green-100',
      text: 'text-green-700',
      dot: 'bg-green-500',
    },
    warning: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-700',
      dot: 'bg-yellow-500',
    },
    critical: {
      bg: 'bg-red-100',
      text: 'text-red-700',
      dot: 'bg-red-500',
    },
  };

  const platformEmojis: Record<string, string> = {
    Meta: '📘',
    Google: '🔍',
    TikTok: '🎵',
    Shopify: '🛍️',
  };

  return (
    <div className="bg-white rounded-lg border shadow-sm p-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-5 w-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">Channel Health</h3>
      </div>

      <div className="space-y-3">
        {channelHealth.map(channel => {
          const styles = statusStyles[channel.status];
          
          return (
            <div
              key={channel.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{platformEmojis[channel.platform] || '📊'}</span>
                <div>
                  <p className="font-medium text-gray-900">{channel.name}</p>
                  <p className="text-xs text-gray-500">{channel.roas.toFixed(2)}x ROAS</p>
                </div>
              </div>

              <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${styles.bg}`}>
                <div className={`w-2 h-2 rounded-full ${styles.dot}`}></div>
                <span className={`text-xs font-medium ${styles.text}`}>
                  {channel.statusLabel}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex justify-between text-sm">
          <span className="text-gray-500">Overall Health</span>
          <span className={`font-medium ${
            oracle.globalRiskLevel === 'green' ? 'text-green-600' :
            oracle.globalRiskLevel === 'yellow' ? 'text-yellow-600' : 'text-red-600'
          }`}>
            {oracle.globalRiskLevel === 'green' ? '🟢 Good' :
             oracle.globalRiskLevel === 'yellow' ? '🟡 Monitor' : '🔴 Action Needed'}
          </span>
        </div>
      </div>
    </div>
  );
}
