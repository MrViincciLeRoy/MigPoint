from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import get_db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user data
    cursor.execute('SELECT * FROM users WHERE id = %s', (current_user.id,))
    user = cursor.fetchone()
    
    # Get today's earnings
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = %s AND type = 'earn' AND DATE(timestamp) = %s
    """, (current_user.id, today))
    today_earnings = cursor.fetchone()['total']
    
    # Get earn count
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM transactions 
        WHERE user_id = %s AND type = 'earn'
    """, (current_user.id,))
    earn_count = cursor.fetchone()['count']
    
    # Get all ads
    cursor.execute('SELECT * FROM ads')
    ads = cursor.fetchall()
    
    # Get recently watched ads (5 min cooldown)
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        SELECT ad_id 
        FROM watched_ads 
        WHERE user_id = %s AND timestamp > %s
    """, (current_user.id, five_minutes_ago))
    recently_watched = cursor.fetchall()
    recently_watched_ids = [row['ad_id'] for row in recently_watched]
    
    # Get total watch count
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM watched_ads 
        WHERE user_id = %s
    """, (current_user.id,))
    total_watched = cursor.fetchone()['count']
    
    # Get recent transactions
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE user_id = %s 
        ORDER BY timestamp DESC 
        LIMIT 5
    """, (current_user.id,))
    transactions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Filter out recently watched ads
    available_ads = [ad for ad in ads if ad['id'] not in recently_watched_ids]
    
    return render_template('main/dashboard.html', 
                         user=user, 
                         today_earnings=today_earnings, 
                         earn_count=earn_count,
                         watched_count=total_watched, 
                         ads=available_ads,
                         recently_watched_ids=recently_watched_ids,
                         all_ads_count=len(ads),
                         transactions=transactions)

@main_bp.route('/watch_ad/<int:ad_id>')
@login_required
def watch_ad(ad_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if watched in last 5 minutes
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        SELECT * FROM watched_ads 
        WHERE user_id = %s AND ad_id = %s AND timestamp > %s
    """, (current_user.id, ad_id, five_minutes_ago))
    recently_watched = cursor.fetchone()
    
    if recently_watched:
        cursor.close()
        conn.close()
        flash('⏳ Please wait 5 minutes before watching this ad again', 'warning')
        return redirect(url_for('main.dashboard'))
    
    # Get ad details
    cursor.execute('SELECT * FROM ads WHERE id = %s', (ad_id,))
    ad = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not ad:
        flash('Ad not found', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/watch_ad.html', ad=ad)

@main_bp.route('/complete_ad/<int:ad_id>', methods=['POST'])
@login_required
def complete_ad(ad_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if watched in last 5 minutes
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        SELECT * FROM watched_ads 
        WHERE user_id = %s AND ad_id = %s AND timestamp > %s
    """, (current_user.id, ad_id, five_minutes_ago))
    recently_watched = cursor.fetchone()
    
    if recently_watched:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Please wait before watching again'}), 400
    
    # Get ad details
    cursor.execute('SELECT * FROM ads WHERE id = %s', (ad_id,))
    ad = cursor.fetchone()
    
    if ad:
        try:
            # Record the watch
            cursor.execute("""
                INSERT INTO watched_ads (user_id, ad_id) 
                VALUES (%s, %s)
            """, (current_user.id, ad_id))
            
            # Add transaction
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, description) 
                VALUES (%s, %s, %s, %s)
            """, (current_user.id, 'earn', ad['reward'], f"Watched: {ad['title']}"))
            
            # Update user balance
            cursor.execute("""
                UPDATE users 
                SET balance = balance + %s 
                WHERE id = %s
            """, (ad['reward'], current_user.id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'reward': ad['reward']})
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"Error completing ad: {e}")
            return jsonify({'error': str(e)}), 500
    
    cursor.close()
    conn.close()
    return jsonify({'error': 'Not found'}), 404