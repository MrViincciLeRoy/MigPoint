"""
clickadu_provider.py - Clickadu Integration
Provides Clickadu native ads and banners
"""

import requests
import json
from datetime import datetime
from config_clickadu import ClickaduConfig

class ClickaduProvider:
    """Clickadu ad provider integration"""
    
    def __init__(self):
        self.api_token = ClickaduConfig.API_TOKEN
        self.zones = ClickaduConfig.ZONES
        self.script_url = ClickaduConfig.SCRIPT_URL
    
    def get_ad_code(self, placement='dashboard_top'):
        """
        Generate Clickadu ad code for a placement
        
        Args:
            placement: Zone placement identifier
            
        Returns:
            dict with ad code and metadata
        """
        zone_config = ClickaduConfig.get_zone(placement)
        
        if not zone_config:
            return {
                'success': False,
                'error': f'Invalid placement: {placement}'
            }
        
        try:
            zone_id = zone_config['zone_id']
            
            # Generate the ad container HTML
            ad_code = {
                'success': True,
                'zone_id': zone_id,
                'placement': placement,
                'format': zone_config['format'],
                'html': self._generate_html(zone_id),
                'script': self._generate_script_tag(zone_id),
                'ecpm': zone_config['ecpm'],
                'timestamp': datetime.now().isoformat()
            }
            
            return ad_code
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_html(self, zone_id):
        """Generate Clickadu ad container HTML"""
        return f'''
        <div class="clickadu-ad-container" data-zone="{zone_id}">
            <div id="clickadu-zone-{zone_id}"></div>
        </div>
        '''
    
    def _generate_script_tag(self, zone_id):
        """Generate Clickadu script tag"""
        return f'''
        <script>
            (function() {{
                var script = document.createElement('script');
                script.src = '{self.script_url}';
                script.async = true;
                script.onload = function() {{
                    if (window.ClickaduDisplay) {{
                        window.ClickaduDisplay.displayZone('{zone_id}');
                    }}
                }};
                document.head.appendChild(script);
            }})();
        </script>
        '''
    
    def get_stats(self, date_from=None, date_to=None, group_by='geo'):
        """
        Get Clickadu statistics from API
        
        Args:
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            group_by: Group statistics by attribute
            
        Returns:
            dict with stats data
        """
        try:
            params = {
                'token': self.api_token,
                'format': 'json',
                'groupBy': group_by
            }
            
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
            
            response = requests.get(
                ClickaduConfig.API_ENDPOINTS['stats'],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def track_impression(self, zone_id, user_id=None):
        """Track ad impression"""
        return {
            'zone_id': zone_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'event': 'impression'
        }
    
    def track_click(self, zone_id, user_id=None):
        """Track ad click"""
        return {
            'zone_id': zone_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'event': 'click'
        }
