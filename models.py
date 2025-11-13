"""
models.py - Updated for psycopg v3 compatibility
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

# Try psycopg v3 first, fallback to psycopg2
try:
    import psycopg
    from psycopg.rows import dict_row
    USING_PSYCOPG3 = True
    print("✓ Using psycopg v3")
except ImportError:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USING_PSYCOPG3 = False
    print("✓ Using psycopg2")

# Load .env file from root directory
load_dotenv()

# Aiven PostgreSQL Configuration with proper defaults
DATABASE_CONFIG = {
    'host': os.getenv('AIVEN_HOST'),
    'port': int(os.getenv('AIVEN_PORT', 5432)),
    'dbname': os.getenv('AIVEN_DB'),  # psycopg3 uses 'dbname'
    'user': os.getenv('AIVEN_USER'),
    'password': os.getenv('AIVEN_PASSWORD'),
    'sslmode': 'require'
}

# Validate configuration
def validate_config():
    """Check if all required environment variables are set"""
    required = ['AIVEN_HOST', 'AIVEN_DB', 'AIVEN_USER', 'AIVEN_PASSWORD']
    missing = [key for key in required if not os.getenv(key)]
    
    if missing:
        print("\n" + "="*60)
        print("❌ ERROR: Missing database configuration!")
        print("="*60)
        print(f"Missing environment variables: {', '.join(missing)}")
        print("\nPlease set these in your environment or .env file")
        print("="*60 + "\n")
        raise ValueError(f"Missing required environment variables: {missing}")
    
    print("\n✓ Database configuration loaded successfully")
    print(f"  Host: {DATABASE_CONFIG['host']}")
    print(f"  Database: {DATABASE_CONFIG['dbname']}")
    print(f"  User: {DATABASE_CONFIG['user']}\n")

# Validate on import
validate_config()

def get_db():
    """Get PostgreSQL database connection (compatible with both psycopg versions)"""
    try:
        if USING_PSYCOPG3:
            # psycopg v3 syntax
            conn = psycopg.connect(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                dbname=DATABASE_CONFIG['dbname'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                sslmode=DATABASE_CONFIG['sslmode'],
                row_factory=dict_row
            )
        else:
            # psycopg2 syntax
            conn = psycopg2.connect(
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['dbname'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                sslmode=DATABASE_CONFIG['sslmode'],
                cursor_factory=RealDictCursor
            )
        return conn
    except Exception as e:
        print("\n" + "="*60)
        print("❌ DATABASE CONNECTION ERROR")
        print("="*60)
        print(f"Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your environment variables are correct")
        print("2. Verify your IP is whitelisted in Aiven console")
        print("3. Ensure SSL is enabled")
        print("="*60 + "\n")
        raise

def init_db():
    """Initialize PostgreSQL database with tables (only if not exist)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if tables already exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
    """)
    tables_exist = cursor.fetchone()
    
    if tables_exist:
        print("\n✓ Database already initialized (tables exist)")
        cursor.close()
        conn.close()
        return
    
    print("\n🔧 Initializing database for the first time...")
    
    # Users table
    print("  Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone VARCHAR(10) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name VARCHAR(100) NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            balance INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Transactions table
    print("  Creating transactions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type VARCHAR(20) NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ads table
    print("  Creating ads table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            advertiser TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            reward INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            type VARCHAR(20) NOT NULL
        )
    """)
    
    # Watched ads table
    print("  Creating watched_ads table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watched_ads (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            ad_id INTEGER NOT NULL REFERENCES ads(id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Trading orders table
    print("  Creating trading_orders table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trading_orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type VARCHAR(10) NOT NULL,
            amount INTEGER NOT NULL,
            price_per_point DECIMAL(10, 4) NOT NULL,
            status VARCHAR(20) DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            filled_at TIMESTAMP
        )
    """)
    
    # Trades table
    print("  Creating trades table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            buyer_id INTEGER NOT NULL REFERENCES users(id),
            seller_id INTEGER NOT NULL REFERENCES users(id),
            amount INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            fee DECIMAL(10, 2) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ad impressions table
    print("  Creating ad_impressions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ad_impressions (
            id SERIAL PRIMARY KEY,
            provider VARCHAR(50) NOT NULL,
            ad_id VARCHAR(100) NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'shown',
            watch_time INTEGER,
            completed_at TIMESTAMP
        )
    """)
    
    # Provider stats table
    print("  Creating provider_stats table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provider_stats (
            id SERIAL PRIMARY KEY,
            provider VARCHAR(50) UNIQUE NOT NULL,
            impressions INTEGER DEFAULT 0,
            completions INTEGER DEFAULT 0,
            last_served TIMESTAMP
        )
    """)
    
    # Crypto wallets table
    print("  Creating crypto_wallets table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_wallets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) UNIQUE,
            wallet_address VARCHAR(100),
            private_key_encrypted TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Crypto transactions table
    print("  Creating crypto_transactions table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto_transactions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            type VARCHAR(20) NOT NULL,
            amount_migp INTEGER,
            amount_crypto DECIMAL(18, 8),
            crypto_currency VARCHAR(10),
            tx_hash VARCHAR(100),
            status VARCHAR(20) DEFAULT 'pending',
            fee DECIMAL(10, 2),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("  ✓ All tables created")
    
    # Insert demo data
    print("\n  Adding demo data...")
    demo_password = generate_password_hash('demo123')
    
    demo_users = [
        ('0821234567', demo_password, 'Admin User', True, 1250),
        ('0829876543', demo_password, 'John Doe', False, 450),
        ('0834567890', demo_password, 'Jane Smith', False, 280)
    ]
    
    for phone, pwd, name, is_admin, balance in demo_users:
        try:
            cursor.execute('''
                INSERT INTO users (phone, password_hash, name, is_admin, balance) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (phone) DO NOTHING
            ''', (phone, pwd, name, is_admin, balance))
        except Exception as e:
            print(f"    Warning: Could not insert user {phone}: {e}")
    
    demo_ads = [
        ('MTN Mega Deal', 'MTN', 'Get 50% more data!', 
         'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN', 5, 30, 'video'),
        ('Shoprite Fresh', 'Shoprite', 'Fresh produce!', 
         'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite', 5, 15, 'image'),
        ('Nike Back to School', 'Nike', 'New gear!', 
         'https://via.placeholder.com/400x300/000/FFF?text=Nike', 10, 45, 'video')
    ]
    
    for title, advertiser, desc, img, reward, duration, ad_type in demo_ads:
        try:
            cursor.execute('''
                INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (title, advertiser, desc, img, reward, duration, ad_type))
        except Exception as e:
            print(f"    Warning: Could not insert ad {title}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("  ✓ Demo data added")
    print("\n" + "="*60)
    print("✅ Database initialized successfully!")
    print("="*60 + "\n")


class User(UserMixin):
    def __init__(self, id, phone, name, is_admin, balance):
        self.id = id
        self.phone = phone
        self.name = name
        self.is_admin = bool(is_admin)
        self.balance = balance
    
    @staticmethod
    def get(user_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_data:
                return User(
                    user_data['id'], 
                    user_data['phone'], 
                    user_data['name'], 
                    user_data['is_admin'], 
                    user_data['balance']
                )
            return None
        except Exception as e:
            print(f"Error in User.get: {e}")
            return None
    
    @staticmethod
    def create(phone, password, name):
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (phone, password_hash, name, balance) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id
            ''', (phone, generate_password_hash(password), name, 0))
            
            user_id = cursor.fetchone()['id']
            conn.commit()
            cursor.close()
            conn.close()
            return User.get(user_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
            return None
    
    @staticmethod
    def verify_password(phone, password):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone = %s', (phone,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_data:
                return None
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                return User(
                    user_data['id'], 
                    user_data['phone'], 
                    user_data['name'], 
                    user_data['is_admin'], 
                    user_data['balance']
                )
            
            return None
        except Exception as e:
            print(f"Error in verify_password: {e}")
            return None