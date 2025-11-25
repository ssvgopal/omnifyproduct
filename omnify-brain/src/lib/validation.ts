/**
 * Platform Validation Utilities
 * Ensures only MVP platforms are accepted
 */

export const MVP_PLATFORMS_TECHNICAL = ['meta_ads', 'google_ads', 'tiktok_ads', 'shopify'] as const;
export const MVP_PLATFORMS_DISPLAY = ['Meta', 'Google', 'TikTok', 'Shopify'] as const;

export type MVPPlatformTechnical = typeof MVP_PLATFORMS_TECHNICAL[number];
export type MVPPlatformDisplay = typeof MVP_PLATFORMS_DISPLAY[number];
export type MVPPlatform = MVPPlatformTechnical | MVPPlatformDisplay;

/**
 * Validates if a platform is an MVP platform
 */
export function isValidMVPPlatform(platform: string): platform is MVPPlatform {
  return (
    MVP_PLATFORMS_TECHNICAL.includes(platform as MVPPlatformTechnical) ||
    MVP_PLATFORMS_DISPLAY.includes(platform as MVPPlatformDisplay)
  );
}

/**
 * Normalizes platform name to technical format
 */
export function normalizePlatform(platform: string): MVPPlatformTechnical | null {
  const platformMap: Record<string, MVPPlatformTechnical> = {
    'meta': 'meta_ads',
    'meta_ads': 'meta_ads',
    'Meta': 'meta_ads',
    'google': 'google_ads',
    'google_ads': 'google_ads',
    'Google': 'google_ads',
    'tiktok': 'tiktok_ads',
    'tiktok_ads': 'tiktok_ads',
    'TikTok': 'tiktok_ads',
    'shopify': 'shopify',
    'Shopify': 'shopify',
  };

  return platformMap[platform] || null;
}

/**
 * Validates platform and returns error response if invalid
 */
export function validatePlatform(platform: string | null | undefined): { valid: boolean; error?: Response } {
  if (!platform) {
    return {
      valid: false,
      error: new Response(
        JSON.stringify({ error: 'Platform is required. MVP supports: Meta Ads, Google Ads, TikTok Ads, Shopify only.' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      ),
    };
  }

  if (!isValidMVPPlatform(platform)) {
    return {
      valid: false,
      error: new Response(
        JSON.stringify({ 
          error: `Invalid platform: ${platform}. MVP supports: Meta Ads, Google Ads, TikTok Ads, Shopify only.`,
          supported: MVP_PLATFORMS_DISPLAY,
        }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      ),
    };
  }

  return { valid: true };
}

