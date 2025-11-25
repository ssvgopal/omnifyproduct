import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /**
   * Explicitly set the Turbopack root so that environment variables are
   * loaded from this app directory instead of the monorepo root.
   *
   * Without this, Next.js may pick `C:\\share\\repos\\ai` as the workspace
   * root (because of multiple lockfiles) and ignore `omnify-brain/.env.local`,
   * which causes `process.env.SUPABASE_SERVICE_ROLE_KEY` to be undefined and
   * triggers the `supabaseKey is required.` runtime error.
   */
  turbopack: {
    root: __dirname,
  },
  reactCompiler: true,
};

export default nextConfig;
