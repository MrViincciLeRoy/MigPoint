from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import get_db
from datetime import datetime, timedelta
from achieve.ad_providers_enhanced import ad_manager

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    today = datetime.now().strftime('%Y-%m-%d')
    today_earnings = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = 'earn' AND DATE(timestamp) = ?", 
        (current_user.id, today)
    ).fetchone()['total']
    earn_count = conn.execute(
        'SELECT COUNT(*) as count FROM transactions WHERE user_id = ? AND type = "earn"', 
        (current_user.id,)
    ).fetchone()['count']
    
    # Get total watch count from ad_impressions
    total_watched = conn.execute(
        'SELECT COUNT(*) as count FROM ad_impressions WHERE user_id = ? AND status = "completed"', 
        (current_user.id,)
    ).fetchone()['count']
    
    # Get recent transactions
    transactions = conn.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", 
        (current_user.id,)
    ).fetchall()
    
    conn.close()
    
    # Fetch available ads from ad manager
    available_ads = []
    for i in range(3):  # Try to get 3 ads
        ad = ad_manager.get_ad(user_id=current_user.id, user_country='ZA')
        if ad:
            available_ads.append(ad)
    
    return render_template('main/dashboard.html', 
                         user=user, 
                         today_earnings=today_earnings, 
                         earn_count=earn_count,
                         watched_count=total_watched, 
                         ads=available_ads,
                         all_ads_count=len(available_ads),
                         transactions=transactions)

@main_bp.route('/watch_ad/<provider>/<ad_id>')
@login_required
def watch_ad(provider, ad_id):
    """Watch an ad from a specific provider"""
    # In a real implementation, you'd retrieve the ad details
    # For now, fetch a new ad
    ad = ad_manager.get_ad(user_id=current_user.id, user_country='ZA')
    
    if not ad:
        flash('⏳ No ads available right now. Try again later!', 'warning')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/watch_ad_new.html', ad=ad)

@main_bp.route('/complete_ad', methods=['POST'])
@login_required
def complete_ad():
    """Complete ad viewing and award points"""
    from flask import request
    
    data = request.get_json()
    provider = data.get('provider')
    ad_id = data.get('ad_id')
    reward = data.get('reward', 5)
    watch_time = data.get('watch_time', 0)
    
    # IMPORTANT: Validate watch time for real ads
    # Only demo ads can be skipped
    if provider != 'demo':
        # Get the expected duration from the ad
        # In production, you'd verify this against the actual ad data
        expected_duration = data.get('expected_duration', 30)
        
        # Require at least 90% completion for real ads
        minimum_watch_time = expected_duration * 0.9
        
        if watch_time < minimum_watch_time:
            return jsonify({
                'error': 'Insufficient watch time',
                'message': f'You must watch at least {int(minimum_watch_time)} seconds'
            }), 400
    
    try:
        conn = get_db()
        
        # Award points
        conn.execute(
            'INSERT INTO transactions (user_id, type, amount, description) VALUES (?, ?, ?, ?)',
            (current_user.id, 'earn', reward, f"Watched: {provider} ad")
        )
        conn.execute(
            'UPDATE users SET balance = balance + ? WHERE id = ?', 
            (reward, current_user.id)
        )
        
        conn.commit()
        conn.close()
        
        # Track completion
        ad_manager.complete_ad(provider, ad_id, current_user.id, watch_time)
        
        return jsonify({'success': True, 'reward': reward})
        
    except Exception as e:
        print(f"Error completing ad: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/ad_providers')
@login_required
def ad_providers():
    """Show status of all ad providers"""
    providers = ad_manager.get_enabled_providers()
    stats = ad_manager.get_provider_stats()
    
    return render_template('main/ad_providers.html', 
                         providers=providers,
                         stats=stats)

@main_bp.route('/test_ad')
@login_required
def test_ad():
    """Test endpoint to fetch ad from all providers"""
    results = []
    
    for provider in ad_manager.providers:
        if provider.enabled:
            print(f"\n{'='*60}")
            print(f"Testing: {provider.name}")
            print(f"{'='*60}")
            
            ad = provider.fetch_ad(user_country='ZA')
            results.append({
                'provider': provider.name,
                'enabled': provider.enabled,
                'success': ad is not None,
                'ad': ad
            })
    
    return jsonify({
        'results': results,
        'timestamp': datetime.now().isoformat()
    })
