#!/usr/bin/env python3
"""
Migrate watched_ads table to support TEXT ad_ids instead of INTEGER
This allows storing Adsterra ad IDs which are strings
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('AIVEN_HOST'),
    port=os.getenv('AIVEN_PORT'),
    database=os.getenv('AIVEN_DB'),
    user=os.getenv('AIVEN_USER'),
    password=os.getenv('AIVEN_PASSWORD'),
    sslmode='require'
)

cursor = conn.cursor()

try:
    print("🔄 Migrating watched_ads table...")
    
    # Drop the old foreign key constraint if it exists
    cursor.execute("""
        ALTER TABLE watched_ads 
        DROP CONSTRAINT IF EXISTS watched_ads_ad_id_fkey;
    """)
    print("   ✓ Dropped foreign key constraint")
    
    # Change ad_id from INTEGER to TEXT
    cursor.execute("""
        ALTER TABLE watched_ads 
        ALTER COLUMN ad_id TYPE TEXT;
    """)
    print("   ✓ Changed ad_id column type to TEXT")
    
    conn.commit()
    print("✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()
