'use client';

import useSWR from 'swr';
import { BrainState } from '../types';

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch brain state');
  }
  return res.json();
};

export function useBrainState() {
  const {
    data,
    error,
    isLoading,
    mutate,
  } = useSWR<BrainState>('/api/brain/state', fetcher, {
    refreshInterval: 60000, // Refresh every minute
    revalidateOnFocus: true,
  });

  const recompute = async () => {
    try {
      const res = await fetch('/api/brain/compute', { method: 'POST' });
      if (!res.ok) {
        throw new Error('Failed to recompute brain state');
      }
      await mutate(); // Revalidate after computation
    } catch (err: any) {
      console.error('[useBrainState] Recompute error:', err);
      throw err;
    }
  };

  return {
    brainState: data,
    isLoading,
    error,
    recompute,
  };
}
