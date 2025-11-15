"""
clickadu_blueprint.py - Clickadu Ad Routes
Handles Clickadu ad serving and tracking
"""

from flask import Blueprint, render_template_string, request, jsonify
from clickadu_provider import ClickaduProvider
from config_clickadu import ClickaduConfig

clickadu_bp = Blueprint('clickadu', __name__, url_prefix='/clickadu')
provider = ClickaduProvider()

@clickadu_bp.route('/ad/<placement>', methods=['GET'])
def get_ad(placement):
    """Get Clickadu ad code for a placement"""
    ad_code = provider.get_ad_code(placement)
    return jsonify(ad_code)

@clickadu_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get Clickadu statistics"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        group_by = request.args.get('group_by', 'geo')
        
        stats = provider.get_stats(date_from, date_to, group_by)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@clickadu_bp.route('/track/impression', methods=['POST'])
def track_impression():
    """Track ad impression"""
    data = request.get_json()
    zone_id = data.get('zone_id')
    user_id = data.get('user_id')
    
    result = provider.track_impression(zone_id, user_id)
    return jsonify(result)

@clickadu_bp.route('/track/click', methods=['POST'])
def track_click():
    """Track ad click"""
    data = request.get_json()
    zone_id = data.get('zone_id')
    user_id = data.get('user_id')
    
    result = provider.track_click(zone_id, user_id)
    return jsonify(result)

@clickadu_bp.route('/config', methods=['GET'])
def get_config():
    """Get Clickadu configuration"""
    return jsonify({
        'enabled': ClickaduConfig.is_enabled(),
        'zones': ClickaduConfig.ZONES,
        'script_url': ClickaduConfig.SCRIPT_URL
    })
