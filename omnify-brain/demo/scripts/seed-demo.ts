import fs from 'fs';
import path from 'path';
import { ChannelData, CreativeData, DailyMetric } from '../src/lib/types';

// Configuration
const DATA_DIR = path.join(process.cwd(), 'src', 'data', 'seeds');
const DAYS_TO_GENERATE = 30;

// Ensure directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 1. Generate Channels
const channels: ChannelData[] = [
    {
        id: 'ch_meta',
        name: 'Meta Ads',
        platform: 'Meta',
        spend: 0,
        revenue: 0,
        impressions: 0,
        clicks: 0,
        conversions: 0,
        roas: 0,
        cpa: 0,
        ctr: 0.012
    },
    {
        id: 'ch_google',
        name: 'Google Ads',
        platform: 'Google',
        spend: 0,
        revenue: 0,
        impressions: 0,
        clicks: 0,
        conversions: 0,
        roas: 0,
        cpa: 0,
        ctr: 0.025
    },
    {
        id: 'ch_tiktok',
        name: 'TikTok Ads',
        platform: 'TikTok',
        spend: 0,
        revenue: 0,
        impressions: 0,
        clicks: 0,
        conversions: 0,
        roas: 0,
        cpa: 0,
        ctr: 0.008
    }
];

// 2. Generate Daily Metrics (Simulating the Scenario)
// Scenario:
// - Meta: Steady, good performance (Winner)
// - Google: Stable (Neutral)
// - TikTok: Declining performance over last 7 days (Loser)
// - Creative C12 (Meta): High spend, but fatigue starting 3 days ago

const dailyMetrics: DailyMetric[] = [];
const creatives: CreativeData[] = [];

// Helper to add noise
const noise = (val: number, percent: number) => val * (1 + (Math.random() * percent * 2 - percent));

const today = new Date();

for (let i = DAYS_TO_GENERATE; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    const dateStr = date.toISOString().split('T')[0];

    // Meta (Winner)
    const metaSpend = noise(1500, 0.1);
    const metaRoas = noise(3.2, 0.1);
    const metaRev = metaSpend * metaRoas;

    dailyMetrics.push({
        date: dateStr,
        channelId: 'ch_meta',
        spend: Math.round(metaSpend),
        revenue: Math.round(metaRev),
        roas: parseFloat(metaRoas.toFixed(2)),
        status: metaRoas > 2.5 ? 'winner' : 'neutral'
    });

    // Google (Neutral)
    const googleSpend = noise(800, 0.05);
    const googleRoas = noise(2.1, 0.05);
    const googleRev = googleSpend * googleRoas;

    dailyMetrics.push({
        date: dateStr,
        channelId: 'ch_google',
        spend: Math.round(googleSpend),
        revenue: Math.round(googleRev),
        roas: parseFloat(googleRoas.toFixed(2)),
        status: 'neutral'
    });

    // TikTok (Loser - Declining)
    let tiktokSpend = noise(1200, 0.1);
    let tiktokRoas = 1.8; // Base

    // Decay in last 10 days
    if (i < 10) {
        tiktokRoas = 1.8 - ((10 - i) * 0.1); // Drops to 0.8
    } else {
        tiktokRoas = noise(1.8, 0.1);
    }

    const tiktokRev = tiktokSpend * tiktokRoas;

    dailyMetrics.push({
        date: dateStr,
        channelId: 'ch_tiktok',
        spend: Math.round(tiktokSpend),
        revenue: Math.round(tiktokRev),
        roas: parseFloat(tiktokRoas.toFixed(2)),
        status: tiktokRoas < 1.5 ? 'loser' : 'neutral'
    });
}

// 3. Generate Creatives (Specific focus on C12 Fatigue)
const creativeList = [
    { id: 'cr_c12', name: 'Creative C12 - UGC Testimonial', channelId: 'ch_meta', baseRoas: 3.5 },
    { id: 'cr_c13', name: 'Creative C13 - Product Shot', channelId: 'ch_meta', baseRoas: 2.8 },
    { id: 'cr_t01', name: 'TikTok Trend #1', channelId: 'ch_tiktok', baseRoas: 1.2 },
];

creativeList.forEach(cr => {
    let roas = cr.baseRoas;
    // C12 Fatigue Logic: High ROAS initially, drops sharply in last 3 days
    if (cr.id === 'cr_c12') {
        // Current ROAS (simulated for "today")
        roas = 1.9;
    }

    creatives.push({
        id: cr.id,
        name: cr.name,
        channelId: cr.channelId,
        spend: 5000, // Aggregate
        revenue: 5000 * roas,
        impressions: 100000,
        clicks: 2500,
        ctr: 0.025,
        roas: roas,
        status: 'active',
        launchDate: '2023-10-01'
    });
});

// Write to files
fs.writeFileSync(path.join(DATA_DIR, 'channels.json'), JSON.stringify(channels, null, 2));
fs.writeFileSync(path.join(DATA_DIR, 'daily_metrics.json'), JSON.stringify(dailyMetrics, null, 2));
fs.writeFileSync(path.join(DATA_DIR, 'creatives.json'), JSON.stringify(creatives, null, 2));

console.log('Seed data generated successfully in src/data/seeds/');
