import { NextRequest, NextResponse } from 'next/server';
import { DataSyncService } from '@/lib/services/data-sync';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { organizationId, platform, credentials, dateRange } = body;

        if (!organizationId) {
            return NextResponse.json(
                { error: 'organizationId is required' },
                { status: 400 }
            );
        }

        const syncService = new DataSyncService();

        let result;
        if (platform && credentials) {
            // Sync specific platform
            result = await syncService.syncPlatform({
                organizationId,
                platform,
                credentials,
                dateRange: dateRange ? {
                    start: new Date(dateRange.start),
                    end: new Date(dateRange.end)
                } : undefined
            });
        } else {
            // Sync all platforms
            result = await syncService.syncAllPlatforms(organizationId);
        }

        return NextResponse.json(result);
    } catch (error: any) {
        console.error('[API] Sync error:', error);
        return NextResponse.json(
            { error: error.message || 'Sync failed' },
            { status: 500 }
        );
    }
}
