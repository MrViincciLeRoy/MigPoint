from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_caching import Cache
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import models AFTER loading env
from models import User, init_db, init_pool

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')

# Performance optimizations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache static files for 1 year
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Initialize caching
cache = Cache(app)

# Initialize connection pool
init_pool()

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.wallet import wallet_bp
from blueprints.admin import admin_bp
from ad_providers_config import AdProvidersConfig

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# Debug route to list all routes
@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:30s} {methods:20s} {rule}")
        output.append(line)
    return '<br>'.join(sorted(output))

if __name__ == '__main__':
    # Check if required environment variables are set
    required_vars = ['AIVEN_HOST', 'AIVEN_DB', 'AIVEN_USER', 'AIVEN_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("\n" + "="*60)
        print("⚠️  WARNING: Missing environment variables!")
        print("="*60)
        print(f"Missing: {', '.join(missing)}")
        print("\nFor local development:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your Aiven credentials")
        print("\nFor Render deployment:")
        print("  1. Go to your Render dashboard")
        print("  2. Navigate to Environment tab")
        print("  3. Add these variables:")
        for var in missing:
            print(f"     {var}=your-value-here")
        print("="*60 + "\n")
        exit(1)
    
    # Check if database is initialized
    try:
        from models import get_db
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        cursor.close()
        conn.close()
        print("\n✓ Database connection verified")
    except Exception as e:
        print("\n" + "="*60)
        print("⚠️  DATABASE NOT INITIALIZED")
        print("="*60)
        print("The database tables don't exist yet.")
        print("\nFor first-time setup, you need to initialize the database.")
        print("Contact your admin to run: init_db()")
        print("="*60 + "\n")
        # Don't exit - let the app try to initialize on first request
    
    print("\n" + "="*60)
    print("🚀 MIG POINTS APP - Running on Aiven PostgreSQL")
    print("="*60)
    print("Demo Users (password: demo123):")
    print("  👑 Admin: 0821234567")
    print("  👤 User1: 0829876543")
    print("  👤 User2: 0834567890")
    print("="*60)
    
    # Print ad providers status
    AdProvidersConfig.print_status()
    
    # Get port from environment (Render sets this automatically)
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n🔗 Running on port {port}")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)