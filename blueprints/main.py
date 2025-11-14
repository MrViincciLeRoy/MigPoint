from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import get_db, return_db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Check if we just earned points
    earned = request.args.get('earned')
    if earned:
        flash(f'🎉 +{earned} MIGP earned!', 'success')
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # ONE query to get everything we need
        today = datetime.now().strftime('%Y-%m-%d')
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get user, today's earnings, earn count, and watch count in ONE query
        cursor.execute("""
            SELECT 
                u.*,
                COALESCE(SUM(CASE WHEN t.type = 'earn' AND DATE(t.timestamp) = %s THEN t.amount ELSE 0 END), 0) as today_earnings,
                COUNT(DISTINCT CASE WHEN t.type = 'earn' THEN t.id END) as earn_count,
                COUNT(DISTINCT w.id) as watched_count
            FROM users u
            LEFT JOIN transactions t ON t.user_id = u.id
            LEFT JOIN watched_ads w ON w.user_id = u.id
            WHERE u.id = %s
            GROUP BY u.id
        """, (today, current_user.id))
        
        result = cursor.fetchone()
        user = result
        today_earnings = result['today_earnings']
        earn_count = result['earn_count']
        watched_count = result['watched_count']
        
        # Get all ads
        cursor.execute('SELECT * FROM ads')
        ads = cursor.fetchall()
        
        # Get recently watched ad IDs
        cursor.execute("""
            SELECT ad_id FROM watched_ads 
            WHERE user_id = %s AND timestamp > %s
        """, (current_user.id, five_minutes_ago))
        recently_watched_ids = [row['ad_id'] for row in cursor.fetchall()]
        
        # Get recent transactions
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 5
        """, (current_user.id,))
        transactions = cursor.fetchall()
        
        cursor.close()
        
        # Filter available ads
        available_ads = [ad for ad in ads if ad['id'] not in recently_watched_ids]
        
        return render_template('main/dashboard.html', 
                             user=user, 
                             today_earnings=today_earnings, 
                             earn_count=earn_count,
                             watched_count=watched_count, 
                             ads=available_ads,
                             recently_watched_ids=recently_watched_ids,
                             all_ads_count=len(ads),
                             transactions=transactions)
    finally:
        return_db(conn)

@main_bp.route('/watch_ad/<int:ad_id>')
@login_required
def watch_ad(ad_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Check cooldown and get ad in ONE query
        cursor.execute("""
            SELECT 
                a.*,
                EXISTS(
                    SELECT 1 FROM watched_ads 
                    WHERE user_id = %s AND ad_id = %s AND timestamp > %s
                ) as recently_watched
            FROM ads a
            WHERE a.id = %s
        """, (current_user.id, ad_id, five_minutes_ago, ad_id))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            flash('Ad not found', 'danger')
            return redirect(url_for('main.dashboard'))
        
        if result['recently_watched']:
            flash('⏳ Wait 5 minutes before watching again', 'warning')
            return redirect(url_for('main.dashboard'))
        
        return render_template('main/watch_ad.html', ad=result)
    finally:
        return_db(conn)

@main_bp.route('/complete_ad/<int:ad_id>', methods=['POST'])
@login_required
def complete_ad(ad_id):
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        five_minutes_ago = (datetime.now() - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Check if recently watched
        cursor.execute("""
            SELECT 1 FROM watched_ads 
            WHERE user_id = %s AND ad_id = %s AND timestamp > %s
        """, (current_user.id, ad_id, five_minutes_ago))
        
        if cursor.fetchone():
            cursor.close()
            return jsonify({'error': 'Please wait before watching again'}), 400
        
        # Get ad reward
        cursor.execute('SELECT reward, title FROM ads WHERE id = %s', (ad_id,))
        ad = cursor.fetchone()
        
        if not ad:
            cursor.close()
            return jsonify({'error': 'Ad not found'}), 404
        
        # Insert all in ONE transaction
        cursor.execute("""
            WITH ins_watch AS (
                INSERT INTO watched_ads (user_id, ad_id) 
                VALUES (%s, %s)
            ),
            ins_trans AS (
                INSERT INTO transactions (user_id, type, amount, description) 
                VALUES (%s, 'earn', %s, %s)
            )
            UPDATE users SET balance = balance + %s WHERE id = %s
        """, (
            current_user.id, ad_id,
            current_user.id, ad['reward'], f"Watched: {ad['title']}",
            ad['reward'], current_user.id
        ))
        
        conn.commit()
        cursor.close()
        
        return jsonify({'success': True, 'reward': ad['reward']})
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to complete ad'}), 500
    finally:
        return_db(conn)