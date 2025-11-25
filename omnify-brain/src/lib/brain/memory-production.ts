import { supabaseAdmin } from '@/lib/db/supabase';
import { BrainModule, MemoryOutput } from '../types';

export class MemoryModuleProduction implements BrainModule<{ organizationId: string }, MemoryOutput> {
    name = 'MEMORY_PRODUCTION';

    async process(input: { organizationId: string }): Promise<MemoryOutput> {
        const { organizationId } = input;

        // 1. Fetch all channels for the organization
        const { data: channels, error: channelsError } = await supabaseAdmin
            .from('channels')
            .select('*')
            .eq('organization_id', organizationId)
            .eq('is_active', true);

        if (channelsError || !channels) {
            throw new Error('Failed to fetch channels');
        }

        // 2. Fetch daily metrics for all channels (last 30 days)
        const { data: metrics, error: metricsError } = await supabaseAdmin
            .from('daily_metrics')
            .select('*')
            .in('channel_id', channels.map(c => c.id))
            .gte('date', new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])
            .order('date', { ascending: false });

        if (metricsError || !metrics) {
            throw new Error('Failed to fetch metrics');
        }

        // 3. Calculate totals
        const totalSpend = metrics.reduce((sum, m) => sum + (m.spend || 0), 0);
        const totalRevenue = metrics.reduce((sum, m) => sum + (m.revenue || 0), 0);
        const blendedRoas = totalSpend > 0 ? totalRevenue / totalSpend : 0;

        // 4. Analyze channel performance
        const channelPerformance = channels.map(channel => {
            const channelMetrics = metrics.filter(m => m.channel_id === channel.id);
            const chSpend = channelMetrics.reduce((sum, m) => sum + (m.spend || 0), 0);
            const chRevenue = channelMetrics.reduce((sum, m) => sum + (m.revenue || 0), 0);
            const chRoas = chSpend > 0 ? chRevenue / chSpend : 0;

            // Determine status
            let status: 'winner' | 'loser' | 'neutral' = 'neutral';
            if (chRoas > 2.5) status = 'winner';
            else if (chRoas < 1.8) status = 'loser';

            return {
                id: channel.id,
                name: channel.name,
                roas: parseFloat(chRoas.toFixed(2)),
                status,
                contribution: totalRevenue > 0 ? (chRevenue / totalRevenue) * 100 : 0
            };
        });

        // 5. LTV Simulation (would be calculated from customer data in production)
        const ltvMultiplier = 1.25;
        const ltvRoas = blendedRoas * ltvMultiplier;

        return {
            totalSpend,
            totalRevenue,
            blendedRoas: parseFloat(blendedRoas.toFixed(2)),
            channels: channelPerformance,
            ltvRoas: parseFloat(ltvRoas.toFixed(2))
        };
    }
}
