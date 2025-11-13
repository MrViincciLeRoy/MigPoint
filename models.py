from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    conn = sqlite3.connect('migpoints.db')
    conn.row_factory = dict_factory  # Changed to dict_factory for better compatibility
    return conn

def init_db():
    conn = sqlite3.connect('migpoints.db')
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        phone TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, 
        name TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0, 
        balance INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL, 
        amount INTEGER NOT NULL, 
        description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id))""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        title TEXT NOT NULL,
        advertiser TEXT NOT NULL, 
        description TEXT, 
        image_url TEXT,
        reward INTEGER NOT NULL, 
        duration INTEGER NOT NULL,
        type TEXT NOT NULL)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS watched_ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL,
        ad_id INTEGER NOT NULL, 
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(ad_id) REFERENCES ads(id))""")
    
    demo_password = generate_password_hash('demo123')
    for phone, pwd, name, is_admin, balance in [
        ('0821234567', demo_password, 'Admin User', 1, 1250),
        ('0829876543', demo_password, 'John Doe', 0, 450),
        ('0834567890', demo_password, 'Jane Smith', 0, 280)]:
        try:
            c.execute('INSERT INTO users (phone, password_hash, name, is_admin, balance) VALUES (?, ?, ?, ?, ?)',
                     (phone, pwd, name, is_admin, balance))
        except: 
            pass
    
    for title, advertiser, desc, img, reward, duration, ad_type in [
        ('MTN Mega Deal', 'MTN', 'Get 50% more data!', 'https://via.placeholder.com/400x300/0066CC/FFF?text=MTN', 5, 30, 'video'),
        ('Shoprite Fresh', 'Shoprite', 'Fresh produce!', 'https://via.placeholder.com/400x300/00AA00/FFF?text=Shoprite', 5, 15, 'image'),
        ('Nike Back to School', 'Nike', 'New gear!', 'https://via.placeholder.com/400x300/000/FFF?text=Nike', 10, 45, 'video')]:
        try:
            c.execute('INSERT INTO ads (title, advertiser, description, image_url, reward, duration, type) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (title, advertiser, desc, img, reward, duration, ad_type))
        except: 
            pass
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

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
            user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
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
        try:
            c = conn.cursor()
            c.execute('INSERT INTO users (phone, password_hash, name, balance) VALUES (?, ?, ?, ?)',
                     (phone, generate_password_hash(password), name, 0))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            return User.get(user_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.close()
            return None
    
    @staticmethod
    def verify_password(phone, password):
        try:
            conn = get_db()
            user_data = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
            conn.close()
            
            if not user_data:
                print(f"No user found with phone: {phone}")
                return None
            
            # Debug: Print available keys
            print(f"User data keys: {user_data.keys() if user_data else 'None'}")
            
            if user_data and 'password_hash' in user_data:
                if check_password_hash(user_data['password_hash'], password):
                    return User(
                        user_data['id'], 
                        user_data['phone'], 
                        user_data['name'], 
                        user_data['is_admin'], 
                        user_data['balance']
                    )
            
            print("Password verification failed")
            return None
        except Exception as e:
            print(f"Error in verify_password: {e}")
            import traceback
            traceback.print_exc()
            return None