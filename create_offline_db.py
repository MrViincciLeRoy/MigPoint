"""
create_offline_db.py - Create offline SQLite database copy
Run this once to initialize the offline database, then it will auto-sync with online data
"""

import sqlite3
import os
from pathlib import Path

# Create offline database in project root
OFFLINE_DB_PATH = 'offline_data.db'

def create_offline_db():
    """Create SQLite database with same schema as PostgreSQL"""
    
    # Remove existing database if it exists
    if os.path.exists(OFFLINE_DB_PATH):
        os.remove(OFFLINE_DB_PATH)
        print(f"Removed existing {OFFLINE_DB_PATH}")
    
    # Create new database
    conn = sqlite3.connect(OFFLINE_DB_PATH)
    cursor = conn.cursor()
    
    print(f"Creating offline database: {OFFLINE_DB_PATH}\n")
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone VARCHAR(10) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name VARCHAR(100) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                balance INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created users table")
        
        # Create transactions table
        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                type VARCHAR(20) NOT NULL,
                amount INTEGER NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created transactions table")
        
        # Create ads table
        cursor.execute('''
            CREATE TABLE ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                advertiser TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                reward INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                type VARCHAR(20) NOT NULL,
                ad_type VARCHAR(20),
                provider VARCHAR(20)
            )
        ''')
        print("✓ Created ads table")
        
        # Create watched_ads table
        cursor.execute('''
            CREATE TABLE watched_ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                ad_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✓ Created watched_ads table")
        
        # Create ad_impressions table
        cursor.execute('''
            CREATE TABLE ad_impressions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider VARCHAR(50) NOT NULL,
                ad_id TEXT NOT NULL,
                user_id INTEGER NOT NULL REFERENCES users(id),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'shown',
                watch_time INTEGER,
                completed_at TIMESTAMP
            )
        ''')
        print("✓ Created ad_impressions table")
        
        # Create indices
        cursor.execute('CREATE INDEX idx_watched_ads_user ON watched_ads(user_id, timestamp)')
        cursor.execute('CREATE INDEX idx_watched_ads_cooldown ON watched_ads(user_id, ad_id, timestamp)')
        cursor.execute('CREATE INDEX idx_transactions_user ON transactions(user_id, timestamp)')
        print("✓ Created indices")
        
        # Insert demo users
        from werkzeug.security import generate_password_hash
        demo_password = generate_password_hash('demo123')
        
        cursor.execute('''
            INSERT INTO users (phone, password_hash, name, is_admin, balance) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('0821234567', demo_password, 'Admin User', True, 1250))
        
        cursor.execute('''
            INSERT INTO users (phone, password_hash, name, is_admin, balance) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('0829876543', demo_password, 'John Doe', False, 450))
        
        cursor.execute('''
            INSERT INTO users (phone, password_hash, name, is_admin, balance) 
            VALUES (?, ?, ?, ?, ?)
        ''', ('0834567890', demo_password, 'Jane Smith', False, 280))
        
        print("✓ Inserted demo users")
        
        # Insert demo ads
        cursor.execute('''
            INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('MTN Mega Deal', 'MTN', 'Get 50% more data!', 
              'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN', 5, 30, 'video'))
        
        cursor.execute('''
            INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Shoprite Fresh', 'Shoprite', 'Fresh produce!', 
              'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite', 5, 15, 'image'))
        
        cursor.execute('''
            INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('Nike Back to School', 'Nike', 'New gear!', 
              'https://via.placeholder.com/400x300/000/FFF?text=Nike', 10, 45, 'video'))
        
        print("✓ Inserted demo ads")
        
        conn.commit()
        print(f"\n✓ Offline database created successfully: {OFFLINE_DB_PATH}")
        print("\nDatabase is ready for offline use!")
        print("Set DB_MODE=offline in .env to use this database")
        
    except Exception as e:
        print(f"\n✗ Error creating database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    create_offline_db()
