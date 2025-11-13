"""
migrate_database.py - Add missing tables for ad provider tracking
Run this once to update your existing database
"""

import sqlite3

def migrate_database():
    """Add missing tables to existing database"""
    
    print("\n" + "="*60)
    print("DATABASE MIGRATION - Adding Ad Provider Tables")
    print("="*60 + "\n")
    
    conn = sqlite3.connect('migpoints.db')
    c = conn.cursor()
    
    try:
        # Check if ad_impressions table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ad_impressions'")
        if not c.fetchone():
            print("📝 Creating ad_impressions table...")
            c.execute("""CREATE TABLE ad_impressions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                ad_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'shown',
                watch_time INTEGER,
                completed_at DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id))""")
            print("✓ ad_impressions table created")
        else:
            print("✓ ad_impressions table already exists")
        
        # Check if provider_stats table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='provider_stats'")
        if not c.fetchone():
            print("📝 Creating provider_stats table...")
            c.execute("""CREATE TABLE provider_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT UNIQUE NOT NULL,
                impressions INTEGER DEFAULT 0,
                completions INTEGER DEFAULT 0,
                last_served DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
            print("✓ provider_stats table created")
        else:
            print("✓ provider_stats table already exists")
        
        # Create indexes for better performance
        print("📝 Creating indexes...")
        try:
            c.execute("CREATE INDEX IF NOT EXISTS idx_impressions_user ON ad_impressions(user_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_impressions_provider ON ad_impressions(provider)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_impressions_status ON ad_impressions(status)")
            print("✓ Indexes created")
        except Exception as e:
            print(f"⚠️  Index creation: {e}")
        
        conn.commit()
        
        # Verify tables
        print("\n📊 Database Tables:")
        c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = c.fetchall()
        for table in tables:
            c.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = c.fetchone()[0]
            print(f"  ✓ {table[0]}: {count} rows")
        
        print("\n" + "="*60)
        print("✓ MIGRATION COMPLETE!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
