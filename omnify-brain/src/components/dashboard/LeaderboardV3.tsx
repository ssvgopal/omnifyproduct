'use client';

/**
 * Leaderboard V3 - FACE Wireframe Component
 * 
 * Displays Winners/Losers ranking for creatives and channels.
 * Per FACE_Wireframes_v1: Right sidebar leaderboard tile.
 */

import { BrainStateV3 } from '@/lib/types';
import { TrendingUp, TrendingDown, Award, AlertTriangle } from 'lucide-react';

interface LeaderboardV3Props {
  state: BrainStateV3;
}

interface LeaderboardItem {
  id: string;
  name: string;
  roas: number;
  spend: number;
  trend: 'up' | 'down' | 'stable';
  type: 'channel' | 'creative';
}

export function LeaderboardV3({ state }: LeaderboardV3Props) {
  const { memory, oracle } = state;

  // Build leaderboard from channels
  const channelItems: LeaderboardItem[] = memory.channels.map(ch => ({
    id: ch.id,
    name: ch.name,
    roas: ch.roas,
    spend: ch.spend,
    trend: ch.trend as 'up' | 'down' | 'stable',
    type: 'channel',
  }));

  // Sort by ROAS
  const sortedItems = [...channelItems].sort((a, b) => b.roas - a.roas);
  const winners = sortedItems.slice(0, 3);
  const losers = sortedItems.slice(-3).reverse();

  // Get fatiguing creatives from oracle
  const fatiguingCreatives = oracle.creativeFatigue.map(cf => ({
    id: cf.creativeId,
    name: cf.creativeName,
    fatigueProbability: cf.fatigueProbability7d,
    performanceDrop: cf.predictedPerformanceDrop,
  }));

  return (
    <div className="bg-white rounded-lg border shadow-sm">
      {/* Winners Section */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-3">
          <Award className="h-5 w-5 text-green-600" />
          <h3 className="font-semibold text-gray-900">Top Performers</h3>
        </div>
        <div className="space-y-2">
          {winners.map((item, index) => (
            <LeaderboardRow
              key={item.id}
              rank={index + 1}
              item={item}
              variant="winner"
            />
          ))}
        </div>
      </div>

      {/* Losers Section */}
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <h3 className="font-semibold text-gray-900">Underperformers</h3>
        </div>
        <div className="space-y-2">
          {losers.map((item, index) => (
            <LeaderboardRow
              key={item.id}
              rank={sortedItems.length - losers.length + index + 1}
              item={item}
              variant="loser"
            />
          ))}
        </div>
      </div>

      {/* Fatiguing Creatives */}
      {fatiguingCreatives.length > 0 && (
        <div className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingDown className="h-5 w-5 text-orange-600" />
            <h3 className="font-semibold text-gray-900">Fatiguing Creatives</h3>
          </div>
          <div className="space-y-2">
            {fatiguingCreatives.slice(0, 3).map((creative) => (
              <div
                key={creative.id}
                className="flex items-center justify-between p-2 bg-orange-50 rounded-lg"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {creative.name}
                  </p>
                  <p className="text-xs text-orange-600">
                    -{(creative.performanceDrop * 100).toFixed(0)}% performance drop
                  </p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-orange-600">
                    {(creative.fatigueProbability * 100).toFixed(0)}%
                  </span>
                  <p className="text-xs text-gray-500">risk</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================
// Leaderboard Row Component
// ============================================

interface LeaderboardRowProps {
  rank: number;
  item: LeaderboardItem;
  variant: 'winner' | 'loser';
}

function LeaderboardRow({ rank, item, variant }: LeaderboardRowProps) {
  const TrendIcon = item.trend === 'up' ? TrendingUp : item.trend === 'down' ? TrendingDown : null;
  const trendColor = item.trend === 'up' ? 'text-green-500' : item.trend === 'down' ? 'text-red-500' : 'text-gray-400';
  
  const bgColor = variant === 'winner' ? 'bg-green-50' : 'bg-red-50';
  const roasColor = variant === 'winner' ? 'text-green-600' : 'text-red-600';

  return (
    <div className={`flex items-center gap-3 p-2 rounded-lg ${bgColor}`}>
      {/* Rank */}
      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
        variant === 'winner' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
      }`}>
        {rank}
      </div>

      {/* Name & Spend */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
        <p className="text-xs text-gray-500">${(item.spend / 1000).toFixed(1)}K spend</p>
      </div>

      {/* ROAS & Trend */}
      <div className="text-right flex items-center gap-1">
        <span className={`text-sm font-bold ${roasColor}`}>
          {item.roas.toFixed(2)}x
        </span>
        {TrendIcon && <TrendIcon className={`h-4 w-4 ${trendColor}`} />}
      </div>
    </div>
  );
}
