import { createClient } from '@supabase/supabase-js';

// Browser/client-side Supabase client using the public anon key.
// This MUST NOT use the service role key.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabaseBrowser = createClient(supabaseUrl, supabaseAnonKey);


