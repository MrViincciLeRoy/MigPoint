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
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    today = datetime.now().strftime('%Y-%m-%d')
    today_earnings = conn.execute("SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = 'earn' AND DATE(timestamp) = ?", 
                                  (current_user.id, today)).fetchone()['total']
    earn_count = conn.execute('SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND type = "earn"', (current_user.id,)).fetchone()['count']
    
    # Get all ads
    ads = conn.execute('SELECT * FROM ads').fetchall()
    
    # Get watched ads in the last 5 minutes (cooldown period)
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    recently_watched = conn.execute(
        'SELECT ad_id FROM watched_ads WHERE user_id = ? AND timestamp > ?', 
        (current_user.id, five_minutes_ago)
    ).fetchall()
    recently_watched_ids = [row['ad_id'] for row in recently_watched]
    
    # Get total watch count
    total_watched = conn.execute('SELECT COUNT(*) as count FROM watched_ads WHERE user_id = ?', (current_user.id,)).fetchone()['count']
    
    transactions = conn.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (current_user.id,)).fetchall()
    conn.close()
    
    # Filter out recently watched ads (5 min cooldown)
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
    
    # Check if watched in last 5 minutes
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    recently_watched = conn.execute(
        'SELECT * FROM watched_ads WHERE user_id = ? AND ad_id = ? AND timestamp > ?', 
        (current_user.id, ad_id, five_minutes_ago)
    ).fetchone()
    
    if recently_watched:
        conn.close()
        flash('⏳ Please wait 5 minutes before watching this ad again', 'warning')
        return redirect(url_for('main.dashboard'))
    
    ad = conn.execute('SELECT * FROM ads WHERE id = ?', (ad_id,)).fetchone()
    conn.close()
    if not ad:
        flash('Ad not found', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('main/watch_ad.html', ad=ad)

@main_bp.route('/complete_ad/<int:ad_id>', methods=['POST'])
@login_required
def complete_ad(ad_id):
    conn = get_db()
    
    # Check if watched in last 5 minutes
    five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    recently_watched = conn.execute(
        'SELECT * FROM watched_ads WHERE user_id = ? AND ad_id = ? AND timestamp > ?', 
        (current_user.id, ad_id, five_minutes_ago)
    ).fetchone()
    
    if recently_watched:
        conn.close()
        return jsonify({'error': 'Please wait before watching again'}), 400
    
    ad = conn.execute('SELECT * FROM ads WHERE id = ?', (ad_id,)).fetchone()
    if ad:
        try:
            # Record the watch (can be multiple times, just tracks timing)
            conn.execute('INSERT INTO watched_ads (user_id, ad_id) VALUES (?, ?)', 
                        (current_user.id, ad_id))
            conn.execute('INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
                        (current_user.id, 'earn', ad['reward'], f"Watched: {ad['title']}"))
            conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', 
                        (ad['reward'], current_user.id))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'reward': ad['reward']})
        except Exception as e:
            conn.close()
            print(f"Error completing ad: {e}")
            return jsonify({'error': str(e)}), 500
    conn.close()
    return jsonify({'error': 'Not found'}), 404