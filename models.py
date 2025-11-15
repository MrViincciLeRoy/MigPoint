"""
models.py - Database abstraction with support for PostgreSQL and SQLite
Automatically switches between online (PostgreSQL) and offline (SQLite) modes
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import atexit
import sqlite3

# Load .env file
load_dotenv()

# Determine database mode
DB_MODE = os.getenv('DB_MODE', 'online').lower()

print(f"\n🔄 Database Mode: {DB_MODE.upper()}")

if DB_MODE == 'offline':
    # SQLite offline mode
    OFFLINE_DB_PATH = os.getenv('OFFLINE_DB_PATH', 'offline_data.db')
    print(f"📁 Using SQLite database: {OFFLINE_DB_PATH}")
    
    if not os.path.exists(OFFLINE_DB_PATH):
        print(f"⚠️  Offline database not found: {OFFLINE_DB_PATH}")
        print("   Run: python create_offline_db.py")
        raise FileNotFoundError(f"Offline database not found: {OFFLINE_DB_PATH}")
    
    USE_SQLITE = True
    db_pool = None
else:
    # PostgreSQL online mode
    USE_SQLITE = False
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    
    DATABASE_CONFIG = {
        'host': os.getenv('AIVEN_HOST'),
        'port': int(os.getenv('AIVEN_PORT', 5432)),
        'database': os.getenv('AIVEN_DB'),
        'user': os.getenv('AIVEN_USER'),
        'password': os.getenv('AIVEN_PASSWORD'),
        'sslmode': 'require'
    }
    
    db_pool = None
    print(f"🗄️  Using PostgreSQL: {DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}")

# ============================================================================
# QUERY PARAMETER CONVERSION (PostgreSQL %s → SQLite ?)
# ============================================================================

def convert_query(query):
    """
    Convert PostgreSQL %s placeholders to SQLite ? placeholders.
    Only converts when using SQLite (offline mode).
    
    Usage:
        cursor.execute(convert_query("SELECT * FROM users WHERE id = %s"), (1,))
    """
    if USE_SQLITE:
        # Replace PostgreSQL %s with SQLite ?
        return query.replace('%s', '?')
    return query

def safe_row_access(row, key, index):
    """
    Safely access row data regardless of database type.
    PostgreSQL returns dicts, SQLite returns tuples.
    
    Usage:
        safe_row_access(row, 'id', 0)  # Returns row['id'] or row[0]
    """
    if row is None:
        return None
    try:
        # Try dict access (PostgreSQL)
        return row[key]
    except (TypeError, KeyError):
        # Fall back to tuple access (SQLite)
        return row[index]

# ============================================================================
# POSTGRESQL CONNECTION POOL (for online mode)
# ============================================================================

def init_pool():
    """Initialize PostgreSQL connection pool with appropriate size"""
    global db_pool
    
    if USE_SQLITE:
        return  # No pool needed for SQLite
    
    if db_pool is not None:
        return  # Already initialized
    
    try:
        db_pool = pool.ThreadedConnectionPool(
            minconn=2,
            maxconn=20,
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            sslmode=DATABASE_CONFIG['sslmode'],
            connect_timeout=10
        )
        print("✓ PostgreSQL connection pool initialized (2-20 connections)\n")
    except Exception as e:
        print(f"❌ Failed to initialize connection pool: {e}")
        raise

# ============================================================================
# UNIFIED DATABASE CONNECTION INTERFACE
# ============================================================================

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically switches between PostgreSQL and SQLite.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # do work
            cursor.close()
    """
    global db_pool
    
    if USE_SQLITE:
        # SQLite mode
        conn = sqlite3.connect(OFFLINE_DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()
    else:
        # PostgreSQL mode
        if db_pool is None:
            init_pool()
        
        conn = None
        try:
            conn = db_pool.getconn()
            conn.cursor_factory = RealDictCursor
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if conn:
                db_pool.putconn(conn)

def get_db():
    """
    Legacy function for backward compatibility.
    WARNING: You MUST call return_db(conn) when done!
    
    Consider using get_db_connection() context manager instead.
    """
    global db_pool
    
    if USE_SQLITE:
        conn = sqlite3.connect(OFFLINE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    else:
        if db_pool is None:
            init_pool()
        
        try:
            conn = db_pool.getconn()
            conn.cursor_factory = RealDictCursor
            return conn
        except Exception as e:
            print(f"Error getting connection: {e}")
            raise

def return_db(conn):
    """Return connection to pool (or close SQLite connection)"""
    global db_pool
    
    if USE_SQLITE:
        if conn:
            try:
                conn.rollback()
            except:
                pass
            conn.close()
    else:
        if db_pool and conn:
            try:
                if not conn.closed:
                    conn.rollback()
                db_pool.putconn(conn)
            except Exception as e:
                print(f"Error returning connection: {e}")

def close_all_connections():
    """Close all connections in pool (called on shutdown)"""
    global db_pool
    
    if USE_SQLITE:
        print("✓ SQLite database connections closed")
    else:
        if db_pool:
            try:
                db_pool.closeall()
                print("✓ All PostgreSQL connections closed")
            except Exception as e:
                print(f"Error closing connections: {e}")

# Register cleanup on exit
atexit.register(close_all_connections)

# ============================================================================
# DATABASE VALIDATION AND INITIALIZATION
# ============================================================================

def validate_config():
    """Check if all required environment variables are set"""
    if USE_SQLITE:
        return  # SQLite doesn't need validation
    
    required = ['AIVEN_HOST', 'AIVEN_DB', 'AIVEN_USER', 'AIVEN_PASSWORD']
    missing = [key for key in required if not os.getenv(key)]
    
    if missing:
        print("\n" + "="*60)
        print("❌ ERROR: Missing database configuration!")
        print("="*60)
        print(f"Missing environment variables: {', '.join(missing)}")
        print("="*60 + "\n")
        raise ValueError(f"Missing required environment variables: {missing}")
    
    print(f"✓ Database: {DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}")

validate_config()

def init_db():
    """Initialize database with tables (works with both modes)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        try:
            if USE_SQLITE:
                # Check SQLite
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='users'
                """)
            else:
                # Check PostgreSQL
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'users'
                """)
            
            if cursor.fetchone():
                print("✓ Database already initialized")
                return
            
            print("🔧 Initializing database...")
            
            # Create all tables (same schema for both databases)
            if USE_SQLITE:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone VARCHAR(10) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        is_admin BOOLEAN DEFAULT 0,
                        balance INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        type VARCHAR(20) NOT NULL,
                        amount INTEGER NOT NULL,
                        description TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ads (
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
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS watched_ads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        ad_id TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_watched_ads_user 
                    ON watched_ads(user_id, timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_watched_ads_cooldown 
                    ON watched_ads(user_id, ad_id, timestamp)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transactions_user 
                    ON transactions(user_id, timestamp)
                """)
            else:
                # PostgreSQL version
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        phone VARCHAR(10) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        balance INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        type VARCHAR(20) NOT NULL,
                        amount INTEGER NOT NULL,
                        description TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE TABLE IF NOT EXISTS ads (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        advertiser TEXT NOT NULL,
                        description TEXT,
                        image_url TEXT,
                        reward INTEGER NOT NULL,
                        duration INTEGER NOT NULL,
                        type VARCHAR(20) NOT NULL,
                        ad_type VARCHAR(20),
                        provider VARCHAR(20)
                    );
                    
                    CREATE TABLE IF NOT EXISTS watched_ads (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        ad_id TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_watched_ads_user 
                        ON watched_ads(user_id, timestamp);
                    CREATE INDEX IF NOT EXISTS idx_watched_ads_cooldown 
                        ON watched_ads(user_id, ad_id, timestamp);
                    CREATE INDEX IF NOT EXISTS idx_transactions_user 
                        ON transactions(user_id, timestamp);
                """)
            
            # Insert demo data
            demo_password = generate_password_hash('demo123')
            
            cursor.execute("""
                INSERT INTO users (phone, password_hash, name, is_admin, balance) 
                VALUES (?, ?, ?, ?, ?)
            """, ('0821234567', demo_password, 'Admin User', 1, 1250)) if USE_SQLITE else None
            
            if not USE_SQLITE:
                cursor.execute("""
                    INSERT INTO users (phone, password_hash, name, is_admin, balance) 
                    VALUES 
                        ('0821234567', %s, 'Admin User', true, 1250),
                        ('0829876543', %s, 'John Doe', false, 450),
                        ('0834567890', %s, 'Jane Smith', false, 280)
                    ON CONFLICT (phone) DO NOTHING
                """, (demo_password, demo_password, demo_password))
            else:
                cursor.execute("""
                    INSERT INTO users (phone, password_hash, name, is_admin, balance) 
                    VALUES (?, ?, ?, ?, ?)
                """, ('0829876543', demo_password, 'John Doe', 0, 450))
                cursor.execute("""
                    INSERT INTO users (phone, password_hash, name, is_admin, balance) 
                    VALUES (?, ?, ?, ?, ?)
                """, ('0834567890', demo_password, 'Jane Smith', 0, 280))
            
            conn.commit()
            print("✓ Database initialized")
            
        finally:
            cursor.close()

# ============================================================================
# USER MODEL
# ============================================================================

class User(UserMixin):
    def __init__(self, id, phone, name, is_admin, balance):
        self.id = id
        self.phone = phone
        self.name = name
        self.is_admin = bool(is_admin)
        self.balance = balance
    
    @staticmethod
    def get(user_id):
        """Get user by ID using context manager"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(convert_query('SELECT * FROM users WHERE id = %s'), (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    safe_row_access(user_data, 'id', 0),
                    safe_row_access(user_data, 'phone', 1),
                    safe_row_access(user_data, 'name', 3),
                    safe_row_access(user_data, 'is_admin', 4),
                    safe_row_access(user_data, 'balance', 5)
                )
            return None
    
    @staticmethod
    def create(phone, password, name):
        """Create new user using context manager"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(convert_query('''
                    INSERT INTO users (phone, password_hash, name, balance) 
                    VALUES (%s, %s, %s, 0)
                '''), (phone, generate_password_hash(password), name))
                
                conn.commit()
                
                # Get the created user
                cursor.execute(convert_query('SELECT id FROM users WHERE phone = %s'), (phone,))
                result = cursor.fetchone()
                user_id = safe_row_access(result, 'id', 0)
                cursor.close()
                return User.get(user_id)
            except:
                conn.rollback()
                return None
    
    @staticmethod
    def verify_password(phone, password):
        """Verify user credentials using context manager"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(convert_query('SELECT * FROM users WHERE phone = %s'), (phone,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                pwd_hash = safe_row_access(user_data, 'password_hash', 2)
                if check_password_hash(pwd_hash, password):
                    return User(
                        safe_row_access(user_data, 'id', 0),
                        safe_row_access(user_data, 'phone', 1),
                        safe_row_access(user_data, 'name', 3),
                        safe_row_access(user_data, 'is_admin', 4),
                        safe_row_access(user_data, 'balance', 5)
                    )
            return None
