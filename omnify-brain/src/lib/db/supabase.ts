import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Server-side client with service role (for admin operations)
export const supabaseAdmin = createClient(
    supabaseUrl,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    {
        auth: {
            autoRefreshToken: false,
            persistSession: false
        }
    }
);

// Database types
export interface Organization {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
}

export interface User {
    id: string;
    email: string;
    organization_id: string;
    role: 'admin' | 'member' | 'viewer';
    created_at: string;
    updated_at: string;
}

export interface Channel {
    id: string;
    organization_id: string;
    name: string;
    platform: 'Meta' | 'Google' | 'TikTok' | 'Shopify' | 'Email' | 'LinkedIn';
    external_id?: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface DailyMetricDB {
    id: string;
    channel_id: string;
    date: string;
    spend: number;
    revenue: number;
    impressions: number;
    clicks: number;
    conversions: number;
    roas: number;
    cpa: number;
    ctr: number;
    created_at: string;
}

export interface CreativeDB {
    id: string;
    channel_id: string;
    name: string;
    external_id?: string;
    status: 'active' | 'paused' | 'archived';
    launch_date?: string;
    spend: number;
    revenue: number;
    impressions: number;
    clicks: number;
    roas: number;
    ctr: number;
    created_at: string;
    updated_at: string;
}

export interface BrainStateDB {
    id: string;
    organization_id: string;
    memory_output: any;
    oracle_output: any;
    curiosity_output: any;
    computed_at: string;
    created_at: string;
}

export interface APICredential {
    id: string;
    organization_id: string;
    platform: string;
    credentials: any;
    is_active: boolean;
    last_synced_at?: string;
    created_at: string;
    updated_at: string;
}

export interface SyncJob {
    id: string;
    organization_id: string;
    platform: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    started_at?: string;
    completed_at?: string;
    error_message?: string;
    records_synced: number;
    created_at: string;
}
