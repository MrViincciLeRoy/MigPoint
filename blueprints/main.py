from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from models import get_db_connection, convert_query, safe_row_access
from datetime import datetime, timedelta
from adsterra_provider import AdManager
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize ad managers
ad_manager = AdManager(
    ad_unit_id=os.getenv('ADSTERRA_AD_UNIT_ID'),
    publisher_id=os.getenv('ADSTERRA_PUBLISHER_ID')
)

main_bp = Blueprint('main', __name__)


def get_ad_cooldown_info(user_id, ad_id):
    """
    Check if an ad is on cooldown for a user
    Returns: (is_on_cooldown: bool, seconds_remaining: int, last_watched: datetime)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get the most recent watch for this user + ad combo
        cursor.execute(convert_query("""
            SELECT timestamp,
                   EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - timestamp)) as seconds_ago
            FROM watched_ads 
            WHERE user_id = %s AND ad_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """), (user_id, ad_id))
        
        result = cursor.fetchone()
        
        if not result:
            # Never watched this ad
            return False, 0, None
        
        seconds_ago = int(safe_row_access(result, 'seconds_ago', 0))
        cooldown_seconds = 1 * 60  # 1 minute
        
        if seconds_ago < cooldown_seconds:
            # Still on cooldown
            seconds_remaining = cooldown_seconds - seconds_ago
            return True, seconds_remaining, safe_row_access(result, 'timestamp', 1)
        else:
            # Cooldown expired
            return False, 0, safe_row_access(result, 'timestamp', 1)


def calculate_ad_reward(ad_data, user_id):
    """Calculate dynamic reward based on ad type and user bonuses"""
    base_reward = float(ad_data['reward'])
    bonus_amount = 0.0
    bonus_details = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if first ad today (50% bonus)
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(convert_query("""
            SELECT COUNT(*) as count FROM transactions 
            WHERE user_id = %s 
            AND type = 'earn'
            AND DATE(timestamp) = %s
        """), (user_id, today))
        
        is_first_ad = safe_row_access(cursor.fetchone(), 'count', 0) == 0
        
        if is_first_ad:
            first_ad_bonus = base_reward * 0.5
            bonus_amount += first_ad_bonus
            bonus_details.append(f"🎁 First ad today: +{first_ad_bonus:.1f} MIGP")
        
        # Check for 7-day streak (30% bonus)
        streak_days = 0
        for i in range(7):
            check_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute(convert_query("""
                SELECT COUNT(*) as count FROM transactions
                WHERE user_id = %s
                AND type = 'earn'
                AND DATE(timestamp) = %s
            """), (user_id, check_date))
            
            if safe_row_access(cursor.fetchone(), 'count', 0) > 0:
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
    # Don't process any earned parameters from URL - this prevents tampering
    # Rewards are only recorded via the /complete_ad route in the database
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Get user stats
        cursor.execute(convert_query("""
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
        """), (today, current_user.id))
        
        result = cursor.fetchone()
        user = result
        today_earnings = safe_row_access(result, 'today_earnings', 6)
        earn_count = safe_row_access(result, 'earn_count', 7)
        watched_count = safe_row_access(result, 'watched_count', 8)
        is_first_ad = today_earnings == 0
        
        # Fetch fresh ads from Adsterra/Demo (not from database)
        # Generate 4 fresh ad options for the user
        ads_with_cooldown = []
        
        # Add Adsterra ads (4 ads)
        for i in range(4):
            ad = ad_manager.get_ad(ad_format='native', user_id=current_user.id, user_country='ZA')
            if ad:
                ad_dict = dict(ad)
                ad_dict['id'] = f'adsterra_{i}'
                ad_dict['is_on_cooldown'] = False
                ad_dict['cooldown_seconds'] = 0
                ad_dict['last_watched'] = None
                ads_with_cooldown.append(ad_dict)
                print(f"✅ Added Adsterra ad {i}. Total ads: {len(ads_with_cooldown)}")
        
        print(f"📊 Final ads list: {len(ads_with_cooldown)} ads")
        for ad in ads_with_cooldown:
            print(f"   - {ad.get('provider')} : {ad.get('title')}")
        
        # Get recent transactions
        cursor.execute(convert_query("""
            SELECT * FROM transactions 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT 10
        """), (current_user.id,))
        transactions = cursor.fetchall()
        
        return render_template('main/dashboard.html', 
                             user=user, 
                             today_earnings=today_earnings, 
                             earn_count=earn_count,
                             watched_count=watched_count, 
                             all_ads=ads_with_cooldown,
                             transactions=transactions,
                             is_first_ad=is_first_ad)


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


@main_bp.route('/watch_ad_page')
@login_required
def watch_ad_page():
    """Display the ad watching page"""
    return render_template('main/watch_ad.html')


@main_bp.route('/watch_ad', methods=['POST'])
@login_required
def watch_ad():
    """Watch an ad (accepts POST with ad data)"""
    try:
        data = request.get_json()
        
        provider = data.get('provider', 'demo')
        
        # Debug: log incoming ad data
        print(f"\n📨 INCOMING AD DATA:")
        print(f"   provider: {provider}")
        print(f"   title: {data.get('title')}")
        
        # Handle Adsterra and other ads
        ad = {
                'id': data.get('ad_id', 'adsterra_0'),
                'title': data.get('title', 'Ad'),
                'description': data.get('description', ''),
                'advertiser': data.get('advertiser', ''),
                'image_url': data.get('image_url', ''),
                'reward': float(data.get('reward', 2.1)),
                'duration': int(data.get('duration', 10)),  # Changed default from 30 to 10
                'provider': data.get('provider', 'demo'),
                'format': data.get('format', 'native'),
                'click_url': data.get('click_url'),
                'impression_url': data.get('impression_url'),
                # Preserve Adsterra embed data
                'is_embed': data.get('is_embed', False),
                'embed_script': data.get('embed_script'),
                'embed_container': data.get('embed_container'),
                'embed_script_id': data.get('embed_script_id'),
                'ad_unit_id': data.get('ad_unit_id'),
                'unit_name': data.get('unit_name'),
                'ecpm': data.get('ecpm'),
                'type': data.get('type')
            }
        
        # Calculate bonuses
        base_reward = ad['reward']
        bonus_amount = 0.0
        bonus_details = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if first ad today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(convert_query("""
                SELECT COUNT(*) as count FROM transactions 
                WHERE user_id = %s AND type = 'earn' AND DATE(timestamp) = %s
            """), (current_user.id, today))
            
            is_first_ad = safe_row_access(cursor.fetchone(), 'count', 0) == 0
            
            if is_first_ad:
                first_ad_bonus = base_reward * 0.5
                bonus_amount += first_ad_bonus
                bonus_details.append(f"🎁 First ad today: +{first_ad_bonus:.1f} MIGP")
            
            # Weekend bonus
            is_weekend = datetime.now().weekday() in [5, 6]
            if is_weekend:
                weekend_bonus = base_reward * 0.2
                bonus_amount += weekend_bonus
                bonus_details.append(f"🎉 Weekend bonus: +{weekend_bonus:.1f} MIGP")
        
        total_reward = base_reward + bonus_amount
        
        reward_info = {
            'base': round(base_reward, 1),
            'bonus': round(bonus_amount, 1),
            'total': round(total_reward, 1),
            'bonus_details': bonus_details,
            'provider': ad['provider']
        }
        
        print(f"✅ ALLOWED: User {current_user.id} watching ad '{ad['title']}' from {ad['provider']}")
        
        return jsonify({
            'success': True,
            'ad': ad,
            'reward_info': reward_info
        })
    
    except Exception as e:
        print(f"❌ ERROR in watch_ad: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400


@main_bp.route('/complete_ad', methods=['POST'])
@login_required
def complete_ad():
    """Complete watching an ad and award points"""
    try:
        # Get the ad data from the request
        data = request.get_json() or {}
        
        ad_id = data.get('ad_id', 'unknown')
        ad_title = data.get('title', 'Ad')
        ad_reward = float(data.get('reward', 2.1))
        provider = data.get('provider', 'demo')
        watch_time = int(data.get('watch_time', 30))
        
        print(f"📝 Completing ad: {ad_title} ({provider}) - Watch time: {watch_time}s")
        
        # Calculate reward with bonuses
        base_reward = ad_reward
        bonus_amount = 0.0
        bonus_details = []
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if first ad today (50% bonus)
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(convert_query("""
                SELECT COUNT(*) as count FROM transactions 
                WHERE user_id = %s 
                AND type = 'earn'
                AND DATE(timestamp) = %s
            """), (current_user.id, today))
            
            is_first_ad = safe_row_access(cursor.fetchone(), 'count', 0) == 0
            
            if is_first_ad:
                first_ad_bonus = base_reward * 0.5
                bonus_amount += first_ad_bonus
                bonus_details.append(f"🎁 First ad today: +{first_ad_bonus:.1f} MIGP")
            
            # Check if weekend (20% bonus)
            is_weekend = datetime.now().weekday() in [5, 6]
            if is_weekend:
                weekend_bonus = base_reward * 0.2
                bonus_amount += weekend_bonus
                bonus_details.append(f"🎉 Weekend bonus: +{weekend_bonus:.1f} MIGP")
        
        total_reward = base_reward + bonus_amount
        
        description = f"Watched: {ad_title}"
        if bonus_details:
            bonus_text = ", ".join(bonus_details)
            description += f" ({bonus_text})"
        
        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Record the watch (using ad_id as string since Adsterra ads have string IDs)
            cursor.execute(convert_query("""
                INSERT INTO watched_ads (user_id, ad_id, timestamp) 
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                RETURNING id, timestamp
            """), (current_user.id, str(ad_id)))
            
            watch_record = cursor.fetchone()
            
            # Insert transaction
            cursor.execute(convert_query("""
                INSERT INTO transactions (user_id, type, amount, description) 
                VALUES (%s, 'earn', %s, %s)
            """), (current_user.id, total_reward, description))
            
            # Update balance
            cursor.execute(convert_query("""
                UPDATE users SET balance = balance + %s WHERE id = %s
            """), (total_reward, current_user.id))
            
            conn.commit()
        
        timestamp = safe_row_access(watch_record, 'timestamp', 1)
        print(f"✅ COMPLETED: User {current_user.id} watched {provider} ad '{ad_title}' at {timestamp}")
        print(f"   Reward: {total_reward} MIGP (Base: {base_reward}, Bonus: {bonus_amount})")
        
        response = {
            'success': True, 
            'reward': total_reward,
            'base': round(base_reward, 1),
            'bonus': round(bonus_amount, 1),
            'provider': provider,
            'cooldown_until': (datetime.now() + timedelta(minutes=1)).isoformat()
        }
        
        if bonus_details:
            response['bonus_message'] = ' | '.join(bonus_details)
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to complete ad'}), 500
