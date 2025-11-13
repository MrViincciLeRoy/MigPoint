from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_required
from models import User, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret-key-in-production'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))

# Register blueprints
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.wallet import wallet_bp
from blueprints.admin import admin_bp

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
    init_db()
    print("\n" + "="*60)
    print("MIG POINTS APP")
    print("="*60)
    print("Demo Users (password: demo123):")
    print("  👑 Admin: 0821234567")
    print("  👤 User1: 0829876543")
    print("  👤 User2: 0834567890")
    print("="*60)
    print("\n🔗 Visit http://localhost:5000/routes to see all routes")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)