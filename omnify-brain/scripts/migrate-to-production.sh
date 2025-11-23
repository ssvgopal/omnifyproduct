#!/bin/bash

# Omnify Brain - Migrate MVP to Production Structure
# This script separates the MVP demo from production codebase

set -e

echo "🚀 Starting migration to production structure..."

# Step 1: Create demo directory
echo "📁 Creating demo directory..."
mkdir -p demo

# Step 2: Move MVP files to demo
echo "📦 Moving MVP files to demo/..."
mv src/app demo/ 2>/dev/null || echo "app already moved"
mv src/components demo/ 2>/dev/null || echo "components already moved"
mv src/lib demo/ 2>/dev/null || echo "lib already moved"
mv src/data demo/ 2>/dev/null || echo "data already moved"
mv scripts demo/ 2>/dev/null || echo "scripts already moved"

# Step 3: Copy config files to demo
echo "⚙️ Copying config files to demo/..."
cp next.config.ts demo/ 2>/dev/null || echo "next.config.ts already exists"
cp tsconfig.json demo/ 2>/dev/null || echo "tsconfig.json already exists"
cp tailwind.config.ts demo/ 2>/dev/null || echo "tailwind.config.ts already exists"
cp postcss.config.mjs demo/ 2>/dev/null || echo "postcss.config.mjs already exists"
cp components.json demo/ 2>/dev/null || echo "components.json already exists"

# Step 4: Create demo package.json
echo "📝 Creating demo package.json..."
cat > demo/package.json << 'EOF'
{
  "name": "omnify-brain-demo",
  "version": "1.0.0",
  "description": "Omnify AI Marketing Brain - MVP Demo (Static, No Dependencies)",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3001",
    "build": "next build",
    "start": "next start -p 3001",
    "lint": "eslint",
    "seed": "tsx scripts/seed-demo.ts",
    "brain": "tsx scripts/run-brain.ts",
    "demo": "npm run seed && npm run brain && npm run dev"
  },
  "dependencies": {
    "next": "16.0.3",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "@radix-ui/react-avatar": "^1.1.11",
    "@radix-ui/react-progress": "^1.1.8",
    "@radix-ui/react-separator": "^1.1.8",
    "@radix-ui/react-slot": "^1.2.4",
    "@radix-ui/react-tabs": "^1.1.13",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "lucide-react": "^0.554.0",
    "tailwind-merge": "^3.4.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.0.3",
    "tailwindcss": "^4",
    "tsx": "^4.7.0",
    "typescript": "^5"
  }
}
EOF

# Step 5: Create demo README
echo "📄 Creating demo README..."
cat > demo/README.md << 'EOF'
# Omnify Brain - MVP Demo

**Self-contained demo with zero external dependencies**

## Quick Start

```bash
# Install dependencies
npm install

# Run complete demo
npm run demo

# Or run steps individually:
npm run seed    # Generate demo data
npm run brain   # Process brain cycle
npm run dev     # Start dashboard
```

Open [http://localhost:3001](http://localhost:3001)

## What This Is

A fully functional prototype showcasing:
- MEMORY: Attribution & ROI analysis
- ORACLE: Predictive risk detection
- CURIOSITY: Prescriptive actions

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- TailwindCSS + shadcn/ui
- Static JSON data (no database)

## Production Version

See parent directory for full production implementation with:
- Supabase database
- Real API integrations (Meta, Google, TikTok, Shopify)
- AI/ML services (OpenAI, Anthropic)
- Authentication & multi-tenancy
EOF

# Step 6: Create production src structure
echo "🏗️ Creating production src structure..."
mkdir -p src/app/{api,\(auth\),\(dashboard\)}
mkdir -p src/components/{ui,auth,dashboard,integrations,onboarding,shared}
mkdir -p src/lib/{auth,brain,integrations,ai,services,db,hooks,utils}
mkdir -p tests/{unit,integration,e2e}

# Step 7: Create placeholder files
echo "📝 Creating placeholder files..."

# Middleware
cat > src/middleware.ts << 'EOF'
import { withAuth } from 'next-auth/middleware';

export default withAuth({
  callbacks: {
    authorized: ({ token }) => !!token,
  },
});

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*', '/api/brain/:path*'],
};
EOF

# Root layout
cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Omnify Brain - AI Marketing Intelligence',
  description: 'Production SaaS platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

# Landing page
cat > src/app/page.tsx << 'EOF'
export default function LandingPage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Omnify Brain</h1>
        <p className="text-xl text-muted-foreground mb-8">
          AI-Powered Marketing Intelligence
        </p>
        <a
          href="/login"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Get Started
        </a>
      </div>
    </div>
  );
}
EOF

# Step 8: Update root package.json
echo "📦 Updating root package.json..."
cat > package.json << 'EOF'
{
  "name": "omnify-brain-production",
  "version": "1.0.0",
  "description": "Omnify AI Marketing Brain - Production SaaS",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test",
    "demo": "cd demo && npm run demo"
  },
  "dependencies": {
    "@anthropic-ai/sdk": "^0.70.1",
    "@radix-ui/react-avatar": "^1.1.11",
    "@radix-ui/react-dialog": "^1.1.8",
    "@radix-ui/react-dropdown-menu": "^2.1.8",
    "@radix-ui/react-progress": "^1.1.8",
    "@radix-ui/react-separator": "^1.1.8",
    "@radix-ui/react-slot": "^1.2.4",
    "@radix-ui/react-tabs": "^1.1.13",
    "@supabase/auth-helpers-nextjs": "^0.10.0",
    "@supabase/supabase-js": "^2.84.0",
    "axios": "^1.13.2",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "date-fns": "^4.1.0",
    "lucide-react": "^0.554.0",
    "next": "16.0.3",
    "next-auth": "^4.24.13",
    "openai": "^6.9.1",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "recharts": "^2.10.0",
    "sonner": "^1.3.0",
    "swr": "^2.2.4",
    "tailwind-merge": "^3.4.0",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@tailwindcss/postcss": "^4",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/react": "^14.1.2",
    "@types/jest": "^29.5.11",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.0.3",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "tailwindcss": "^4",
    "tsx": "^4.7.0",
    "typescript": "^5"
  }
}
EOF

# Step 9: Create .gitignore updates
echo "🔒 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Production
.env.local
.env.production

# Demo
demo/.next
demo/node_modules
demo/data/outputs/
demo/data/seeds/
EOF

echo ""
echo "✅ Migration complete!"
echo ""
echo "📋 Next steps:"
echo "1. Install demo dependencies:    cd demo && npm install"
echo "2. Test demo:                    cd demo && npm run demo"
echo "3. Install production deps:      npm install"
echo "4. Set up Supabase:              See PRODUCTION_PLAN.md Phase 1"
echo "5. Configure .env.local:         Copy from .env.example"
echo ""
echo "🎯 Demo URL: http://localhost:3001"
echo "🚀 Production URL: http://localhost:3000"
