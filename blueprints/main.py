from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import get_db, return_db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)


def get_ad_cooldown_info(user_id, ad_id):
    """
    Check if an ad is on cooldown for a user
    Returns: (is_on_cooldown: bool, seconds_remaining: int, last_watched: datetime)
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get the most recent watch for this user + ad combo
        cursor.execute("""
            SELECT timestamp,
                   EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - timestamp)) as seconds_ago
            FROM watched_ads 
            WHERE user_id = %s AND ad_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (user_id, ad_id))
        
        result = cursor.fetchone()
        
        if not result:
            # Never watched this ad
            return False, 0, None
        
        seconds_ago = int(result['seconds_ago'])
        cooldown_seconds = 5 * 60  # 5 minutes
        
        if seconds_ago < cooldown_seconds:
            # Still on cooldown
            seconds_remaining = cooldown_seconds - seconds_ago
            return True, seconds_remaining, result['timestamp']
        else:
            # Cooldown expired
            return False, 0, result['timestamp']
    
    finally:
        cursor.close()
        return_db(conn)


def calculate_ad_reward(ad_data, user_id):
    """Calculate dynamic reward based on ad type and user bonuses"""
    base_reward = float(ad_data['reward'])
    bonus_amount = 0.0
    bonus_details = []
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if first ad today (50% bonus)
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT COUNT(*) as count FROM transactions 
            WHERE user_id = %s 
            AND type = 'earn'
            AND DATE(timestamp) = %s
        """, (user_id, today))
        
        is_first_ad = cursor.fetchone()['count'] == 0
        
        if is_first_ad:
            first_ad_bonus = base_reward * 0.5
            bonus_amount += first_ad_bonus
            bonus_details.append(f"🎁 First ad today: +{first_ad_bonus:.1f} MIGP")
        
        # Check for 7-day streak (30% bonus)
        streak_days = 0
        for i in range(7):
            check_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(*) as count FROM transactions
                WHERE user_id = %s
                AND type = 'earn'
                AND DATE(timestamp) = %s
            """, (user_id, check_date))
            
            if cursor.fetchone()['count'] > 0:
                streak_days += 1
            else:
                break
        
        if streak_days >= 7:
            streak_bonus = base_reward * 0.3
            bonus_amount += streak_bonus
            bonus_details.append(f"🔥 7-day streak: +{streak_bonus:.1f} MIGP")
        
        # Check if weekend (20% bonus)
        is_weekend = datetime.now().weekday() in [5, 6]
        if is_weekend:
            weekend_bonus = base_reward * 0.2
            bonus_amount += weekend_bonus
            bonus_details.append(f"🎉 Weekend bonus: +{weekend_bonus:.1f} MIGP")
        
    finally:
        cursor.close()
        return_db(conn)
    
    total_reward = base_reward + bonus_amount
    
    return {
        'base': round(base_reward, 1),
        'bonus': round(bonus_amount, 1),
        'total': round(total_reward, 1),
        'bonus_details': bonus_details
    }


