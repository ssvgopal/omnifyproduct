import { BrainModule, DailyMetric, MemoryOutput, ChannelData } from '../types';

export class MemoryModule implements BrainModule<{ dailyMetrics: DailyMetric[], channels: ChannelData[] }, MemoryOutput> {
    name = 'MEMORY';

    async process(input: { dailyMetrics: DailyMetric[], channels: ChannelData[] }): Promise<MemoryOutput> {
        const { dailyMetrics, channels } = input;

        // 1. Calculate Totals
        const totalSpend = dailyMetrics.reduce((sum, m) => sum + m.spend, 0);
        const totalRevenue = dailyMetrics.reduce((sum, m) => sum + m.revenue, 0);
        const blendedRoas = totalSpend > 0 ? totalRevenue / totalSpend : 0;

        // 2. Analyze Channels
        const channelPerformance = channels.map(channel => {
            const channelMetrics = dailyMetrics.filter(m => m.channelId === channel.id);
            const chSpend = channelMetrics.reduce((sum, m) => sum + m.spend, 0);
            const chRevenue = channelMetrics.reduce((sum, m) => sum + m.revenue, 0);
            const chRoas = chSpend > 0 ? chRevenue / chSpend : 0;

            // Determine Status
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

        // 3. LTV Simulation (Multiplier)
        const ltvMultiplier = 1.25; // Assumed LTV uplift
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
