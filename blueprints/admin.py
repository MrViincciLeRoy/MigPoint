from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import get_db, return_db
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
    try:
        cursor = conn.cursor()
        
        # Get total users
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        
        # Get total ad views
        cursor.execute('SELECT COUNT(*) as count FROM watched_ads')
        total_ad_views = cursor.fetchone()['count']
        
        # Get total earned
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = %s
        """, ('earn',))
        total_earned = cursor.fetchone()['total']
        
        # Get total spent
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE type = %s
        """, ('spend',))
        total_spent = cursor.fetchone()['total']
        
        # Get all users
        cursor.execute('SELECT * FROM users ORDER BY balance DESC')
        users = cursor.fetchall()
        
        # Get all ads
        cursor.execute('SELECT * FROM ads')
        ads = cursor.fetchall()
        
        cursor.close()
        
        return render_template('admin/dashboard.html', 
                             total_users=total_users, 
                             total_ad_views=total_ad_views,
                             total_earned=total_earned, 
                             total_spent=total_spent, 
                             users=users, 
                             ads=ads)
    finally:
        return_db(conn)