@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    earned = request.args.get('earned')
    if earned:
        flash(f'🎉 +{earned} MIGP earned!', 'success')
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get user stats
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
        is_first_ad = today_earnings == 0
        
        # Get ALL ads
        cursor.execute('SELECT * FROM ads ORDER BY reward DESC')
        all_ads = cursor.fetchall()
        
        # Get cooldown info for each ad
        ads_with_cooldown = []
        for ad in all_ads:
            is_cooldown, seconds_left, last_watched = get_ad_cooldown_info(current_user.id, ad['id'])
            
            ad_dict = dict(ad)
            ad_dict['is_on_cooldown'] = is_cooldown
            ad_dict['cooldown_seconds'] = seconds_left
            ad_dict['last_watched'] = last_watched
            
            ads_with_cooldown.append(ad_dict)
        
        # Get recent transactions
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 10
        """, (current_user.id,))
        transactions = cursor.fetchall()
        
        cursor.close()
        
        return render_template('main/dashboard.html', 
                             user=user, 
                             today_earnings=today_earnings, 
                             earn_count=earn_count,
                             watched_count=watched_count, 
                             all_ads=ads_with_cooldown,
                             transactions=transactions,
                             is_first_ad=is_first_ad)
    finally:
        return_db(conn)


@main_bp.route('/check_cooldown/<int:ad_id>')
@login_required
def check_cooldown(ad_id):
    """API endpoint to check cooldown status"""
    is_cooldown, seconds_left, last_watched = get_ad_cooldown_info(current_user.id, ad_id)
    
    return jsonify({
        'on_cooldown': is_cooldown,
        'seconds_remaining': seconds_left,
        'minutes_remaining': seconds_left // 60,
        'last_watched': last_watched.isoformat() if last_watched else None
    })


@main_bp.route('/watch_ad/<int:ad_id>')
@login_required
def watch_ad(ad_id):
    # STRICT COOLDOWN CHECK
    is_cooldown, seconds_left, last_watched = get_ad_cooldown_info(current_user.id, ad_id)
    
    if is_cooldown:
        minutes_left = (seconds_left // 60) + 1
        flash(f'⏳ This ad is on cooldown! Wait {minutes_left} more minute(s)', 'warning')
        print(f"🚫 BLOCKED: User {current_user.id} tried to watch ad {ad_id} on cooldown ({seconds_left}s left)")
        return redirect(url_for('main.dashboard'))
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ads WHERE id = %s", (ad_id,))
        ad = cursor.fetchone()
        cursor.close()
        
        if not ad:
            flash('Ad not found', 'danger')
            return redirect(url_for('main.dashboard'))
        
        reward_info = calculate_ad_reward(ad, current_user.id)
        
        print(f"✅ ALLOWED: User {current_user.id} watching ad {ad_id}")
        
        return render_template('main/watch_ad.html', 
                             ad=ad, 
                             reward_info=reward_info)
    finally:
        return_db(conn)


@main_bp.route('/complete_ad/<int:ad_id>', methods=['POST'])
@login_required
def complete_ad(ad_id):
    # DOUBLE CHECK COOLDOWN BEFORE COMPLETING
    is_cooldown, seconds_left, last_watched = get_ad_cooldown_info(current_user.id, ad_id)
    
    if is_cooldown:
        print(f"🚫 BLOCKED COMPLETION: User {current_user.id} tried to complete ad {ad_id} on cooldown")
        return jsonify({'error': f'Ad is on cooldown. Wait {seconds_left} seconds'}), 403
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        
        # Get ad details
        cursor.execute("""
            SELECT reward, title, 
                   COALESCE(ad_type, type, 'demo') as ad_type, 
                   duration 
            FROM ads WHERE id = %s
        """, (ad_id,))
        ad = cursor.fetchone()
        
        if not ad:
            cursor.close()
            return jsonify({'error': 'Ad not found'}), 404
        
        # Calculate reward
        reward_info = calculate_ad_reward(ad, current_user.id)
        final_reward = reward_info['total']
        
        description = f"Watched: {ad['title']}"
        if reward_info['bonus'] > 0:
            bonus_text = ", ".join(reward_info['bonus_details'])
            description += f" ({bonus_text})"
        
        # CRITICAL: Record the watch with timestamp
        cursor.execute("""
            INSERT INTO watched_ads (user_id, ad_id, timestamp) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            RETURNING id, timestamp
        """, (current_user.id, ad_id))
        
        watch_record = cursor.fetchone()
        
        # Insert transaction
        cursor.execute("""
            INSERT INTO transactions (user_id, type, amount, description) 
            VALUES (%s, 'earn', %s, %s)
        """, (current_user.id, final_reward, description))
        
        # Update balance
        cursor.execute("""
            UPDATE users SET balance = balance + %s WHERE id = %s
        """, (final_reward, current_user.id))
        
        conn.commit()
        
        print(f"✅ COMPLETED: User {current_user.id} watched ad {ad_id} at {watch_record['timestamp']}")
        print(f"   Reward: {final_reward} MIGP | Cooldown starts now for 5 minutes")
        
        cursor.close()
        
        response = {
            'success': True, 
            'reward': final_reward,
            'base': reward_info['base'],
            'bonus': reward_info['bonus'],
            'cooldown_until': (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
        if reward_info['bonus'] > 0:
            response['bonus_message'] = ' | '.join(reward_info['bonus_details'])
        
        return jsonify(response)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to complete ad'}), 500
    finally:
        return_db(conn)
