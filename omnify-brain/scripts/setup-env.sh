#!/bin/bash

# Omnify Brain - Environment Setup Script
# Creates .env.local with all required variables

set -e

echo "🔧 Setting up environment variables..."

# Check if .env.local already exists
if [ -f .env.local ]; then
    read -p "⚠️  .env.local already exists. Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create .env.local
cat > .env.local << 'EOF'
# Omnify Brain - Production Environment Variables
# Generated: $(date)

# ============================================
# SUPABASE (Required)
# ============================================
# Get from: https://app.supabase.com/project/_/settings/api
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# ============================================
# NEXTAUTH (Required)
# ============================================
# Generate secret: openssl rand -base64 32
NEXTAUTH_SECRET=
NEXTAUTH_URL=http://localhost:3000

# ============================================
# META ADS (Optional - for platform integration)
# ============================================
# Get from: https://developers.facebook.com/apps/
META_ADS_ACCESS_TOKEN=
META_ADS_ACCOUNT_ID=

# ============================================
# GOOGLE ADS (Optional)
# ============================================
# Get from: https://console.cloud.google.com/
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=
GOOGLE_ADS_DEVELOPER_TOKEN=

# ============================================
# TIKTOK ADS (Optional)
# ============================================
# Get from: https://business-api.tiktok.com/
TIKTOK_ADS_ACCESS_TOKEN=
TIKTOK_ADS_ADVERTISER_ID=

# ============================================
# SHOPIFY (Optional)
# ============================================
# Get from: https://[store].myshopify.com/admin/apps/private
SHOPIFY_STORE_URL=
SHOPIFY_ACCESS_TOKEN=

# ============================================
# AI SERVICES (Optional - for AI features)
# ============================================
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=

# ============================================
# MONITORING (Optional - for production)
# ============================================
# Get from: https://sentry.io/
SENTRY_DSN=

# Get from: https://logrocket.com/
LOGROCKET_APP_ID=

# ============================================
# CRON (Required for scheduled syncs)
# ============================================
# Generate: openssl rand -base64 32
CRON_SECRET=

# ============================================
# STRIPE (Optional - for billing)
# ============================================
# Get from: https://dashboard.stripe.com/apikeys
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=

# ============================================
# EMAIL (Optional - for notifications)
# ============================================
# SMTP settings for email notifications
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@omnify.ai
EOF

echo ""
echo "✅ Created .env.local"
echo ""
echo "📋 Required setup steps:"
echo ""
echo "1️⃣  SUPABASE (Required)"
echo "   - Go to: https://app.supabase.com/"
echo "   - Create new project"
echo "   - Copy URL and keys to .env.local"
echo "   - Run: supabase/migrations/001_initial_schema.sql"
echo ""
echo "2️⃣  NEXTAUTH (Required)"
echo "   - Generate secret: openssl rand -base64 32"
echo "   - Paste into NEXTAUTH_SECRET"
echo ""
echo "3️⃣  PLATFORM APIS (Optional)"
echo "   - Meta Ads: https://developers.facebook.com/"
echo "   - Google Ads: https://console.cloud.google.com/"
echo "   - TikTok Ads: https://business-api.tiktok.com/"
echo "   - Shopify: https://[store].myshopify.com/admin/apps"
echo ""
echo "4️⃣  AI SERVICES (Optional)"
echo "   - OpenAI: https://platform.openai.com/api-keys"
echo "   - Anthropic: https://console.anthropic.com/"
echo ""
echo "5️⃣  CRON SECRET (Required)"
echo "   - Generate: openssl rand -base64 32"
echo "   - Paste into CRON_SECRET"
echo ""
echo "📝 Edit .env.local and fill in your credentials"
echo ""
echo "🚀 After setup, run: npm run dev"
