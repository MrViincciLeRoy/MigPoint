from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import get_db
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Login required', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Admin access only', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_ad_views = conn.execute('SELECT COUNT(*) as count FROM watched_ads').fetchone()['count']
    total_earned = conn.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = "earn"').fetchone()['total']
    total_spent = conn.execute('SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE type = "spend"').fetchone()['total']
    users = conn.execute('SELECT * FROM users ORDER BY balance DESC').fetchall()
    ads = conn.execute('SELECT * FROM ads').fetchall()
    conn.close()
    return render_template('admin/dashboard.html', total_users=total_users, total_ad_views=total_ad_views,
                         total_earned=total_earned, total_spent=total_spent, users=users, ads=ads)