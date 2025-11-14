"""
models.py - Optimized with connection pooling for better performance
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Load .env file
load_dotenv()

# Aiven PostgreSQL Configuration
DATABASE_CONFIG = {
    'host': os.getenv('AIVEN_HOST'),
    'port': int(os.getenv('AIVEN_PORT', 5432)),
    'database': os.getenv('AIVEN_DB'),
    'user': os.getenv('AIVEN_USER'),
    'password': os.getenv('AIVEN_PASSWORD'),
    'sslmode': 'require'
}

# Connection pool for better performance
db_pool = None

def init_pool():
    """Initialize connection pool"""
    global db_pool
    if db_pool is None:
        try:
            db_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=DATABASE_CONFIG['host'],
                port=DATABASE_CONFIG['port'],
                database=DATABASE_CONFIG['database'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                sslmode=DATABASE_CONFIG['sslmode']
            )
            print("✓ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Failed to initialize connection pool: {e}")
            raise

def get_db():
    """Get PostgreSQL database connection from pool"""
    global db_pool
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
    """Return connection to pool"""
    global db_pool
    if db_pool and conn:
        db_pool.putconn(conn)

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
        print("="*60 + "\n")
        raise ValueError(f"Missing required environment variables: {missing}")
    
    print(f"✓ Database: {DATABASE_CONFIG['host']}/{DATABASE_CONFIG['database']}")

# Validate on import
validate_config()

def init_db():
    """Initialize PostgreSQL database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'users'
    """)
    
    if cursor.fetchone():
        print("✓ Database already initialized")
        cursor.close()
        return_db(conn)
        return
    
    print("🔧 Initializing database...")
    
    # Create all tables
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
            type VARCHAR(20) NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS watched_ads (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            ad_id INTEGER NOT NULL REFERENCES ads(id),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_watched_ads_user ON watched_ads(user_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id, timestamp);
    """)
    
    # Insert demo data
    demo_password = generate_password_hash('demo123')
    
    cursor.execute("""
        INSERT INTO users (phone, password_hash, name, is_admin, balance) 
        VALUES 
            ('0821234567', %s, 'Admin User', true, 1250),
            ('0829876543', %s, 'John Doe', false, 450),
            ('0834567890', %s, 'Jane Smith', false, 280)
        ON CONFLICT (phone) DO NOTHING
    """, (demo_password, demo_password, demo_password))
    
    cursor.execute("""
        INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) 
        VALUES 
            ('MTN Mega Deal', 'MTN', 'Get 50% more data!', 
             'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN', 5, 30, 'video'),
            ('Shoprite Fresh', 'Shoprite', 'Fresh produce!', 
             'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite', 5, 15, 'image'),
            ('Nike Back to School', 'Nike', 'New gear!', 
             'https://via.placeholder.com/400x300/000/FFF?text=Nike', 10, 45, 'video')
    """)
    
    conn.commit()
    cursor.close()
    return_db(conn)
    print("✓ Database initialized")


class User(UserMixin):
    def __init__(self, id, phone, name, is_admin, balance):
        self.id = id
        self.phone = phone
        self.name = name
        self.is_admin = bool(is_admin)
        self.balance = balance
    
    @staticmethod
    def get(user_id):
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data:
                return User(
                    user_data['id'], 
                    user_data['phone'], 
                    user_data['name'], 
                    user_data['is_admin'], 
                    user_data['balance']
                )
            return None
        finally:
            return_db(conn)
    
    @staticmethod
    def create(phone, password, name):
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (phone, password_hash, name, balance) 
                VALUES (%s, %s, %s, 0) 
                RETURNING id
            ''', (phone, generate_password_hash(password), name))
            
            user_id = cursor.fetchone()['id']
            conn.commit()
            cursor.close()
            return User.get(user_id)
        except:
            conn.rollback()
            return None
        finally:
            return_db(conn)
    
    @staticmethod
    def verify_password(phone, password):
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE phone = %s', (phone,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                return User(
                    user_data['id'], 
                    user_data['phone'], 
                    user_data['name'], 
                    user_data['is_admin'], 
                    user_data['balance']
                )
            return None
        finally:
            return_db(conn)