import { NextRequest, NextResponse } from 'next/server';
import { supabaseAdmin } from '@/lib/db/supabase';

// This endpoint should be called by Vercel Cron or external cron service
// Vercel Cron config: vercel.json or dashboard settings
// Schedule: 0 6 * * * (6 AM UTC daily)

export async function GET(request: NextRequest) {
  // Verify cron secret (for security)
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  try {
    // Get all active organizations with connected platforms
    const { data: organizations, error: orgError } = await supabaseAdmin
      .from('organizations')
      .select('id');

    if (orgError || !organizations) {
      console.error('[CRON] Error fetching organizations:', orgError);
      return NextResponse.json(
        { error: 'Failed to fetch organizations' },
        { status: 500 }
      );
    }

    const results = [];

    for (const org of organizations) {
      // Get connected platforms for this organization
      const { data: credentials } = await supabaseAdmin
        .from('api_credentials')
        .select('platform')
        .eq('organization_id', org.id)
        .eq('is_active', true);

      if (!credentials || credentials.length === 0) {
        continue; // Skip organizations with no connections
      }

      // Sync each platform
      for (const cred of credentials) {
        try {
          const syncResponse = await fetch(
            `${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/connectors/${cred.platform.toLowerCase()}/sync`,
            {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                // In production, use service account or API key for internal calls
                'X-Internal-Request': 'true',
                'X-Organization-Id': org.id,
              },
            }
          );

          if (syncResponse.ok) {
            const syncData = await syncResponse.json();
            results.push({
              organizationId: org.id,
              platform: cred.platform,
              success: true,
              recordsSynced: syncData.recordsSynced || 0,
            });
          } else {
            results.push({
              organizationId: org.id,
              platform: cred.platform,
              success: false,
              error: await syncResponse.text(),
            });
          }
        } catch (error: any) {
          results.push({
            organizationId: org.id,
            platform: cred.platform,
            success: false,
            error: error.message,
          });
        }
      }

      // Run brain cycle after sync
      try {
        const brainResponse = await fetch(
          `${process.env.NEXTAUTH_URL || 'http://localhost:3000'}/api/brain-cycle`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-Internal-Request': 'true',
              'X-Organization-Id': org.id,
            },
          }
        );

        if (brainResponse.ok) {
          results.push({
            organizationId: org.id,
            platform: 'brain-cycle',
            success: true,
          });
        }
      } catch (error: any) {
        results.push({
          organizationId: org.id,
          platform: 'brain-cycle',
          success: false,
          error: error.message,
        });
      }
    }

    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      organizationsProcessed: organizations.length,
      results,
    });
  } catch (error: any) {
    console.error('[CRON] Daily sync error:', error);
    return NextResponse.json(
      { error: error.message || 'Cron job failed' },
      { status: 500 }
    );
  }
}

