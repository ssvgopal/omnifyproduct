#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migrations against Supabase PostgreSQL database
"""
import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def run_migration(migration_file: str):
    """Run a SQL migration file"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
        sys.exit(1)
    
    print(f"🔗 Connecting to Supabase: {supabase_url}")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)
    
    # Read migration file
    migration_path = Path(__file__).parent / 'migrations' / migration_file
    
    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_path}")
        sys.exit(1)
    
    print(f"📄 Reading migration: {migration_file}")
    
    with open(migration_path, 'r') as f:
        sql_content = f.read()
    
    # Note: Supabase Python client doesn't support raw SQL execution
    # You need to run this migration manually in Supabase SQL Editor
    print("\n" + "="*60)
    print("⚠️  MANUAL MIGRATION REQUIRED")
    print("="*60)
    print("\nThe Supabase Python client doesn't support raw SQL execution.")
    print("Please run this migration manually:")
    print("\n1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Navigate to: SQL Editor")
    print("4. Copy and paste the following SQL:\n")
    print("-"*60)
    print(sql_content)
    print("-"*60)
    print("\n5. Click 'Run' to execute the migration")
    print("\nAlternatively, use the Supabase CLI:")
    print(f"   supabase db execute --file {migration_path}")
    print("="*60)

if __name__ == '__main__':
    migration_file = '001_api_keys_schema.sql'
    
    if len(sys.argv) > 1:
        migration_file = sys.argv[1]
    
    run_migration(migration_file)
